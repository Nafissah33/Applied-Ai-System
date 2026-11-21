# Model card: PawPal+ AI planner

## Overview
- **System:** agentic planner with TF-IDF retrieval (RAG) and a small trained Naive Bayes profile classifier. No LLM, no API key.
- **Intended use:** suggesting a daily care schedule for a pet owner's dog or cat from a short free-text description.
- **Not intended for:** medical advice, diagnosis, dosing, or emergencies. The system refuses these and points to a veterinarian.

## How decisions are made
1. Input guardrail (block or warn), 2. profile parsing (keyword rules plus the classifier), 3. retrieval of the top 3 matching knowledge sections, 4. task proposal from structured `TASK:` lines in those sections, 5. output guardrail, 6. revision and scheduling with a self-check loop, 7. confidence score, 8. explanation that quotes the retrieved passage and cites its source. Every step is written to a trace (see `ai_interactions.md`) and each request is logged to `logs/pawpal.log`.

Confidence is `min(1, best retrieval score / 0.5)`, capped at 0.30 for unsupported species and 0.30 when retrieval is off. Plans below 0.50 carry a "review this yourself" warning.

## Data
- **Knowledge base:** markdown files in `knowledge/` written for this project (general guidance, not veterinary-reviewed), plus owner notes in `knowledge/custom/`.
- **Classifier training data:** 900 synthetic examples from `data/generate_training_data.py` (seed 7).

## Specialized model: profile classifier
- **What:** two-part Naive Bayes (unigram + bigram features): a 3-class life-stage model and one yes/no model per condition (joint, weight, anxious, indoor).
- **Training data:** synthetic, built from phrase pools. About 30% of examples have no age cue and are labeled `adult`. **Synthetic data is the main weakness**: the model learns the pools' wording and can pick up spurious links (for example, "couch" appeared only in joint phrases until I added furniture-chewing phrases to the anxious pool).
- **How it is used:** rules run first; the classifier adds conditions with probability >= 0.9 and may replace the default `adult` stage only at >= 0.9 confidence. If the model file is missing, the planner logs a warning and uses rules alone.
- **Baseline vs specialized** on `data/heldout_eval.jsonl` (20 hand-written requests whose wording is not in the training pools):

| Method | Stage and conditions both correct |
|---|---|
| Keyword rules only (baseline) | 8/20 |
| Rules + classifier at 0.9 | **14/20** |

  Caveat: I tried thresholds 0.7, 0.8, 0.9 and 0.95 on these same 20 examples (12, 12, 14 and 15 correct) and picked 0.9 as a conservative round value, so 14/20 is slightly optimistic and the sample is small. The classifier alone scored 10/20 and the rules alone 8/20, which is why they are combined.
- **Remaining errors:** vague age cues ("thirteen", "slowing down"), unusual condition wording ("pudgy", "pacing and panting"), and occasional false positives.

## Evaluation (`python evals/run_evals.py`, 32 checks, all passing)
| Experiment | Result |
|---|---|
| Guardrails (11 inputs: medical, injection, empty, too long, low budget, 3 valid) | 11/11 correct |
| Expected specialized task present, retrieval ON vs OFF (6 requests) | **6/6 vs 0/6** |
| Plan invariants (feeding and water present, budget respected) | 6/6 |
| Consistency (3 runs per request, identical output) | 6/6 |
| Specialization: explanations citing a source | 100% specialized vs 0% baseline |
| Specialized model vs rules (20 held-out requests) | 14/20 vs 8/20 |
| RAG grounding: explanations quoting a retrieved sentence | 20/20 |

### Before/after: retrieval
Request: "senior dog with arthritis, 45 minutes".
- **Baseline (no retrieval):** Fresh water check, Feeding, 30-minute Walk. Confidence 0.30.
- **With retrieval:** Fresh water check, Feeding, 15-minute Low-impact leash walk, Mobility check, Gentle joint massage. Confidence 0.99, each task cites its source.

### Before/after: explanation style (specialization and grounding)
| | Baseline | Specialized and grounded |
|---|---|---|
| Example | `Low-impact leash walk scheduled (high priority).` | `[HIGH] Low-impact leash walk, 15 min. Why: "Dogs with joint pain or arthritis benefit from low-impact exercise such as slow leash walks and avoiding stairs or jumping." Source: Dog Care Basics > Joint and arthritis support for dogs. Placed 08:15-08:30 after higher-priority care.` |
| Avg words per explanation | 5.6 | about 30 |
| Cites a source | 0% | 100% |

The eval checks that every retrieval-backed explanation quotes a sentence that really appears in a retrieved passage.

## Limitations and risks
- Keyword retrieval misses paraphrases; unseen conditions get no specialized guidance.
- The knowledge base is small and unreviewed by a veterinarian, so output could be incomplete or wrong for a real pet. High confidence means "the request matched a document well", not "the advice is medically correct".
- Guardrails are pattern-based, so a cleverly worded dosage question could slip past them. The output guardrail is a second layer that rejects dosage text in tasks.
- Only dogs and cats have detailed guidance.
- Evaluation cases were written by the same person who built the system, so they under-represent unexpected inputs.

## Responsible use
The system never adds tasks to a pet without a user click, shows its sources and confidence, and warns when it is unsure. Users should treat plans as suggestions and consult a veterinarian for health decisions.

## Reflection: AI collaboration, accepted and rejected suggestions, limitations

*Draft written with Claude Code from what happened while building the AI layer. Edit it into your own words and add anything from earlier in the project.*

**How I collaborated with AI.** I used Claude Code to map the grading rubric onto concrete files, design the `pawpal_ai/` package (retriever, classifier, guardrails, planner), write the evaluation harness, and debug. The most useful prompts were specific ones: pasting the rubric and asking for a requirement-to-file mapping, and asking the assistant to run the evals and explain each failure. I treated its code as a first draft to be tested, not trusted.

**A suggestion I accepted.** The assistant recommended building the system offline, with a swappable design, instead of depending on a paid LLM. I accepted it and skipped the API key. That made the system free, deterministic (three identical runs) and easy for anyone to run, and it made consistency testing meaningful.

**A suggestion I rejected or revised.** The assistant first proposed an LLM-driven planner through the Claude API, and I rejected it for the offline version. I also revised the assistant's first guardrail: it treated any high-priority feeding task as proof that a feeding existed, so "Appetite and water check" satisfied both feeding and water. My evaluation harness caught this when an indoor-cat plan had no Feeding task, and I changed the check to look at the task title. A second revision came from the same harness: the self-check loop stopped after 3 attempts and could not drop redundant meals, so a 20-minute plan lost its water check. I raised the limit and added a rule to collapse redundant meals. When I added the classifier, its first version guessed a life stage even when none was given, and the fix was in the training data, not the code.

**System limitations.**
- The knowledge base is small and was not reviewed by a veterinarian, so plans can be incomplete or wrong for a real pet. High confidence means "the request matched a document well", not "the advice is medically correct".
- Retrieval is keyword-based and misses paraphrases; profile parsing knows a fixed set of species, stages and conditions.
- The classifier is trained on synthetic data and evaluated on only 20 examples, with a threshold chosen on that same set.
- Guardrails are pattern-based, so a cleverly worded dosage question could get past them (the output guardrail is a second layer).
- Evaluation cases were written by the person who built the system, so they under-represent unexpected inputs.
- The scheduler lays tasks out sequentially from 08:00 and treats preferred time only as an ordering hint.

**Future improvements.** Embedding-based retrieval, a vet-reviewed knowledge base, a larger and independently written test set, and an optional LLM backend with evals that compare offline and LLM modes.
