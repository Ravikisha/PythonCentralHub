"""Figure for *Capstone 5 — A Recommender with an Honest Evaluation*."""

import functools
import importlib.util
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from _style import Palette, figure  # noqa: E402

KS = (5, 10, 20)


def _phase10():
    path = os.path.join(HERE, "..", "phase-10-applied", "_data.py")
    spec = importlib.util.spec_from_file_location("pch_phase10_data", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@functools.lru_cache(maxsize=1)
def setup():
    R, _, _, _ = _phase10().interactions()
    rng = np.random.default_rng(0)

    train = R.copy()
    held = {}
    for u in range(R.shape[0]):
        seen = np.flatnonzero(R[u])
        if len(seen) >= 5:
            pick = int(rng.choice(seen))
            train[u, pick] = 0
            held[u] = pick

    popularity = train.sum(0).astype(float)
    norms = np.linalg.norm(train, axis=0)
    norms[norms == 0] = 1.0
    unit = train / norms
    similarity = unit.T @ unit
    np.fill_diagonal(similarity, 0.0)
    activity = {u: int(train[u].sum()) for u in held}

    scorers = {
        "popularity": lambda u: popularity,
        "item-item": lambda u: train[u] @ similarity,
        "blend": lambda u: (popularity if activity[u] < 5
                            else train[u] @ similarity),
    }
    return {"train": train, "held": held, "activity": activity,
            "scorers": scorers, "n_items": R.shape[1]}


def top_k(scorer, user, k):
    d = setup()
    scores = np.asarray(scorer(user), dtype=float).copy()
    scores[np.flatnonzero(d["train"][user])] = -np.inf
    return np.argsort(-scores)[:k]


@functools.lru_cache(maxsize=1)
def results():
    d = setup()
    out = {}
    for name, scorer in d["scorers"].items():
        hits, shown = {}, set()
        for k in KS:
            found = 0
            for user, item in d["held"].items():
                recommended = top_k(scorer, user, k)
                if k == 10:
                    shown.update(recommended.tolist())
                found += int(item in recommended)
            hits[k] = found / len(d["held"])
        out[name] = {"hits": hits, "catalogue": len(shown)}
    return out


def hits_and_coverage(fig, axes, p: Palette) -> None:
    """Two metrics that disagree about which recommender is better."""
    d = setup()
    res = results()
    names = list(res)
    colours = {"popularity": p.amber, "item-item": p.blue, "blend": p.green}

    axs = fig.subplots(1, 2, width_ratios=[1.2, 1])

    idx = np.arange(len(KS))
    for offset, name in zip((-0.26, 0.0, 0.26), names):
        values = [res[name]["hits"][k] for k in KS]
        axs[0].bar(idx + offset, values, 0.25, color=colours[name], label=name)
        for i, v in enumerate(values):
            axs[0].annotate(f"{v:.4f}", (i + offset, v + 0.006), ha="center",
                            fontsize=8, color=colours[name])
    axs[0].set_xticks(idx)
    axs[0].set_xticklabels([f"hit rate at {k}" for k in KS], fontsize=9.5)
    axs[0].set_ylim(0, max(res["blend"]["hits"].values()) * 1.30)
    axs[0].set_ylabel(f"share of {len(d['held']):,} held-out items found")
    axs[0].set_title("Ranked against all 600 items, never a sample",
                     fontsize=10.5)
    axs[0].legend(loc="upper left", fontsize=8.5)

    coverage = [res[n]["catalogue"] for n in names]
    axs[1].bar(np.arange(len(names)), coverage,
               color=[colours[n] for n in names], width=0.55)
    for i, value in enumerate(coverage):
        axs[1].annotate(f"{value} of {d['n_items']}\n"
                        f"({value / d['n_items']:.1%})",
                        (i, value + 8), ha="center", fontsize=9, color=p.muted)
    axs[1].set_xticks(np.arange(len(names)))
    axs[1].set_xticklabels(names, fontsize=9.5)
    axs[1].set_ylim(0, d["n_items"] * 0.72)
    axs[1].set_ylabel("distinct items ever recommended (top 10)")
    axs[1].set_title("Catalogue coverage: the metric nobody reports",
                     fontsize=10.5)

    fig.suptitle("Popularity reaches hit@10 0.1976 by recommending 20 items to "
                 "everybody.", fontsize=10.5, color=p.muted)


FIGURES = [
    figure("hits-and-coverage", hits_and_coverage, size=(8.8, 4.0), axes=False),
]
