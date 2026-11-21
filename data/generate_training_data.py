"""Generate the synthetic training set for the profile classifier (deterministic, seed 7).

Each example combines a pet noun, a life-stage phrase, zero or more condition phrases, and a time budget.
Phrase pools below are the TRAINING vocabulary. data/heldout_eval.jsonl uses different wording on purpose.
"""

import json
import random
from pathlib import Path

PETS = ["my dog", "my cat", "our puppy", "our kitten", "my dog Max", "my cat Luna", "the dog", "my golden retriever", "my tabby"]
STAGE = {
    "young": ["is a puppy", "is a kitten", "is only 8 weeks old", "is a few months old", "is young and playful", "just came home as a baby", "is newborn"],
    "adult": ["is 3 years old", "is an adult", "is fully grown", "is 5 years old", "is healthy and in his prime", "is two years old"],
    "senior": ["is a senior", "is elderly", "is 14 years old", "is getting up there in age", "is an old boy", "has a grey muzzle", "is in her golden years", "is aging"],
}
COND = {
    "joint": ["has arthritis", "is stiff in the morning", "is limping", "has sore joints", "has hip dysplasia", "is creaky", "struggles with stairs", "is slow to get up", "has trouble jumping on the couch", "has painful hips"],
    "weight": ["is overweight", "needs to lose weight", "is chubby", "is too heavy", "is on a diet", "is putting on pounds", "is obese", "keeps gaining weight"],
    "anxious": ["is anxious", "is hyper", "is restless", "gets bored easily", "destroys furniture", "is nervous around noises", "barks all day", "has high energy", "keeps pacing", "has separation anxiety", "tears up the sofa", "chews the cushions"],
    "indoor": ["is an indoor pet", "never goes outside", "lives in an apartment", "stays inside all day", "is a house pet"],
}
TIMES = ["I have 30 minutes", "only 45 minutes today", "1 hour available", "20 minutes free", "I have an hour", "60 minutes today"]
NEUTRAL = ["Plan a day for", "Help me care for", "Schedule care for", "What should I do with"]


def main(n: int = 900, seed: int = 7) -> None:
    rng = random.Random(seed)
    rows = []
    for _ in range(n):
        stage = rng.choice(list(STAGE))
        k = rng.choices([0, 1, 2], weights=[3, 4, 1])[0]
        conds = rng.sample(list(COND), k)
        parts = [f"{rng.choice(NEUTRAL)} {rng.choice(PETS)}."]
        if rng.random() < 0.3:
            stage = "adult"  # no age cue given: default life stage is adult
            lead = "It" if not conds else None
            parts.append("It " + COND[conds[0]][rng.randrange(len(COND[conds[0]]))] if conds else "")
            parts += [f"and {rng.choice(COND[c])}" for c in conds[1:]]
        else:
            parts.append(f"It {rng.choice(STAGE[stage])}")
            parts += [f"and {rng.choice(COND[c])}" for c in conds]
        text = " ".join(parts) + f". {rng.choice(TIMES)}."
        rows.append({"text": text, "stage": stage, "conditions": sorted(conds)})
    out = Path(__file__).parent / "profile_training.jsonl"
    out.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")
    print(f"wrote {len(rows)} examples to {out}")


if __name__ == "__main__":
    main()
