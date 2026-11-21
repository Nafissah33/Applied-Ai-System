"""Retrieval component: index markdown knowledge files and rank sections with TF-IDF cosine similarity.

Pure Python (no external dependencies, no API key). Multi-source: every .md file under the
knowledge directory (including knowledge/custom/) is indexed, and each chunk remembers its source.
"""

from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

DEFAULT_KNOWLEDGE_DIR = Path(__file__).resolve().parent.parent / "knowledge"

_STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "has", "have", "in", "is", "it",
    "its", "of", "on", "or", "that", "the", "their", "to", "with", "my", "me", "i", "he", "she",
    "plan", "day", "need", "needs", "can", "should", "will", "but", "so", "do", "does", "not", "all",
    "also", "if", "when", "only", "than", "this", "these", "they", "them", "very", "about", "any",
    "minute", "minutes", "min", "mins", "hour", "hours", "week", "today", "please",
}


def tokenize(text: str) -> list[str]:
    """Lowercase, drop stopwords and numbers, and lightly stem plurals/verb endings."""
    tokens = []
    for word in re.findall(r"[a-z]+", text.lower()):
        if word in _STOPWORDS:
            continue
        for suffix in ("ing", "ed", "es", "s"):
            if word.endswith(suffix) and len(word) - len(suffix) >= 4:
                word = word[: -len(suffix)]
                break
        tokens.append(word)
    return tokens


@dataclass
class Chunk:
    source: str
    species: str
    heading: str
    text: str
    path: str
    suggestions: list[dict] = field(default_factory=list)
    score: float = 0.0

    @property
    def citation(self) -> str:
        return f"{self.source} > {self.heading}"


def _parse_front_matter(raw: str) -> tuple[dict, str]:
    if raw.startswith("---"):
        _, front, body = raw.split("---", 2)
        meta = {}
        for line in front.strip().splitlines():
            if ":" in line:
                key, value = line.split(":", 1)
                meta[key.strip()] = value.strip()
        return meta, body
    return {}, raw


def _parse_suggestion(line: str) -> dict | None:
    """Parse `TASK: title | minutes | priority | category | HH:MM` into a dict, or None if malformed."""
    parts = [p.strip() for p in line[len("TASK:"):].split("|")]
    if len(parts) < 4:
        return None
    try:
        minutes = int(parts[1])
    except ValueError:
        return None
    return {
        "title": parts[0],
        "duration_minutes": minutes,
        "priority": parts[2].lower(),
        "category": parts[3],
        "preferred_time": parts[4] if len(parts) > 4 and parts[4] else None,
    }


def load_chunks(knowledge_dir: Path | str = DEFAULT_KNOWLEDGE_DIR) -> list[Chunk]:
    """Read every markdown file under knowledge_dir and split it into one chunk per `##` section."""
    chunks: list[Chunk] = []
    for path in sorted(Path(knowledge_dir).rglob("*.md")):
        if path.name.lower() == "readme.md":
            continue
        meta, body = _parse_front_matter(path.read_text(encoding="utf-8"))
        if "source" not in meta:
            continue
        for section in re.split(r"^## ", body, flags=re.MULTILINE)[1:]:
            heading, _, content = section.partition("\n")
            prose, suggestions = [], []
            for line in content.strip().splitlines():
                if line.startswith("TASK:"):
                    parsed = _parse_suggestion(line)
                    if parsed:
                        suggestions.append(parsed)
                else:
                    prose.append(line)
            chunks.append(
                Chunk(
                    source=meta["source"],
                    species=meta.get("species", "any"),
                    heading=heading.strip(),
                    text=" ".join(prose).strip(),
                    path=str(path),
                    suggestions=suggestions,
                )
            )
    return chunks


class KnowledgeRetriever:
    def __init__(self, knowledge_dir: Path | str = DEFAULT_KNOWLEDGE_DIR):
        self.chunks = load_chunks(knowledge_dir)
        self._doc_tokens = [tokenize(c.heading + " " + c.heading + " " + c.text) for c in self.chunks]
        n = len(self.chunks)
        df = Counter(term for tokens in self._doc_tokens for term in set(tokens))
        self._idf = {term: math.log(1 + n / count) for term, count in df.items()}
        self._vectors = [self._vectorize(tokens) for tokens in self._doc_tokens]

    def _vectorize(self, tokens: list[str]) -> dict[str, float]:
        counts = Counter(tokens)
        vec = {t: (1 + math.log(c)) * self._idf.get(t, 0.0) for t, c in counts.items()}
        norm = math.sqrt(sum(v * v for v in vec.values()))
        return {t: v / norm for t, v in vec.items()} if norm else {}

    def search(self, query: str, species: str | None = None, top_k: int = 3, min_score: float = 0.1) -> list[Chunk]:
        """Return up to top_k chunks scoring at least min_score, filtered to the species (plus 'any')."""
        query_vec = self._vectorize(tokenize(query))
        scored = []
        for chunk, vec in zip(self.chunks, self._vectors):
            if species and chunk.species not in (species, "any"):
                continue
            score = sum(w * vec.get(t, 0.0) for t, w in query_vec.items())
            if score >= min_score:
                scored.append((score, chunk))
        scored.sort(key=lambda pair: pair[0], reverse=True)
        results = []
        for score, chunk in scored[:top_k]:
            results.append(Chunk(**{**chunk.__dict__, "score": round(score, 3)}))
        return results
