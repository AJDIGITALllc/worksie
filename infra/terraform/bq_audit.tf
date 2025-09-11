resource "google_bigquery_dataset" "ops" {
  project     = var.project_id
  dataset_id  = "ops"
  location    = var.region
  description = "Operational analytics (audit events, SLO outcomes, promotions)"
  delete_contents_on_destroy = true
}

resource "google_bigquery_table" "audit_events_raw" {
  project    = var.project_id
  dataset_id = google_bigquery_dataset.ops.dataset_id
  table_id   = "audit_events_raw"
  deletion_protection = false

  time_partitioning {
    type  = "DAY"
    field = null # Ingestion-time partitioning
  }

  schema = <<EOF
[
  {"name":"data","type":"JSON","mode":"NULLABLE"},
  {"name":"attributes","type":"JSON","mode":"NULLABLE"},
  {"name":"publish_time","type":"TIMESTAMP","mode":"NULLABLE"}
]
EOF
}

resource "google_pubsub_subscription" "audit_events_bq_sub" {
  project = var.project_id
  name    = "audit-events-bq-sub"
  topic   = google_pubsub_topic.audit_events.name

  bigquery_config {
    table              = "${google_bigquery_table.audit_events_raw.project}.${google_bigquery_table.audit_events_raw.dataset_id}.${google_bigquery_table.audit_events_raw.table_id}"
    use_topic_schema   = false
    write_metadata     = true
  }

  ack_deadline_seconds = 20
}
