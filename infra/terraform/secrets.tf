resource "google_secret_manager_secret" "admin_api_bearer" {
  project   = var.project_id
  secret_id = "admin-api-bearer"

  replication {
    automatic = true
  }
}

# Grant the rollback function's service account access to the secret.
# The SA is defined in alerts.tf
resource "google_secret_manager_secret_iam_member" "admin_api_bearer_access" {
  project   = var.project_id
  secret_id = google_secret_manager_secret.admin_api_bearer.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.rollback_fn_sa.email}"
}
