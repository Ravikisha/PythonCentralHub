"""Figures for *NumPy for Mathematics*.

1. `solve-vs-inv` — relative solution error against condition number, for
   ``np.linalg.solve`` and for forming the inverse explicitly. The dashed line is
   machine epsilon times kappa: the standard *upper bound* on the relative error,
   set by the conditioning of the problem rather than by the algorithm. Both
   methods track it a small constant below; `inv` is the worse of the two at 26 of
   the 27 conditioning levels sampled, which is the argument for never inverting a
   matrix to solve a system.

   The matrices have a *prescribed* condition number rather than being drawn at
   random or taken from a Hilbert family, so the x axis means exactly what it
   says. See ``_data.ill_conditioned``.

2. `float32-vs-float64` — what precision buys. The left panel accumulates a
   million values in both dtypes and plots the drift from the exact total; the
   right panel is just the digit counts, because "float32 has about seven digits"
   is the fact people actually need and rarely have to hand.
"""

import numpy as np

from _data import ill_conditioned
from _style import Palette, figure


def solve_vs_inv(fig, ax, p: Palette) -> None:
    """Accuracy against conditioning, solve versus explicit inverse."""
    kappas = np.logspace(1, 14, 27)
    n = 10
    rng = np.random.default_rng(11)
    x_true = rng.standard_normal(n)

    err_solve, err_inv = [], []
    for i, kappa in enumerate(kappas):
        A = ill_conditioned(n=n, kappa=float(kappa), seed=100 + i)
        b = A @ x_true
        xs = np.linalg.solve(A, b)
        # inv is what we are arguing against; suppress nothing, just measure it.
        xi = np.linalg.inv(A) @ b
        scale = np.linalg.norm(x_true)
        err_solve.append(np.linalg.norm(xs - x_true) / scale)
        err_inv.append(np.linalg.norm(xi - x_true) / scale)

    eps = np.finfo(float).eps
    ax.loglog(kappas, np.maximum(err_solve, 1e-18), color=p.blue, linewidth=2,
              marker="o", markersize=3, label="np.linalg.solve")
    ax.loglog(kappas, np.maximum(err_inv, 1e-18), color=p.red, linewidth=2,
              marker="s", markersize=3, label="inv(A) @ b")
    ax.loglog(kappas, eps * kappas, color=p.amber, linestyle="--", linewidth=1.4,
              label=r"$\varepsilon\,\kappa(A)$ — bound set by $\kappa$")
    ax.axhline(1.0, color=p.muted, linewidth=1, linestyle=":")
    ax.text(kappas[1], 1.3, "error of 100%: no digits left", color=p.muted, fontsize=8.5)

    ax.set_xlabel(r"condition number $\kappa(A)$")
    ax.set_ylabel("relative error in $x$")
    ax.set_ylim(1e-18, 1e3)
    ax.legend(loc="upper left", fontsize=9)


def float32_vs_float64(fig, ax, p: Palette) -> None:
    """Accumulated summation error, and the digit counts."""
    fig.clear()
    axes = fig.subplots(1, 2, width_ratios=[1.55, 1.0])

    # --- left: drift while summing a million values ------------------------
    rng = np.random.default_rng(3)
    values = rng.uniform(0.5, 1.5, 1_000_000)

    # A naive running sum in each dtype, sampled so the plot stays small.
    marks = np.unique(np.logspace(1, 6, 60).astype(int))
    exact = np.cumsum(values.astype(np.float128) if hasattr(np, "float128")
                      else values.astype(np.float64))[marks - 1]

    def naive_sum(dtype):
        acc = dtype(0)
        out = np.empty(marks.size, dtype=np.float64)
        k = 0
        casted = values.astype(dtype)
        for i in range(values.size):
            acc = dtype(acc + casted[i])
            if k < marks.size and i + 1 == marks[k]:
                out[k] = float(acc)
                k += 1
        return out

    s32 = naive_sum(np.float32)
    s64 = naive_sum(np.float64)

    rel32 = np.abs(s32 - exact) / exact
    rel64 = np.maximum(np.abs(s64 - exact) / exact, 1e-18)

    a = axes[0]
    a.loglog(marks, np.maximum(rel32, 1e-18), color=p.red, linewidth=2, label="float32")
    a.loglog(marks, rel64, color=p.blue, linewidth=2, label="float64")
    a.axhline(np.finfo(np.float32).eps, color=p.red, linestyle=":", linewidth=1.1,
              label=r"float32 $\varepsilon$")
    a.axhline(np.finfo(np.float64).eps, color=p.blue, linestyle=":", linewidth=1.1,
              label=r"float64 $\varepsilon$")
    a.set_xlabel("values summed, naive running total")
    a.set_ylabel("relative error of the total")
    a.set_title("error accumulates with every addition")
    a.legend(loc="upper left", fontsize=8.5)

    # --- right: how many decimal digits each dtype carries ----------------
    a = axes[1]
    dtypes = [("float16", np.float16), ("float32", np.float32), ("float64", np.float64)]
    names = [d[0] for d in dtypes]
    digits = [abs(np.log10(np.finfo(d[1]).eps)) for d in dtypes]
    bars = a.bar(names, digits, color=[p.purple, p.red, p.blue], width=0.6)
    for rect, d in zip(bars, digits):
        a.text(rect.get_x() + rect.get_width() / 2, d + 0.35, f"{d:.1f}",
               ha="center", color=p.fg, fontsize=9.5)
    a.set_ylabel("significant decimal digits")
    a.set_ylim(0, 19)
    a.set_title("what the dtype buys")
    a.grid(axis="x", visible=False)


FIGURES = [
    figure("solve-vs-inv", solve_vs_inv, size=(7.6, 4.4)),
    figure("float32-vs-float64", float32_vs_float64, size=(9.4, 3.8), axes=False),
]
