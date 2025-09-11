resource "google_monitoring_alert_policy" "error_rate_5xx" {
  project      = var.project_id
  display_name = "SLO: Inference 5xx > 5% (auto-rollback candidate)"
  combiner     = "OR"

  conditions {
    display_name = "5xx ratio > 5% for 5m"
    condition_monitoring_query_language {
      duration = "300s" # 5 minutes sustained
      query    = <<-MQL
        # Rate of total requests
        total = fetch run_revision
          | metric 'run.googleapis.com/request_count'
          | filter resource.service_name == 'worksie-inference'
          | align rate(1m)
          | every 1m;

        # Rate of 5xx requests
        errors = fetch run_revision
          | metric 'run.googleapis.com/request_count'
          | filter resource.service_name == 'worksie-inference'
          | filter metric.response_code_class == '5xx'
          | align rate(1m)
          | every 1m;

        # Ratio in percent
        join (errors, total)
          | value val(0) / val(1) * 100
      MQL
      trigger { count = 1 }
      comparison = "COMPARISON_GT"
      threshold_value = 5
    }
  }

  notification_channels = [
    google_monitoring_notification_channel.inference_latency_pubsub.name
  ]

  documentation {
    content  = "Auto-mitigate high 5xx by reducing canary or rolling back. See audit_events for promote/rollback trail."
    mime_type = "text/markdown"
  }

  enabled = true
}
