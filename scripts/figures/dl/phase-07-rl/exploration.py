"""Figures for *Exploration vs Exploitation (Bandits and Epsilon Schedules)*.

A bandit is the smallest problem where the central RL difficulty appears: the
only way to learn which action is best is to take actions that might not be.
Everything here is numpy, and the optimal arm is known by construction, so
*regret* -- reward given up against always pulling the best arm -- is an exact
quantity rather than an estimate.

``epsilon-sweep``
    Cumulative regret and the share of pulls that were optimal, for several
    fixed exploration rates plus a decaying one.

``strategies``
    Epsilon-greedy against optimistic initialisation and UCB, over many seeds,
    with the spread across seeds shown rather than a single lucky run.

``difficulty``
    How the ranking changes when the arms get closer together -- the regime
    where exploration matters most is also where it is hardest.
"""

from __future__ import annotations

import functools
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "..", ".."))

from _rl import Bandit  # noqa: E402
from _style import Palette, figure  # noqa: E402

ARMS = 10
STEPS = 1000
SEEDS = 200
EPSILONS = (0.0, 0.01, 0.1, 0.3)
SPREADS = (0.2, 0.5, 1.0, 2.0)


def _run(strategy: str, steps: int, seed: int, epsilon: float = 0.1,
         optimistic: float = 0.0, confidence: float = 2.0,
         spread: float = 1.0) -> dict:
    """One bandit run. Returns per-step regret and optimal-action flags."""
    bandit = Bandit(arms=ARMS, seed=seed, spread=spread)
    rng = np.random.default_rng(seed + 10_000)
    estimates = np.full(ARMS, optimistic, dtype="float64")
    counts = np.zeros(ARMS, dtype="int64")
    regret = np.zeros(steps)
    optimal = np.zeros(steps)
    decay = strategy == "decaying"
    for step in range(steps):
        if strategy == "ucb":
            # An unpulled arm is infinitely uncertain, so it goes first.
            unseen = np.flatnonzero(counts == 0)
            if len(unseen):
                arm = int(unseen[0])
            else:
                bonus = confidence * np.sqrt(np.log(step + 1) / counts)
                arm = int(np.argmax(estimates + bonus))
        else:
            rate = (1.0 / (1.0 + step / 100.0)) if decay else epsilon
            if rng.random() < rate:
                arm = int(rng.integers(0, ARMS))
            else:
                arm = int(np.argmax(estimates))
        reward = bandit.pull(arm)
        counts[arm] += 1
        estimates[arm] += (reward - estimates[arm]) / counts[arm]
        regret[step] = bandit.regret(arm)
        optimal[step] = 1.0 if arm == bandit.best else 0.0
    return {"regret": np.cumsum(regret), "optimal": optimal,
            "final_regret": float(np.sum(regret))}


@functools.lru_cache(maxsize=32)
def _average(strategy: str, epsilon: float = 0.1, optimistic: float = 0.0,
             spread: float = 1.0, seeds: int = None) -> dict:
    """Average over seeds: one bandit run says almost nothing on its own."""
    seeds = SEEDS if seeds is None else int(seeds)
    runs = [_run(strategy, STEPS, seed, epsilon, optimistic, spread=spread)
            for seed in range(seeds)]
    regret = np.stack([run["regret"] for run in runs])
    optimal = np.stack([run["optimal"] for run in runs])
    finals = np.array([run["final_regret"] for run in runs])
    return {"regret": regret.mean(axis=0),
            "optimal": optimal.mean(axis=0),
            "final_mean": float(finals.mean()),
            "final_sd": float(finals.std()),
            "final_best": float(finals.min()),
            "final_worst": float(finals.max()),
            "optimal_share": float(optimal[:, -200:].mean())}


@functools.lru_cache(maxsize=1)
def _epsilon_runs() -> dict:
    out = {f"epsilon = {value}": _average("greedy", epsilon=value)
           for value in EPSILONS}
    out["epsilon = 1/(1+t/100)"] = _average("decaying")
    return out


@functools.lru_cache(maxsize=1)
def _strategy_runs() -> dict:
    return {
        "greedy (epsilon 0)": _average("greedy", epsilon=0.0),
        "epsilon-greedy 0.1": _average("greedy", epsilon=0.1),
        "decaying epsilon": _average("decaying"),
        "optimistic start (+5)": _average("greedy", epsilon=0.0,
                                          optimistic=5.0),
        "UCB (c = 2)": _average("ucb"),
    }


@functools.lru_cache(maxsize=1)
def _difficulty_runs() -> dict:
    out = {}
    for spread in SPREADS:
        out[spread] = {
            "epsilon-greedy 0.1": _average("greedy", epsilon=0.1,
                                           spread=spread, seeds=80),
            "UCB (c = 2)": _average("ucb", spread=spread, seeds=80),
            "greedy (epsilon 0)": _average("greedy", epsilon=0.0,
                                           spread=spread, seeds=80),
        }
    return out


def epsilon_sweep(fig, axes, p: Palette) -> None:
    runs = _epsilon_runs()
    left, right = fig.subplots(1, 2)
    colors = (p.muted, p.blue, p.green, p.red, p.amber)
    steps = np.arange(1, len(next(iter(runs.values()))["regret"]) + 1)
    for (label, entry), color in zip(runs.items(), colors):
        left.plot(steps, entry["regret"], lw=1.9, color=color,
                  label=f"{label} (ends {entry['final_mean']:.1f})")
        right.plot(steps, entry["optimal"], lw=1.6, color=color, label=label)
    left.set_xlabel("pull")
    left.set_ylabel("cumulative regret")
    left.set_title(f"{ARMS} arms, {STEPS} pulls, mean of {SEEDS} bandits",
                   fontsize=10)
    left.legend(fontsize=7.5, loc="upper left")

    right.axhline(1.0, color=p.muted, lw=1.0, ls=":")
    right.set_xlabel("pull")
    right.set_ylabel("share of runs picking the best arm")
    right.set_ylim(0, 1.05)
    right.set_title("pure greedy plateaus below the others", fontsize=10)
    right.legend(fontsize=7.5, loc="lower right")


def strategies(fig, axes, p: Palette) -> None:
    runs = _strategy_runs()
    left, right = fig.subplots(1, 2, width_ratios=(1.1, 1.0))
    labels = list(runs)
    positions = np.arange(len(labels))
    means = [runs[label]["final_mean"] for label in labels]
    spread = [runs[label]["final_sd"] for label in labels]
    left.barh(positions, means, 0.55, xerr=spread, color=p.blue,
              error_kw={"ecolor": p.muted, "capsize": 3})
    for y, label in zip(positions, labels):
        entry = runs[label]
        left.annotate(f"{entry['final_mean']:.1f} ± {entry['final_sd']:.1f}"
                      f"   (best {entry['final_best']:.1f}, "
                      f"worst {entry['final_worst']:.1f})",
                      (entry["final_mean"] + entry["final_sd"], y),
                      xytext=(6, 0), textcoords="offset points", va="center",
                      fontsize=7, color=p.fg)
    left.set_yticks(positions)
    left.set_yticklabels(labels, fontsize=8)
    left.invert_yaxis()
    left.set_xlim(0, max(m + s for m, s in zip(means, spread)) * 1.9)
    left.set_xlabel(f"total regret after {STEPS} pulls (mean ± sd)")
    left.set_title(f"mean of {SEEDS} bandits per strategy", fontsize=10)

    steps = np.arange(1, STEPS + 1)
    for label, color in zip(labels, (p.muted, p.blue, p.amber, p.green,
                                     p.purple)):
        right.plot(steps, runs[label]["regret"], lw=1.9, color=color,
                   label=label)
    right.set_xlabel("pull")
    right.set_ylabel("cumulative regret")
    right.set_title("the shape matters: flat means it has stopped paying",
                    fontsize=10)
    right.legend(fontsize=7.5, loc="upper left")


def difficulty(fig, axes, p: Palette) -> None:
    runs = _difficulty_runs()
    left, right = fig.subplots(1, 2)
    spreads = list(runs)
    labels = list(runs[spreads[0]])
    for label, color in zip(labels, (p.blue, p.purple, p.muted)):
        left.plot(spreads, [runs[s][label]["final_mean"] for s in spreads],
                  "o-", ms=6, lw=2.0, color=color, label=label)
        for spread in spreads:
            value = runs[spread][label]["final_mean"]
            left.annotate(f"{value:.1f}", (spread, value), xytext=(0, 7),
                          textcoords="offset points", ha="center",
                          fontsize=7, color=color)
    left.set_xlabel("spread of the arm means (harder to the left)")
    left.set_ylabel(f"total regret after {STEPS} pulls")
    left.set_title("closer arms cost less per mistake", fontsize=10)
    left.legend(fontsize=8, loc="upper left")

    for label, color in zip(labels, (p.blue, p.purple, p.muted)):
        right.plot(spreads,
                   [runs[s][label]["optimal_share"] for s in spreads],
                   "s-", ms=6, lw=2.0, color=color, label=label)
        for spread in spreads:
            value = runs[spread][label]["optimal_share"]
            right.annotate(f"{value:.2f}", (spread, value), xytext=(0, 7),
                           textcoords="offset points", ha="center",
                           fontsize=7, color=color)
    right.set_xlabel("spread of the arm means")
    right.set_ylabel("share of the last 200 pulls that were optimal")
    right.set_ylim(0, 1.1)
    right.set_title("but they are much harder to tell apart", fontsize=10)
    right.legend(fontsize=8, loc="lower right")


FIGURES = [
    figure("epsilon-sweep", epsilon_sweep, size=(9.4, 3.5), axes=False),
    figure("strategies", strategies, size=(9.8, 3.6), axes=False),
    figure("difficulty", difficulty, size=(9.4, 3.5), axes=False),
]


if __name__ == "__main__":
    example = Bandit(arms=ARMS, seed=0)
    print(f"=== the test bed: {ARMS} arms, Gaussian rewards ===")
    print("arm means (seed 0): "
          + ", ".join(f"{value:+.3f}" for value in example.means))
    print(f"best arm {example.best} at {example.best_mean:+.4f}; regret is")
    print("measured against always pulling it, so 0 is the unreachable ideal")

    print(f"\n=== fixed exploration rates, {STEPS} pulls, "
          f"{SEEDS} bandits each ===")
    runs = _epsilon_runs()
    print(f"{'setting':24s} {'total regret':>13} {'sd':>7} "
          f"{'optimal share (last 200)':>26}")
    for label, entry in runs.items():
        print(f"{label:24s} {entry['final_mean']:13.2f} "
              f"{entry['final_sd']:7.2f} {entry['optimal_share']:26.4f}")

    print(f"\n=== strategies compared ===")
    strategy_runs = _strategy_runs()
    print(f"{'strategy':24s} {'total regret':>13} {'sd':>7} {'best':>8} "
          f"{'worst':>8} {'optimal share':>14}")
    for label, entry in strategy_runs.items():
        print(f"{label:24s} {entry['final_mean']:13.2f} "
              f"{entry['final_sd']:7.2f} {entry['final_best']:8.2f} "
              f"{entry['final_worst']:8.2f} {entry['optimal_share']:14.4f}")
    print("the spread across seeds is wide enough that a single run cannot")
    print("rank these strategies -- which is the real lesson of the table")

    print(f"\n=== how hard is the problem? (80 bandits per cell) ===")
    difficulty_runs = _difficulty_runs()
    print(f"{'arm spread':>11} " + " ".join(f"{name:>22}" for name
                                            in _difficulty_runs()[SPREADS[0]]))
    for spread in SPREADS:
        row = difficulty_runs[spread]
        print(f"{spread:11.1f} " + " ".join(
            f"{row[name]['final_mean']:22.2f}" for name in row))
    print("regret falls as the arms get closer, but that is not the agent")
    print("doing better: each mistake simply costs less when the arms are")
    print("nearly identical. The optimal-action share is the honest view")
