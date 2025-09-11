import base64
import json
import os
import urllib.request

ADMIN_API = os.environ.get("ADMIN_API_URL")
API_BEARER = os.environ.get("API_BEARER", "")

def call_rollback():
    """Calls the admin API to trigger a model rollback."""
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

    except Exception as e:
        print(f"An error occurred while processing the alert: {e}")
        # Re-raising the exception can be useful for triggering retries
        # or for surfacing the error in Cloud Functions logs.
        raise
