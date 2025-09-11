variable "worksie_assets_bucket_name" {
  description = "The name of the GCS bucket for Worksie assets."
  type        = string
}

variable "admin_api_url" {
  description = "The URL of the admin API for the rollback function to call."
  type        = string
}

variable "admin_api_audience" {
  description = "The audience for the Google-signed ID token."
  type        = string
}


resource "google_pubsub_topic" "alerts_inference_latency" {
  project = var.project_id
  name    = "alerts-inference-latency"
}

resource "google_pubsub_subscription" "alerts_inference_latency_sub" {
  project = var.project_id
  name    = "alerts-inference-latency-sub"
  topic   = google_pubsub_topic.alerts_inference_latency.name
  ack_deadline_seconds = 30
}

resource "google_monitoring_alert_policy" "p95_latency_slo" {
  project      = var.project_id
  display_name = "SLO: Inference P95 > 3s (auto-rollback)"
  combiner     = "OR"
  conditions {
    display_name = "Cloud Run P95 > 3s"
    condition_threshold {
      filter = <<-EOT
        metric.type="run.googleapis.com/request_latencies"
        resource.type="cloud_run_revision"
        resource.label."service_name"="worksie-inference"
      EOT
      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_PERCENTILE_95"
        cross_series_reducer = "REDUCE_MEAN"
        group_by_fields = [
          "resource.label.project_id",
          "resource.label.service_name"
        ]
      }
      duration = "300s" # sustained 5 minutes
      comparison = "COMPARISON_GT"
      threshold_value = 3000
      trigger { count = 1 }
    }
  }

  notification_channels = [
    google_monitoring_notification_channel.inference_latency_pubsub.name
  ]

  documentation {
    content  = "Auto-rollback if P95 latency sustained > 3s."
    mime_type = "text/markdown"
  }

  enabled = true
}

resource "google_monitoring_notification_channel" "inference_latency_pubsub" {
  project      = var.project_id
  display_name = "PubSub: alerts-inference-latency"
  type         = "pubsub"
  labels = {
    topic = google_pubsub_topic.alerts_inference_latency.id
  }
}

resource "google_service_account" "rollback_fn_sa" {
  project      = var.project_id
  account_id   = "slo-rollback-fn"
  display_name = "SLO Auto Rollback Function SA"
}

resource "google_project_iam_member" "fn_pubsub_subscriber" {
  project = var.project_id
  role    = "roles/pubsub.subscriber"
  member  = "serviceAccount:${google_service_account.rollback_fn_sa.email}"
}

resource "google_cloudfunctions2_function" "slo_rollback_fn" {
  project     = var.project_id
  name        = "slo-rollback-fn"
  location    = var.region
  description = "Consumes Monitoring alerts and triggers model rollback"

  build_config {
    runtime     = "python311"
    entry_point = "entrypoint"
    source {
      storage_source {
        bucket = var.worksie_assets_bucket_name
        object = "functions/slo-rollback-fn.zip"
      }
    }
  }

  service_config {
    available_memory    = "256M"
    timeout_seconds     = 30
    environment_variables = {
      ADMIN_API_URL          = var.admin_api_url
      ADMIN_API_AUDIENCE     = var.admin_api_audience
      AUTO_ROLLBACK_DRYRUN   = "false"
    }
    service_account_email = google_service_account.rollback_fn_sa.email
  }

  event_trigger {
    trigger_region = var.region
    event_type     = "google.cloud.pubsub.topic.v1.messagePublished"
    pubsub_topic   = google_pubsub_topic.alerts_inference_latency.id
    retry_policy   = "RETRY_POLICY_RETRY"
  }
}
