import os
import json
import time
import sys
from google.cloud import firestore

# It's good practice to initialize clients once
db = firestore.Client()

# The user prompt included a publisher client here, but the promoter worker
# only writes to Firestore and audit logs. The audit log writing function
# can initialize its own publisher. This adheres to the single responsibility
# principle for this worker.

def write_audit(event: dict):
    # Lazily initialize publisher to avoid creating it if not needed.
    from google.cloud import pubsub_v1
    publisher = pubsub_v1.PublisherClient()
    AUDIT_TOPIC = os.getenv("AUDIT_TOPIC", "projects/your-gcp-project-id/topics/audit-events")

    event["ts"] = int(time.time() * 1000)
    try:
        publisher.publish(AUDIT_TOPIC, json.dumps(event).encode("utf-8"))
    except Exception as e:
        print(f"Error publishing audit event: {e}", file=sys.stderr)


def promote(model_id: str, rollout: float, requested_by: str, notes: str):
    """Promotes a model to a given rollout ratio."""
    doc_ref = db.collection("model_registry").document(model_id)
    doc = doc_ref.get()
    if not doc.exists:
        raise ValueError(f"Model {model_id} not found in model_registry")

    # Find the current active model to link it as the previous version.
    q = db.collection("model_registry").where("isActive", "==", True).limit(1).stream()
    active_models = list(q)
    active_model_doc = active_models[0] if active_models else None
    prev_id = active_model_doc.id if active_model_doc else None

    # Use a transaction to ensure atomicity
    @firestore.transactional
    def update_in_transaction(transaction, new_model_ref, active_model_doc):
        # Deactivate the old model if it exists
        if active_model_doc:
            transaction.update(active_model_doc.reference, {"isActive": False})

        # Activate the new model and set its rollout details
        transaction.update(new_model_ref, {
            "isActive": True,
            "rolloutRatio": rollout,
            "prevModelId": prev_id,
            "notes": notes,
            "updatedAt": firestore.SERVER_TIMESTAMP
        })

    transaction = db.transaction()
    update_in_transaction(transaction, doc_ref, active_model_doc)

    write_audit({
        "type": "model.promote",
        "modelId": model_id,
        "prevModelId": prev_id,
        "rolloutRatio": rollout,
        "requestedBy": requested_by,
        "notes": notes
    })
    return {"activeModelId": model_id, "prevModelId": prev_id, "rolloutRatio": rollout}


def rollback(to_model_id: str | None, requested_by: str):
    """Rolls back the active model to a specified previous version."""
    q = db.collection("model_registry").where("isActive", "==", True).limit(1).stream()
    active_models = list(q)
    if not active_models:
        raise ValueError("No active model to rollback from")

    active_model_doc = active_models[0]
    active_data = active_model_doc.to_dict()

    target_id = to_model_id or active_data.get("prevModelId")
    if not target_id:
        raise ValueError("No previous model ID recorded for the active model. Cannot rollback.")

    target_ref = db.collection("model_registry").document(target_id)
    if not target_ref.get().exists:
        raise ValueError(f"Rollback target model {target_id} not found.")

    @firestore.transactional
    def rollback_in_transaction(transaction, current_active_ref, new_active_ref):
        transaction.update(current_active_ref, {"isActive": False, "rolloutRatio": 0.0})
        transaction.update(new_active_ref, {"isActive": True, "rolloutRatio": 1.0, "updatedAt": firestore.SERVER_TIMESTAMP})

    transaction = db.transaction()
    rollback_in_transaction(transaction, active_model_doc.reference, target_ref)

    write_audit({
        "type": "model.rollback",
        "from": active_model_doc.id,
        "to": target_id,
        "requestedBy": requested_by
    })
    return {"activeModelId": target_id, "rolledBackFrom": active_model_doc.id}


def main():
    """Entry point for the Cloud Run Job."""
    if len(sys.argv) < 2:
        print("No payload provided. Exiting.", file=sys.stderr)
        return

    try:
        payload_str = sys.argv[1]
        payload = json.loads(payload_str)

        action = payload.get("action")
        requested_by = payload.get("requestedBy")
        if not requested_by:
            raise ValueError("'requestedBy' is a required payload field.")

        if action == "rollback":
            result = rollback(payload.get("rollbackTo"), requested_by)
            print(f"Rollback successful: {result}")
        else:
            # Default action is promote
            model_id = payload.get("modelId")
            rollout = float(payload.get("rolloutRatio", 0.10))
            notes = payload.get("notes", "")
            if not model_id:
                raise ValueError("'modelId' is required for promotion.")

            result = promote(model_id, rollout, requested_by, notes)
            print(f"Promotion successful: {result}")

    except json.JSONDecodeError:
        print(f"Error: Invalid JSON payload provided: {sys.argv[1]}", file=sys.stderr)
        sys.exit(1)
    except (ValueError, KeyError) as e:
        print(f"Error processing payload: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
