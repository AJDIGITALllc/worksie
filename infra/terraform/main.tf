variable "project_id" {
  description = "The GCP project ID."
  type        = string
}

variable "region" {
  description = "The GCP region for resources."
  type        = string
  default     = "us-central1"
}

variable "promoter_image" {
  description = "The Docker image for the model promoter service."
  type        = string
}

resource "google_pubsub_topic" "promote_model" {
  project = var.project_id
  name    = "promote-model"
}

resource "google_pubsub_topic" "audit_events" {
  project = var.project_id
  name    = "audit-events"
}

resource "google_cloud_run_v2_job" "model_promoter" {
  project  = var.project_id
  name     = "model-promoter"
  location = var.region
  template {
    template {
      containers {
        image = var.promoter_image
        env {
          name  = "PROJECT_ID"
          value = var.project_id
        }
      }
    }
  }
}
