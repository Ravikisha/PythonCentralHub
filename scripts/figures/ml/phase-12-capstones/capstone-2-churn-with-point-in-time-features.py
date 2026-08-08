"""Figure for *Capstone 2 — Churn with Point-in-Time Features*."""

import functools
import importlib.util
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from _style import Palette, figure  # noqa: E402

SAVE_RATE = 0.30          # probability the offer retains a customer who would churn
CUSTOMER_VALUE = 120.0    # value of a retained customer
OFFERS = (4, 8, 16, 24, 32)


def _phase11():
    path = os.path.join(HERE, "..", "phase-11-engineering", "_data.py")
    spec = importlib.util.spec_from_file_location("pch_phase11_data", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@functools.lru_cache(maxsize=1)
def setup():
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler

    data = _phase11()
    events, future, churn = data.event_log()
    ids = np.arange(len(churn))
    features = data.window_features(events, 30, data.CUTOFF, ids)

    rng = np.random.default_rng(21)
    train = np.zeros(len(churn), dtype=bool)
    train[rng.permutation(len(churn))[:int(0.7 * len(churn))]] = True

    model = make_pipeline(StandardScaler(),
                          LogisticRegression(max_iter=2000)).fit(features[train],
                                                                 churn[train])
    return {"proba": model.predict_proba(features[~train])[:, 1],
            "y": churn[~train], "n": int((~train).sum()),
            "events": events, "future": future, "churn": churn, "ids": ids,
            "train": train, "features": features, "data": data}


def campaign_value(contact, y, offer):
    """Euros saved by retaining churners, minus the cost of every offer sent."""
    retained = float((contact & (y == 1)).sum()) * SAVE_RATE * CUSTOMER_VALUE
    return retained - float(contact.sum()) * offer


def value_of_targeting(fig, axes, p: Palette) -> None:
    """What the model is worth depends entirely on what the offer costs."""
    d = setup()
    proba, y = d["proba"], d["y"]
    rng = np.random.default_rng(5)

    model_value, everybody, random_value, thresholds, contacted = [], [], [], [], []
    for offer in OFFERS:
        t = offer / (SAVE_RATE * CUSTOMER_VALUE)
        chosen = proba >= t
        thresholds.append(t)
        contacted.append(int(chosen.sum()))
        model_value.append(campaign_value(chosen, y, offer))
        everybody.append(campaign_value(np.ones(len(y), dtype=bool), y, offer))
        draw = np.zeros(len(y), dtype=bool)
        draw[rng.permutation(len(y))[:int(chosen.sum())]] = True
        random_value.append(campaign_value(draw, y, offer))

    idx = np.arange(len(OFFERS))
    axs = fig.subplots(1, 2, width_ratios=[1.15, 1])

    axs[0].bar(idx - 0.26, everybody, 0.25, color=p.muted,
               label="contact everybody")
    axs[0].bar(idx, random_value, 0.25, color=p.amber,
               label="random, same volume")
    axs[0].bar(idx + 0.26, model_value, 0.25, color=p.blue,
               label="model, threshold from the costs")
    axs[0].axhline(0, color=p.fg, lw=1)
    for i, v in enumerate(model_value):
        axs[0].annotate(f"{v:,.0f}", (i + 0.26, v + 700), ha="center",
                        fontsize=8, color=p.blue)
    axs[0].set_xticks(idx)
    axs[0].set_xticklabels([f"EUR {o}\nt*={t:.2f}"
                            for o, t in zip(OFFERS, thresholds)], fontsize=8.5)
    axs[0].set_xlabel("cost of the retention offer")
    axs[0].set_ylabel(f"campaign value over {d['n']:,} customers (EUR)")
    axs[0].set_title("Untargeted loses money from EUR 16", fontsize=10.5)
    axs[0].legend(loc="lower left", fontsize=8)

    gain = [m - r for m, r in zip(model_value, random_value)]
    axs[1].plot(OFFERS, gain, "o-", color=p.green, lw=2.4)
    for o, g, c in zip(OFFERS, gain, contacted):
        axs[1].annotate(f"{g:,.0f}\n({c} contacted)", (o, g),
                        textcoords="offset points", xytext=(0, 10),
                        ha="center", fontsize=8.5, color=p.green)
    axs[1].set_xlabel("cost of the retention offer")
    axs[1].set_ylabel("value of the model over random targeting (EUR)")
    axs[1].set_ylim(min(gain) - 400, max(gain) * 1.35)
    axs[1].set_title("Worth most when the offer is dear", fontsize=10.5)

    fig.suptitle(f"Same model (AUC 0.7060), five sets of economics. Contact if "
                 f"p > offer / (save rate x customer value).",
                 fontsize=10.5, color=p.muted)


FIGURES = [
    figure("value-of-targeting", value_of_targeting, size=(8.8, 4.1), axes=False),
]
