"""Shared Easy/Hard demo tasks — keep arc + Streamlit UI in sync."""

from __future__ import annotations

from nines import Task

PALINDROME = Task(
    prompt=(
        "Write a Python function is_palindrome(s: str) -> bool that returns True "
        "iff s equals its reverse. Case-sensitive, spaces matter. Empty string is True. "
        "Code only."
    )
)

# Strict billing parser — many edges; models usually miss some under the checker.
PARSE_MONEY = Task(
    prompt=(
        "Write a Python function parse_money(text: str) -> int for checkout.\n"
        "Return integer cents. Rules (all mandatory):\n"
        "1) Accept only an optional leading '$', optional thousands commas in US "
        "grouping (e.g. 1,234,567), and optional '.' with 0–2 decimal digits.\n"
        "2) Examples that MUST work: '$1,234.56'->123456, '1234.5'->123450, "
        "'12'->1200, '  $0.99 '->99, '$.5'->50, '0'->0.\n"
        "3) MUST raise ValueError for: '', '  ', '-1', '+1', '1.2.3', 'abc', "
        "'1.234' (>2 decimals), '1,23' (EU-style), '12,34.56' (bad grouping), "
        "'$€1', '1 234.56' (spaces inside), '--1', 'NaN'.\n"
        "4) Do not accept bare commas as decimal separators.\n"
        "Respond with ONLY the function source."
    ),
    context="Wrong cents = wrong charges. Checker is strict.",
)

PRESETS = {
    "easy": {
        "label": "Easy clear — is_palindrome",
        "task": PALINDROME,
        "expect": "clear",
    },
    "hard": {
        "label": "Hard refuse — parse_money",
        "task": PARSE_MONEY,
        "expect": "refuse",
    },
}
