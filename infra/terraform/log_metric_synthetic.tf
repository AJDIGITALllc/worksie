# Matches logs like: "SYNTHETIC api elapsed_ms=123"
resource "google_logging_metric" "synthetic_latency_api" {
  project     = var.project_id
  name        = "synthetic_latency_api_ms"
  description = "Latency (ms) extracted from API /synthetic logs"
  filter      = "resource.type=\"cloud_run_revision\" AND jsonPayload.message:\"SYNTHETIC api elapsed_ms=\" OR textPayload:\"SYNTHETIC api elapsed_ms=\""

  value_extractor = "REGEXP_EXTRACT(textPayload, \"elapsed_ms=(\\d+)\")"
  metric_descriptor {
    metric_kind = "GAUGE"
    value_type  = "INT64"
    unit        = "ms"
    display_name = "Synthetic API Latency (ms)"
  }

  label_extractors = {
    "service" = "EXTRACT(resource.labels.service_name)"
  }
}

resource "google_logging_metric" "synthetic_latency_inference" {
  project     = var.project_id
  name        = "synthetic_latency_inference_ms"
  description = "Latency (ms) extracted from Inference /synthetic logs"
  filter      = "resource.type=\"cloud_run_revision\" AND jsonPayload.message:\"SYNTHETIC inference elapsed_ms=\" OR textPayload:\"SYNTHETIC inference elapsed_ms=\""

  value_extractor = "REGEXP_EXTRACT(textPayload, \"elapsed_ms=(\\d+)\")"
  metric_descriptor {
    metric_kind = "GAUGE"
    value_type  = "INT64"
    unit        = "ms"
    display_name = "Synthetic Inference Latency (ms)"
  }

  label_extractors = {
    "service" = "EXTRACT(resource.labels.service_name)"
  }
}
