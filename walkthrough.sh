#!/usr/bin/env bash
# One-command walkthrough of PawPal+ AI, designed for recording a video or a live demo.
# Usage: bash walkthrough.sh            (pauses between steps; press Enter to continue)
#        NONSTOP=1 bash walkthrough.sh  (no pauses)
set -e
cd "$(dirname "$0")"
PY=python3; [ -x .venv/bin/python ] && PY=.venv/bin/python

step() { echo; echo "=============================================================================="; echo "$1"; echo "=============================================================================="; }
pause() { [ -n "$NONSTOP" ] || read -r -p "-- press Enter to continue --" _; }

step "1/6  Unit tests (41 tests)"
$PY -m pytest -q
pause

step "2/6  Senior dog with arthritis: RAG + trained classifier + agent trace"
$PY demo.py "I have a senior dog with arthritis, I only have 45 minutes today"
pause

step "3/6  Baseline for comparison: same request with retrieval turned off"
$PY demo.py --baseline "I have a senior dog with arthritis, I only have 45 minutes today" | sed -n '/^Profile/,/^Confidence/p'
pause

step "4/6  Custom documents (RAG enhancement): Luna's vet notes change the plan"
$PY demo.py "Luna cat, 30 minutes" | sed -n '/^Profile/,/^Confidence/p'
pause

step "5/6  Guardrails: dosage question and an emergency are refused"
$PY demo.py "What dose of ibuprofen can I give my dog?" | sed -n '/^REQUEST/,/^Agent trace/p'
$PY demo.py "my dog ate chocolate what should I give him, 30 minutes" | sed -n '/^REQUEST/,/^Agent trace/p'
pause

step "6/6  Evaluation harness: predefined cases, pass/fail summary"
$PY evals/run_evals.py | sed -n '/## Summary/,$p'
echo; echo "Done. Full logs: evidence/   Results: evals/results.md"
