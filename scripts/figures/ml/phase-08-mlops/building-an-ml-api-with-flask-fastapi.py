"""Figures for *Building an ML API with Flask/FastAPI*."""

import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _data import breast_cancer_split  # noqa: E402
from _style import Palette, figure  # noqa: E402


def batching_throughput(fig, axes, p: Palette) -> None:
    """Per-call overhead dominates, so batching is very nearly free.

    Absolute milliseconds depend on the machine, so the figure plots throughput
    (rows per second) and the *ratio* between batch sizes — both of which hold
    up across hardware in a way a raw latency number does not.
    """
    from sklearn.ensemble import RandomForestClassifier

    X_tr, X_te, y_tr, y_te = breast_cancer_split()
    model = RandomForestClassifier(n_estimators=500, random_state=0,
                                   n_jobs=1).fit(X_tr, y_tr)

    sizes = [1, 2, 4, 8, 16, 32, 64, 128]
    per_call, throughput = [], []
    for bs in sizes:
        batch = X_te[:bs] if bs <= len(X_te) else np.resize(X_te, (bs, X_te.shape[1]))
        model.predict(batch)                       # warm up
        reps = max(3, int(300 / bs ** 0.5))
        start = time.perf_counter()
        for _ in range(reps):
            model.predict(batch)
        elapsed = (time.perf_counter() - start) / reps
        per_call.append(elapsed * 1000)
        throughput.append(bs / elapsed)

    axs = fig.subplots(1, 2)

    axs[0].plot(sizes, per_call, "o-", color=p.blue)
    axs[0].set_xscale("log", base=2)
    axs[0].set_xlabel("rows per predict() call")
    axs[0].set_ylabel("milliseconds per call")
    axs[0].set_ylim(0, max(per_call) * 1.3)
    axs[0].set_title("One call costs about the same\nwhatever you put in it",
                     fontsize=11)

    axs[1].plot(sizes, throughput, "o-", color=p.amber, label="measured")
    ideal = [throughput[0] * s for s in sizes]
    axs[1].plot(sizes, ideal, "--", color=p.muted, lw=1.4,
                label="perfectly linear in batch size")
    axs[1].set_xscale("log", base=2)
    axs[1].set_yscale("log")
    axs[1].set_xlabel("rows per predict() call")
    axs[1].set_ylabel("rows per second (log scale)")
    axs[1].set_title("So throughput rises almost linearly", fontsize=11)
    axs[1].legend(loc="upper left", fontsize=9)

    fig.suptitle("Measured on one loaded machine — read the SHAPE, not the "
                 "millisecond values", fontsize=10, color=p.muted)


def request_lifecycle(fig, axes, p: Palette) -> None:
    """Where a prediction request's work actually goes, and what to cache."""
    axes.axis("off")

    stages = [
        ("HTTP parse\n+ validate", 0.02, 0.16, p.blue, "per request"),
        ("Build the\nfeature row", 0.20, 0.18, p.blue, "per request"),
        ("LOAD MODEL", 0.40, 0.18, p.red, "startup only!"),
        ("predict()", 0.60, 0.16, p.green, "per request"),
        ("Serialise\nJSON", 0.78, 0.16, p.blue, "per request"),
    ]
    from matplotlib.patches import FancyArrow, Rectangle

    for label, x0, w, col, note in stages:
        axes.add_patch(Rectangle((x0, 0.52), w, 0.26, facecolor=col, alpha=0.22,
                                 edgecolor=col, lw=2))
        axes.annotate(label, (x0 + w / 2, 0.65), ha="center", va="center",
                      fontsize=9.5, color=p.fg)
        axes.annotate(note, (x0 + w / 2, 0.44), ha="center", va="center",
                      fontsize=8.5,
                      color=p.red if note.startswith("startup") else p.muted)
        if x0 > 0.02:
            axes.annotate("", xy=(x0 - 0.005, 0.65), xytext=(x0 - 0.025, 0.65),
                          arrowprops=dict(arrowstyle="->", color=p.muted, lw=1.4))

    axes.annotate("Everything blue happens on every request and must be fast.\n"
                  "The red box is the one thing that must NOT be in the "
                  "request path.",
                  (0.5, 0.20), ha="center", fontsize=10, color=p.fg)
    axes.set_xlim(0, 1)
    axes.set_ylim(0.08, 0.88)
    axes.set_title("The request path, and the one box that does not belong in it")


FIGURES = [
    figure("batching-throughput", batching_throughput, size=(8.6, 3.8), axes=False),
    figure("request-lifecycle", request_lifecycle, size=(8.6, 3.0)),
]
