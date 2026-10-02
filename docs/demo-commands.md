# Demo commands (hackathon)

## Stage UI — shill this

Projector-friendly Streamlit: Easy/Hard presets, Haiku by default, live attempt
feed, green/red Receipt card.

```bash
pip install -e ".[demo]"
export ANTHROPIC_API_KEY=...
streamlit run demo/app.py
```

1. **Easy clear** → expect green `target_met: true`
2. **Hard refuse** → expect red + detail / per-model rates (Haiku may refuse sooner)

## Stage answer (15/15 suspicion)

> Nothing failed because the task is easy — that's the point. One shot gives
> you an answer; we give you the fact that it's safe. On the hard task, look
> what happens.

Then pivot to Hard refuse in the UI (or `python examples/demo_arc.py`).

## Code-open fallback

Smallest explainable script — open `examples/minimal.py` on stage, then:

```bash
python examples/minimal.py
```

Expect: `target_met: True`, `15/15`, `wilson_low` ≈ 0.80, ~$0.02.  
Stage line if asked about 15/15: see above, then pivot to the full arc.

## Full terminal arc (T9)

```bash
python examples/demo_arc.py
```

Drop weaker models when per-config rates show them dragging the pool:

```bash
python examples/demo_arc.py --models opus,sonnet
```

1. `is_palindrome` → clears `target=0.7` (mechanism works)
2. Strict `parse_money` → usually refuses; always prints per-model rates + failure reasons
