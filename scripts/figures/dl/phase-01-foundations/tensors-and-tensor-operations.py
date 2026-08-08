"""Figures for *Tensors and Tensor Operations*.

``matmul-scaling``
    Measured matmul time against n on a log-log axis, with an n-cubed reference
    line. The slope is the point: doubling n costs eight times the work.

``dtype-cost``
    Bytes and matmul time for float16, float32 and float64 at the same shape.
    float16 halves the memory and, on this CPU, costs orders of magnitude more
    time — a result worth seeing before choosing a dtype to "save memory".

``broadcasting``
    A schematic of the rule that lets a (3,1) and a (1,4) tensor add. Nothing is
    measured here; it is the diagram the rule deserves.
"""

from __future__ import annotations

import functools
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "..", ".."))

from _style import Palette, figure  # noqa: E402

SIZES = (64, 128, 256, 512, 1024)
DTYPE_N = 512


def _time_matmul(n: int, dtype: str, repeats: int = 3) -> float:
    rng = np.random.default_rng(0)
    A = rng.normal(size=(n, n)).astype(dtype)
    B = rng.normal(size=(n, n)).astype(dtype)
    A @ B                                        # warm up caches and kernels
    start = time.perf_counter()
    for _ in range(repeats):
        A @ B
    return (time.perf_counter() - start) / repeats


@functools.lru_cache(maxsize=1)
def _scaling() -> dict:
    return {n: _time_matmul(n, "float32", repeats=5) for n in SIZES}


@functools.lru_cache(maxsize=1)
def _dtypes() -> dict:
    out = {}
    for dtype in ("float16", "float32", "float64"):
        seconds = _time_matmul(DTYPE_N, dtype, repeats=1)
        out[dtype] = {"seconds": seconds,
                      "bytes": np.zeros((DTYPE_N, DTYPE_N), dtype=dtype).nbytes}
    return out


def matmul_scaling(fig, axes, p: Palette) -> None:
    timings = _scaling()
    ax = fig.subplots(1, 1)
    ns = np.array(SIZES, dtype=float)
    seconds = np.array([timings[n] for n in SIZES])

    ax.loglog(ns, seconds, "o-", color=p.blue, lw=2.0, ms=6, label="measured")
    reference = seconds[-1] * (ns / ns[-1]) ** 3
    ax.loglog(ns, reference, "--", color=p.muted, lw=1.4,
              label="n$^3$ reference, matched at n=1024")
    for n, s in zip(SIZES, seconds):
        ax.annotate(f"{s * 1e3:.2f} ms", (n, s), textcoords="offset points",
                    xytext=(6, -10), fontsize=7.5, color=p.fg)
    ax.set_xlabel("n  (multiplying two n x n float32 matrices)")
    ax.set_ylabel("seconds per matmul")
    ax.set_title("2n$^3$ flops in theory; the slope only matches once n is large",
                 fontsize=10.5)
    ax.legend(fontsize=8, loc="upper left")


def dtype_cost(fig, axes, p: Palette) -> None:
    results = _dtypes()
    left, right = fig.subplots(1, 2)
    names = list(results)
    positions = np.arange(len(names))
    colors = [p.green, p.blue, p.amber]

    megabytes = [results[n]["bytes"] / 1e6 for n in names]
    left.bar(positions, megabytes, 0.55, color=colors)
    for x, value in zip(positions, megabytes):
        left.annotate(f"{value:.1f} MB", (x, value), textcoords="offset points",
                      xytext=(0, 4), ha="center", fontsize=8, color=p.fg)
    left.set_xticks(positions)
    left.set_xticklabels(names)
    left.set_ylabel(f"megabytes for one {DTYPE_N}x{DTYPE_N} matrix")
    left.set_title("memory: exactly what you would expect", fontsize=10)
    left.set_ylim(0, max(megabytes) * 1.25)

    seconds = [results[n]["seconds"] for n in names]
    right.bar(positions, seconds, 0.55, color=colors)
    for x, value in zip(positions, seconds):
        right.annotate(f"{value:.4f}s" if value < 1 else f"{value:.2f}s",
                       (x, value), textcoords="offset points", xytext=(0, 4),
                       ha="center", fontsize=8, color=p.fg)
    right.set_xticks(positions)
    right.set_xticklabels(names)
    right.set_yscale("log")
    right.set_ylabel("seconds per matmul (log scale)")
    right.set_title("speed: not what you would expect", fontsize=10)
    ratio = seconds[0] / seconds[1]
    right.annotate(f"float16 is {ratio:,.0f}x slower\nthan float32 on this CPU",
                   xy=(0, seconds[0]), xytext=(0.35, seconds[0] * 0.25),
                   color=p.red, fontsize=8,
                   arrowprops=dict(arrowstyle="->", color=p.red, lw=1.0))


def broadcasting(fig, axes, p: Palette) -> None:
    ax = fig.subplots(1, 1)
    ax.set_xlim(0, 12.4)
    ax.set_ylim(-0.6, 4.2)
    ax.axis("off")

    def grid(x0, y0, rows, cols, values, label, color):
        for r in range(rows):
            for c in range(cols):
                ax.add_patch(plt_rect(x0 + c, y0 - r, color))
                ax.text(x0 + c + 0.5, y0 - r + 0.5, values(r, c), ha="center",
                        va="center", fontsize=9, color=p.bg if color != p.bg else p.fg)
        ax.text(x0 + cols / 2, y0 + 1.15, label, ha="center", fontsize=9.5, color=p.fg)

    def plt_rect(x, y, color):
        from matplotlib.patches import Rectangle

        return Rectangle((x, y), 0.94, 0.94, facecolor=color, edgecolor=p.bg, lw=1.2)

    grid(0.2, 3.0, 3, 1, lambda r, c: f"a{r}", "a: shape (3, 1)", p.blue)
    ax.text(1.7, 2.0, "+", ha="center", va="center", fontsize=16, color=p.fg)
    grid(2.4, 3.0, 1, 4, lambda r, c: f"b{c}", "b: shape (1, 4)", p.amber)
    ax.text(7.0, 2.0, "=", ha="center", va="center", fontsize=16, color=p.fg)
    grid(7.7, 3.0, 3, 4, lambda r, c: f"a{r}+b{c}", "a + b: shape (3, 4)", p.green)

    ax.text(6.2, -0.35,
            "each operand is stretched along the axis where it has length 1 — "
            "no copy is made",
            ha="center", fontsize=8.5, color=p.muted)


FIGURES = [
    figure("matmul-scaling", matmul_scaling, size=(7.0, 3.6), axes=False),
    figure("dtype-cost", dtype_cost, size=(9.0, 3.4), axes=False),
    figure("broadcasting", broadcasting, size=(8.4, 2.8), axes=False),
]


if __name__ == "__main__":
    for n, seconds in _scaling().items():
        print(f"n={n:5d}  {seconds * 1e3:9.3f} ms  "
              f"{2 * n ** 3 / seconds / 1e9:7.2f} GFLOP/s")
    for dtype, info in _dtypes().items():
        print(f"{dtype:8s} {info['bytes'] / 1e6:6.2f} MB  {info['seconds']:10.4f} s")
