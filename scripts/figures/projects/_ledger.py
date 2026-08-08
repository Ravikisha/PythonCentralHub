"""Shared access to the run ledger for projects figures.

Every figure in this group is drawn from ``docs/projects_run_ledger.json``,
which ``scripts/projects_run.py`` writes by actually executing the projects.
Nothing here invents a number: if the ledger is missing, the figures fail
loudly rather than drawing something plausible.
"""

from __future__ import annotations

import functools
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
LEDGER = os.path.join(REPO, "docs", "projects_run_ledger.json")


@functools.lru_cache(maxsize=1)
def ledger() -> dict:
    if not os.path.exists(LEDGER):
        raise FileNotFoundError(
            f"no run ledger at {LEDGER}. Run `python scripts/projects_run.py` "
            f"first — these figures report what happened when the projects "
            f"were executed, so there is nothing to draw without it.")
    with open(LEDGER, encoding="utf-8") as handle:
        return json.load(handle)


def runs() -> list[dict]:
    return ledger()["runs"]


def tier_of(row: dict) -> str:
    parts = row["source"].split("/")
    return parts[1] if len(parts) > 1 else "?"


def outcome(row: dict) -> str:
    if row["ok"]:
        return "ran"
    return row["skipped"] or "failed"
