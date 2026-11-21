"""Train the specialized profile classifier: python train_profile_model.py"""

import json
from pathlib import Path

from pawpal_ai.classifier import DEFAULT_MODEL_PATH, ProfileClassifier

DATA = Path(__file__).parent / "data" / "profile_training.jsonl"

if __name__ == "__main__":
    examples = [json.loads(line) for line in DATA.read_text(encoding="utf-8").splitlines() if line.strip()]
    model = ProfileClassifier.train(examples)
    model.save()
    print(f"trained on {len(examples)} synthetic examples -> {DEFAULT_MODEL_PATH}")
