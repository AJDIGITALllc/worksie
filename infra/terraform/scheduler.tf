resource "google_cloud_scheduler_job" "synthetic_ping_inference" {
  project     = var.project_id
  name        = "synthetic-ping-inference"
  schedule    = "*/5 * * * *"  # every 5 minutes
  time_zone   = "UTC"

  http_target {
    uri         = "https://${var.inference_domain}/synthetic"
    http_method = "GET"
    oidc_token {
      service_account_email = google_service_account.rollback_fn_sa.email
      audience              = "https://${var.inference_domain}"
    }
  }
}

resource "google_cloud_scheduler_job" "synthetic_ping_api" {
  project     = var.project_id
  name        = "synthetic-ping-api"
  schedule    = "*/5 * * * *"
  time_zone   = "UTC"

  http_target {
    uri         = "https://${var.api_domain}/synthetic"
    http_method = "GET"
    oidc_token {
      service_account_email = google_service_account.rollback_fn_sa.email
      audience              = "https://${var.api_domain}"
    }
  }
}
