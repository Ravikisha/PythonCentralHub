"""Figures for *Hyperparameter Tuning with KerasTuner*.

KerasTuner is not installed on this machine and nothing may be downloaded, so
the two algorithms it implements are written out here and measured directly.
That is arguably the better lesson anyway: random search and successive halving
are twenty lines each, and the interesting question is not their API but how
much of a fixed budget each one wastes.

Every strategy below spends the SAME total number of training epochs. Comparing
search strategies on anything else measures the budget, not the strategy.

``budget``
    Best accuracy found against epochs spent, for grid, random and successive
    halving.

``halving``
    What successive halving actually does: which configurations survive each
    rung, and how often it discards the eventual winner.

``landscape``
    The search space itself -- how much of it is good, which is what decides
    whether searching is worth anything.
"""

from __future__ import annotations

import functools
import itertools
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "..", ".."))

from _dl import dataset, seed_everything, tf  # noqa: E402
from _style import Palette, figure  # noqa: E402

LIMIT = 6000
BUDGET = 96              # total training epochs every strategy may spend
FULL_EPOCHS = 8          # epochs for a "full" evaluation
RUNGS = (1, 2, 5)        # successive-halving rung lengths
KEEP = 0.5               # fraction surviving each rung

UNITS = (32, 64, 128)
RATES = (3e-4, 1e-3, 3e-3)
DROPOUTS = (0.0, 0.3)


@functools.lru_cache(maxsize=1)
def _data() -> dict:
    return dataset("mnist", limit=LIMIT, flat=True)


def _space() -> list:
    return [{"units": u, "rate": r, "dropout": d}
            for u, r, d in itertools.product(UNITS, RATES, DROPOUTS)]


@functools.lru_cache(maxsize=512)
def _train(units: int, rate: float, dropout: float, epochs: int) -> float:
    """Train one configuration for `epochs` and return validation accuracy.

    Cached, so a configuration promoted through several rungs is not retrained
    from scratch each time -- which is what a real tuner does with checkpoints.
    """
    keras = tf().keras
    data = _data()
    seed_everything(0)
    layers = [keras.layers.Input((784,)),
              keras.layers.Dense(units, activation="relu")]
    if dropout:
        layers.append(keras.layers.Dropout(dropout))
    layers += [keras.layers.Dense(units, activation="relu"),
               keras.layers.Dense(10, activation="softmax")]
    model = keras.Sequential(layers)
    model.compile(keras.optimizers.Adam(rate),
                  "sparse_categorical_crossentropy", metrics=["accuracy"])
    history = model.fit(data["x_train"], data["y_train"], epochs=int(epochs),
                        batch_size=128, verbose=0,
                        validation_data=(data["x_test"], data["y_test"]))
    return float(history.history["val_accuracy"][-1])


@functools.lru_cache(maxsize=1)
def _exhaustive() -> dict:
    """Every configuration at full length -- the answer the searches aim at."""
    started = time.perf_counter()
    scores = {}
    for config in _space():
        key = (config["units"], config["rate"], config["dropout"])
        scores[key] = _train(*key, FULL_EPOCHS)
    best = max(scores, key=scores.get)
    return {"scores": scores, "best": best, "best_score": scores[best],
            "epochs": len(scores) * FULL_EPOCHS,
            "seconds": time.perf_counter() - started}


def _random_search(budget: int, seed: int) -> dict:
    """Sample configurations and train each one fully, until the budget runs out."""
    rng = np.random.default_rng(seed)
    space = _space()
    order = rng.permutation(len(space))
    spent = 0
    best = 0.0
    trace = []
    for index in order:
        if spent + FULL_EPOCHS > budget:
            break
        config = space[index]
        key = (config["units"], config["rate"], config["dropout"])
        score = _train(*key, FULL_EPOCHS)
        spent += FULL_EPOCHS
        best = max(best, score)
        trace.append({"epochs": spent, "best": best})
    return {"best": best, "spent": spent, "trace": trace,
            "evaluated": len(trace)}


def _successive_halving(budget: int, seed: int) -> dict:
    """Train many configurations briefly, keep the best half, train them longer."""
    rng = np.random.default_rng(seed)
    space = _space()
    survivors = [space[i] for i in rng.permutation(len(space))]
    spent = 0
    trace = []
    rounds = []
    best = 0.0
    for rung, epochs in enumerate(RUNGS):
        scored = []
        for config in survivors:
            key = (config["units"], config["rate"], config["dropout"])
            if spent + epochs > budget:
                break
            score = _train(*key, epochs)
            spent += epochs
            best = max(best, score)
            scored.append((score, config))
            trace.append({"epochs": spent, "best": best})
        if not scored:
            break
        scored.sort(key=lambda pair: pair[0], reverse=True)
        rounds.append({"rung": rung, "epochs": epochs,
                       "evaluated": len(scored),
                       "scores": [pair[0] for pair in scored],
                       "kept": max(1, int(len(scored) * KEEP))})
        survivors = [pair[1] for pair in scored[:max(1, int(len(scored) * KEEP))]]
    # Spend whatever is left giving the leader a full-length run.
    if survivors and spent + FULL_EPOCHS <= budget:
        key = (survivors[0]["units"], survivors[0]["rate"],
               survivors[0]["dropout"])
        score = _train(*key, FULL_EPOCHS)
        spent += FULL_EPOCHS
        best = max(best, score)
        trace.append({"epochs": spent, "best": best})
    return {"best": best, "spent": spent, "trace": trace, "rounds": rounds,
            "final": survivors[0] if survivors else None}


def _grid(budget: int) -> dict:
    """The space in a fixed order, full length each, until the budget is gone."""
    spent = 0
    best = 0.0
    trace = []
    for config in _space():
        if spent + FULL_EPOCHS > budget:
            break
        key = (config["units"], config["rate"], config["dropout"])
        score = _train(*key, FULL_EPOCHS)
        spent += FULL_EPOCHS
        best = max(best, score)
        trace.append({"epochs": spent, "best": best})
    return {"best": best, "spent": spent, "trace": trace,
            "evaluated": len(trace)}


@functools.lru_cache(maxsize=1)
def _searches() -> dict:
    exhaustive = _exhaustive()
    random_runs = [_random_search(BUDGET, seed) for seed in range(5)]
    halving_runs = [_successive_halving(BUDGET, seed) for seed in range(5)]
    grid = _grid(BUDGET)
    return {
        "exhaustive": exhaustive,
        "grid": {"best": grid["best"], "spent": grid["spent"],
                 "trace": grid["trace"], "runs": [grid]},
        "random": {"best": float(np.mean([r["best"] for r in random_runs])),
                   "sd": float(np.std([r["best"] for r in random_runs])),
                   "spent": random_runs[0]["spent"],
                   "trace": random_runs[0]["trace"], "runs": random_runs},
        "halving": {"best": float(np.mean([r["best"] for r in halving_runs])),
                    "sd": float(np.std([r["best"] for r in halving_runs])),
                    "spent": halving_runs[0]["spent"],
                    "trace": halving_runs[0]["trace"], "runs": halving_runs},
    }


@functools.lru_cache(maxsize=1)
def _short_vs_long() -> dict:
    """Does a one-epoch score predict the eight-epoch one? Halving assumes so."""
    space = _space()
    short = []
    long = []
    for config in space:
        key = (config["units"], config["rate"], config["dropout"])
        short.append(_train(*key, RUNGS[0]))
        long.append(_train(*key, FULL_EPOCHS))
    short = np.array(short)
    long = np.array(long)
    order_short = np.argsort(-short)
    order_long = np.argsort(-long)
    keep = max(1, int(len(space) * KEEP))
    survives = len(set(order_short[:keep].tolist())
                   & set(order_long[:1].tolist())) > 0
    return {"short": short, "long": long,
            "correlation": float(np.corrcoef(short, long)[0, 1]),
            "winner_survives": bool(survives),
            "best_long_rank_at_short": int(
                np.where(order_short == int(order_long[0]))[0][0]) + 1,
            "space": space}


def budget(fig, axes, p: Palette) -> None:
    searches = _searches()
    exhaustive = searches["exhaustive"]
    left, right = fig.subplots(1, 2, width_ratios=(1.15, 1.0))
    colours = {"grid": p.muted, "random": p.blue, "halving": p.green}
    for name in ("grid", "random", "halving"):
        trace = searches[name]["trace"]
        left.step([point["epochs"] for point in trace],
                  [point["best"] for point in trace], where="post", lw=2.0,
                  color=colours[name],
                  label=f"{name} ({searches[name]['best']:.4f})")
    left.axhline(exhaustive["best_score"], color=p.amber, lw=1.4, ls="--",
                 label=f"exhaustive ({exhaustive['best_score']:.4f}, "
                       f"{exhaustive['epochs']} epochs)")
    left.set_xlabel("training epochs spent")
    left.set_ylabel("best validation accuracy found")
    left.set_title(f"the same {BUDGET}-epoch budget, three strategies",
                   fontsize=10)
    left.legend(fontsize=7.5, loc="lower right")

    names = ["grid", "random", "halving"]
    positions = np.arange(len(names))
    bests = [searches[name]["best"] for name in names]
    errors = [searches[name].get("sd", 0.0) for name in names]
    right.bar(positions, bests, 0.5, yerr=errors,
              color=[colours[name] for name in names],
              error_kw={"ecolor": p.fg, "capsize": 4})
    for x, name in zip(positions, names):
        entry = searches[name]
        gap = exhaustive["best_score"] - entry["best"]
        right.annotate(f"{entry['best']:.4f}\n({gap:+.4f})",
                       (x, entry["best"]), xytext=(0, 5),
                       textcoords="offset points", ha="center", fontsize=7.5,
                       color=p.fg)
    right.axhline(exhaustive["best_score"], color=p.amber, lw=1.3, ls="--")
    right.set_xticks(positions)
    right.set_xticklabels(names)
    right.set_ylim(min(bests) - 0.03, exhaustive["best_score"] + 0.02)
    right.set_ylabel("best accuracy found")
    right.set_title("distance from the exhaustive answer", fontsize=10)


def halving(fig, axes, p: Palette) -> None:
    searches = _searches()
    rounds = searches["halving"]["runs"][0]["rounds"]
    short = _short_vs_long()
    left, right = fig.subplots(1, 2)
    for entry in rounds:
        positions = np.arange(len(entry["scores"]))
        colours = [p.green if i < entry["kept"] else p.red
                   for i in range(len(entry["scores"]))]
        left.scatter(positions, entry["scores"], s=42, color=colours,
                     label=f"rung {entry['rung']} ({entry['epochs']} epochs)"
                     if entry["rung"] == 0 else None)
        left.plot(positions, entry["scores"], lw=1.0, color=p.muted, alpha=0.5)
    left.set_xlabel("configuration, ranked within its rung")
    left.set_ylabel("validation accuracy")
    left.set_title("green survives to the next rung, red is discarded",
                   fontsize=10)

    right.scatter(short["short"], short["long"], s=48, color=p.blue)
    limits = [min(short["short"].min(), short["long"].min()) - 0.02,
              max(short["short"].max(), short["long"].max()) + 0.02]
    right.plot(limits, limits, lw=1.1, ls="--", color=p.muted)
    best_index = int(np.argmax(short["long"]))
    right.scatter([short["short"][best_index]], [short["long"][best_index]],
                  s=120, facecolors="none", edgecolors=p.green, linewidths=2)
    right.annotate(f"eventual winner\n(rank "
                   f"{short['best_long_rank_at_short']} after "
                   f"{RUNGS[0]} epoch)",
                   (short["short"][best_index], short["long"][best_index]),
                   xytext=(8, -22), textcoords="offset points", fontsize=7.5,
                   color=p.green)
    right.set_xlabel(f"accuracy after {RUNGS[0]} epoch")
    right.set_ylabel(f"accuracy after {FULL_EPOCHS} epochs")
    right.set_title(f"does an early score predict the final one? "
                    f"r = {short['correlation']:.4f}", fontsize=10)


def landscape(fig, axes, p: Palette) -> None:
    exhaustive = _exhaustive()
    scores = exhaustive["scores"]
    left, right = fig.subplots(1, 2)
    values = np.array(list(scores.values()))
    left.hist(values, bins=12, color=p.blue)
    left.axvline(values.max(), color=p.green, lw=1.6, ls="--",
                 label=f"best {values.max():.4f}")
    left.axvline(float(np.median(values)), color=p.amber, lw=1.4, ls=":",
                 label=f"median {np.median(values):.4f}")
    left.set_xlabel("validation accuracy")
    left.set_ylabel("configurations")
    left.set_title(f"all {len(values)} configurations, "
                   f"{FULL_EPOCHS} epochs each", fontsize=10)
    left.legend(fontsize=8)

    by_rate = {}
    for (units, rate, dropout), score in scores.items():
        by_rate.setdefault(rate, []).append(score)
    rates = sorted(by_rate)
    positions = np.arange(len(rates))
    means = [float(np.mean(by_rate[rate])) for rate in rates]
    spread = [float(np.std(by_rate[rate])) for rate in rates]
    right.bar(positions, means, 0.5, yerr=spread, color=p.purple,
              error_kw={"ecolor": p.muted, "capsize": 4})
    for x, rate in zip(positions, rates):
        right.annotate(f"{np.mean(by_rate[rate]):.4f}",
                       (x, np.mean(by_rate[rate])), xytext=(0, 5),
                       textcoords="offset points", ha="center", fontsize=8,
                       color=p.fg)
    right.set_xticks(positions)
    right.set_xticklabels([f"{rate:g}" for rate in rates])
    right.set_xlabel("learning rate")
    right.set_ylabel("mean accuracy across the other settings")
    right.set_ylim(min(means) - 0.05, max(means) + 0.03)
    right.set_title("one hyperparameter dominates the rest", fontsize=10)


FIGURES = [
    figure("budget", budget, size=(9.6, 3.5), axes=False),
    figure("halving", halving, size=(9.6, 3.5), axes=False),
    figure("landscape", landscape, size=(9.4, 3.4), axes=False),
]


if __name__ == "__main__":
    space = _space()
    exhaustive = _exhaustive()
    print(f"=== the search space: {len(space)} configurations ===")
    print(f"units {UNITS}, learning rates {RATES}, dropout {DROPOUTS}")
    print(f"exhaustive search: {exhaustive['epochs']} epochs, "
          f"{exhaustive['seconds']:.0f}s, best "
          f"{exhaustive['best_score']:.4f} at units={exhaustive['best'][0]}, "
          f"rate={exhaustive['best'][1]:g}, dropout={exhaustive['best'][2]:g}")
    values = np.array(list(exhaustive["scores"].values()))
    print(f"across the space: best {values.max():.4f}, median "
          f"{np.median(values):.4f}, worst {values.min():.4f}")

    print(f"\n=== three strategies, {BUDGET} epochs each ===")
    searches = _searches()
    print(f"{'strategy':12s} {'best found':>11} {'sd':>8} {'spent':>7} "
          f"{'gap to exhaustive':>18}")
    for name in ("grid", "random", "halving"):
        entry = searches[name]
        gap = exhaustive["best_score"] - entry["best"]
        print(f"{name:12s} {entry['best']:11.4f} "
              f"{entry.get('sd', 0.0):8.4f} {entry['spent']:7d} "
              f"{gap:+18.4f}")
    print(f"exhaustive spent {exhaustive['epochs']} epochs -- "
          f"{exhaustive['epochs'] / BUDGET:.1f}x the budget the others had")

    print(f"\n=== successive halving, rung by rung ===")
    rounds = searches["halving"]["runs"][0]["rounds"]
    for entry in rounds:
        print(f"rung {entry['rung']}: {entry['evaluated']:2d} configs x "
              f"{entry['epochs']} epoch(s), keeping {entry['kept']:2d}, "
              f"best {max(entry['scores']):.4f}, "
              f"worst {min(entry['scores']):.4f}")

    short = _short_vs_long()
    print(f"\n=== the assumption halving depends on ===")
    print(f"correlation between a {RUNGS[0]}-epoch score and an "
          f"{FULL_EPOCHS}-epoch score: {short['correlation']:.4f}")
    print(f"the eventual winner ranked #{short['best_long_rank_at_short']} of "
          f"{len(space)} after {RUNGS[0]} epoch")
    print("halving only works if early performance ranks configurations")
    print("roughly the way final performance does. When it does not, the")
    print("method confidently discards the best option in the first rung")
