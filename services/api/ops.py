from fastapi import APIRouter
from google.cloud import monitoring_v3, firestore
import os
import time

router = APIRouter(prefix="/v1/ops", tags=["ops"])
monitoring_client = monitoring_v3.MetricServiceClient()
db = firestore.Client()
PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
CACHE = {"p95": (0, [])}  # (ts, series)

def fetch_p95_series(minutes=30):
    if not PROJECT:
        raise ValueError("GOOGLE_CLOUD_PROJECT environment variable not set.")

    project_name = f"projects/{PROJECT}"
    end = time.time()
    start = end - minutes * 60
    interval = monitoring_v3.TimeInterval(
        end_time={"seconds": int(end)}, start_time={"seconds": int(start)}
    )

    request = monitoring_v3.ListTimeSeriesRequest(
        name=project_name,
        filter='metric.type="run.googleapis.com/request_latencies" '
               'resource.type="cloud_run_revision" '
               'resource.label."service_name"="worksie-inference"',
        interval=interval,
        aggregation=monitoring_v3.Aggregation(
            alignment_period={"seconds": 60},
            per_series_aligner=monitoring_v3.Aggregation.Aligner.ALIGN_PERCENTILE_95,
        ),
    )

    series = monitoring_client.list_time_series(request=request)
    points = []
    for ts in series:
        for p in ts.points:
            # The value can be in either distribution_value or double_value
            value = p.value.distribution_value.mean if p.value.WhichOneof("value") == "distribution_value" else p.value.double_value
            ms = int(value)
            t = int(p.interval.end_time.seconds)
            points.append((t, ms))

    points.sort()
    return points[-30:]

@router.get("/summary")
def ops_summary():
    # Fetch P95 latency with caching
    ts, data = CACHE["p95"]
    now = time.time()
    if now - ts > 30: # Cache for 30 seconds
        data = fetch_p95_series()
        CACHE["p95"] = (now, data)

    # Fetch current model from Firestore
    try:
        q = db.collection("model_registry").where("isActive", "==", True).limit(1).stream()
        active_models = list(q)
        if not active_models:
            model_data = {"error": "No active model found."}
        else:
            model_data = active_models[0].to_dict()
    except Exception as e:
        model_data = {"error": f"Failed to fetch model from Firestore: {e}"}

    return {"p95": data, "model": model_data}
