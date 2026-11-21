# PawPal+ AI: from a scheduler to an applied AI system

**Author:** Nafissatou LO · 491 Applied AI for Engineers · Fall 2026

**Repo:** https://github.com/Nafissah33/Applied-Ai-System

## Summary
I took PawPal+, a rule-based pet-care scheduler I built earlier, and extended it into an end-to-end AI system. You describe a pet in plain English ("senior dog with arthritis, 45 minutes today"), and the system retrieves care guidance, understands the request with a small trained classifier, checks its own output with guardrails, schedules the day with the original `Scheduler`, and explains each choice with a quoted source. It runs offline with no API key.

## What I built
- **Retrieval (RAG):** TF-IDF search over dog, cat, general and custom markdown guides. Retrieved sections decide which tasks are proposed, and explanations quote the retrieved sentence.
- **Specialized model:** a Naive Bayes classifier trained on 900 synthetic examples that reads life stage and conditions from free text. On 20 held-out paraphrased requests, keyword rules alone were right 8/20 times; rules plus the classifier were right 14/20 (tuned on the same 20 examples, so slightly optimistic).
- **Agentic workflow:** eight traced steps with a self-check loop that revises the plan if essential care is missed.
- **Guardrails:** input checks (injection, medical or dosage questions, empty or oversized input, tiny budgets) and output checks (schema, no dosage text, duplicates, forced feeding and water).
- **Evaluation:** 32 predefined checks, all passing, plus 30 unit tests.

## Results
| Check | Result |
|---|---|
| Expected specialized task, retrieval on vs off | 6/6 vs 0/6 |
| Guardrail cases (incl. adversarial) | 11/11 |
| Identical output across 3 runs | 6/6 |
| Classifier + rules vs rules (held-out) | 14/20 vs 8/20 |
| Explanations quoting a retrieved sentence | 20/20 |

## What I learned
My own evaluation harness found bugs that reading the code did not: a guardrail that treated "Appetite and water check" as both feeding and water, and a self-check loop that gave up too early. AI-written code looks confident, so it needs tests on edge cases before it can be trusted. I also learned how much a trained model depends on its data: the first classifier guessed a life stage when none was given, and fixing it was a data change, not a code change.

## Limitations
Keyword retrieval misses paraphrases, the classifier is trained on synthetic data and tested on a small set, and the guidance is general and not veterinary-reviewed. High confidence means "well matched", not "medically correct".

## Links
- Architecture diagram: `diagrams/architecture.mmd`
- Model card: `model_card.md`
- Agent traces: `ai_interactions.md`
- Reflection: `reflection.md`
- Evaluation results: `evals/results.md`
