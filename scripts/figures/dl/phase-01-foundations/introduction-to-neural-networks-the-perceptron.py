"""Figures for *Introduction to Neural Networks (The Perceptron)*.

``perceptron-gates``
    The four two-input gates with the boundary the perceptron rule actually
    found. Three are separable and it finds a line; XOR is not, and the panel
    shows why no line can work.

``perceptron-convergence``
    Misclassified rows per epoch. AND, OR and NAND reach zero and stop; XOR
    oscillates forever, which is what "does not converge" looks like.

``xor-ceiling``
    An exhaustive search over 40,401 (w1, w2) pairs at the best bias for each,
    scoring every one on XOR. The impossibility proof says no line separates
    it; this is the same statement as a number -- the best any single neuron
    reaches is 3 of 4, and 0 of 40,401 reach 4.
"""

from __future__ import annotations

import functools
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "..", ".."))

from _style import Palette, figure  # noqa: E402

X = np.array([[0.0, 0.0], [0.0, 1.0], [1.0, 0.0], [1.0, 1.0]])
GATES = {
    "AND": np.array([0, 0, 0, 1]),
    "OR": np.array([0, 1, 1, 1]),
    "NAND": np.array([1, 1, 1, 0]),
    "XOR": np.array([0, 1, 1, 0]),
}
MAX_EPOCHS = 40


def _train(y, lr=0.1, max_epochs=MAX_EPOCHS, seed=0):
    """The perceptron rule, recording the error count after every epoch."""
    rng = np.random.default_rng(seed)
    w = rng.normal(0, 0.01, 2)
    b = 0.0
    history = []
    for _ in range(max_epochs):
        errors = 0
        for xi, target in zip(X, y):
            prediction = 1 if xi @ w + b > 0 else 0
            update = lr * (target - prediction)
            if update != 0:
                w = w + update * xi
                b = b + update
                errors += 1
        history.append(errors)
    return w, b, history


@functools.lru_cache(maxsize=1)
def _runs() -> dict:
    return {name: _train(y) for name, y in GATES.items()}


GRID = 201
SPAN = 4.0


@functools.lru_cache(maxsize=1)
def _ceiling() -> dict:
    """Score every weight pair on every gate, exhaustively.

    For each (w1, w2) the bias is chosen to be the best one available, so the
    search is not being defeated by a bad intercept. There is nothing left for
    a single neuron to try after this.
    """
    axis = np.linspace(-SPAN, SPAN, GRID)
    w1, w2 = np.meshgrid(axis, axis)
    projections = np.stack([w1 * x[0] + w2 * x[1] for x in X], axis=-1)
    # Candidate biases: the midpoints between distinct projections, plus a
    # margin either side, so every distinct labelling of the four rows is
    # reachable.
    candidates = np.concatenate(
        [projections, projections + 0.5, projections - 0.5], axis=-1)
    out = {}
    for name, y in GATES.items():
        best = np.zeros((GRID, GRID), dtype="int8")
        for index in range(candidates.shape[-1]):
            bias = -candidates[..., index][..., None]
            correct = ((projections + bias) > 0).astype("int8")
            score = (correct == y).sum(axis=-1)
            best = np.maximum(best, score.astype("int8"))
        out[name] = best
    return {"axis": axis, "scores": out,
            "cells": GRID * GRID,
            "perfect": {name: int((grid == 4).sum())
                        for name, grid in out.items()},
            "best": {name: int(grid.max()) for name, grid in out.items()}}


def xor_ceiling(fig, axes, p: Palette) -> None:
    info = _ceiling()
    panels = fig.subplots(1, 2, width_ratios=(1.0, 1.0))
    left, right = panels
    axis = info["axis"]
    mesh = left.pcolormesh(axis, axis, info["scores"]["XOR"], cmap="magma",
                           vmin=0, vmax=4, shading="auto")
    fig.colorbar(mesh, ax=left, fraction=0.046, ticks=(0, 1, 2, 3, 4),
                 label="rows classified correctly")
    left.set_xlabel("w1")
    left.set_ylabel("w2")
    left.set_title(f"XOR: best is {info['best']['XOR']} of 4, "
                   f"reached nowhere in {info['cells']:,} cells", fontsize=9.5)

    names = list(GATES)
    positions = np.arange(len(names))
    shares = [info["perfect"][name] / info["cells"] for name in names]
    colours = [p.green if share > 0 else p.red for share in shares]
    right.bar(positions, shares, color=colours, width=0.6)
    for position, name, share in zip(positions, names, shares):
        right.annotate(f"{info['perfect'][name]:,}\n({share:.1%})",
                       (position, share), xytext=(0, 3),
                       textcoords="offset points", ha="center", fontsize=8,
                       color=p.fg)
    right.set_xticks(positions)
    right.set_xticklabels(names)
    right.set_ylabel("share of weight pairs that solve the gate")
    right.set_title(f"{info['cells']:,} weight pairs, best bias for each",
                    fontsize=9.5)


def perceptron_gates(fig, axes, p: Palette) -> None:
    runs = _runs()
    grid = fig.subplots(1, 4)
    for ax, (name, y) in zip(grid, GATES.items()):
        w, b, history = runs[name]
        for point, label in zip(X, y):
            ax.scatter(*point, s=90, zorder=3,
                       color=p.amber if label else p.blue,
                       edgecolor=p.bg, linewidth=1.0)
        solved = history[-1] == 0
        if solved and abs(w[1]) > 1e-9:
            xs = np.array([-0.4, 1.4])
            ax.plot(xs, -(w[0] * xs + b) / w[1], color=p.green, lw=2.0)
        elif solved:
            ax.axvline(-b / w[0], color=p.green, lw=2.0)
        else:
            # The proof, drawn: join the two positives and join the two negatives.
            # Those segments intersect, so the two classes' convex hulls overlap and
            # no straight line can have one class strictly on each side.
            positives = X[y == 1]
            negatives = X[y == 0]
            ax.plot(positives[:, 0], positives[:, 1], color=p.amber, lw=1.6, ls="--")
            ax.plot(negatives[:, 0], negatives[:, 1], color=p.blue, lw=1.6, ls="--")
            ax.scatter([0.5], [0.5], marker="x", s=80, color=p.red, zorder=4, lw=2.0)
            ax.annotate("the segments cross:\nhulls overlap", (0.52, 0.42),
                        ha="center", va="top", color=p.red, fontsize=7.5)
        ax.set_title(f"{name} — {'solved' if solved else 'impossible'}", fontsize=10)
        ax.set_xlim(-0.4, 1.4)
        ax.set_ylim(-0.4, 1.4)
        ax.set_xticks([0, 1])
        ax.set_yticks([0, 1])
        ax.set_xlabel("x1", fontsize=9)
    grid[0].set_ylabel("x2", fontsize=9)


def perceptron_convergence(fig, axes, p: Palette) -> None:
    runs = _runs()
    ax = fig.subplots(1, 1)
    colors = {"AND": p.blue, "OR": p.green, "NAND": p.purple, "XOR": p.red}
    for name in GATES:
        _, _, history = runs[name]
        ax.plot(range(1, len(history) + 1), history, "o-", ms=3.5, lw=1.8,
                color=colors[name], label=name)
    ax.set_xlabel("epoch")
    ax.set_ylabel("misclassified rows (of 4)")
    ax.set_yticks([0, 1, 2, 3, 4])
    ax.set_title("Three gates reach zero errors and stop. XOR never does.", fontsize=10.5)
    ax.legend(fontsize=8, ncol=4, loc="upper right")


# Both draw functions build their own axes, so _style must not add one.
FIGURES = [
    figure("perceptron-gates", perceptron_gates, size=(9.6, 2.8), axes=False),
    figure("perceptron-convergence", perceptron_convergence, size=(7.2, 3.2), axes=False),
    figure("xor-ceiling", xor_ceiling, size=(9.0, 4.0), axes=False),
]


if __name__ == "__main__":
    ceiling = _ceiling()
    print("=== exhaustive search over single neurons ===")
    print(f"{'gate':>6} {'best of 4':>10} {'solving pairs':>15} {'share':>9}")
    for name in GATES:
        share = ceiling["perfect"][name] / ceiling["cells"]
        print(f"{name:>6} {ceiling['best'][name]:10d} "
              f"{ceiling['perfect'][name]:15,} {share:9.4%}")
    print(f"searched {ceiling['cells']:,} weight pairs per gate, "
          f"best bias chosen for each\n")

    for name, (w, b, history) in _runs().items():
        first_zero = next((i + 1 for i, e in enumerate(history) if e == 0), None)
        print(f"{name:5s} w=[{w[0]:+.2f},{w[1]:+.2f}] b={b:+.2f}  "
              f"first zero-error epoch: {first_zero}  errors: {history[:12]}")
