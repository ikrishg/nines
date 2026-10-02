#!/usr/bin/env python3
"""Two-task demo arc: clean win (is_palindrome) then hard billing parse.

Demo command (live API key required):

    python examples/demo_arc.py

1) is_palindrome @ target=0.7 — should clear (mechanism works)
2) parse_money (strict) @ target=0.7 — usually refuses; always prints
   per-model rates + failure reasons
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time

from demo.tasks import PALINDROME, PARSE_MONEY
from nines import Budget, run
from nines.report import format_config_line, format_failure_summary


def _print_receipt(label: str, receipt, elapsed: float) -> None:
    wilson = (
        f"[{receipt.wilson_low:.2f}, {receipt.wilson_high:.2f}]"
        if receipt.wilson_low is not None and receipt.wilson_high is not None
        else "n/a"
    )
    print("=" * 60)
    print(f"{label}")
    print("=" * 60)
    print(
        json.dumps(
            {
                "elapsed_s": round(elapsed, 1),
                "verifiable": receipt.verifiable,
                "checker_validated": receipt.checker_validated,
                "target": receipt.target,
                "target_met": receipt.target_met,
                "passes": receipt.passes,
                "trials": receipt.trials,
                "wilson": wilson,
                "total_cost_usd": round(receipt.total_cost_usd, 4),
                "detail": receipt.detail,
                "canary_detail": receipt.canary_detail,
                "by_model": format_config_line(receipt),
                "failures": format_failure_summary(receipt),
                "best_output_preview": (receipt.best_output or "")[:240],
            },
            indent=2,
        )
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Two-task Nines demo arc")
    parser.add_argument(
        "--models",
        default="opus,sonnet,haiku",
        help="Comma-separated solver tiers (default: opus,sonnet,haiku). "
        "Example: --models opus,sonnet to drop haiku.",
    )
    args = parser.parse_args()
    models = tuple(m.strip() for m in args.models.split(",") if m.strip())

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ANTHROPIC_API_KEY required for demo_arc", file=sys.stderr)
        return 2

    budget = Budget(max_cost_usd=3.0, max_attempts=25)
    t0 = time.time()
    r1 = run(
        PALINDROME,
        target=0.7,
        budget=budget,
        initial_batch=5,
        max_workers=5,
        models=models,
    )
    _print_receipt("1/2 CLEAN WIN — is_palindrome (target=0.7)", r1, time.time() - t0)

    t1 = time.time()
    r2 = run(
        PARSE_MONEY,
        target=0.7,
        budget=budget,
        initial_batch=5,
        max_workers=5,
        models=models,
    )
    _print_receipt(
        "2/2 HARD TASK — parse_money strict (target=0.7)", r2, time.time() - t1
    )

    total = time.time() - t0
    print("=" * 60)
    print(
        f"TOTAL {total:.1f}s | "
        f"palindrome target_met={r1.target_met} | "
        f"parse_money target_met={r2.target_met}"
    )
    # Non-negotiable: clean task must clear. Hard task prints why either way.
    return 0 if r1.target_met else 1


if __name__ == "__main__":
    raise SystemExit(main())
