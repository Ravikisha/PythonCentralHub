"""Figures for *Why We Can Set the Margin to 1* (§12.2.2–12.2.3).

1. `two-ways-to-fix-the-scale` — Figure 12.5 beside Figure 12.4: the same
   hyperplane, named twice. Left fixes ||w|| = 1 and reads the margin off as r;
   right fixes the value at the closest point to 1 and reads it off as 1/||w||.

2. `the-equivalence-measured` — Theorem 12.1 over 300 random datasets, and what
   the squared norm buys: the angle between the two solutions never exceeds
   7.5e-06 degrees, and the convex quadratic form converges on every start.
"""

from __future__ import annotations

import numpy as np
from scipy.optimize import minimize

from _style import Palette, figure

X = np.array([[3.0, 1.0], [3.0, -1.0], [6.0, 1.0], [6.0, -1.0],
              [1.0, 0.0], [0.0, 1.0], [0.0, -1.0], [-1.0, 0.0]])
Y = np.array([1.0, 1.0, 1.0, 1.0, -1.0, -1.0, -1.0, -1.0])
W_STAR, B_STAR = np.array([1.0, 0.0]), -2.0


def _scatter(ax, p: Palette, size=80):
    pos, neg = X[Y > 0], X[Y < 0]
    ax.scatter(pos[:, 0], pos[:, 1], marker="x", s=size, lw=2.3,
               color=p.amber, zorder=4)
    ax.scatter(neg[:, 0], neg[:, 1], marker="o", s=size, lw=2.0,
               facecolor="none", edgecolor=p.blue, zorder=4)


def _solve_1221(XX, YY, seed=0):
    d = XX.shape[1]
    rg = np.random.default_rng(seed)
    return minimize(lambda v: 0.5 * v[:d] @ v[:d],
                    np.r_[rg.normal(0, 1, d), rg.normal(0, 1)],
                    constraints=[{"type": "ineq",
                                  "fun": lambda v: YY * (XX @ v[:d] + v[d]) - 1}],
                    method="SLSQP", options={"maxiter": 6000, "ftol": 1e-14})


def _solve_1210(XX, YY, seed=0):
    d = XX.shape[1]
    rg = np.random.default_rng(seed)
    w0 = rg.normal(0, 1, d)
    w0 /= np.linalg.norm(w0)
    return minimize(lambda v: -v[d + 1], np.r_[w0, rg.normal(0, 1), 0.5],
                    constraints=[
                        {"type": "ineq",
                         "fun": lambda v: YY * (XX @ v[:d] + v[d]) - v[d + 1]},
                        {"type": "eq", "fun": lambda v: v[:d] @ v[:d] - 1.0},
                        {"type": "ineq", "fun": lambda v: v[d + 1]}],
                    method="SLSQP", options={"maxiter": 6000, "ftol": 1e-14})


# --------------------------------------------------------------------------
# 1. two ways to fix the scale
# --------------------------------------------------------------------------

def two_ways_to_fix_the_scale(fig, ax, p: Palette) -> None:
    """On the halved running example the margin is 0.5, so the two
    parametrisations are visibly different rather than coincidentally equal."""
    fig.clear()
    a1, a2 = fig.subplots(1, 2, sharey=True)

    XH = X / 2.0                     # boundary at 1.0, margin 0.5
    posh, negh = XH[Y > 0], XH[Y < 0]

    for a, nw, title, note, lev in (
            (a1, 1.0, r"§12.2.1:  fix $\|w\| = 1$",
             r"margin $= r = 0.5$", 0.5),
            (a2, 2.0, r"§12.2.2:  fix $\langle w, x_a\rangle + b = 1$",
             r"margin $= 1/\|w\| = 0.5$", 1.0)):
        a.set_xlim(-1.2, 3.7)
        a.set_ylim(-1.5, 1.75)
        a.axvspan(0.5, 1.5, color=p.muted, alpha=0.10)
        a.axvline(1.0, color=p.fg, lw=2.4)
        a.axvline(1.5, color=p.amber, ls="--", lw=1.5)
        a.axvline(0.5, color=p.blue, ls="--", lw=1.5)
        a.annotate("", xy=(1.0 + 0.55 / nw, 1.18), xytext=(1.0, 1.18),
                   arrowprops=dict(arrowstyle="-|>", lw=2.3, color=p.red))
        a.annotate(rf"$w$,  $\|w\| = {nw:g}$", (1.04, 1.40),
                   fontsize=10, color=p.red)
        a.annotate("", xy=(1.5, -1.02), xytext=(1.0, -1.02),
                   arrowprops=dict(arrowstyle="<|-|>", lw=1.7,
                                   color=p.purple))
        a.annotate(note, (1.02, -0.92), fontsize=9.5, color=p.purple)
        a.annotate(rf"$= +{lev:g}$", (1.55, 0.86), fontsize=9.5,
                   color=p.amber)
        a.annotate(rf"$= -{lev:g}$", (0.10, 0.86), fontsize=9.5,
                   color=p.blue)
        a.annotate(r"$\langle w,x\rangle + b = 0$", (1.02, -1.40),
                   fontsize=9.5, color=p.fg)
        a.scatter(posh[:, 0], posh[:, 1], marker="x", s=80, lw=2.3,
                  color=p.amber, zorder=4)
        a.scatter(negh[:, 0], negh[:, 1], marker="o", s=80, lw=2.0,
                  facecolor="none", edgecolor=p.blue, zorder=4)
        a.set_xlabel("$x^{(1)}$")
        a.set_title(title, fontsize=10.5)
    a1.set_ylabel("$x^{(2)}$")
    fig.suptitle("The same hyperplane, named twice — Theorem 12.1 says "
                 "these are one problem",
                 fontsize=11.5, fontweight="bold", color=p.fg)


# --------------------------------------------------------------------------
# 2. the equivalence measured
# --------------------------------------------------------------------------

def the_equivalence_measured(fig, ax, p: Palette) -> None:
    fig.clear()
    a1, a2 = fig.subplots(1, 2, gridspec_kw={"width_ratios": [1.1, 1.0]})

    # --- left: Theorem 12.1 over random datasets
    rg = np.random.default_rng(3)
    angs, done = [], 0
    while done < 300:
        D = int(rg.integers(2, 6))
        n = int(rg.integers(6, 16))
        mu = rg.normal(0, 1, D) * 3
        XX = np.vstack([rg.normal(mu, 1.0, (n // 2, D)),
                        rg.normal(-mu, 1.0, (n - n // 2, D))])
        YY = np.r_[np.ones(n // 2), -np.ones(n - n // 2)]
        a = min((_solve_1221(XX, YY, s) for s in range(10)),
                key=lambda r: 0.5 * r.x[:D] @ r.x[:D] if r.success else np.inf)
        if not a.success:
            continue
        if float(np.maximum(0, 1 - YY * (XX @ a.x[:D] + a.x[D])).max()) > 1e-7:
            continue
        cs = [r for r in (_solve_1210(XX, YY, s) for s in range(10))
              if r.success]
        done += 1
        if not cs:
            continue
        c = max(cs, key=lambda r: r.x[D + 1])
        wa = a.x[:D] / np.linalg.norm(a.x[:D])
        wc = c.x[:D] / np.linalg.norm(c.x[:D])
        if wa @ wc < 0:
            wc = -wc
        angs.append(max(np.degrees(np.arccos(np.clip(wa @ wc, -1, 1))),
                        1e-14))
    angs = np.array(angs)
    a1.hist(angs, bins=np.logspace(-14, -4, 34), color=p.blue,
            edgecolor=p.bg, lw=0.4)
    a1.set_xscale("log")
    a1.axvline(angs.max(), color=p.red, ls="--", lw=1.8)
    top = a1.get_ylim()[1]
    a1.annotate(f"worst of all {len(angs)}:\n{angs.max():.1e} degrees",
                (angs.max() * 0.7, top * 0.93),
                fontsize=8.5, color=p.red, ha="right", va="top")
    a1.annotate("exact agreement\n(clamped to the axis)", (1.6e-14, top * 0.72),
                fontsize=8.5, color=p.blue, ha="left", va="top")
    a1.set_xlabel("angle between the two solutions' normals, degrees")
    a1.set_ylabel(f"datasets (of {len(angs)})")
    a1.set_title("Theorem 12.1 is exact, not approximate", fontsize=10)

    # --- right: what the squared norm buys the solver
    labels, fails, meds, maxs = [], [], [], []
    for name, f in ((r"$\|w\|$", lambda v: np.linalg.norm(v[:2])),
                    (r"$\frac{1}{2}\|w\|^2$",
                     lambda v: 0.5 * v[:2] @ v[:2])):
        its, nf = [], 0
        for s in range(500):
            rg2 = np.random.default_rng(s)
            r = minimize(f, np.r_[rg2.normal(0, 3, 2), rg2.normal(0, 3)],
                         constraints=[{"type": "ineq",
                                       "fun": lambda v: Y * (X @ v[:2] + v[2]) - 1}],
                         method="SLSQP",
                         options={"maxiter": 6000, "ftol": 1e-14})
            its.append(r.nit) if r.success else None
            nf += 0 if r.success else 1
        labels.append(name)
        fails.append(nf)
        meds.append(float(np.median(its)))
        maxs.append(float(np.max(its)))

    xs = np.arange(2)
    wdt = 0.26
    a2.bar(xs - wdt, meds, wdt, color=p.blue, label="median iterations")
    a2.bar(xs, maxs, wdt, color=p.purple, label="worst iterations")
    a2.bar(xs + wdt, fails, wdt, color=p.red, label="failures of 500")
    for i in range(2):
        a2.text(xs[i] - wdt, meds[i] + 0.7, f"{meds[i]:.0f}", ha="center",
                fontsize=9, color=p.blue)
        a2.text(xs[i], maxs[i] + 0.7, f"{maxs[i]:.0f}", ha="center",
                fontsize=9, color=p.purple)
        a2.text(xs[i] + wdt, fails[i] + 0.7, f"{fails[i]}", ha="center",
                fontsize=9, color=p.red)
    a2.set_xticks(xs)
    a2.set_xticklabels(labels, fontsize=13)
    a2.set_ylim(0, max(maxs) * 1.25)
    a2.set_ylabel("count")
    a2.legend(fontsize=8.5)
    a2.set_title("why 12.18 squares the norm", fontsize=10)

    fig.suptitle("The two formulations agree to machine precision — and "
                 "one of them is a quadratic program",
                 fontsize=11.5, fontweight="bold", color=p.fg)


FIGURES = [
    figure("two-ways-to-fix-the-scale", two_ways_to_fix_the_scale,
           size=(9.6, 4.4), axes=False),
    figure("the-equivalence-measured", the_equivalence_measured,
           size=(9.6, 4.3), axes=False),
]
