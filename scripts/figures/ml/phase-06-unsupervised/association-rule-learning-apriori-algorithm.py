"""Figures for *Association Rule Learning (Apriori Algorithm)*."""

import os
import sys
from itertools import combinations

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _data import BASKETS  # noqa: E402
from _style import Palette, figure  # noqa: E402

ITEMS = sorted({i for b in BASKETS for i in b})
N = len(BASKETS)


def _support(itemset):
    s = set(itemset)
    return sum(1 for b in BASKETS if s <= set(b)) / N


def item_supports(fig, axes, p: Palette) -> None:
    """Level 1 of Apriori: count every single item, then apply min_support."""
    sup = sorted(((i, _support([i])) for i in ITEMS), key=lambda t: -t[1])
    names = [s[0] for s in sup]
    vals = [s[1] for s in sup]
    thr = 0.20
    colors = [p.blue if v >= thr else p.muted for v in vals]

    axes.barh(names[::-1], vals[::-1], color=colors[::-1])
    axes.axvline(thr, color=p.red, ls="--", lw=1.6,
                 label=f"min_support = {thr:.0%} ({int(thr * N)} of {N} baskets)")
    for i, (n, v) in enumerate(zip(names[::-1], vals[::-1])):
        axes.annotate(f"{v:.2f}", (v + 0.012, i), va="center", color=p.muted,
                      fontsize=9)
    axes.set_xlabel("support")
    axes.set_xlim(0, 0.75)
    axes.set_title(f"Single-item support across {N} baskets")
    axes.legend(loc="lower right")


def candidate_pruning(fig, axes, p: Palette) -> None:
    """The downward-closure property collapses the candidate count each level."""
    thr = 0.20
    frequent = {1: [frozenset([i]) for i in ITEMS if _support([i]) >= thr]}
    generated, kept = {1: len(ITEMS)}, {1: len(frequent[1])}

    k = 2
    while frequent.get(k - 1):
        prev = frequent[k - 1]
        cands = set()
        for a, b in combinations(prev, 2):
            u = a | b
            if len(u) == k and all(frozenset(s) in set(prev)
                                   for s in combinations(u, k - 1)):
                cands.add(u)
        generated[k] = len(cands)
        frequent[k] = [c for c in cands if _support(c) >= thr]
        kept[k] = len(frequent[k])
        k += 1

    levels = sorted(generated)
    naive = [len(list(combinations(ITEMS, L))) for L in levels]
    x = np.arange(len(levels))
    w = 0.27

    axes.bar(x - w, naive, w, color=p.muted, label="all possible itemsets")
    axes.bar(x, [generated[L] for L in levels], w, color=p.amber,
             label="candidates Apriori generates")
    axes.bar(x + w, [kept[L] for L in levels], w, color=p.blue,
             label="frequent (support ≥ 20%)")
    for xi, L in zip(x, levels):
        axes.annotate(str(naive[xi]), (xi - w, naive[xi] + 0.4), ha="center",
                      color=p.muted, fontsize=9)
        axes.annotate(str(generated[L]), (xi, generated[L] + 0.4), ha="center",
                      color=p.amber, fontsize=9)
        axes.annotate(str(kept[L]), (xi + w, kept[L] + 0.4), ha="center",
                      color=p.blue, fontsize=9)
    axes.set_xticks(x)
    axes.set_xticklabels([f"{L}-itemsets" for L in levels])
    axes.set_ylabel("count")
    axes.set_title("Pruning by downward closure")
    axes.legend()


def rule_scatter(fig, axes, p: Palette) -> None:
    """Every rule as a point: support, confidence, lift."""
    thr = 0.15
    freq = []
    for size in (2, 3):
        for c in combinations(ITEMS, size):
            if _support(c) >= thr:
                freq.append(frozenset(c))

    rows = []
    for fs in freq:
        for r in range(1, len(fs)):
            for ante in combinations(sorted(fs), r):
                cons = fs - set(ante)
                sup = _support(fs)
                conf = sup / _support(ante)
                lift = conf / _support(cons)
                rows.append((sup, conf, lift,
                             ",".join(ante) + " → " + ",".join(sorted(cons))))

    sup = np.array([r[0] for r in rows])
    conf = np.array([r[1] for r in rows])
    lift = np.array([r[2] for r in rows])

    span = max(lift.max() - 1.0, 1.0 - lift.min())
    sc = axes.scatter(sup, conf, c=lift, s=90, cmap="coolwarm",
                      vmin=1 - span, vmax=1 + span, edgecolors=p.bg,
                      linewidths=0.7)
    best = int(np.argmax(lift))
    worst = int(np.argmin(lift))
    axes.annotate(f"strongest: {rows[best][3]}  (lift {lift[best]:.2f})",
                  (0.03, 0.06), xycoords="axes fraction", fontsize=9, color=p.red)
    axes.annotate(f"weakest: {rows[worst][3]}  (lift {lift[worst]:.2f})",
                  (0.03, 0.01), xycoords="axes fraction", fontsize=9, color=p.blue)
    axes.set_xlabel("support")
    axes.set_ylabel("confidence")
    axes.set_ylim(0.18, 1.12)
    axes.set_title("Rules with support ≥ 15% — colour is lift")
    cb = fig.colorbar(sc, ax=axes, fraction=0.046)
    cb.set_label("lift", color=p.fg)
    cb.ax.tick_params(colors=p.muted)


def confidence_trap(fig, axes, p: Palette) -> None:
    """A high-confidence rule can still be worse than guessing."""
    rules = [
        "bread → butter",
        "butter → bread",
        "milk → bread",
        "beer → chips",
        "jam → milk",
        "chips → bread",
    ]
    conf, lift, names = [], [], []
    for name in rules:
        a, c = [s.strip() for s in name.split("→")]
        sup = _support([a, c])
        cf = sup / _support([a])
        lf = cf / _support([c])
        conf.append(cf)
        lift.append(lf)
        names.append(name)

    order = np.argsort(conf)[::-1]
    x = np.arange(len(names))
    axs = fig.subplots(1, 2, sharey=False)
    axs[0].bar(x, [conf[i] for i in order], color=p.blue)
    axs[0].set_xticks(x)
    axs[0].set_xticklabels([names[i] for i in order], rotation=35, ha="right",
                           fontsize=9)
    axs[0].set_ylabel("confidence")
    axs[0].set_title("Ranked by confidence")

    axs[1].bar(x, [lift[i] for i in order],
               color=[p.green if lift[i] > 1 else p.red for i in order])
    axs[1].axhline(1.0, color=p.muted, ls="--", lw=1.4, label="lift = 1 (independent)")
    axs[1].set_xticks(x)
    axs[1].set_xticklabels([names[i] for i in order], rotation=35, ha="right",
                           fontsize=9)
    axs[1].set_ylabel("lift")
    axs[1].set_title("Lift divides by how common the consequent already is")
    axs[1].legend()
    axs[0].annotate("80% confidence,\nbut bread is in 65%\nof baskets anyway",
                    (0.30, 0.62), xycoords="axes fraction", fontsize=9,
                    color=p.amber)


FIGURES = [
    figure("item-supports", item_supports, size=(7.4, 3.8)),
    figure("candidate-pruning", candidate_pruning, size=(7.8, 3.8)),
    figure("rule-scatter", rule_scatter, size=(7.8, 4.2)),
    figure("confidence-trap", confidence_trap, size=(8.6, 3.8), axes=False),
]
