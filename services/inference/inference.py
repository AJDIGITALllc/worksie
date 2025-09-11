import hashlib
import random
from .metrics import record_model_served

# This would be a real model loader in a production system.
def load_model(version: str):
    """A dummy model loader."""
    print(f"Loading model version: {version}")
    # Simulate a model object with a run method
    class Model:
        def __init__(self, version):
            self.version = version
        def run(self, image_path):
            return f"Prediction from model {self.version} for image {image_path}"
    return Model(version)

# This would fetch metadata from a reliable source like Firestore or a cache.
def get_active_model_meta() -> dict:
    """
    A dummy function to get the active model's metadata.
    In a real system, this would read from Firestore and be cached with a TTL.
    """
    return {
        "version": "2025.09.10-auto-v7",
        "rolloutRatio": 0.10,
        "prevModelId": "2025.08.31-v6"
    }

def bucketize(key: str) -> float:
    """
    Hashes a key into a stable, uniformly distributed float between 0.0 and 1.0.
    """
    h = hashlib.sha256(key.encode("utf-8")).hexdigest()
    # Use the first 8 characters of the hex hash for a 32-bit integer
    return int(h[:8], 16) / 0xFFFFFFFF

def pick_model(user_or_org_id: str, active_model: dict) -> str:
    """
    Selects a model version based on the rollout ratio and a stable hash of the user/org ID.
    """
    rollout = float(active_model.get("rolloutRatio", 1.0))

    # If it's a full rollout, everyone gets the active model.
    if rollout >= 1.0:
        return active_model["version"]

    # If it's a canary, bucket the user/org and decide
    bucket = bucketize(user_or_org_id)
    if bucket < rollout:
        # User is in the canary group
        return active_model["version"]
    else:
        # User is in the control group (gets the previous stable model)
        # Fallback to the active model if no previous model is specified
        return active_model.get("prevModelId") or active_model["version"]

def predict(image_path: str, org_id: str):
    """
    Main prediction function that incorporates canary selection.
    """
    # 1. Get the current active model configuration
    active_model_meta = get_active_model_meta()

    # 2. Pick a model version based on the org_id and rollout strategy
    model_version = pick_model(org_id, active_model_meta)

    # 3. Load the selected model (this should be cached in a real system)
    model = load_model(model_version)

    # 4. Record which model was served for monitoring
    record_model_served(model_version)

    # 5. Run the prediction
    return model.run(image_path)

# Example usage:
if __name__ == "__main__":
    org_ids = [f"org_{i}" for i in range(20)]
    print("Simulating predictions for 20 organizations...")
    for org_id in org_ids:
        result = predict("path/to/image.jpg", org_id)
        print(f"[{org_id}] -> {result}")
