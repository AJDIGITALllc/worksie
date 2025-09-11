import base64
import json
import os
import urllib.request
from datetime import datetime, timedelta, timezone
from google.cloud import firestore
from google.oauth2 import id_token
from google.auth.transport import requests as grequests

ADMIN_API_BASE_URL = os.environ.get("ADMIN_API_URL")
ADMIN_API_AUDIENCE = os.environ.get("ADMIN_API_AUDIENCE")
DEBOUNCE_MINUTES = 15

db = firestore.Client()

def get_id_token():
    """Fetches a Google-signed ID token for the specified audience."""
    if not ADMIN_API_AUDIENCE:
        raise ValueError("ADMIN_API_AUDIENCE environment variable not set.")
    return id_token.fetch_id_token(grequests.Request(), ADMIN_API_AUDIENCE)

def get_active_model_id_from_firestore():
    """Fetches the currently active model ID directly from Firestore."""
    q = db.collection("model_registry").where("isActive", "==", True).limit(1).stream()
    active_models = list(q)
    if not active_models:
        raise RuntimeError("No active model found in Firestore.")
    return active_models[0].id

def call_rollback():
    """Calls the admin API to trigger a model rollback."""
    if not ADMIN_API_BASE_URL:
        raise ValueError("ADMIN_API_URL is not set.")

    token = get_id_token()
    url = f"{ADMIN_API_BASE_URL}/v1/admin/models/rollback"
    req = urllib.request.Request(
        url,
        data=json.dumps({}).encode("utf-8"), # Rollback to previous model by default
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        print(f"Admin API response: {resp.read().decode('utf-8')}")
        return resp.status

def clamp_canary():
    """Calls the promote endpoint to set the canary rollout ratio to 0."""
    active_model_id = get_active_model_id_from_firestore()
    if not active_model_id:
        raise ValueError("Could not determine active model ID to clamp.")

    token = get_id_token()
    url = f"{ADMIN_API_BASE_URL}/v1/admin/models/promote"
    payload = {
        "modelId": active_model_id,
        "rolloutRatio": 0.0,
        "notes": f"auto-clamp of {active_model_id} to 0% due to 5xx error rate alert"
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        print(f"Admin API response for clamping canary: {resp.read().decode('utf-8')}")
        return resp.status

def entrypoint(event, context):
    """
    Cloud Function entry point that is triggered by a Pub/Sub message.
    """
    print(f"Received event: {event}")

    # --- Dry-Run Mode Logic ---
    is_dry_run = os.environ.get("AUTO_ROLLBACK_DRYRUN", "false").lower() == "true"
    if is_dry_run:
        print("DRY RUN: Auto-rollback would be triggered, but is in dry-run mode. No action taken.")
        return

    # --- Debounce Logic ---
    now = datetime.now(timezone.utc)
    debounce_ref = db.collection("ops").document("last_rollback_ts")
    debounce_doc = debounce_ref.get()

    if debounce_doc.exists:
        last_rollback_ts = debounce_doc.to_dict().get("timestamp")
        if last_rollback_ts and (now - last_rollback_ts) < timedelta(minutes=DEBOUNCE_MINUTES):
            print(f"Rollback triggered recently. Debouncing for {DEBOUNCE_MINUTES} minutes. Ignoring alert.")
            return
    # --- End Debounce Logic ---

    try:
        if 'data' not in event:
            print("No 'data' field in the event payload. Ignoring.")
            return

        data = base64.b64decode(event["data"]).decode("utf-8")
        alert = json.loads(data)
        alert_text = json.dumps(alert)

        # Determine mitigation strategy based on alert type
        if "5xx" in alert_text:
            print("5xx error rate alert received. Clamping canary to 0%.")
            status = clamp_canary()
            print(f"Canary clamp triggered. Admin API status code: {status}")
        elif "run.googleapis.com/request_latencies" in alert_text or "p95_latency_slo" in alert_text:
            print("Latency alert received. Triggering full rollback...")
            status = call_rollback()
            print(f"Rollback triggered. Admin API status code: {status}")
        else:
            print("Ignoring alert that is not a latency or 5xx alert.")
            return

        # If mitigation was successful, update the timestamp
        if 200 <= status < 300:
            debounce_ref.set({"timestamp": now})
            print(f"Updated debounce timestamp to {now.isoformat()}")

    except Exception as e:
        print(f"An error occurred while processing the alert: {e}")
        raise
