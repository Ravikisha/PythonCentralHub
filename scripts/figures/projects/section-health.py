"""Figures for the projects section landing.

These report on the section itself rather than on any one project: what
happened when all 264 project files were executed, and what stands between the
rest and running. They exist because the honest first thing to say about a
collection of 203 projects is how many of them work.

``run-outcomes``
    Every project file by outcome, split by tier. "Ran" means the process
    exited zero with stdin closed and no display; everything else is named by
    the reason it could not.

``blockers``
    What stops the 190 that did not run, ranked. Each bar is a concrete piece
    of work rather than a category of failure.
"""

from __future__ import annotations

import functools
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "..", ".."))

from _ledger import outcome, runs, tier_of  # noqa: E402
from _style import Palette, figure  # noqa: E402

TIERS = ("beginners", "intermediate", "advance")
ORDER = ("ran", "failed", "needs stdin", "needs a display",
         "module not installed", "blocking server loop", "unbounded loop",
         "timeout", "syntax error")


@functools.lru_cache(maxsize=1)
def _counts() -> dict:
    rows = runs()
    grid = {tier: {kind: 0 for kind in ORDER} for tier in TIERS}
    reasons: dict[str, int] = {}
    for row in rows:
        tier = tier_of(row)
        kind = outcome(row)
        if tier in grid and kind in grid[tier]:
            grid[tier][kind] += 1
        if kind == "module not installed":
            for module in row["reason"].split(", "):
                if module:
                    reasons[module] = reasons.get(module, 0) + 1
    return {"grid": grid, "modules": reasons, "total": len(rows),
            "ran": sum(1 for row in rows if row["ok"]),
            "artifacts": sum(len(row["artifacts"]) for row in rows)}


def run_outcomes(fig, axes, p: Palette) -> None:
    info = _counts()
    ax = fig.subplots(1, 1)
    palette = {
        "ran": p.green, "failed": p.red, "needs stdin": p.amber,
        "needs a display": p.purple, "module not installed": p.muted,
        "blocking server loop": p.blue, "unbounded loop": p.blue,
        "timeout": p.red, "syntax error": p.red,
    }
    positions = np.arange(len(TIERS))
    left = np.zeros(len(TIERS))
    for kind in ORDER:
        values = np.array([info["grid"][tier][kind] for tier in TIERS],
                          dtype=float)
        if not values.any():
            continue
        ax.barh(positions, values, left=left, height=0.55,
                color=palette[kind], label=kind)
        for index, value in enumerate(values):
            if value >= 6:
                ax.annotate(f"{int(value)}", (left[index] + value / 2,
                                              positions[index]),
                            ha="center", va="center", fontsize=8, color=p.bg)
        left += values
    ax.set_yticks(positions)
    ax.set_yticklabels([tier for tier in TIERS])
    ax.set_xlabel("project files")
    ax.set_title(f"{info['total']} project files executed headlessly — "
                 f"{info['ran']} ran", fontsize=10)
    ax.legend(fontsize=7, ncol=3, loc="lower right")
    ax.invert_yaxis()


def blockers(fig, axes, p: Palette) -> None:
    info = _counts()
    left, right = fig.subplots(1, 2, width_ratios=(1.0, 1.1))

    kinds = [kind for kind in ORDER if kind != "ran"]
    totals = [sum(info["grid"][tier][kind] for tier in TIERS)
              for kind in kinds]
    keep = [(kind, total) for kind, total in zip(kinds, totals) if total]
    positions = np.arange(len(keep))
    left.barh(positions, [total for _, total in keep], color=p.amber,
              height=0.6)
    for position, (_, total) in zip(positions, keep):
        left.annotate(f"{total}", (total, position), xytext=(4, 0),
                      textcoords="offset points", fontsize=8, color=p.fg,
                      va="center")
    left.set_yticks(positions)
    left.set_yticklabels([kind for kind, _ in keep], fontsize=8)
    left.set_xlabel("project files")
    left.set_title("what stops the rest", fontsize=10)
    left.invert_yaxis()

    modules = sorted(info["modules"].items(), key=lambda kv: -kv[1])[:10]
    positions = np.arange(len(modules))
    right.barh(positions, [count for _, count in modules], color=p.muted,
               height=0.6)
    for position, (_, count) in zip(positions, modules):
        right.annotate(f"{count}", (count, position), xytext=(4, 0),
                       textcoords="offset points", fontsize=8, color=p.fg,
                       va="center")
    right.set_yticks(positions)
    right.set_yticklabels([name for name, _ in modules], fontsize=8)
    right.set_xlabel("project files that import it")
    right.set_title("missing modules, most blocking first", fontsize=10)
    right.invert_yaxis()


FIGURES = [
    figure("run-outcomes", run_outcomes, size=(8.8, 3.4), axes=False),
    figure("blockers", blockers, size=(9.2, 4.0), axes=False),
]


if __name__ == "__main__":
    info = _counts()
    print(f"=== {info['total']} project files ===")
    print(f"{'tier':14} " + " ".join(f"{kind[:11]:>12}" for kind in ORDER))
    for tier in TIERS:
        row = info["grid"][tier]
        print(f"{tier:14} " + " ".join(f"{row[kind]:>12}" for kind in ORDER))
    print(f"\nran: {info['ran']} of {info['total']}")
    print(f"artifacts produced by those runs: {info['artifacts']}")
    print("\nmissing modules, most blocking first:")
    for name, count in sorted(info["modules"].items(),
                              key=lambda kv: -kv[1])[:12]:
        print(f"  {count:4}  {name}")
