# Nines

Your agent is right ~70% of the time. Tell Nines the bar you need — get a **receipt**, or an honest refuse.

Nines is a **reliability compiler** for Claude: declare `target` + `budget`, synthesize an independent checker, fan out diverse solvers, escalate until a **Wilson lower bound** clears the target (or stop with `target_met: false`). No silent best-guess when nothing passes.

```python
from nines import run, Task, Budget

receipt = run(
    Task(prompt="Write is_palindrome(s: str) -> bool. Empty string is True. Code only."),
    target=0.8,
    budget=Budget(max_cost_usd=2.0, max_attempts=25),
    models=("opus", "sonnet"),  # drop tiers that drag the pool
)
if receipt.target_met:
    ship(receipt.best_output)
else:
    escalate_to_human(receipt.detail)
```

License: **Apache 2.0** — embeddable infrastructure, not GPL copyleft.

## Single-shot vs Nines (measured, same task)

Task: `is_palindrome`. Live Claude. Costs ≈ adapter estimates, not invoices.

| Approach | Models | Target | Cleared? | Checker passes | Approx. cost | Note |
| --- | --- | --- | --- | ---: | ---: | --- |
| **Without Nines** | Sonnet ×1 | — | Unknown | 1 try, no bound | **~$0.001** | Answer, no trust signal |
| **Nines** | Opus+Sonnet+Haiku | **0.70** | **Yes** | 15 / 15 | **~$0.02** | Stops at min *n* for Wilson @ 100% |
| **Nines** | Opus+Sonnet | **0.70** | **Yes** | 15 / 15 | **~$0.03** | Same bar, stronger pool |
| **Nines** | Opus+Sonnet | **0.80** | **Yes** | 25 / 25 | **~$0.06** | Higher bar → more samples |
| **Nines** | Opus only | **0.90** | **Yes** | 40 / 40 | **~$0.13** | `max_attempts=40` |
| **Nines** (refuse) | Opus only | **0.90** | **No** | 0 | **$0** | Same target, **smaller attempt budget** (`max_attempts=25`): 25/25 Wilson low ≈ 0.87 &lt; 0.90 → unreachable, no spend |

**Why so many perfect rows?** Easy task + early stop. At 100% pass rate, Wilson needs ~15 / 25 / 40 trials to clear 0.7 / 0.8 / 0.9 — so the table *should* look like that. You did not gain a “better” palindrome; you gained **knowing** it’s safe to ship. One shot gives an answer and no idea whether to trust it. On a hard task the pool *does* fail — see `parse_money` below.

**Receipt words, plain English:**

| Field | Meaning |
| --- | --- |
| **Checker pass** | Independent QA said yes. Second process that only knows the *rules*, not the draft. |
| **`target_met`** | Wilson **lower bound** ≥ your target — not a lucky point estimate. Green = ship. Red = human. |

### Technical spine (why this isn’t vibes)

- **Wilson score interval (z≈1.96), not Wald.** Wald intervals lie at the edges (0/n, n/n) — exactly where agent demos live. `target_met` iff lower bound ≥ `target`.
- **Canary / mutation check.** Before trusting a checker, run a known-bad candidate (and known-good when we have one). A checker that accepts garbage is discarded — the degenerate case “passes everything because it checks nothing.”
- **Honest scope.** We measure **checker-pass rate**, not ground-truth correctness. If the verifier is wrong, the receipt is wrong (Stroebl et al.–style caveat). Canary reduces that risk; it does not erase it.
- **Hard-task refusal is the product.** Strict `parse_money` often returns `target_met: false` with e.g. `opus: 5/8 · sonnet: 7/8 · haiku: 1/9` and assertion-failure frequencies — decline to lie, then optionally drop weak models via `models=`.

## What ships

1. Independent verifier synthesis + canary  
2. Diverse fan-out (model × effort × framing)  
3. Wilson-gated `target_met`  
4. Budget stop; zero passes ⇒ no silent best-guess  

Seam: `nines.run(task, *, target, budget) -> Receipt`. Claims map: [`docs/claims.md`](docs/claims.md).

## Demo (~2 min)

```bash
pip install -e ".[demo]"
export ANTHROPIC_API_KEY=...

# Stage UI — Haiku default, live attempts, green/red Receipt
streamlit run demo/app.py

# Code-open fallback — open examples/minimal.py, then run it
python examples/minimal.py

# Full terminal arc: clean win → honest refuse
python examples/demo_arc.py --models opus,sonnet

python -m demo.compare --fallback --trials 25 --target 0.7
```

**Stage line if asked about 15/15:** *Nothing failed because the task is easy — that’s the point. One shot gives you an answer; we give you the fact that it’s safe. On the hard task, look what happens.* → pivot to `parse_money` refuse.

## Limits

- Target above best Wilson lower bound for `max_attempts` → immediate unreachable refuse.  
- Subjective tasks → `verifiable=False`, no solver spend.  
- Subprocess sandbox is **not** multi-tenant isolation.  
- Not a novel model; not a production SLA.
