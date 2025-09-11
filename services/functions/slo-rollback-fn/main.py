import base64
import json
import os
import urllib.request
from datetime import datetime, timedelta, timezone
from google.cloud import firestore

ADMIN_API = os.environ.get("ADMIN_API_URL")
API_BEARER = os.environ.get("API_BEARER", "")
DEBOUNCE_MINUTES = 15

db = firestore.Client()

def call_rollback():
    """Calls the admin API to trigger a model rollback."""
    # --- Dry-Run Mode Logic ---
    is_dry_run = os.environ.get("AUTO_ROLLBACK_DRYRUN", "false").lower() == "true"
    if is_dry_run:
        print("DRY RUN: Auto-rollback would be triggered, but is in dry-run mode. No action taken.")
        # Return a success-like status so the rest of the function proceeds
        return 200
    # --- End Dry-Run Mode Logic ---

    if not ADMIN_API:
        print("ADMIN_API_URL environment variable not set. Cannot call rollback API.")
        return 500

    req = urllib.request.Request(
        ADMIN_API,
        data=json.dumps({}).encode("utf-8"), # Rollback to previous model by default
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_BEARER}"
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        print(f"Admin API response: {resp.read().decode('utf-8')}")
        return resp.status

def entrypoint(event, context):
    """
    Cloud Function entry point that is triggered by a Pub/Sub message.
    """
    print(f"Received event: {event}")

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
        # The actual data is in the 'data' field, base64 encoded.
        if 'data' not in event:
            print("No 'data' field in the event payload. Ignoring.")
            return

        data = base64.b64decode(event["data"]).decode("utf-8")
        alert = json.loads(data)

        # Check if the alert is the one we are interested in.
        # This is a simple check; a real implementation might be more robust.
        alert_text = json.dumps(alert)
        if "run.googleapis.com/request_latencies" not in alert_text and "p95_latency_slo" not in alert_text:
            print("Ignoring alert that is not a latency alert.")
            return

        print("Latency alert received. Triggering rollback...")
        status = call_rollback()
        print(f"Rollback triggered. Admin API status code: {status}")

        # If rollback was successful, update the timestamp
        if 200 <= status < 300:
            debounce_ref.set({"timestamp": now})
            print(f"Updated debounce timestamp to {now.isoformat()}")

    except Exception as e:
        print(f"An error occurred while processing the alert: {e}")
        # Re-raising the exception can be useful for triggering retries
        # or for surfacing the error in Cloud Functions logs.
        raise
