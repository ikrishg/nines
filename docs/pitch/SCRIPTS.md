# Nines — pitch deck script + Remotion video package

Audience: Push to Prod judges (Anthropic architects + AI ops).
Tone: technical, honest, visual-first. Not CEO fluff.

**Built assets:** Remotion app at [`remotion/`](remotion/) — compositions `PitchDeck` + `DemoReel`. See [`remotion/README.md`](remotion/README.md).

**Assets in this folder**

| File piece | Use |
| --- | --- |
| §1 Pitch deck **script** | What you say + what each slide shows (~90s) |
| §2 Pitch deck **prompt** | Past reference for regenerating the deck |
| §3 Demo video **script** | Ad-lib VO over the shipped `DemoReel` (~85s) |
| §4 Remotion **prompt** | Storyboard matching the shipped composition |
| §5 Wald vs Wilson | One visual you must be able to explain |

---

## 1. Pitch deck script (~90 seconds)

**Rule:** one idea per slide. Never put the live terminal on a slide — that is the demo.
Headings below match `PitchDeck` in Remotion Studio.

### Slide 1 — Title
**On screen:** Giant **NINES**. Sub: *Reliability compiler for Claude*. Mono: `Apache 2.0 · github.com/kkrishguptaa/nines`.
**Say:**
> Agents are right most of the time. Shipping needs a number — and a system that refuses when it can’t prove it.

### Slide 2 — Hope is not a reliability bar
**On screen:** Two panels — “Ask Claude once / then hope” vs “Declared reliability / missing today”.
**Say:**
> Today you pick a model and hope. Nothing lets you declare a reliability target and spend compute until the m
ath clears it — or stop honestly.

### Slide 3 — One public seam
**On screen:** Code card:

```python
receipt = run(task, target=0.8, budget=Budget(...))
# target_met  → ship
# else        → human
```

**Say:**
> One public seam. You name the bar and the budget. You get a Receipt — green ship or red escalate. Never a silent best-guess when nothing passed.

### Slide 4 — Verifier first, then evidence
**On screen:** Pipeline draw-on:

`task → synthesize → canary → fan-out → gate → Wilson → receipt`

Callouts: *independent* · *known-bad* · *model×effort×framing* · *lower bound ≥ target*.

**Say:**
> Verifier first — from the task alone. Canary kills checkers that accept garbage. Then diverse solvers. Every candidate gated. `target_met` only if the Wilson lower bound clears your target.

### Slide 5 — Wilson, not Wald
**On screen:** §5 diagram under “15 passes / 15 trials”. Caption about Wald lying at the edges.
**Say:**
> Textbook Wald intervals collapse at perfect or zero passes. Wilson stays honest at the edges. Fifteen perfect trials → lower bound about **0.80**. That’s why attempt counts are 15 / 25 / 40 for 0.7 / 0.8 / 0.9 — not arbitrary.

### Slide 6 — You pay for evidence
**On screen:** Cost table (perfect runs):

| Target | Attempts | LLM calls | Cost USD |
| --- | ---: | ---: | ---: |
| 0.7 | 15 | 17 | 0.02 |
| 0.8 | 25 | 27 | 0.06 |
| 0.9 | 40 | 42 | 0.13 |

Footer: *Setup is about two calls. The rest is sampling.*

**Say:**
> Setup is almost free — two calls, three if canary regenerates. The rest is sampling. You’re paying for evidence, and you choose how much.

### Slide 7 — Clear the bar — or refuse
**On screen:** Split receipts — green `is_palindrome` · `target_met: true` · 15/15 · ~$0.02; red `parse_money` · `target_met: false` · opus 5/8 · sonnet 7/8 · haiku 1/9.
**Say:**
> Easy task: you didn’t gain a better answer — you gained **knowing**. Hard task: the pool fails, and we **refuse**. Everyone else will show something working. We can show a product declining to lie.

### Slide 8 — What we claim
**On screen:** Claimed vs not claimed columns + Stroebl-style caveat (checker-pass rate ≠ ground truth).
**Say:**
> We’re infrastructure around Claude — Apache 2.0, embeddable. Judges: ask us anything about the Receipt. Demo next.

**Q&A lines (memorize):**
- *15/15?* Easy task + early stop. Gain is knowing. Hard task next.
- *39/40?* Knife-edge — that’s why Wilson, not vibes.
- *Imperfect verifier?* We raise Stroebl ourselves; canary is the honesty gate.

---

## 2. Prompt — generate the pitch deck (Cursor)

```text
Build / refresh the Nines PitchDeck Remotion composition under docs/pitch/remotion/.

Constraints:
- Audience: Anthropic / AI infra judges, NOT generic startup CEOs.
- 8 slides matching docs/pitch/SCRIPTS.md §1 (headings + visual intent).
- Visual-first; no eyebrow kickers; amber #F5A524 on charcoal #0E1116.
- Fonts: Bricolage Grotesque + IBM Plex Mono via @remotion/google-fonts.
- Brand URL: github.com/kkrishguptaa/nines only — never nines.run as a domain.
- Do not invent claims beyond docs/claims.md and README.md.
```

---

## 3. Demo video script — ad-lib VO (~85s)

**Source of truth:** composition `DemoReel` (`docs/pitch/remotion/src/compositions/DemoReel.tsx`), 2550 frames @ 30fps.
**Render:** `cd docs/pitch/remotion && npm run render:reel` → `out/nines-reel.mp4`.
**Brand:** GitHub only — do **not** say or show `nines.run` as a website.

| Time | On screen (exact beat) | You say (ad-lib around this) |
| --- | --- | --- |
| **0:00–0:05** | **NINES** · “Reliability compiler for Claude” · amber rule | “Your agent is right most of the time. That’s not a shipping bar.” |
| **0:05–0:16** | Heading: “Per-step errors compound”. Bars 1→95%, 5→77%, 10→60%, **20→36%**. Caption: `20 steps × 95% each → ≈36% end-to-end`. Source: PRD problem statement | “Errors compound. Twenty steps at ninety-five percent each finish around thirty-six percent. High-stakes work stays manual.” |
| **0:16–0:23** | Card “single-shot Claude” → “An answer. No measured reliability.” | “Ask once and you get an answer — not measured reliability.” |
| **0:23–0:42** | Heading: “How Nines works”. Phase 1 Setup (~2 LLM calls): Task → Synthesize → Canary. Phase 2 Sample: Fan-out → Gate → Wilson → Receipt. Footer: escalate if Wilson low &lt; target; zero passes → no silent best-guess | “Nines compiles reliability. Independent checker. Canary. Diverse solvers. Gate every candidate. Escalate until Wilson clears the bar — or refuse.” |
| **0:42–0:52** | Heading: “Wilson, not Wald”. 15/15: Wald width→0; Wilson lower bound ≈0.80 | “Wald lies at perfect streaks. Wilson keeps an honest lower bound. Fifteen perfect trials only clear about eighty percent.” |
| **0:52–1:02** | “Easy task clears the bar” · green Receipt `is_palindrome` · `target_met: true` · 15/15 · ~$0.02 | “Easy task: you gained knowing — a receipt it’s safe to ship.” |
| **1:02–1:14** | “Hard task — refuse to lie” · red Receipt `parse_money` · `target_met: false` · opus 5/8 · sonnet 7/8 · haiku 1/9 | “Hard task: the pool splits. We refuse. No silent best-guess.” |
| **1:14–1:25** | Staggered: “Declare the bar. / Buy the evidence. / Or get an honest no.” · `Apache 2.0 · github.com/kkrishguptaa/nines` | “Declare the bar. Buy the evidence. Or get an honest no.” |

**Four beats to remember:** compound → how it works → clear → refuse.

---

## 4. Remotion storyboard (shipped)

Matches `DemoReel` sequences — do not drift from these times without updating the composition.

1. **0–5s** Title
2. **5–16s** Problem compounding (PRD math)
3. **16–23s** Single-shot hope
4. **23–42s** How Nines works (setup + sample loop)
5. **42–52s** Wald vs Wilson
6. **52–62s** Green Receipt
7. **62–74s** Red Receipt
8. **74–85s** End card

Design tokens: charcoal `#0E1116`, paper `#F4F1EA`, accent amber `#F5A524`. Motion: Bézier ease-out entrances + soft beat exits. Numbers in `src/data/copy.ts`.

---

## 5. Wald vs Wilson — explain this once, clearly

**Wald (textbook):**
\[
\hat p \pm z\sqrt{\hat p(1-\hat p)/n}
\]
At \(\hat p = 1\) (or 0), width **0** → false certainty after any perfect streak.

**Wilson (what Nines uses):** lower bound stays honest at the edges.
At 15/15 (z≈1.96): lower bound ≈ **0.80**.
So: **15 → ~0.80**, **25 → ~0.87**, **40 → ~0.91** — minimum *n* to clear 0.7 / 0.8 / 0.9 at 100% pass.

---

## Stage pairing

1. Play the **85s** reel (`out/nines-reel.mp4`) **or** skip to live.
2. Live: `python examples/demo_arc.py --models opus,sonnet` — clean win → refuse.
3. If asked about 15/15, use the stage line in `docs/demo-commands.md`, then point at the red receipt.
