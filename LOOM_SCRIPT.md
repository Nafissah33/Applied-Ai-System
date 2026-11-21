# Loom video script (about 3 minutes, optional)

Grading is based on the README's text evidence, not the video. Record only if you want to. You do not need to show installation or file structure.

**Setup before recording:** open a terminal in the project folder, run `source .venv/bin/activate`, and make the font large. Start Loom, then run `bash walkthrough.sh` and press Enter between steps while you talk.

| Time | On screen | Say (in your own words) |
|---|---|---|
| 0:00 | Terminal, `bash walkthrough.sh` starts | "This is PawPal+ AI. I extended my earlier pet-care scheduler into an AI system that retrieves care guidance, understands plain-English requests, and checks its own work. It runs offline, no API key." |
| 0:20 | Step 1: tests pass | "41 unit tests pass." |
| 0:30 | Step 2: arthritic senior dog | "I typed one sentence. The classifier read 'senior' and 'arthritis', retrieval found joint-care guidance, and the plan has a short low-impact walk. Each task quotes its source, and the trace shows every tool the agent called, including a self-check." |
| 1:10 | Step 3: baseline | "Without retrieval, the same dog gets a generic 30-minute walk at low confidence. That is the difference RAG makes." |
| 1:30 | Step 4: Luna | "With a custom vet-notes document, the plan follows Luna's vet's advice: wet food and extra water, instead of a generic routine." |
| 1:50 | Step 5: guardrails | "Asking for a medication dose is refused with a vet referral, and a poisoning emergency tells the user to call an emergency vet instead of making a schedule." |
| 2:20 | Step 6: evaluation | "The evaluation harness runs 39 predefined cases and prints a pass/fail summary, plus average confidence and how the trained classifier compares to keyword rules." |
| 2:45 | Back to the camera or the README | "Limitations: the knowledge base isn't vet-reviewed, and confidence measures how well a request matched, not whether the advice is correct. Everything is in the repo, with a model card documenting this. Thanks for watching." |

After recording, send me the Loom link and I will add it to the README.
