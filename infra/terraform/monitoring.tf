resource "google_monitoring_dashboard" "inference_ops" {
  project = var.project_id
  dashboard_json = <<EOF
{
  "displayName": "Worksie — Inference Ops",
  "gridLayout": {
    "columns": "2",
    "widgets": [
      {
        "title": "Cloud Run P50/P95 Latency (worksie-inference)",
        "xyChart": {
          "chartOptions": { "mode": "COLOR" },
          "dataSets": [
            {
              "plotType": "LINE",
              "legendTemplate": "P50",
              "minAlignmentPeriod": "60s",
              "timeSeriesQuery": {
                "timeSeriesFilter": {
                  "filter": "metric.type=\\"run.googleapis.com/request_latencies\\" resource.type=\\"cloud_run_revision\\" resource.label.\\"service_name\\"=\\"worksie-inference\\"",
                  "aggregation": { "perSeriesAligner": "ALIGN_PERCENTILE_50", "alignmentPeriod": "60s" },
                  "secondaryAggregation": { "perSeriesAligner": "ALIGN_MEAN" }
                }
              }
            },
            {
              "plotType": "LINE",
              "legendTemplate": "P95",
              "minAlignmentPeriod": "60s",
              "timeSeriesQuery": {
                "timeSeriesFilter": {
                  "filter": "metric.type=\\"run.googleapis.com/request_latencies\\" resource.type=\\"cloud_run_revision\\" resource.label.\\"service_name\\"=\\"worksie-inference\\"",
                  "aggregation": { "perSeriesAligner": "ALIGN_PERCENTILE_95", "alignmentPeriod": "60s" },
                  "secondaryAggregation": { "perSeriesAligner": "ALIGN_MEAN" }
                }
              }
            }
          ],
          "yAxis": { "label": "ms", "scale": "LINEAR" }
        }
      },
      {
        "title": "Request Rate & 5xx Error %",
        "xyChart": {
          "dataSets": [
            {
              "legendTemplate": "Requests",
              "timeSeriesQuery": {
                "timeSeriesFilter": {
                  "filter": "metric.type=\\"run.googleapis.com/request_count\\" resource.type=\\"cloud_run_revision\\" resource.label.\\"service_name\\"=\\"worksie-inference\\"",
                  "aggregation": { "alignmentPeriod":"60s","perSeriesAligner":"ALIGN_RATE" }
                }
              }
            },
            {
              "legendTemplate": "5xx %",
              "timeSeriesQuery": {
                "timeSeriesFilter": {
                  "filter": "metric.type=\\"run.googleapis.com/request_count\\" resource.type=\\"cloud_run_revision\\" resource.label.\\"service_name\\"=\\"worksie-inference\\" metric.label.\\"response_code_class\\"=\\"5xx\\"",
                  "aggregation": { "alignmentPeriod":"60s","perSeriesAligner":"ALIGN_RATE" }
                },
                "unitOverride": "%"
              }
            }
          ]
        }
      },
      {
        "title": "Pub/Sub Backlog: refine-jobs",
        "xyChart": {
          "dataSets": [
            {
              "legendTemplate": "Backlog msgs",
              "timeSeriesQuery": {
                "timeSeriesFilter": {
                  "filter": "metric.type=\\"pubsub.googleapis.com/subscription/num_undelivered_messages\\" resource.label.\\"subscription_id\\"=\\"refine-jobs-sub\\""
                }
              }
            }
          ]
        }
      },
      {
        "title": "Model Split (custom metric)",
        "pieChart": {
          "dataSets": [
            {
              "timeSeriesQuery": {
                "timeSeriesFilter": {
                  "filter": "metric.type=\\"custom.googleapis.com/worksie/inference/model_served\\""
                }
              }
            }
          ]
        }
      }
    ]
  }
}
EOF
}
