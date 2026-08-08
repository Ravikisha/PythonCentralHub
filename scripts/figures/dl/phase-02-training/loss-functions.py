"""Figures for *Loss Functions: Choosing What to Minimise*.

``regression-losses``
    MSE, MAE and Huber against the error, and — more usefully — their
    derivatives, because the derivative is what training actually sees.

``classification-losses``
    Cross-entropy against the probability assigned to the truth, next to hinge
    and 0-1 loss. The vertical asymptote is the whole point.

``from-logits``
    Measured error of computing softmax and then its log, against letting the
    loss consume raw logits. The naive path stops being merely inaccurate and
    starts returning inf.
"""

from __future__ import annotations

import functools
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "..", ".."))

from _dl import tf  # noqa: E402
from _style import Palette, figure  # noqa: E402

DELTA = 1.0
MAGNITUDES = (1.0, 10.0, 30.0, 60.0, 90.0, 200.0, 400.0, 800.0)


def huber(error: np.ndarray, delta: float = DELTA) -> np.ndarray:
    small = np.abs(error) <= delta
    return np.where(small, 0.5 * error ** 2,
                    delta * (np.abs(error) - 0.5 * delta))


def huber_gradient(error: np.ndarray, delta: float = DELTA) -> np.ndarray:
    return np.clip(error, -delta, delta)


def regression_losses(fig, axes, p: Palette) -> None:
    left, right = fig.subplots(1, 2)
    error = np.linspace(-4, 4, 400)

    # MAE's derivative is undefined at 0; a nan there draws the jump honestly
    # instead of joining -1 to +1 with a vertical line.
    mae_gradient = np.sign(error)
    mae_gradient[np.abs(error) < 0.02] = np.nan

    curves = (("MSE  e^2", error ** 2, 2 * error, p.blue),
              ("MAE  |e|", np.abs(error), mae_gradient, p.green),
              (f"Huber d={DELTA:g}", huber(error), huber_gradient(error),
               p.amber))
    for label, value, gradient, color in curves:
        left.plot(error, value, lw=2.0, color=color, label=label)
        right.plot(error, gradient, lw=2.0, color=color, label=label)

    left.set_xlabel("error (prediction - target)")
    left.set_ylabel("loss")
    left.set_ylim(0, 8)
    left.set_title("the loss", fontsize=10)
    left.legend(fontsize=8)

    right.axhline(0, color=p.grid, lw=1.0)
    right.axvline(-DELTA, color=p.grid, lw=0.8, ls=":")
    right.axvline(DELTA, color=p.grid, lw=0.8, ls=":")
    right.set_xlabel("error (prediction - target)")
    right.set_ylabel("d loss / d error")
    right.set_title("the derivative — what training actually sees", fontsize=10)
    right.legend(fontsize=8)


def classification_losses(fig, axes, p: Palette) -> None:
    left, right = fig.subplots(1, 2)
    probability = np.linspace(0.001, 1.0, 500)
    left.plot(probability, -np.log(probability), lw=2.0, color=p.blue,
              label="cross-entropy  -log p")
    left.plot(probability, 1.0 - probability, lw=2.0, color=p.green,
              label="1 - p (linear, for scale)")
    left.plot(probability, (probability < 0.5).astype(float), lw=2.0,
              color=p.red, ls="--", label="0-1 loss (not differentiable)")
    for point in (0.9, 0.5, 0.1, 0.01):
        left.scatter([point], [-np.log(point)], s=34, color=p.amber, zorder=5)
        left.annotate(f"p={point:g}: {-np.log(point):.2f}",
                      (point, -np.log(point)), textcoords="offset points",
                      xytext=(8, 2), fontsize=7.5, color=p.amber)
    left.set_xlabel("probability assigned to the correct class")
    left.set_ylabel("loss")
    left.set_ylim(0, 5)
    left.set_title("cross-entropy has no upper bound", fontsize=10)
    left.legend(fontsize=7.5)

    # The gradient with respect to the logit is the reason this pairing works.
    logit = np.linspace(-6, 6, 400)
    sigmoid = 1.0 / (1.0 + np.exp(-logit))
    right.plot(logit, -np.log(sigmoid), lw=2.0, color=p.blue,
               label="BCE for y=1, as a function of the logit")
    right.plot(logit, sigmoid - 1.0, lw=2.0, color=p.amber,
               label="d BCE / d logit  =  sigmoid(z) - y")
    right.axhline(0, color=p.grid, lw=1.0)
    right.set_xlabel("logit z")
    right.set_ylabel("loss / gradient")
    right.set_title("sigmoid + BCE: the gradient is just the error",
                    fontsize=10)
    right.legend(fontsize=7.5)


@functools.lru_cache(maxsize=1)
def _from_logits() -> dict:
    """Two ways to compute the same cross-entropy, at growing logit scale."""
    keras = tf().keras
    rows = []
    for magnitude in MAGNITUDES:
        logits = np.array([[0.0, magnitude]], dtype="float32")
        labels = np.array([0])                     # the *wrong*, unlikely class
        stable = float(keras.losses.sparse_categorical_crossentropy(
            labels, logits, from_logits=True).numpy()[0])
        probabilities = tf().nn.softmax(logits).numpy()
        naive = float(keras.losses.sparse_categorical_crossentropy(
            labels, probabilities, from_logits=False).numpy()[0])
        exact = float(np.logaddexp(0.0, magnitude))   # -log softmax_0 exactly
        rows.append({"magnitude": magnitude, "stable": stable, "naive": naive,
                     "exact": exact,
                     "probability": float(probabilities[0, 0])})
    return {"rows": rows}


def from_logits(fig, axes, p: Palette) -> None:
    rows = _from_logits()["rows"]
    ax = fig.subplots(1, 1)
    magnitudes = [r["magnitude"] for r in rows]
    exact = [r["exact"] for r in rows]
    stable = [r["stable"] for r in rows]
    naive = [r["naive"] if np.isfinite(r["naive"]) else np.nan for r in rows]

    ax.plot(magnitudes, exact, "-", lw=6.0, color=p.grid, alpha=0.55,
            solid_capstyle="round", label="exact value: log(1 + e^z)")
    ax.plot(magnitudes, stable, "s-", ms=4, lw=1.8, color=p.green,
            label="from_logits=True (lies on the exact curve)")
    ax.plot(magnitudes, naive, "^-", ms=5, lw=1.8, color=p.red,
            label="softmax first, then the loss")

    # The naive path does not blow up — it flattens. Keras clips probabilities
    # to epsilon, so every loss past that point returns -log(epsilon).
    ceiling = max(r["naive"] for r in rows)
    ax.axhline(ceiling, color=p.red, lw=1.2, ls=":")
    ax.annotate(f"clamped at {ceiling:.4f} = -log(1e-7)\n"
                f"no gradient signal past here",
                (magnitudes[-2], ceiling), textcoords="offset points",
                xytext=(-10, -34), ha="right", fontsize=8, color=p.red)
    wrong = next((r for r in rows if r["exact"] > 0
                  and abs(r["naive"] - r["exact"]) / r["exact"] > 0.01), None)
    if wrong:
        ax.axvline(wrong["magnitude"], color=p.amber, lw=1.2, ls=":")
        ax.annotate(f"already {abs(wrong['naive'] - wrong['exact']) / wrong['exact']:.0%} "
                    f"too low at a gap of {wrong['magnitude']:g}",
                    (wrong["magnitude"], max(exact)),
                    textcoords="offset points", xytext=(14, -8), fontsize=8,
                    color=p.amber)

    ax.set_yscale("log")
    ax.set_xlabel("logit gap between the two classes")
    ax.set_ylabel("cross-entropy of the unlikely class (log scale)")
    ax.set_title("The same loss, computed two ways", fontsize=10.5)
    ax.legend(fontsize=8, loc="lower right")


FIGURES = [
    figure("regression-losses", regression_losses, size=(9.2, 3.4), axes=False),
    figure("classification-losses", classification_losses, size=(9.2, 3.6),
           axes=False),
    figure("from-logits", from_logits, size=(7.8, 3.8), axes=False),
]


if __name__ == "__main__":
    print("=== regression losses at a few errors (Huber delta=1) ===")
    print(f"{'error':>7} {'MSE':>10} {'MAE':>8} {'Huber':>10} "
          f"{'dMSE':>8} {'dMAE':>7} {'dHuber':>8}")
    for e in (0.1, 0.5, 1.0, 2.0, 5.0, 20.0):
        arr = np.array([e])
        print(f"{e:7.1f} {e ** 2:10.4f} {e:8.4f} {huber(arr)[0]:10.4f} "
              f"{2 * e:8.2f} {1.0:7.2f} {huber_gradient(arr)[0]:8.2f}")

    errors = np.array([0.5, -0.5, 1.0, -1.0, 20.0])
    print(f"\nfor errors {errors.tolist()}:")
    print(f"  MSE   {np.mean(errors ** 2):.4f}   "
          f"outlier share {errors[-1] ** 2 / np.sum(errors ** 2):.4f}")
    print(f"  MAE   {np.mean(np.abs(errors)):.4f}   "
          f"outlier share {abs(errors[-1]) / np.sum(np.abs(errors)):.4f}")
    print(f"  Huber {np.mean(huber(errors)):.4f}   "
          f"outlier share {huber(errors)[-1] / np.sum(huber(errors)):.4f}")

    print("\n=== cross-entropy at a few probabilities ===")
    for prob in (0.99, 0.9, 0.5, 0.1, 0.01, 0.001):
        print(f"  p={prob:<6} -log p = {-np.log(prob):.6f}")

    print("\n=== from_logits stability ===")
    print(f"{'gap':>7} {'exact':>14} {'from_logits':>14} {'naive':>14} "
          f"{'softmax p0':>12}")
    for row in _from_logits()["rows"]:
        print(f"{row['magnitude']:7.0f} {row['exact']:14.6f} "
              f"{row['stable']:14.6f} {row['naive']:14.6f} "
              f"{row['probability']:12.3e}")
