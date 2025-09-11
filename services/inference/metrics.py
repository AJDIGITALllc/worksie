from google.cloud import monitoring_v3
import time
import os
import sys

# Initialize clients once to be reused.
try:
    client = monitoring_v3.MetricServiceClient()
    # GOOGLE_CLOUD_PROJECT should be automatically available in any GCP environment.
    project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
    if not project_id:
        raise ValueError("GOOGLE_CLOUD_PROJECT environment variable not set.")
    project_name = f"projects/{project_id}"
except Exception as e:
    print(f"Failed to initialize Monitoring client: {e}", file=sys.stderr)
    client = None
    project_name = None

def record_model_served(model_version: str):
    """
    Records a custom metric to Cloud Monitoring indicating which model version was served.
    """
    if not client or not project_name:
        print("Monitoring client not available. Skipping metric recording.", file=sys.stderr)
        return

    series = monitoring_v3.TimeSeries()
    series.metric.type = "custom.googleapis.com/worksie/inference/model_served"
    series.metric.labels["model_version"] = model_version

    # Using "global" resource type for simplicity.
    # In a real-world scenario, you might want to associate this with the
    # specific Cloud Run revision or other resource.
    series.resource.type = "global"
    series.resource.labels["project_id"] = project_id

    # Create a data point.
    point = monitoring_v3.Point()
    point.value.int64_value = 1
    now = time.time()
    point.interval.end_time.seconds = int(now)
    point.interval.end_time.nanos = int((now - point.interval.end_time.seconds) * 10**9)
    series.points = [point]

    try:
        client.create_time_series(name=project_name, time_series=[series])
        print(f"Successfully recorded metric for model: {model_version}")
    except Exception as e:
        print(f"Error creating time series: {e}", file=sys.stderr)
