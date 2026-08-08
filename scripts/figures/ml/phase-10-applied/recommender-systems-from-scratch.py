"""Figures for *Recommender Systems from Scratch*."""

import functools
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _data import interactions  # noqa: E402
from _style import Palette, figure  # noqa: E402

K = 10


def bpr(train, k=16, epochs=30, lr=0.05, reg=0.01, seed=1):
    """Bayesian personalised ranking by SGD: rank a seen item above an unseen one."""
    rng = np.random.default_rng(seed)
    n_users, n_items = train.shape
    P = rng.normal(0, 0.1, (n_users, k))
    Q = rng.normal(0, 0.1, (n_items, k))
    pairs = np.argwhere(train == 1)

    for _ in range(epochs):
        rng.shuffle(pairs)
        for u, i in pairs:
            j = int(rng.integers(0, n_items))
            while train[u, j] == 1:
                j = int(rng.integers(0, n_items))
            gradient = 1.0 / (1.0 + np.exp(P[u] @ (Q[i] - Q[j])))
            pu, qi, qj = P[u].copy(), Q[i].copy(), Q[j].copy()
            P[u] += lr * (gradient * (qi - qj) - reg * pu)
            Q[i] += lr * (gradient * pu - reg * qi)
            Q[j] += lr * (-gradient * pu - reg * qj)
    return P, Q


@functools.lru_cache(maxsize=1)
def setup():
    R, _, _, _ = interactions()
    rng = np.random.default_rng(0)

    train = R.copy()
    held = {}
    for u in range(R.shape[0]):
        seen = np.flatnonzero(R[u])
        if len(seen) >= 5:                     # leave one out per active user
            pick = int(rng.choice(seen))
            train[u, pick] = 0
            held[u] = pick

    popularity = train.sum(0).astype(float)
    norms = np.linalg.norm(train, axis=0)
    norms[norms == 0] = 1.0
    unit = train / norms
    similarity = unit.T @ unit
    np.fill_diagonal(similarity, 0.0)

    P, Q = bpr(train)

    scorers = {
        "random": lambda u, r=np.random.default_rng(7): r.random(R.shape[1]),
        "popularity": lambda u: popularity,
        "item-item cosine": lambda u: train[u] @ similarity,
        "BPR matrix factorisation": lambda u: Q @ P[u],
    }
    return {"R": R, "train": train, "held": held, "popularity": popularity,
            "similarity": similarity, "P": P, "Q": Q, "scorers": scorers}


def evaluate(scorer, sampled=None, k=K, seed=3):
    """Hit rate and NDCG at k, either against all items or against `sampled` negatives."""
    d = setup()
    train, held = d["train"], d["held"]
    rng = np.random.default_rng(seed)
    all_items = np.arange(train.shape[1])

    hits, ndcg, ranks = 0, 0.0, []
    for u, item in held.items():
        scores = np.asarray(scorer(u), dtype=float)
        known = np.flatnonzero(train[u])
        if sampled is None:
            scores = scores.copy()
            scores[known] = -np.inf
            rank = int((scores > scores[item]).sum()) + 1
        else:
            pool = np.setdiff1d(all_items, np.append(known, item))
            negatives = rng.choice(pool, sampled, replace=False)
            rank = int((scores[negatives] > scores[item]).sum()) + 1
        ranks.append(rank)
        if rank <= k:
            hits += 1
            ndcg += 1.0 / np.log2(rank + 1)

    n = len(held)
    return {"hit": hits / n, "ndcg": ndcg / n,
            "mean_rank": float(np.mean(ranks)),
            "median_rank": float(np.median(ranks))}


def the_matrix(fig, axes, p: Palette) -> None:
    """A user-item matrix is two orders of magnitude sparser than text."""
    d = setup()
    R, train = d["R"], d["train"]

    axs = fig.subplots(1, 2, width_ratios=[1.4, 1])

    block = R[:150, :150]
    axs[0].imshow(block, cmap="Blues", aspect="auto", vmin=0, vmax=1.4)
    axs[0].set_xlabel("first 150 items")
    axs[0].set_ylabel("first 150 users")
    axs[0].grid(False)
    axs[0].set_title(f"A 150x150 corner: {block.mean():.2%} filled", fontsize=10.5)

    per_user = R.sum(1)
    per_item = R.sum(0)
    order = np.argsort(per_item)[::-1]
    top_share = per_item[order[:60]].sum() / per_item.sum()

    facts = [
        ("users x items", f"{R.shape[0]:,} x {R.shape[1]:,}"),
        ("interactions", f"{int(R.sum()):,}"),
        ("density", f"{R.mean():.2%}"),
        ("median per user", f"{np.median(per_user):.0f}"),
        ("users with fewer than 5", f"{int((per_user < 5).sum()):,}"),
        ("items with none at all", f"{int((per_item == 0).sum())}"),
        ("top 10% of items hold", f"{top_share:.1%} of clicks"),
        ("evaluable users", f"{len(d['held']):,}"),
    ]
    axs[1].axis("off")
    for i, (label, value) in enumerate(facts):
        yy = 0.94 - i * 0.115
        axs[1].annotate(label, (0.02, yy), fontsize=10, color=p.muted)
        axs[1].annotate(value, (0.98, yy), fontsize=10.5, color=p.fg,
                        ha="right", fontweight="bold")
    axs[1].set_xlim(0, 1)
    axs[1].set_ylim(0, 1)
    axs[1].set_title("The matrix in numbers", fontsize=10.5)

    fig.suptitle("2.02% of the cells are filled, and the empty ones are the "
                 "prediction target — not missing data.",
                 fontsize=10.5, color=p.muted)


def long_tail(fig, axes, p: Palette) -> None:
    """Popularity is a power law, which is why it is such a strong baseline."""
    d = setup()
    per_item = d["R"].sum(0)
    order = np.argsort(per_item)[::-1]
    sorted_counts = per_item[order]
    cumulative = np.cumsum(sorted_counts) / sorted_counts.sum()

    axs = fig.subplots(1, 2)

    axs[0].plot(np.arange(1, len(sorted_counts) + 1), sorted_counts,
                color=p.blue, lw=2.0)
    axs[0].set_xscale("log")
    axs[0].set_yscale("symlog")
    axs[0].set_xlabel("item rank (log)")
    axs[0].set_ylabel("interactions (symlog)")
    axs[0].set_title(f"Most popular item: {sorted_counts[0]} clicks; "
                     f"{int((per_item == 0).sum())} items have none",
                     fontsize=10.5)

    frac = np.arange(1, len(cumulative) + 1) / len(cumulative)
    axs[1].plot(frac, cumulative, color=p.amber, lw=2.4)
    axs[1].plot([0, 1], [0, 1], color=p.muted, lw=1, ls="--",
                label="if all items were equal")
    at10 = float(cumulative[int(0.1 * len(cumulative)) - 1])
    axs[1].scatter([0.1], [at10], color=p.red, s=60, zorder=5)
    axs[1].annotate(f"top 10% of items\n{at10:.1%} of interactions",
                    (0.12, at10 - 0.10), fontsize=9.5, color=p.red)
    axs[1].set_xlabel("fraction of items, most popular first")
    axs[1].set_ylabel("cumulative share of interactions")
    axs[1].set_title("The head is heavy but not overwhelming", fontsize=10.5)
    axs[1].legend(loc="lower right", fontsize=8.5)

    fig.suptitle("Recommending the most popular items is not a straw man: it is "
                 "a real 0.1976 hit rate.", fontsize=10.5, color=p.muted)


def baselines(fig, axes, p: Palette) -> None:
    """Four scorers, ranked against all 600 items."""
    d = setup()
    names = list(d["scorers"])
    results = [evaluate(d["scorers"][n]) for n in names]

    axs = fig.subplots(1, 2)
    idx = np.arange(len(names))
    colours = [p.muted, p.amber, p.blue, p.green]

    axs[0].barh(idx, [r["hit"] for r in results], color=colours, height=0.55)
    for i, r in enumerate(results):
        axs[0].annotate(f"{r['hit']:.4f}", (r["hit"] + 0.008, i), va="center",
                        fontsize=9.5, color=p.muted)
    axs[0].set_yticks(idx)
    axs[0].set_yticklabels(names, fontsize=9)
    axs[0].set_xlim(0, max(r["hit"] for r in results) * 1.25)
    axs[0].set_xlabel(f"hit rate at {K} (full ranking)")
    axs[0].set_title(f"Is the held-out item in the top {K} of 600?",
                     fontsize=10.5)

    axs[1].barh(idx, [r["median_rank"] for r in results], color=colours,
                height=0.55)
    for i, r in enumerate(results):
        axs[1].annotate(f"{r['median_rank']:.0f}", (r["median_rank"] + 5, i),
                        va="center", fontsize=9.5, color=p.muted)
    axs[1].set_yticks(idx)
    axs[1].set_yticklabels([])
    axs[1].set_xlim(0, max(r["median_rank"] for r in results) * 1.22)
    axs[1].set_xlabel("median rank of the held-out item")
    axs[1].set_title("Lower is better; random sits at 295", fontsize=10.5)

    fig.suptitle("Item-item cosine, in six lines of numpy, beats matrix "
                 "factorisation at this data size.",
                 fontsize=10.5, color=p.muted)


def sampled_negatives(fig, axes, p: Palette) -> None:
    """Ranking against 100 sampled negatives roughly doubles every metric."""
    d = setup()
    names = ["popularity", "item-item cosine", "BPR matrix factorisation"]
    full = [evaluate(d["scorers"][n]) for n in names]
    sampled = [evaluate(d["scorers"][n], sampled=100) for n in names]

    idx = np.arange(len(names))
    axes.bar(idx - 0.2, [r["hit"] for r in full], 0.4, color=p.blue,
             label="ranked against all 600 items")
    axes.bar(idx + 0.2, [r["hit"] for r in sampled], 0.4, color=p.red,
             label="ranked against 100 sampled negatives")
    for i, (f, s) in enumerate(zip(full, sampled)):
        axes.annotate(f"{f['hit']:.4f}", (i - 0.2, f["hit"] + 0.012),
                      ha="center", fontsize=9, color=p.blue)
        axes.annotate(f"{s['hit']:.4f}\n{s['hit'] / f['hit']:.2f}x",
                      (i + 0.2, s["hit"] + 0.012), ha="center", fontsize=9,
                      color=p.red)
    axes.set_xticks(idx)
    axes.set_xticklabels([n.replace(" ", "\n", 1) for n in names], fontsize=9)
    axes.set_ylim(0, max(r["hit"] for r in sampled) * 1.35)
    axes.set_ylabel(f"hit rate at {K}")
    axes.set_title("The same models, two evaluation protocols")
    axes.legend(loc="upper left", fontsize=9)


def cold_start(fig, axes, p: Palette) -> None:
    """Performance is a function of how much history the user has."""
    d = setup()
    train, held = d["train"], d["held"]
    activity = np.array([int(train[u].sum()) for u in held])
    users = np.array(list(held))

    buckets = [(4, 4), (5, 7), (8, 10), (11, 15), (16, 61)]
    labels, series = [], {n: [] for n in ("popularity", "item-item cosine",
                                          "BPR matrix factorisation")}
    for lo, hi in buckets:
        mask = (activity >= lo) & (activity <= hi)
        chosen = set(users[mask].tolist())
        if not chosen:
            continue
        labels.append((f"{lo}" if lo == hi else f"{lo}-{hi}")
                      + f"\nn={len(chosen)}")
        for name in series:
            scorer = d["scorers"][name]
            hits = 0
            for u in chosen:
                item = held[u]
                scores = np.asarray(scorer(u), dtype=float).copy()
                scores[np.flatnonzero(train[u])] = -np.inf
                if int((scores > scores[item]).sum()) + 1 <= K:
                    hits += 1
            series[name].append(hits / len(chosen))

    idx = np.arange(len(labels))
    for offset, (name, colour) in zip((-0.26, 0.0, 0.26),
                                      (("popularity", p.amber),
                                       ("item-item cosine", p.blue),
                                       ("BPR matrix factorisation", p.green))):
        axes.bar(idx + offset, series[name], 0.25, color=colour, label=name)
        for i, v in enumerate(series[name]):
            axes.annotate(f"{v:.2f}", (i + offset, v + 0.008), ha="center",
                          fontsize=8, color=colour)
    axes.set_xticks(idx)
    axes.set_xticklabels(labels, fontsize=9)
    axes.set_ylabel(f"hit rate at {K}")
    axes.set_ylim(0, max(max(v) for v in series.values()) * 1.30)
    axes.set_xlabel("interactions the user has in the training matrix")
    axes.set_title("Personalisation needs history; popularity does not")
    axes.legend(loc="upper left", fontsize=8.5)


FIGURES = [
    figure("the-matrix", the_matrix, size=(8.8, 3.9), axes=False),
    figure("long-tail", long_tail, size=(8.8, 3.8), axes=False),
    figure("baselines", baselines, size=(8.8, 3.6), axes=False),
    figure("sampled-negatives", sampled_negatives, size=(7.8, 4.0)),
    figure("cold-start", cold_start, size=(8.4, 4.0)),
]
