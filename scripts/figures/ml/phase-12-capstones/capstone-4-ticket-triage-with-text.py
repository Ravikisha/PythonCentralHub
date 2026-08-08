"""Figure for *Capstone 4 — Ticket Triage with Text*."""

import functools
import importlib.util
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from _style import Palette, figure  # noqa: E402

HUMAN_COST = 2.0        # euros to triage a ticket by hand
MISROUTE_COST = 12.0    # euros of delay when the model routes to the wrong queue
THRESHOLDS = (0.0, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95)


def _phase10():
    path = os.path.join(HERE, "..", "phase-10-applied", "_data.py")
    spec = importlib.util.spec_from_file_location("pch_phase10_data", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@functools.lru_cache(maxsize=1)
def setup():
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import train_test_split

    docs, y, names = _phase10().support_tickets()
    d_tr, d_te, y_tr, y_te = train_test_split(docs, y, test_size=0.3,
                                              random_state=0, stratify=y)
    vec = TfidfVectorizer(min_df=2)
    model = LogisticRegression(max_iter=2000).fit(vec.fit_transform(d_tr), y_tr)
    proba = model.predict_proba(vec.transform(d_te))
    return {"y_te": np.asarray(y_te), "pred": proba.argmax(axis=1),
            "conf": proba.max(axis=1), "names": names, "n": len(y_te)}


def policy_cost(threshold):
    d = setup()
    auto = d["conf"] >= threshold
    misrouted = int((d["pred"][auto] != d["y_te"][auto]).sum())
    to_human = int((~auto).sum())
    accuracy = (float((d["pred"][auto] == d["y_te"][auto]).mean())
                if auto.any() else float("nan"))
    return {"coverage": float(auto.mean()), "accuracy": accuracy,
            "misrouted": misrouted, "to_human": to_human,
            "cost": misrouted * MISROUTE_COST + to_human * HUMAN_COST}


def selective_prediction(fig, axes, p: Palette) -> None:
    """How much work the model can take on, at what accuracy, at what cost."""
    d = setup()
    rows = [policy_cost(t) for t in THRESHOLDS]
    coverage = [r["coverage"] for r in rows]
    accuracy = [r["accuracy"] for r in rows]
    costs = [r["cost"] for r in rows]

    axs = fig.subplots(1, 2)

    axs[0].plot(coverage, accuracy, "o-", color=p.blue, lw=2.4)
    for t, c, a in zip(THRESHOLDS, coverage, accuracy):
        axs[0].annotate(f"{t:.2f}", (c, a), textcoords="offset points",
                        xytext=(0, 9), ha="center", fontsize=8, color=p.muted)
    axs[0].axhline(0.95, color=p.amber, lw=1.4, ls="--",
                   label="95% accuracy target")
    best95 = max((r for r in rows if r["accuracy"] >= 0.95),
                 key=lambda r: r["coverage"])
    axs[0].scatter([best95["coverage"]], [best95["accuracy"]], s=110,
                   facecolor="none", edgecolor=p.green, lw=2.2,
                   label=f"{best95['coverage']:.1%} coverage at "
                         f"{best95['accuracy']:.4f}")
    axs[0].set_xlabel("coverage — share of tickets routed automatically")
    axs[0].set_ylabel("accuracy on the routed tickets")
    axs[0].set_title("Confidence thresholds label the points", fontsize=10.5)
    axs[0].legend(loc="lower left", fontsize=8.5)

    axs[1].plot(coverage, costs, "o-", color=p.red, lw=2.4)
    cheapest = min(rows, key=lambda r: r["cost"])
    axs[1].scatter([cheapest["coverage"]], [cheapest["cost"]], s=110,
                   facecolor="none", edgecolor=p.green, lw=2.2,
                   label=f"cheapest: EUR {cheapest['cost']:,.0f}")
    all_human = d["n"] * HUMAN_COST
    all_auto = int((d["pred"] != d["y_te"]).sum()) * MISROUTE_COST
    axs[1].axhline(all_human, color=p.muted, lw=1.4, ls=":",
                   label=f"all human: EUR {all_human:,.0f}")
    axs[1].axhline(all_auto, color=p.amber, lw=1.4, ls="--",
                   label=f"all automatic: EUR {all_auto:,.0f}")
    axs[1].set_xlabel("coverage — share of tickets routed automatically")
    axs[1].set_ylabel(f"cost over {d['n']:,} tickets (EUR)")
    axs[1].set_ylim(0, all_human * 1.15)
    axs[1].set_title(f"Optimum at {cheapest['coverage']:.1%} coverage",
                     fontsize=10.5)
    axs[1].legend(loc="lower center", fontsize=8)

    fig.suptitle(f"Triage by hand costs EUR {HUMAN_COST:.0f}; a misrouted ticket "
                 f"costs EUR {MISROUTE_COST:.0f}. Neither extreme is optimal.",
                 fontsize=10.5, color=p.muted)


FIGURES = [
    figure("selective-prediction", selective_prediction, size=(8.8, 4.0),
           axes=False),
]
