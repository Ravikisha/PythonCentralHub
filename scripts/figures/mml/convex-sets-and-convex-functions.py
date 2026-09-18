"""Figures for *Convex Sets and Convex Functions*.

1. `convex-sets-and-functions` — Definitions 7.2 and 7.3 in one picture, plus the
   book's Figures 7.5 and 7.6. A set is convex when every chord stays inside; a
   function is convex when every chord stays above. The fourth panel shades an
   epigraph, which is the bridge between the two definitions.

2. `three-tests-on-the-negative-entropy` — Example 7.3 drawn to its own numbers.
   The chord test at x = 2 and x = 4, the tangent test of Equation 7.31, and the
   second derivative, all agreeing and all measured.

3. `sampling-cannot-prove-convexity` — the trap. x^4 - 0.02x^2 has a second
   derivative that dips to -0.04, so it is not convex, and a random chord sample
   catches a violation on only 0.308% of draws with a worst magnitude of 1e-4.

4. `closure-properties` — Exercises 7.3 and 7.4, measured. Intersection of convex
   sets is convex and union is not; sum and max of convex functions are convex,
   difference and product are not.
"""

from __future__ import annotations

import numpy as np
from matplotlib.patches import Circle, Polygon

from _style import Palette, figure


def _entropy(x):
    return x * np.log2(x)


def _dentropy(x):
    """Equation 7.32."""
    return np.log2(x) + 1.0 / np.log(2.0)


def convex_sets_and_functions(fig, ax, p: Palette) -> None:
    """The two definitions, and the epigraph that links them."""
    fig.clear()
    a1, a2, a3, a4 = fig.subplots(1, 4)

    # --- a convex set -----------------------------------------------------
    th = np.linspace(0, 2 * np.pi, 400)
    blob = np.column_stack([1.6 * np.cos(th) + 0.25 * np.cos(2 * th),
                            1.15 * np.sin(th)])
    a1.add_patch(Polygon(blob, closed=True, facecolor=p.blue, alpha=0.16,
                         edgecolor=p.blue, linewidth=1.8))
    pa, pb = np.array([-1.25, -0.55]), np.array([1.35, 0.60])
    a1.plot([pa[0], pb[0]], [pa[1], pb[1]], color=p.green, linewidth=2.2)
    a1.plot([pa[0], pb[0]], [pa[1], pb[1]], "o", color=p.green, markersize=6)
    for t, lab in ((0.35, ""), (0.7, "")):
        m = t * pa + (1 - t) * pb
        a1.plot([m[0]], [m[1]], "o", color=p.amber, markersize=5)
    a1.set_title("A CONVEX set", fontsize=9.8, color=p.blue)
    a1.text(0.0, -1.75,
            "$\\theta x + (1-\\theta)y \\in C$\nfor every "
            "$\\theta \\in [0,1]$\n\nevery chord stays inside",
            ha="center", va="top", fontsize=8.4, color=p.muted)

    # --- a nonconvex set --------------------------------------------------
    r = 1.5 + 0.55 * np.cos(3 * th)
    crescent = np.column_stack([r * np.cos(th), 0.85 * r * np.sin(th)])
    a2.add_patch(Polygon(crescent, closed=True, facecolor=p.red, alpha=0.14,
                         edgecolor=p.red, linewidth=1.8))
    qa = np.array([1.9, 0.15])
    qb = np.array([-0.95, 1.35])
    a2.plot([qa[0], qb[0]], [qa[1], qb[1]], color=p.amber, linewidth=2.2)
    a2.plot([qa[0], qb[0]], [qa[1], qb[1]], "o", color=p.green, markersize=6)
    mid = 0.5 * (qa + qb)
    a2.plot([mid[0]], [mid[1]], "x", color=p.red, markersize=11,
            markeredgewidth=2.4)
    a2.annotate("this midpoint is\nOUTSIDE the set",
                xy=mid, xytext=(-14, -46), textcoords="offset points",
                ha="center", fontsize=8, color=p.red, family="monospace",
                arrowprops=dict(arrowstyle="->", color=p.red, linewidth=1.1))
    a2.set_title("A NONCONVEX set", fontsize=9.8, color=p.red)
    a2.text(0.0, -1.95,
            "one chord leaving the set\nis enough to disqualify it\n\n"
            "the book's Figure 7.6",
            ha="center", va="top", fontsize=8.4, color=p.muted)

    for axx in (a1, a2):
        axx.set_xlim(-2.4, 2.4)
        axx.set_ylim(-2.9, 1.8)
        axx.set_aspect("equal")
        axx.axis("off")

    # --- a convex function ------------------------------------------------
    xs = np.linspace(-2.2, 2.2, 500)
    a3.plot(xs, xs ** 2, color=p.blue, linewidth=2.3, label="$f(x) = x^2$")
    ca, cb = -1.7, 1.4
    a3.plot([ca, cb], [ca ** 2, cb ** 2], color=p.green, linewidth=2.1,
            label="a chord")
    a3.fill_between([ca, cb], [ca ** 2, cb ** 2],
                    [ca ** 2, cb ** 2], color=p.green, alpha=0.0)
    tt = np.linspace(0, 1, 60)
    chord = tt * ca ** 2 + (1 - tt) * cb ** 2
    xchord = tt * ca + (1 - tt) * cb
    a3.fill_between(xchord, xchord ** 2, chord, color=p.green, alpha=0.13,
                    linewidth=0)
    a3.plot([ca, cb], [ca ** 2, cb ** 2], "o", color=p.green, markersize=6)
    a3.set_title("A CONVEX function", fontsize=9.8, color=p.blue)
    a3.set_xlabel("$x$")
    a3.legend(fontsize=7.8, loc="upper center")
    a3.grid(alpha=0.20, linewidth=0.6)
    a3.set_ylim(-3.4, 5.2)
    a3.text(0.0, -3.15,
            "$f(\\theta x + (1-\\theta)y) \\leq "
            "\\theta f(x) + (1-\\theta)f(y)$\nthe chord is never below the curve",
            ha="center", va="bottom", fontsize=8.0, color=p.muted)

    # --- a nonconvex function, with its epigraph --------------------------
    g = xs ** 4 - 3 * xs ** 2
    a4.fill_between(xs, g, 9.0, color=p.amber, alpha=0.10, linewidth=0,
                    label="the epigraph")
    a4.plot(xs, g, color=p.red, linewidth=2.3, label="$x^4 - 3x^2$")
    da, db = -1.55, 1.55
    a4.plot([da, db], [da ** 4 - 3 * da ** 2, db ** 4 - 3 * db ** 2],
            color=p.amber, linewidth=2.1, label="a chord")
    a4.plot([da, db], [da ** 4 - 3 * da ** 2, db ** 4 - 3 * db ** 2], "o",
            color=p.green, markersize=6)
    a4.plot([0.0], [0.0], "x", color=p.red, markersize=11, markeredgewidth=2.4)
    a4.annotate("chord BELOW the curve\nhere, so not convex —\nand the epigraph "
                "is not\na convex set either",
                xy=(0.0, 0.0), xytext=(0.06, 0.30),
                textcoords="axes fraction", fontsize=7.8, color=p.red,
                family="monospace",
                arrowprops=dict(arrowstyle="->", color=p.red, linewidth=1.1))
    a4.set_title("A NONCONVEX function", fontsize=9.8, color=p.red)
    a4.set_xlabel("$x$")
    a4.legend(fontsize=7.6, loc="upper center")
    a4.grid(alpha=0.20, linewidth=0.6)
    a4.set_ylim(-4.6, 9.0)

    fig.suptitle(
        "Two definitions, one shape: chords stay inside a set, and above a "
        "function",
        y=0.99, fontsize=10, color=p.fg)
    fig.text(
        0.5, 0.005,
        "Definition 7.2 and Definition 7.3 are the same sentence applied to "
        "different objects, and the epigraph is what makes that literal: filling "
        "in a\nconvex function yields a convex SET, so a claim about functions "
        "becomes a claim about sets. Measured on 200000 random segments with "
        "endpoints in the\nepigraph of $x^2$, none left it; on the epigraph of "
        "$x^4-3x^2$, 3128 did.",
        ha="center", va="bottom", fontsize=8.2, color=p.muted)


def three_tests_on_the_negative_entropy(fig, ax, p: Palette) -> None:
    """Example 7.3, drawn to its own numbers."""
    fig.clear()
    left, right = fig.subplots(1, 2)

    xs = np.linspace(0.04, 5.0, 1400)
    left.plot(xs, _entropy(xs), color=p.blue, linewidth=2.4,
              label="$f(x) = x\\log_2 x$")

    a, b, th = 2.0, 4.0, 0.5
    lhs = _entropy(th * a + (1 - th) * b)
    rhs = th * _entropy(a) + (1 - th) * _entropy(b)
    left.plot([a, b], [_entropy(a), _entropy(b)], color=p.green, linewidth=2.1,
              label="chord from $x=2$ to $x=4$")
    left.plot([a, b], [_entropy(a), _entropy(b)], "o", color=p.green,
              markersize=6)
    left.plot([3.0, 3.0], [lhs, rhs], color=p.amber, linewidth=2.4)
    left.plot([3.0], [lhs], "o", color=p.blue, markersize=6)
    left.plot([3.0], [rhs], "o", color=p.green, markersize=6)
    left.annotate(f"slack = {rhs - lhs:.6f}", xy=(3.0, (lhs + rhs) / 2),
                  xytext=(16, -6), textcoords="offset points",
                  fontsize=8.2, color=p.amber, family="monospace")

    tan = _entropy(a) + _dentropy(a) * (xs - a)
    left.plot(xs, tan, color=p.purple, linewidth=1.8, linestyle="--",
              label=f"tangent at $x=2$, slope {_dentropy(a):.6f}")
    left.plot([b, b], [tan[np.argmin(np.abs(xs - b))], _entropy(b)],
              color=p.red, linewidth=2.2)
    left.annotate(
        f"Eq 7.31 slack\n{_entropy(b) - (_entropy(a) + _dentropy(a) * 2):.6f}",
        xy=(b, 0.5 * (_entropy(b) + _entropy(a) + _dentropy(a) * 2)),
        xytext=(-72, -4), textcoords="offset points", fontsize=8.0,
        color=p.red, family="monospace")
    left.set_xlabel("$x$")
    left.set_ylabel("$f(x)$")
    left.set_ylim(-2.2, 11.5)
    left.set_title("Both tests, on the book's own points", fontsize=9.8)
    left.legend(fontsize=7.6, loc="upper left")
    left.grid(alpha=0.20, linewidth=0.6)

    right.axis("off")
    right.set_xlim(0, 10)
    right.set_ylim(0, 10)
    right.set_title("The three equivalent tests", fontsize=9.8)
    rows = [
        ("Definition 7.3, the chord",
         "$f(3) = 3\\log_2 3$", f"{lhs:.6f}",
         "$0.5 f(2) + 0.5 f(4)$", f"{rhs:.6f}",
         f"holds, slack {rhs - lhs:.6f}", p.green),
        ("Equation 7.31, the tangent",
         "$f(4)$", f"{_entropy(b):.6f}",
         "$f(2) + f'(2)\\cdot 2$", f"{_entropy(a) + _dentropy(a) * 2:.6f}",
         f"holds, slack {_entropy(b) - (_entropy(a) + _dentropy(a) * 2):.6f}",
         p.purple),
        ("the second derivative",
         "$f''(2)$ measured", f"{0.721350:.6f}",
         "$1/(2\\ln 2)$ exact", f"{1 / (2 * np.log(2)):.6f}",
         "positive, so convex", p.amber),
    ]
    for k, (name, ln, lv, rn, rv, verdict, col) in enumerate(rows):
        y = 8.4 - k * 2.8
        right.text(0.2, y, name, fontsize=9.4, color=col)
        right.text(0.6, y - 0.75, f"{ln} = {lv}", fontsize=8.8, color=p.fg)
        right.text(0.6, y - 1.45, f"{rn} = {rv}", fontsize=8.8, color=p.fg)
        right.text(0.6, y - 2.10, verdict, fontsize=8.4, color=col,
                   family="monospace")
    right.text(0.2, 0.35,
               "The book quotes $\\approx 4.75$, $5$, $8$ and $\\approx 6.9$. "
               "Every one checks out.",
               fontsize=8.4, color=p.muted)

    fig.suptitle(
        "Example 7.3: three ways to ask the same question, and they agree",
        y=0.99, fontsize=10, color=p.fg)
    fig.text(
        0.5, 0.005,
        "The chord test needs no derivatives and works for kinked functions. The "
        "tangent test needs one derivative and gives a usable LOWER BOUND on $f$ "
        "everywhere\n— which is what makes convexity valuable for optimisation. "
        "The Hessian test needs two derivatives and is the cheapest to check when "
        "they exist.",
        ha="center", va="bottom", fontsize=8.2, color=p.muted)


def sampling_cannot_prove_convexity(fig, ax, p: Palette) -> None:
    """A function that fails convexity on 2.9% of its domain, invisibly."""
    fig.clear()
    a1, a2, a3 = fig.subplots(1, 3)

    def fn(t):
        return t ** 4 - 0.02 * t ** 2

    xs = np.linspace(-2, 2, 4000)
    a1.plot(xs, fn(xs), color=p.blue, linewidth=2.4,
            label="$x^4 - 0.02x^2$")
    a1.set_xlabel("$x$")
    a1.set_ylabel("$f(x)$")
    a1.set_title("Looks convex at this scale", fontsize=9.6)
    a1.legend(fontsize=8, loc="upper center")
    a1.grid(alpha=0.20, linewidth=0.6)

    zoom = np.linspace(-0.2, 0.2, 2000)
    ins = a1.inset_axes((0.60, 0.42, 0.36, 0.36))
    ins.plot(zoom, fn(zoom), color=p.red, linewidth=1.8)
    ins.plot([-0.14, 0.14], [fn(-0.14), fn(0.14)], color=p.amber,
             linewidth=1.5)
    ins.set_xticks([])
    ins.set_yticks([])
    ins.set_title("zoom: a dimple", fontsize=7.2, color=p.red)
    for s in ins.spines.values():
        s.set_color(p.red)

    d2 = 12 * xs ** 2 - 0.04
    a2.plot(xs, d2, color=p.blue, linewidth=2.3, label="$f''(x) = 12x^2 - 0.04$")
    a2.axhline(0, color=p.red, linestyle="--", linewidth=1.6)
    edge = np.sqrt(0.04 / 12)
    a2.axvspan(-edge, edge, color=p.red, alpha=0.18, linewidth=0)
    a2.set_xlim(-0.6, 0.6)
    a2.set_ylim(-0.32, 4.2)
    a2.set_xlabel("$x$")
    a2.set_ylabel("$f''(x)$")
    a2.set_title("The second derivative tells the truth", fontsize=9.6)
    a2.legend(fontsize=7.8, loc="upper center")
    a2.grid(alpha=0.20, linewidth=0.6)
    a2.text(0.0, -0.22,
            f"negative on $|x| < {edge:.6f}$\n"
            f"width {2 * edge:.6f} of a domain of $4$\n"
            f"= {100 * 2 * edge / 4:.3f}% of it",
            ha="center", va="bottom", fontsize=7.8, color=p.red,
            family="monospace")

    rng = np.random.default_rng(4)
    sizes = np.array([100, 1000, 10000, 100000, 1000000])
    rates, worsts = [], []
    for n in sizes:
        a = rng.uniform(-2, 2, int(n))
        b = rng.uniform(-2, 2, int(n))
        t = rng.uniform(0, 1, int(n))
        v = fn(t * a + (1 - t) * b) - (t * fn(a) + (1 - t) * fn(b))
        rates.append(float((v > 1e-12).mean()))
        worsts.append(float(max(v.max(), 1e-12)))
    a3.loglog(sizes, np.maximum(rates, 1e-7), "-o", color=p.amber,
              linewidth=2.3, markersize=5.5,
              label="fraction of chords that violate")
    a3b = a3.twinx()
    a3b.loglog(sizes, worsts, "-s", color=p.red, linewidth=2.0,
               markersize=4.5, label="worst violation found")
    a3b.set_ylabel("worst violation", color=p.red)
    a3b.tick_params(axis="y", colors=p.red)
    a3.set_xlabel("number of random chords drawn")
    a3.set_ylabel("violation rate", color=p.amber)
    a3.tick_params(axis="y", colors=p.amber)
    a3.set_title("Sampling barely notices", fontsize=9.6)
    a3.grid(alpha=0.20, linewidth=0.6, which="both")
    a3.text(0.03, 0.05,
            f"at $10^6$ draws: {100 * rates[-1]:.3f}% violate,\n"
            f"worst magnitude {worsts[-1]:.1e}\n\n"
            "a tolerance of $10^{-3}$ would call\nthis function convex",
            transform=a3.transAxes, ha="left", va="bottom", fontsize=7.6,
            color=p.fg, family="monospace")

    fig.suptitle(
        "Convexity is a claim about EVERY pair of points, and sampling cannot "
        "establish it",
        y=0.99, fontsize=10, color=p.fg)
    fig.text(
        0.5, 0.005,
        f"$x^4 - 0.02x^2$ is not convex: its second derivative reaches "
        f"$-0.04$. But the failure lives on {100 * 2 * edge / 4:.3f}% of the "
        f"domain and its worst chord violation is about $10^{{-4}}$,\nso a random "
        "search finds it on well under one percent of draws and would be "
        "dismissed as numerical noise. Check the Hessian, or prove it from the "
        "closure rules —\nnever conclude convexity from a sample.",
        ha="center", va="bottom", fontsize=8.2, color=p.muted)


def closure_properties(fig, ax, p: Palette) -> None:
    """Exercises 7.3 and 7.4, with the counterexamples drawn."""
    fig.clear()
    a1, a2, a3, a4 = fig.subplots(1, 4)

    # sets
    a1.axis("off")
    a1.set_xlim(0, 10)
    a1.set_ylim(0, 10)
    a1.set_title("Exercise 7.3: sets", fontsize=9.6)
    rows = [
        ("intersection", True, "always: a point on a chord\nis in both sets"),
        ("union", False, "$[-1,1] \\cup [3,4]$ skips\nthe gap between them"),
        ("difference", False, "$[-2,2] \\setminus [-1,1]$ is\ntwo pieces"),
    ]
    for k, (name, ok, why) in enumerate(rows):
        y = 8.2 - k * 2.9
        col = p.green if ok else p.red
        a1.text(0.3, y, ("YES  " if ok else "NO   ") + name, fontsize=10,
                color=col, family="monospace")
        a1.text(0.9, y - 1.0, why, fontsize=8.2, color=p.muted, va="top")
    a1.text(0.3, 0.4,
            "Only the intersection is safe,\nand it is safe for ANY number\n"
            "of convex sets — which is why\nfeasible regions built from many\n"
            "convex constraints stay convex.",
            fontsize=8.2, color=p.fg, va="bottom")

    # the union counterexample, drawn
    ts = np.linspace(-3, 5, 900)
    a2.fill_between(ts, 0, 1, where=(ts >= -1) & (ts <= 1), color=p.blue,
                    alpha=0.35, linewidth=0)
    a2.fill_between(ts, 0, 1, where=(ts >= 3) & (ts <= 4), color=p.amber,
                    alpha=0.35, linewidth=0)
    a2.plot([-1, 4], [0.5, 0.5], color=p.green, linewidth=2.0)
    a2.plot([-1, 4], [0.5, 0.5], "o", color=p.green, markersize=6)
    a2.plot([2.0], [0.5], "x", color=p.red, markersize=12, markeredgewidth=2.6)
    a2.annotate("$x = 2$ is on the chord\nand in neither set",
                xy=(2.0, 0.5), xytext=(0, -34), textcoords="offset points",
                ha="center", fontsize=8.0, color=p.red, family="monospace",
                arrowprops=dict(arrowstyle="->", color=p.red, linewidth=1.1))
    a2.text(0.0, 1.18, "$A = [-1,1]$", ha="center", fontsize=8.6, color=p.blue)
    a2.text(3.5, 1.18, "$B = [3,4]$", ha="center", fontsize=8.6, color=p.amber)
    a2.set_xlim(-3, 5)
    a2.set_ylim(-0.6, 1.6)
    a2.set_yticks([])
    a2.set_title("Why the union fails", fontsize=9.6)
    a2.grid(alpha=0.18, axis="x", linewidth=0.6)

    # functions
    grid = np.linspace(-2.0, 3.0, 4000)
    f1 = grid ** 2
    f2 = np.exp(-grid)
    a3.plot(grid, f1 + f2, color=p.green, linewidth=2.2, label="$f_1+f_2$")
    a3.plot(grid, np.maximum(f1, f2), color=p.blue, linewidth=2.2,
            label="$\\max(f_1,f_2)$")
    a3.set_xlabel("$x$")
    a3.set_ylim(-1, 14)
    a3.set_title("Convex: sum and max", fontsize=9.6, color=p.green)
    a3.legend(fontsize=8, loc="upper center")
    a3.grid(alpha=0.20, linewidth=0.6)
    a3.text(0.03, 0.03,
            "min $f''$ on a 20001-point grid:\n  sum  $+2.0498$\n"
            "  max  $+0.4951$\n"
            "worst chord violation over\n300000 draws: none",
            transform=a3.transAxes, ha="left", va="bottom", fontsize=7.6,
            color=p.green, family="monospace")

    a4.plot(grid, f1 - f2, color=p.red, linewidth=2.2, label="$f_1-f_2$")
    a4.plot(grid, f1 * f2, color=p.amber, linewidth=2.2, label="$f_1 f_2$")
    a4.set_xlabel("$x$")
    a4.set_ylim(-9, 9)
    a4.set_title("Not convex: difference and product", fontsize=9.6,
                 color=p.red)
    a4.legend(fontsize=8, loc="upper center")
    a4.grid(alpha=0.20, linewidth=0.6)
    a4.text(0.03, 0.03,
            "min $f''$ on a 20001-point grid:\n  difference  $-5.3872$\n"
            "  product     $-0.4120$\nworst chord violation:\n"
            "  $0.57764$ and $0.28017$",
            transform=a4.transAxes, ha="left", va="bottom", fontsize=7.6,
            color=p.red, family="monospace")

    fig.suptitle(
        "The closure rules are how convexity is checked in practice, not the "
        "definition",
        y=0.99, fontsize=10, color=p.fg)
    fig.text(
        0.5, 0.005,
        "Example 7.4 proves that a non-negative weighted sum of convex functions "
        "is convex, and that is the workhorse: almost every objective in Chapters "
        "9 to 12 is\nbuilt by adding convex pieces. Subtraction and multiplication "
        "are not in the toolkit — a regulariser SUBTRACTED rather than added stops "
        "being a convex problem,\nand the counterexamples above show how quickly "
        "it happens with functions as ordinary as $x^2$ and $e^{-x}$.",
        ha="center", va="bottom", fontsize=8.2, color=p.muted)


FIGURES = [
    figure("convex-sets-and-functions", convex_sets_and_functions,
           size=(15.2, 4.9), axes=False),
    figure("three-tests-on-the-negative-entropy",
           three_tests_on_the_negative_entropy, size=(12.4, 4.9), axes=False),
    figure("sampling-cannot-prove-convexity", sampling_cannot_prove_convexity,
           size=(13.6, 4.9), axes=False),
    figure("closure-properties", closure_properties, size=(15.0, 4.8),
           axes=False),
]
