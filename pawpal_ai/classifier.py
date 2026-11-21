"""Specialized model: a small Naive Bayes text classifier trained on a synthetic pet-request dataset.

It predicts a pet's life stage (young / adult / senior) and health-or-behavior conditions
(joint, weight, anxious, indoor) from free text, so paraphrases like "struggles with the stairs"
or "getting up there in age" are understood even when no keyword list contains them.

Pure Python (no dependencies, no API key). Train with `python train_profile_model.py`.
"""

from __future__ import annotations

import json
import math
import re
from collections import Counter
from pathlib import Path

DEFAULT_MODEL_PATH = Path(__file__).resolve().parent.parent / "models" / "profile_model.json"
STAGES = ["young", "adult", "senior"]
CONDITIONS = ["joint", "weight", "anxious", "indoor"]


def features(text: str) -> list[str]:
    """Unigrams plus bigrams of lowercase words."""
    words = re.findall(r"[a-z]+", text.lower())
    return words + [f"{a}_{b}" for a, b in zip(words, words[1:])]


class _NaiveBayes:
    """Multinomial Naive Bayes with Laplace smoothing."""

    def __init__(self, classes: list[str]):
        self.classes = classes
        self.class_counts: Counter = Counter()
        self.word_counts: dict[str, Counter] = {c: Counter() for c in classes}
        self.vocab: set[str] = set()

    def fit(self, texts: list[str], labels: list[str]) -> "_NaiveBayes":
        for text, label in zip(texts, labels):
            self.class_counts[label] += 1
            for f in features(text):
                self.word_counts[label][f] += 1
                self.vocab.add(f)
        return self

    def predict_proba(self, text: str) -> dict[str, float]:
        total_docs = sum(self.class_counts.values())
        feats = [f for f in features(text) if f in self.vocab]
        log_scores = {}
        for c in self.classes:
            total_words = sum(self.word_counts[c].values())
            score = math.log((self.class_counts[c] + 1) / (total_docs + len(self.classes)))
            for f in feats:
                score += math.log((self.word_counts[c][f] + 1) / (total_words + len(self.vocab)))
            log_scores[c] = score
        top = max(log_scores.values())
        exp = {c: math.exp(s - top) for c, s in log_scores.items()}
        norm = sum(exp.values())
        return {c: v / norm for c, v in exp.items()}

    def to_dict(self) -> dict:
        return {"classes": self.classes, "class_counts": dict(self.class_counts),
                "word_counts": {c: dict(w) for c, w in self.word_counts.items()}}

    @classmethod
    def from_dict(cls, data: dict) -> "_NaiveBayes":
        nb = cls(data["classes"])
        nb.class_counts = Counter(data["class_counts"])
        nb.word_counts = {c: Counter(w) for c, w in data["word_counts"].items()}
        nb.vocab = {f for w in nb.word_counts.values() for f in w}
        return nb


class ProfileClassifier:
    def __init__(self, stage_model: _NaiveBayes, condition_models: dict[str, _NaiveBayes]):
        self.stage_model = stage_model
        self.condition_models = condition_models

    @classmethod
    def train(cls, examples: list[dict]) -> "ProfileClassifier":
        """examples: [{"text": str, "stage": str, "conditions": [str, ...]}, ...]"""
        texts = [e["text"] for e in examples]
        stage = _NaiveBayes(STAGES).fit(texts, [e["stage"] for e in examples])
        conds = {c: _NaiveBayes(["yes", "no"]).fit(texts, ["yes" if c in e["conditions"] else "no" for e in examples])
                 for c in CONDITIONS}
        return cls(stage, conds)

    def predict(self, text: str, threshold: float = 0.5) -> dict:
        """Return {"stage", "stage_confidence", "conditions": {name: probability, ...} for those above threshold}."""
        stage_probs = self.stage_model.predict_proba(text)
        stage = max(stage_probs, key=stage_probs.get)
        found = {}
        for name, model in self.condition_models.items():
            p = model.predict_proba(text)["yes"]
            if p >= threshold:
                found[name] = round(p, 3)
        return {"stage": stage, "stage_confidence": round(stage_probs[stage], 3), "conditions": found}

    def save(self, path: Path | str = DEFAULT_MODEL_PATH) -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        data = {"stage": self.stage_model.to_dict(),
                "conditions": {c: m.to_dict() for c, m in self.condition_models.items()}}
        Path(path).write_text(json.dumps(data), encoding="utf-8")

    @classmethod
    def load(cls, path: Path | str = DEFAULT_MODEL_PATH) -> "ProfileClassifier":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls(_NaiveBayes.from_dict(data["stage"]),
                   {c: _NaiveBayes.from_dict(m) for c, m in data["conditions"].items()})
