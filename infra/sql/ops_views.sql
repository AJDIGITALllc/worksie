-- This file contains SQL views for analyzing model audit data in BigQuery.
-- These views should be created in your GCP project after the BigQuery table has been created.
-- You can run these commands using the `bq` CLI tool or in the BigQuery UI.
--
-- IMPORTANT: Before running, you must replace all instances of `your-gcp-project-id`
-- with your actual Google Cloud project ID.

-- 1) Flattened audit events (type, who, model, rollout, ts)
CREATE OR REPLACE VIEW `your-gcp-project-id.ops.audit_events` AS
SELECT
  JSON_VALUE(data, '$.type')            AS event_type,
  JSON_VALUE(data, '$.modelId')         AS model_id,
  JSON_VALUE(data, '$.prevModelId')     AS prev_model_id,
  SAFE_CAST(JSON_VALUE(data, '$.rolloutRatio') AS FLOAT64) AS rollout_ratio,
  JSON_VALUE(data, '$.requestedBy')     AS requested_by,
  TIMESTAMP_MILLIS(SAFE_CAST(JSON_VALUE(data, '$.ts') AS INT64)) AS event_ts,
  publish_time
FROM `your-gcp-project-id.ops.audit_events_raw`;

-- 2) Daily promotions & rollbacks
CREATE OR REPLACE VIEW `your-gcp-project-id.ops.daily_model_changes` AS
SELECT
  DATE(event_ts) AS day,
  event_type,
  COUNT(*)       AS events,
  ARRAY_AGG(STRUCT(model_id, prev_model_id, rollout_ratio, requested_by, event_ts) ORDER BY event_ts DESC LIMIT 50) AS examples
FROM `your-gcp-project-id.ops.audit_events`
WHERE event_type IN ('model.promote','model.rollback')
GROUP BY day, event_type
ORDER BY day DESC, event_type;

-- 3) Canary rollout timeline (latest per day)
CREATE OR REPLACE VIEW `your-gcp-project-id.ops.canary_rollout_timeline` AS
SELECT
  DATE(event_ts) AS day,
  ANY_VALUE(model_id IGNORE NULLS) KEEP (DENSE_RANK LAST ORDER BY event_ts) AS model_id,
  ANY_VALUE(rollout_ratio) KEEP (DENSE_RANK LAST ORDER BY event_ts) AS rollout_ratio
FROM `your-gcp-project-id.ops.audit_events`
WHERE event_type = 'model.promote'
GROUP BY day
ORDER BY day;

-- 4) MTTR after auto-rollback incidents (joins alert incidents if you log them later)
-- This is a placeholder for future implementation. To make this work, you would need to
-- log alert incidents to an audit table and then join it with the rollback events.
-- CREATE OR REPLACE VIEW `your-gcp-project-id.ops.incident_response_time` AS
-- SELECT
--   t_alert.incident_id,
--   t_alert.alert_ts,
--   t_rollback.rollback_ts,
--   TIMESTAMP_DIFF(t_rollback.rollback_ts, t_alert.alert_ts, MINUTE) as minutes_to_rollback
-- FROM `your-gcp-project-id.ops.alerts` t_alert
-- JOIN `your-gcp-project-id.ops.audit_events` t_rollback
--   ON t_rollback.notes LIKE CONCAT('%auto-rollback from incident %', t_alert.incident_id, '%')
-- WHERE t_rollback.event_type = 'model.rollback';
