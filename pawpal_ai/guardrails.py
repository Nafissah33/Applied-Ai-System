"""Reliability component: input guardrails and output guardrails for the AI planner.

Input guardrails decide whether a request may be processed at all (block) or only needs a caveat (warn).
Output guardrails validate and repair the tasks the planner proposes before they reach the schedule.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

MAX_REQUEST_CHARS = 500
MIN_MINUTES, MAX_MINUTES = 10, 600
VALID_PRIORITIES = {"high", "medium", "low"}
MAX_TASK_MINUTES = 180
SUPPORTED_SPECIES = {"dog", "cat"}

VET_MESSAGE = (
    "I can't give medical, diagnosis or dosage advice. Please contact your veterinarian. "
    "I can still schedule a reminder for medication your vet has prescribed."
)

EMERGENCY_MESSAGE = (
    "This sounds like it could be an emergency. I can't help with that. Contact an emergency veterinarian "
    "or a pet poison hotline right away, and don't wait for a care schedule."
)

_EMERGENCY_PATTERNS = [
    r"\b(ate|eaten|eat|swallowed|ingested|licked|drank)\b.*\b(chocolate|grapes?|raisins?|xylitol|onions?|garlic|poison|antifreeze|"
    r"bleach|lily|lilies|medicine|medication|pills?|batteries|battery)\b",
    r"\b(poison(ed|ing|ous)?|toxic)\b",
    r"\b(seizures?|seizing|not breathing|can'?t breathe|struggling to breathe|collapsed|unconscious|bleeding|choking|bloat|"
    r"hit by a car|emergency)\b",
]

_INJECTION_PATTERNS = [
    r"ignore (all |any |the )?(previous|prior|above|earlier) (instructions|rules|prompts?)",
    r"disregard (all |any |the )?(previous|prior|above|your) (instructions|rules)",
    r"(reveal|show|print) (your|the) (system )?prompt",
    r"you are now",
    r"jailbreak",
    r"pretend (to be|you are)",
    r"override (the )?(guardrails?|safety|rules)",
]
_MEDICAL_PATTERNS = [
    r"\bdos(e|age|ing)\b",
    r"\b\d+(\.\d+)?\s?(mg|ml|mcg)\b",
    r"\b(milligram|milliliter)s?\b",
    r"\bprescrib(e|ing)\b(?!d)",
    r"\bdiagnos(e|is|ing)\b",
    r"\b(ibuprofen|tylenol|acetaminophen|aspirin|advil|xylitol)\b",
    r"\bhow much (medicine|medication|insulin|pills?)\b",
    r"\b(how (much|many)|right amount of|safe amount of|enough of)\b.*\b(medicine|medication|meds|pills?|tablets?|"
    r"benadryl|tylenol|aspirin|ibuprofen|insulin|painkillers?|supplements?)\b",
    r"\bwhat is wrong with\b",
]
_DOSE_IN_TITLE = re.compile(r"\b\d+(\.\d+)?\s?(mg|ml|mcg|cc|tablets?|pills?)\b", re.IGNORECASE)
_TIME_RE = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")


@dataclass
class InputCheck:
    allowed: bool
    reason: str = ""
    code: str = "ok"
    warnings: list[str] = field(default_factory=list)


def check_input(text: str, minutes: int | None = None, species: str | None = None) -> InputCheck:
    """Validate a free-text planning request before any processing happens."""
    if not text or not text.strip():
        return InputCheck(False, "Request is empty. Describe your pet and how much time you have.", "empty")
    if len(text) > MAX_REQUEST_CHARS:
        return InputCheck(False, f"Request is too long ({len(text)} > {MAX_REQUEST_CHARS} characters).", "too_long")

    lowered = text.lower()
    for pattern in _INJECTION_PATTERNS:
        if re.search(pattern, lowered):
            return InputCheck(False, "Request looks like an attempt to change the assistant's rules, so it was blocked.", "injection")
    for pattern in _EMERGENCY_PATTERNS:
        if re.search(pattern, lowered):
            return InputCheck(False, EMERGENCY_MESSAGE, "emergency")
    for pattern in _MEDICAL_PATTERNS:
        if re.search(pattern, lowered):
            return InputCheck(False, VET_MESSAGE, "medical")

    warnings = []
    if minutes is not None:
        if minutes < MIN_MINUTES:
            return InputCheck(False, f"{minutes} minutes is too little time to plan a day (minimum {MIN_MINUTES}).", "budget_low")
        if minutes > MAX_MINUTES:
            warnings.append(f"Time budget capped at {MAX_MINUTES} minutes (you asked for {minutes}).")
    if species is not None and species not in SUPPORTED_SPECIES:
        warnings.append(
            "I only have detailed guidance for dogs and cats, so this plan uses general pet-care guidance and has low confidence."
        )
    return InputCheck(True, warnings=warnings)


@dataclass
class OutputCheck:
    tasks: list[dict]
    fixes: list[str] = field(default_factory=list)
    rejected: list[str] = field(default_factory=list)


def validate_tasks(tasks: list[dict]) -> OutputCheck:
    """Validate and repair proposed tasks: schema, bounds, dosage text, duplicates, and essentials."""
    fixes, rejected, clean, seen = [], [], [], set()
    for task in tasks:
        title = str(task.get("title", "")).strip()
        if not title:
            rejected.append("task with empty title")
            continue
        if _DOSE_IN_TITLE.search(title):
            rejected.append(f'"{title}" (contains dosage information)')
            continue

        task = dict(task)
        priority = str(task.get("priority", "")).lower()
        if priority not in VALID_PRIORITIES:
            fixes.append(f'"{title}": invalid priority {priority!r} -> medium')
            priority = "medium"
        task["priority"] = priority

        minutes = task.get("duration_minutes")
        if not isinstance(minutes, int) or minutes < 1:
            rejected.append(f'"{title}" (invalid duration {minutes!r})')
            continue
        if minutes > MAX_TASK_MINUTES:
            fixes.append(f'"{title}": duration {minutes} capped to {MAX_TASK_MINUTES}')
            task["duration_minutes"] = MAX_TASK_MINUTES

        pref = task.get("preferred_time")
        if pref and not _TIME_RE.match(pref):
            fixes.append(f'"{title}": invalid time {pref!r} removed')
            task["preferred_time"] = None

        key = title.lower()
        if key in seen:
            fixes.append(f'"{title}": duplicate removed')
            continue
        seen.add(key)
        clean.append(task)

    has_feeding = any(
        t["priority"] == "high" and any(w in t["title"].lower() for w in ("feeding", "meal", "portion"))
        for t in clean
    )
    if not has_feeding:
        clean.append(
            {"title": "Feeding", "duration_minutes": 10, "priority": "high", "category": "feeding",
             "preferred_time": None, "source": "guardrail: essentials"}
        )
        fixes.append('essential "Feeding" task was missing -> added')
    if not any("water" in t["title"].lower() for t in clean):
        clean.append(
            {"title": "Fresh water check", "duration_minutes": 5, "priority": "high", "category": "feeding",
             "preferred_time": None, "source": "guardrail: essentials"}
        )
        fixes.append('essential "Fresh water check" was missing -> added')
    return OutputCheck(clean, fixes, rejected)
