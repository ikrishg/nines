"""Projector-friendly Streamlit stage UI for Nines.

    pip install -e ".[demo]"
    export ANTHROPIC_API_KEY=...
    streamlit run demo/app.py
"""

from __future__ import annotations

import os
from html import escape

import streamlit as st

from demo.tasks import PARSE_MONEY, PALINDROME, PRESETS
from nines import Budget, Task, run
from nines.report import format_config_line, format_failure_summary
from nines.types import Attempt, Receipt

GITHUB = "https://github.com/kkrishguptaa/nines"
CHARCOAL = "#0E1116"
PAPER = "#F4F0E8"
AMBER = "#F5A524"
GREEN = "#2ECC71"
RED = "#E74C3C"
MUTED = "#9AA3AF"

st.set_page_config(
    page_title="Nines",
    page_icon="▣",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    f"""
<style>
  .stApp {{
    background: {CHARCOAL};
    color: {PAPER};
  }}
  [data-testid="stSidebar"] {{
    background: #12161d;
    border-right: 1px solid #1e2530;
  }}
  [data-testid="stSidebar"] * {{
    color: {PAPER};
  }}
  h1, h2, h3, label, p, span, div {{
    font-family: "IBM Plex Sans", "Segoe UI", sans-serif;
  }}
  .nines-brand {{
    font-size: 3.2rem;
    font-weight: 700;
    letter-spacing: 0.04em;
    color: {PAPER};
    margin: 0 0 0.15rem 0;
  }}
  .nines-sub {{
    color: {MUTED};
    font-size: 1.05rem;
    margin-bottom: 1.25rem;
  }}
  .nines-sub a {{
    color: {AMBER};
    text-decoration: none;
  }}
  .attempt-row {{
    font-family: "IBM Plex Mono", ui-monospace, monospace;
    font-size: 0.95rem;
    padding: 0.35rem 0.6rem;
    border-left: 3px solid {MUTED};
    margin: 0.2rem 0;
    background: #161b22;
  }}
  .attempt-pass {{ border-left-color: {GREEN}; color: {GREEN}; }}
  .attempt-fail {{ border-left-color: {RED}; color: {RED}; }}
  .receipt-card {{
    border: 2px solid {AMBER};
    border-radius: 6px;
    padding: 1.5rem 1.75rem;
    background: #12161d;
    margin-top: 0.75rem;
  }}
  .receipt-card.met {{ border-color: {GREEN}; }}
  .receipt-card.miss {{ border-color: {RED}; }}
  .receipt-verdict {{
    font-size: 3.5rem;
    font-weight: 800;
    letter-spacing: 0.02em;
    line-height: 1.1;
    margin: 0 0 0.75rem 0;
  }}
  .receipt-verdict.met {{ color: {GREEN}; }}
  .receipt-verdict.miss {{ color: {RED}; }}
  .receipt-meta {{
    font-family: "IBM Plex Mono", ui-monospace, monospace;
    font-size: 1.15rem;
    color: {PAPER};
    line-height: 1.7;
  }}
  .receipt-detail {{
    color: {MUTED};
    margin-top: 0.85rem;
    font-size: 0.95rem;
  }}
  .receipt-output {{
    margin-top: 1rem;
    padding: 0.75rem 1rem;
    background: {CHARCOAL};
    border: 1px solid #1e2530;
    font-family: "IBM Plex Mono", ui-monospace, monospace;
    font-size: 0.85rem;
    white-space: pre-wrap;
    color: {PAPER};
    max-height: 220px;
    overflow: auto;
  }}
  div.stButton > button {{
    background: {AMBER};
    color: {CHARCOAL};
    border: none;
    font-weight: 700;
  }}
  div.stButton > button:hover {{
    background: #ffb84d;
    color: {CHARCOAL};
  }}
</style>
""",
    unsafe_allow_html=True,
)


def _attempt_line(i: int, attempt: Attempt) -> str:
    model = attempt.config.get("model", "?")
    effort = attempt.config.get("effort", "?")
    framing = attempt.config.get("framing", "?")
    if attempt.passed:
        cls = "attempt-pass"
        mark = "PASS"
    else:
        cls = "attempt-fail"
        mark = "FAIL"
    reason = ""
    if not attempt.passed:
        raw = (attempt.fail_reason or attempt.error or "")[:80]
        if raw:
            reason = f" — {escape(raw)}"
    return (
        f'<div class="attempt-row {cls}">'
        f"#{i} {escape(str(model))} · {escape(str(effort))} · "
        f"{escape(str(framing))} · <b>{mark}</b>{reason}"
        f"</div>"
    )


def _render_feed(attempts: list[Attempt]) -> str:
    if not attempts:
        return (
            f'<div class="attempt-row" style="color:{MUTED}">'
            "Waiting for attempts…</div>"
        )
    return "\n".join(_attempt_line(i + 1, a) for i, a in enumerate(attempts))


def _receipt_html(receipt: Receipt) -> str:
    met = bool(receipt.target_met)
    cls = "met" if met else "miss"
    verdict = "target_met: true" if met else "target_met: false"
    if receipt.wilson_low is not None and receipt.wilson_high is not None:
        wilson = f"[{receipt.wilson_low:.2f}, {receipt.wilson_high:.2f}]"
    else:
        wilson = "n/a"
    detail = escape(receipt.detail or "—")
    canary = escape(receipt.canary_detail or "—")
    by_model = escape(format_config_line(receipt))
    failures = escape(format_failure_summary(receipt))
    best = escape((receipt.best_output or "(none)")[:600])
    return f"""
<div class="receipt-card {cls}">
  <div class="receipt-verdict {cls}">{verdict}</div>
  <div class="receipt-meta">
    {receipt.passes}/{receipt.trials} passes<br/>
    Wilson {wilson} · target {receipt.target}<br/>
    cost ${receipt.total_cost_usd:.4f}<br/>
    {by_model}
  </div>
  <div class="receipt-detail">
    detail: {detail}<br/>
    canary: {canary}<br/>
    {failures}
  </div>
  <div class="receipt-output">{best}</div>
</div>
"""


def _resolve_task(preset_key: str, custom: str) -> Task:
    custom = custom.strip()
    if custom == PALINDROME.prompt.strip():
        return PALINDROME
    if custom == PARSE_MONEY.prompt.strip():
        return PARSE_MONEY
    if custom:
        return Task(prompt=custom)
    if preset_key == "hard":
        return PARSE_MONEY
    return PALINDROME


def main() -> None:
    st.markdown('<p class="nines-brand">NINES</p>', unsafe_allow_html=True)
    st.markdown(
        f'<p class="nines-sub">Reliability compiler for Claude · '
        f'<a href="{GITHUB}" target="_blank">github.com/kkrishguptaa/nines</a></p>',
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.markdown("### Run settings")
        target = st.slider("target", 0.5, 0.99, 0.7, 0.01)
        max_attempts = st.number_input(
            "max attempts", min_value=1, max_value=60, value=15, step=1
        )
        max_cost = st.number_input(
            "max cost USD", min_value=0.1, max_value=10.0, value=1.0, step=0.1
        )
        st.markdown("### Models")
        use_haiku = st.checkbox("haiku", value=True)
        use_sonnet = st.checkbox("sonnet", value=False)
        use_opus = st.checkbox("opus", value=False)
        models: list[str] = []
        if use_opus:
            models.append("opus")
        if use_sonnet:
            models.append("sonnet")
        if use_haiku:
            models.append("haiku")
        st.caption("Default: haiku only (fast stage path).")

    if "preset" not in st.session_state:
        st.session_state.preset = "easy"
    if "prompt_text" not in st.session_state:
        st.session_state.prompt_text = PALINDROME.prompt

    c1, c2, c3 = st.columns([1, 1, 2])
    with c1:
        if st.button(PRESETS["easy"]["label"], use_container_width=True):
            st.session_state.preset = "easy"
            st.session_state.prompt_text = PALINDROME.prompt
            st.rerun()
    with c2:
        if st.button(PRESETS["hard"]["label"], use_container_width=True):
            st.session_state.preset = "hard"
            st.session_state.prompt_text = PARSE_MONEY.prompt
            st.rerun()
    with c3:
        expect = PRESETS[st.session_state.preset]["expect"]
        st.markdown(
            f"**Preset:** `{st.session_state.preset}` · expect **{expect}**"
        )

    prompt_text = st.text_area(
        "Task prompt (edit for custom)",
        height=160,
        key="prompt_text",
    )

    run_clicked = st.button("Run", type="primary", use_container_width=False)

    feed_title = st.empty()
    feed_box = st.empty()
    receipt_box = st.empty()

    if not run_clicked:
        feed_title.markdown("### Attempt feed")
        feed_box.markdown(
            _render_feed([]),
            unsafe_allow_html=True,
        )
        return

    if not models:
        st.error("Select at least one model (haiku / sonnet / opus).")
        return

    if not os.environ.get("ANTHROPIC_API_KEY"):
        st.error(
            "ANTHROPIC_API_KEY is not set. Export it in this shell, then restart "
            "`streamlit run demo/app.py`."
        )
        return

    task = _resolve_task(st.session_state.preset, prompt_text)
    # Custom text that differs from both presets → treat as custom (no expect badge).
    if prompt_text.strip() not in {PALINDROME.prompt, PARSE_MONEY.prompt}:
        st.info("Running custom prompt.")

    feed_title.markdown("### Attempt feed")
    attempts: list[Attempt] = []
    feed_box.markdown(_render_feed(attempts), unsafe_allow_html=True)

    def on_attempt(attempt: Attempt) -> None:
        attempts.append(attempt)
        feed_box.markdown(_render_feed(attempts), unsafe_allow_html=True)

    with st.spinner("Synthesizing verifier · sampling solvers…"):
        receipt = run(
            task,
            target=float(target),
            budget=Budget(
                max_cost_usd=float(max_cost),
                max_attempts=int(max_attempts),
            ),
            models=tuple(models),
            on_attempt=on_attempt,
            parallel=True,
            initial_batch=5,
        )

    receipt_box.markdown(_receipt_html(receipt), unsafe_allow_html=True)


if __name__ == "__main__":
    main()
