variable "inference_domain" {
  description = "The custom domain for the inference service."
  type        = string
}

variable "api_domain" {
  description = "The custom domain for the admin API service."
  type        = string
}

resource "google_monitoring_uptime_check_config" "inference_uptime" {
  project      = var.project_id
  display_name = "Uptime: worksie-inference /healthz"
  timeout      = "10s"
  period       = "60s"

  http_check {
    path         = "/healthz"
    port         = 443
    use_ssl      = true
    validate_ssl = true
  }

  monitored_resource {
    type = "uptime_url"
    labels = {
      host = var.inference_domain
    }
  }
}

resource "google_monitoring_uptime_check_config" "api_uptime" {
  project      = var.project_id
  display_name = "Uptime: worksie-api /healthz"
  timeout      = "10s"
  period       = "60s"

  http_check {
    path         = "/healthz"
    port         = 443
    use_ssl      = true
    validate_ssl = true
  }

  monitored_resource {
    type = "uptime_url"
    labels = {
      host = var.api_domain
    }
  }
}

resource "google_monitoring_alert_policy" "uptime_down" {
  project      = var.project_id
  display_name = "Uptime: Endpoint down (3m)"
  combiner     = "OR"

  conditions {
    display_name = "Uptime check failing"
    condition_monitoring_query_language {
      duration = "180s"
      query = <<-MQL
        fetch uptime_url
        | metric 'monitoring.googleapis.com/uptime_check/check_passed'
        | filter
            (metric.check_id == '${google_monitoring_uptime_check_config.inference_uptime.uptime_check_id}' ||
             metric.check_id == '${google_monitoring_uptime_check_config.api_uptime.uptime_check_id}')
        | group_by 1m, [value_check_passed_count: count(val())]
        | every 1m
        | condition val() < 1
      MQL
      trigger {
        count = 2 # Trigger if the condition is met for 2 consecutive minutes
      }
    }
  }

  notification_channels = [
    google_monitoring_notification_channel.inference_latency_pubsub.name
  ]
  enabled = true
}
