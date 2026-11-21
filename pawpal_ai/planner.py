"""Agentic planning workflow: validate -> profile -> retrieve -> propose -> check -> schedule -> self-critique -> explain.

Every step is recorded in a trace so the decision-making process can be inspected and saved.
Runs fully offline (no LLM / API key): reasoning is rule-based and grounded in retrieved documents.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date

from pawpal_system import Owner, Pet, Scheduler, Task

from .classifier import ProfileClassifier
from .guardrails import MAX_MINUTES, check_input, validate_tasks
from .log import get_logger
from .retriever import Chunk, KnowledgeRetriever, best_sentence

logger = get_logger()
MODEL_CONDITION_THRESHOLD = 0.9
MODEL_STAGE_CONFIDENCE = 0.9

DEFAULT_MINUTES = 60
MAX_REVISIONS = 8
_PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}
# The tool (function) the agent calls at each step; recorded in every trace entry.
_STEP_TOOLS = {
    "input_guardrail": "guardrails.check_input",
    "specialized_model": "ProfileClassifier.predict",
    "retrieve": "KnowledgeRetriever.search",
    "output_guardrail": "guardrails.validate_tasks",
    "self_check": "Scheduler.detect_conflicts + Scheduler.generate_plan",
}

_CONDITION_WORDS = {
    "joint": ["joint", "arthritis", "arthritic", "stiff", "hip", "hips", "limp", "mobility"],
    "weight": ["overweight", "weight", "fat", "obese", "diet", "chubby"],
    "anxious": ["anxious", "anxiety", "nervous", "hyper", "energetic", "restless", "bored"],
    "indoor": ["indoor"],
}
_STAGE_WORDS = {
    "young": ["puppy", "kitten", "young", "baby"],
    "senior": ["senior", "old", "elderly", "aging", "geriatric"],
}
_SPECIES_WORDS = {"dog": ["dog", "puppy", "pup", "pooch", "canine", "retriever", "lab", "labrador", "poodle", "beagle",
                          "shepherd", "bulldog", "husky", "terrier", "corgi", "dachshund"],
                  "cat": ["cat", "kitten", "kitty", "feline", "tabby", "siamese", "persian", "tomcat"]}
# Tasks that conflict with a health condition, even if a retrieved source (e.g. a custom note) suggests them.
_CONFLICTING_TASKS = {"joint": ("fetch", "jump", "run", "agility", "chase", "sprint")}
_BASELINE_TASKS = {
    "dog": [("Feeding", 10, "high", "feeding"), ("Fresh water check", 5, "high", "feeding"), ("Walk", 30, "medium", "walk")],
    "cat": [("Feeding", 5, "high", "feeding"), ("Fresh water check", 5, "high", "feeding"), ("Play", 15, "medium", "play")],
    "other": [("Feeding", 10, "high", "feeding"), ("Fresh water check", 5, "high", "feeding")],
}


@dataclass
class PlanResult:
    status: str  # "ok" or "refused"
    message: str = ""
    profile: dict = field(default_factory=dict)
    retrieved: list[Chunk] = field(default_factory=list)
    tasks: list[dict] = field(default_factory=list)
    plan: list[dict] = field(default_factory=list)
    dropped: list[str] = field(default_factory=list)
    confidence: float = 0.0
    warnings: list[str] = field(default_factory=list)
    trace: list[dict] = field(default_factory=list)
    explanation: str = ""

    def trace_markdown(self, request: str) -> str:
        lines = [f"**Request:** `{request}`", ""]
        for i, step in enumerate(self.trace, 1):
            tool = f" `[tool: {step['tool']}]`" if step.get("tool") else ""
            lines.append(f"{i}. **{step['step']}**{tool} — {step['detail']}")
        lines.append(f"\n**Outcome:** {self.status}, confidence {self.confidence:.2f}")
        return "\n".join(lines)


def parse_profile(text: str, classifier: ProfileClassifier | None = None) -> dict:
    """Extract species, life stage, conditions, and a time budget from free text.

    Keyword rules run first. If a trained classifier is given it fills the gaps: it can add conditions the
    keywords missed and replace the default "adult" stage, but only when it is highly confident.
    """
    lowered = text.lower()
    raw_words = re.findall(r"[a-z]+", lowered)
    # Also match singular forms so "joints" finds "joint" and "puppies" style plurals still work.
    words = set(raw_words) | {w[:-1] for w in raw_words if w.endswith("s") and len(w) > 3}

    species = "other"
    matched = [name for name, vocab in _SPECIES_WORDS.items() if words & set(vocab)]
    if matched:
        species = matched[0]
    stage = "adult"
    for name, vocab in _STAGE_WORDS.items():
        if words & set(vocab):
            stage = name
            break
    conditions = [name for name, vocab in _CONDITION_WORDS.items() if words & set(vocab)]

    minutes = DEFAULT_MINUTES
    hours = re.search(r"(\d+(?:\.\d+)?)\s*(?:hours?|hrs?|h)\b", lowered)
    mins = re.search(r"(\d+)\s*(?:minutes?|mins?|m)\b", lowered)
    if hours or mins:
        minutes = int(float(hours.group(1)) * 60) if hours else 0
        minutes += int(mins.group(1)) if mins else 0
    profile = {"species": species, "stage": stage, "conditions": conditions, "minutes": minutes}
    if len(matched) > 1:
        profile["mixed_species"] = True
    if classifier is not None:
        pred = classifier.predict(text, threshold=MODEL_CONDITION_THRESHOLD)
        added = [c for c in pred["conditions"] if c not in conditions]
        profile["conditions"] = conditions + added
        if stage == "adult" and pred["stage"] != "adult" and pred["stage_confidence"] >= MODEL_STAGE_CONFIDENCE:
            profile["stage"] = pred["stage"]
            profile["model_stage"] = True
        if added:
            profile["model_conditions"] = added
    return profile


def _query_from_profile(text: str, profile: dict) -> str:
    # Species is applied as a filter, so only add stage/condition words that sharpen the match.
    extra = [] if profile["stage"] == "adult" else [profile["stage"]]
    extra += profile["conditions"]
    if "joint" in profile["conditions"]:
        extra += ["joint", "arthritis", "low-impact"]
    return f"{text} {' '.join(extra)}"


def _explain(entry: dict, task_meta: dict, style: str) -> str:
    task = entry["task"]
    if style == "baseline":
        return f"{task.title} scheduled ({task.priority} priority)."
    source = task_meta.get("source", "general guidance")
    guidance = task_meta.get("guidance")
    why = f'"{guidance}"' if guidance else "chosen for this pet's profile."
    return (
        f"[{task.priority.upper()}] {task.title}, {task.duration_minutes} min. "
        f"Why: {why} Source: {source}. "
        f"Placed {entry['start_time']}-{entry['end_time']} after higher-priority care."
    )


class AIPlanner:
    def __init__(self, retriever: KnowledgeRetriever | None = None, use_model: bool = True):
        self.retriever = retriever or KnowledgeRetriever()
        self.classifier: ProfileClassifier | None = None
        if use_model:
            try:
                self.classifier = ProfileClassifier.load()
            except (OSError, ValueError, KeyError) as exc:
                logger.warning("Profile model unavailable (%s); using keyword rules only.", exc)

    def plan(self, request: str, *, use_retrieval: bool = True, style: str = "specialized",
             use_model: bool = True, today: date | None = None) -> PlanResult:
        """Run the full workflow. Never raises: unexpected errors are logged and returned as status 'error'."""
        try:
            result = self._plan(request, use_retrieval, style, use_model, today)
        except Exception as exc:  # noqa: BLE001 - last-resort safety net for the UI/CLI
            logger.exception("Planner failed for request %r", request)
            return PlanResult(status="error", message=f"Sorry, the planner hit an unexpected error ({type(exc).__name__}). "
                                                      "Nothing was scheduled; see logs/pawpal.log.")
        logger.info("request=%r status=%s confidence=%.2f tasks=%d warnings=%d",
                    request, result.status, result.confidence, len(result.plan), len(result.warnings))
        return result

    def _plan(self, request: str, use_retrieval: bool, style: str, use_model: bool, today: date | None) -> PlanResult:
        result = PlanResult(status="ok")
        trace = result.trace

        def log(step: str, detail: str) -> None:
            trace.append({"step": step, "detail": detail, "tool": _STEP_TOOLS.get(step)})

        # 1. Input guardrail
        profile = parse_profile(request or "", self.classifier if use_model else None)
        verdict = check_input(request, minutes=profile["minutes"], species=profile["species"],
                              mixed_species=profile.get("mixed_species", False))
        if not verdict.allowed:
            log("input_guardrail", f"BLOCKED ({verdict.code}): {verdict.reason}")
            result.status, result.message = "refused", verdict.reason
            return result
        result.warnings.extend(verdict.warnings)
        profile["minutes"] = min(profile["minutes"], MAX_MINUTES)
        result.profile = profile
        log("input_guardrail", "passed" + (f" with warnings: {verdict.warnings}" if verdict.warnings else ""))
        log("profile", f"species={profile['species']}, stage={profile['stage']}, "
                       f"conditions={profile['conditions'] or 'none'}, minutes={profile['minutes']}")
        if profile.get("model_conditions") or profile.get("model_stage"):
            log("specialized_model", f"classifier added conditions={profile.get('model_conditions', [])}"
                                     f"{', stage=' + profile['stage'] if profile.get('model_stage') else ''}")

        # 2. Retrieval
        proposed: list[dict] = []
        if use_retrieval:
            query = _query_from_profile(request, profile)
            # Unsupported species may only see species-neutral ("any") documents.
            species_filter = profile["species"] if profile["species"] != "other" else "any"
            result.retrieved = self.retriever.search(query, species=species_filter, top_k=3)
            log("retrieve", "; ".join(f"{c.citation} (score {c.score})" for c in result.retrieved) or "no relevant documents")
            for chunk in result.retrieved:
                for suggestion in chunk.suggestions:
                    proposed.append({**suggestion, "source": chunk.citation, "chunk_score": chunk.score,
                                     "guidance": best_sentence(chunk.text, suggestion["title"], request)})
        else:
            log("retrieve", "skipped (baseline mode, no retrieval)")
        if not proposed:
            for title, minutes, priority, category in _BASELINE_TASKS[profile["species"]]:
                proposed.append({"title": title, "duration_minutes": minutes, "priority": priority,
                                 "category": category, "preferred_time": None, "source": "built-in defaults",
                                 "chunk_score": 0.0})
            log("propose", f"using {len(proposed)} built-in default tasks")
        else:
            log("propose", f"{len(proposed)} tasks suggested by retrieved documents")

        # 3. Output guardrail
        checked = validate_tasks(proposed)
        tasks = checked.tasks
        for item in checked.rejected:
            log("output_guardrail", f"rejected {item}")
        for fix in checked.fixes:
            log("output_guardrail", f"fixed: {fix}")
        if not checked.rejected and not checked.fixes:
            log("output_guardrail", "all tasks valid")

        # 4. Revise: keep only the best-supported walk, then schedule with self-critique
        walks = [t for t in tasks if t["category"] == "walk"]
        if len(walks) > 1:
            best = max(walks, key=lambda t: t.get("chunk_score", 0.0))
            removed = [t["title"] for t in walks if t is not best]
            tasks = [t for t in tasks if t["category"] != "walk" or t is best]
            log("revise", f"kept most relevant walk \"{best['title']}\"; removed {removed}")

        # Drop tasks that conflict with a known condition (a custom source may suggest high-impact play).
        for condition, keywords in _CONFLICTING_TASKS.items():
            if condition in profile["conditions"]:
                clash = [t["title"] for t in tasks if any(k in t["title"].lower() for k in keywords)]
                if clash:
                    tasks = [t for t in tasks if t["title"] not in clash]
                    log("revise", f"removed high-impact task(s) {clash} because the pet has a {condition} condition")

        # Overlapping feeding plans (e.g. adult-routine meals + a weight-management portion plan):
        # keep the feeding tasks from the single best-matching source and drop the rest.
        feeds = [t for t in tasks if t["category"] == "feeding" and "water" not in t["title"].lower()
                 and t.get("chunk_score", 0.0) > 0]
        feed_sources = {t["source"] for t in feeds}
        if len(feed_sources) > 1:
            best_source = max(feeds, key=lambda t: t["chunk_score"])["source"]
            dropped_feeds = [t["title"] for t in feeds if t["source"] != best_source]
            tasks = [t for t in tasks if t not in feeds or t["source"] == best_source]
            log("revise", f"feeding tasks came from {len(feed_sources)} sections; kept those from "
                          f"\"{best_source}\" and removed overlapping {dropped_feeds}")

        scheduler = Scheduler(profile["minutes"])
        objects = {t["title"]: Task(t["title"], t["duration_minutes"], t["priority"], t["category"],
                                    preferred_time=t.get("preferred_time")) for t in tasks}
        meta = {t["title"]: t for t in tasks}

        for attempt in range(1, MAX_REVISIONS + 1):
            conflicts = scheduler.detect_conflicts(list(objects.values()))
            for first, second in conflicts:
                moved = scheduler.find_next_available_slot(
                    scheduler.generate_plan([first], start_time=first.preferred_time),
                    second.duration_minutes, preferred_time=second.preferred_time)
                log("self_check", f"conflict at {first.preferred_time}: moved \"{second.title}\" to {moved}")
                second.preferred_time = moved
            plan = scheduler.generate_plan(list(objects.values()), today=today)
            scheduled_titles = {e["task"].title for e in plan}
            missed = [t for t in objects.values() if t.title not in scheduled_titles]
            missed_high = [t for t in missed if t.priority == "high"]
            log("self_check", f"attempt {attempt}: scheduled {len(plan)}/{len(objects)} tasks, "
                              f"missed high-priority: {[t.title for t in missed_high] or 'none'}")
            if not missed_high:
                break
            droppable = [t for t in objects.values() if t.priority != "high"]
            if droppable:
                victim = max(droppable, key=lambda t: (_PRIORITY_RANK[t.priority], t.duration_minutes))
            else:
                # Only essentials remain: collapse redundant meals so one feeding + water still fit.
                meals = [t for t in objects.values() if t.category == "feeding" and "water" not in t.title.lower()]
                if len(meals) < 2:
                    # Last resort: shorten a missed essential task to the time still free instead of dropping it.
                    left = profile["minutes"] - sum(e["task"].duration_minutes for e in plan)
                    shrinkable = [t for t in missed_high if t.category != "feeding" and t.duration_minutes > left >= 10]
                    if not shrinkable:
                        break
                    t = shrinkable[0]
                    log("revise", f"shortened \"{t.title}\" from {t.duration_minutes} to {left} min to fit the time budget")
                    meta[t.title]["duration_minutes"] = left
                    t.duration_minutes = left
                    continue
                victim = max(meals, key=lambda t: t.duration_minutes)
            del objects[victim.title]
            log("revise", f"removed \"{victim.title}\" ({victim.priority}) to make room for essential care")

        result.dropped = [t.title for t in objects.values() if t.title not in {e["task"].title for e in plan}]
        result.plan = plan
        result.tasks = [meta[t.title] for t in objects.values()]
        if result.dropped:
            result.warnings.append(f"Did not fit in {profile['minutes']} minutes: {', '.join(result.dropped)}")

        # 5. Confidence
        best_score = max((c.score for c in result.retrieved), default=0.0)
        result.confidence = round(min(1.0, best_score / 0.5), 2) if use_retrieval else 0.3
        if profile["species"] == "other":
            result.confidence = min(result.confidence, 0.3)
        if result.confidence < 0.5:
            result.warnings.append("Low confidence: limited matching guidance. Please review this plan yourself.")
        log("confidence", f"{result.confidence:.2f} (best retrieval score {best_score})")

        # 6. Explain
        explanations = [_explain(e, meta[e["task"].title], style) for e in plan]
        result.explanation = "\n".join(explanations)
        log("explain", f"{len(explanations)} explanations written in '{style}' style")
        return result

    @staticmethod
    def apply_to_pet(result: PlanResult, pet: Pet) -> list[Task]:
        """Add the planner's scheduled tasks to a pet's real task list (call only after user confirms)."""
        added = []
        for entry in result.plan:
            task = entry["task"]
            pet.add_task(task)
            added.append(task)
        return added
