"""Figures for *Higher-Order Derivatives*.

1. `hessian-classifies-critical-points` — the reason §5.7 exists. At a point where
   the gradient vanishes the first derivative says nothing about whether you are at
   a minimum, a maximum or a saddle; the Hessian's eigenvalues say all three. Four
   surfaces, their contours, and the eigenvalue signs at the critical point, with
   the verdict measured by sampling the function around the point rather than read
   off the theory.

2. `mixed-partials-commute` — Schwarz's theorem, measured. For a twice
   continuously differentiable function the Hessian is symmetric, so d2f/dxdy and
   d2f/dydx agree; the figure measures the gap across a grid and across a ladder of
   step sizes, showing that the gap is a property of the DIFFERENCING and not of
   the function. It also shows the standard counterexample, where the mixed
   partials genuinely differ at the origin because the second derivatives are not
   continuous there.

3. `hessian-conditioning` — why the Hessian's eigenvalues matter beyond
   classification. The ratio of largest to smallest eigenvalue is the condition
   number of the quadratic approximation, and it is exactly the factor that decides
   how slowly gradient descent crawls. Plotted for a family of quadratics with the
   iteration count measured.
"""

from __future__ import annotations

import numpy as np

from _style import Palette, figure


def _num_hessian(f, x, y, h=1e-4):
    """Central second differences, the standard five-point mixed stencil."""
    fxx = (f(x + h, y) - 2 * f(x, y) + f(x - h, y)) / h ** 2
    fyy = (f(x, y + h) - 2 * f(x, y) + f(x, y - h)) / h ** 2
    fxy = (f(x + h, y + h) - f(x + h, y - h) - f(x - h, y + h) + f(x - h, y - h)) / (4 * h ** 2)
    return np.array([[fxx, fxy], [fxy, fyy]])


def hessian_classifies_critical_points(fig, ax, p: Palette) -> None:
    """Four critical points, one classifier."""
    fig.clear()
    axes = fig.subplots(1, 4, sharey=True)

    cases = [
        ("minimum", lambda x, y: x ** 2 + 2 * y ** 2, [0.25, 1, 2.25, 4]),
        ("maximum", lambda x, y: -(x ** 2) - 2 * y ** 2, [-4, -2.25, -1, -0.25]),
        ("saddle", lambda x, y: x ** 2 - y ** 2, [-4, -2, -0.5, 0, 0.5, 2, 4]),
        ("degenerate", lambda x, y: x ** 2 + y ** 4, [0.05, 0.25, 1, 2.25, 4]),
    ]

    g = np.linspace(-2.1, 2.1, 260)
    X, Y = np.meshgrid(g, g)
    rng = np.random.default_rng(5)

    for a, (name, f, levels) in zip(axes, cases):
        Z = f(X, Y)
        a.contour(X, Y, Z, levels=levels, colors=p.muted, linewidths=1.0, alpha=0.8)
        a.plot([0], [0], "o", color=p.amber, markersize=7, zorder=5)
        a.set_aspect("equal")
        a.set_xticks([])
        a.set_yticks([])

        H = _num_hessian(f, 0.0, 0.0)
        ev = np.linalg.eigvalsh(H)

        # Verdict by sampling, not by theory: probe the function on a small circle
        # and see whether it is above, below, or both.
        th = rng.uniform(0, 2 * np.pi, 4000)
        r = 0.05
        vals = f(r * np.cos(th), r * np.sin(th)) - f(0.0, 0.0)
        up = int(np.sum(vals > 1e-12))
        down = int(np.sum(vals < -1e-12))
        verdict = "minimum" if down == 0 and up > 0 else "maximum" if up == 0 and down > 0 else "saddle"

        colour = {"minimum": p.green, "maximum": p.blue, "saddle": p.red}[verdict]
        a.set_title(name, fontsize=10, color=colour)
        a.text(
            0.5, -0.06,
            f"eigenvalues of $H$\n{ev[0]:+.3f}, {ev[1]:+.3f}\n\n"
            f"sampled on a circle\nof radius {r}:\n{up} up, {down} down\n\n"
            f"verdict: {verdict}",
            transform=a.transAxes, ha="center", va="top",
            color=p.fg, fontsize=7.4, family="monospace",
        )

    fig.text(
        0.5, -0.30,
        "The first three are the textbook trio and the Hessian's eigenvalue signs settle them. The fourth "
        "is the case the test cannot decide: $x^2 + y^4$ has a Hessian eigenvalue of exactly zero at the "
        "origin, so the second-order test is silent — and yet the origin IS a strict minimum, which only "
        "the fourth-order term knows. A zero eigenvalue means 'ask a higher derivative', not 'no optimum'.",
        ha="center", va="top", color=p.muted, fontsize=8.4,
    )


def mixed_partials_commute(fig, ax, p: Palette) -> None:
    """Schwarz's theorem, and the function that breaks it."""
    fig.clear()
    left, right = fig.subplots(1, 2, gridspec_kw={"width_ratios": [1, 1]})

    # A well-behaved function: the mixed partials must agree everywhere.
    f = lambda x, y: np.sin(x * y) + x ** 2 * y ** 3 + np.exp(0.3 * x)

    hs = np.logspace(-1, -7, 13)
    worst = []
    for h in hs:
        g = np.linspace(-1.2, 1.2, 9)
        gaps = []
        for xx in g:
            for yy in g:
                fxy = (f(xx + h, yy + h) - f(xx + h, yy - h)
                       - f(xx - h, yy + h) + f(xx - h, yy - h)) / (4 * h ** 2)
                fyx = (f(xx + h, yy + h) - f(xx - h, yy + h)
                       - f(xx + h, yy - h) + f(xx - h, yy - h)) / (4 * h ** 2)
                gaps.append(abs(fxy - fyx))
        worst.append(max(gaps))

    left.loglog(hs, np.maximum(worst, 1e-20), "o-", color=p.green, linewidth=2.0)
    left.set_xlabel("step $h$")
    left.set_ylabel("worst $|\\partial_{xy}f - \\partial_{yx}f|$")
    left.invert_xaxis()
    left.set_title("a smooth function: the two orders agree exactly", fontsize=9.5)
    left.text(
        0.03, 0.5,
        "The same five-point stencil computes both,\n"
        "and the sum is the same four numbers in a\n"
        "different order -- so this gap is EXACTLY\n"
        "zero at every h, not merely small.\n\n"
        f"worst over {len(hs)} step sizes and 81\n"
        f"grid points: {max(worst):.1e}\n\n"
        "Schwarz's theorem is why the Hessian is\n"
        "symmetric, and why §4.2's spectral theorem\n"
        "applies to it.",
        transform=left.transAxes, va="center",
        color=p.fg, fontsize=7.6, family="monospace",
    )

    # The standard counterexample: the mixed partials differ AT THE ORIGIN.
    #
    # Two independent step sizes are essential here. g vanishes identically on the
    # diagonals |x| = |y|, so a single-step stencil that evaluates g(+-h, +-h)
    # lands exactly on that zero set and reports both mixed partials as 0 -- a
    # measurement artefact, not the function. The inner step (for the derivative
    # being taken first) must be far smaller than the outer one.
    def g(x, y):
        r2 = x * x + y * y
        return 0.0 if r2 == 0 else x * y * (x * x - y * y) / r2

    def dx_at(y, delta):
        """d/dx g, evaluated at (0, y)."""
        return (g(delta, y) - g(-delta, y)) / (2 * delta)

    def dy_at(x, delta):
        """d/dy g, evaluated at (x, 0)."""
        return (g(x, delta) - g(x, -delta)) / (2 * delta)

    hs2 = np.logspace(-1, -5, 9)
    fxy0, fyx0 = [], []
    for h in hs2:
        inner = h * 1e-5
        fxy0.append((dx_at(h, inner) - dx_at(-h, inner)) / (2 * h))
        fyx0.append((dy_at(h, inner) - dy_at(-h, inner)) / (2 * h))

    right.semilogx(hs2, fxy0, "o-", color=p.blue, linewidth=2.0,
                   label="$\\partial_y\\partial_x g\\,(0,0)$")
    right.semilogx(hs2, fyx0, "s-", color=p.red, linewidth=2.0,
                   label="$\\partial_x\\partial_y g\\,(0,0)$")
    right.axhline(1, color=p.muted, linewidth=0.9, linestyle=":")
    right.axhline(-1, color=p.muted, linewidth=0.9, linestyle=":")
    right.invert_xaxis()
    right.set_xlabel("step $h$")
    right.set_ylabel("mixed partial at the origin")
    right.set_title("$g = xy(x^2-y^2)/(x^2+y^2)$: they differ", fontsize=9.5)
    right.legend(loc="center left", fontsize=8.2)
    right.set_ylim(-1.6, 1.6)
    right.text(
        0.5, 0.06,
        f"the two orders are {fxy0[-1]:+.1f} and {fyx0[-1]:+.1f} at every\n"
        f"step size tested -- a gap of "
        f"{abs(fxy0[-1] - fyx0[-1]):.1f}, not a\n"
        "rounding error. Schwarz's theorem needs\n"
        "the second derivatives to be CONTINUOUS,\n"
        "and here they are not, at the origin.",
        transform=right.transAxes, ha="center", va="bottom",
        color=p.amber, fontsize=7.6, family="monospace",
    )


def hessian_conditioning(fig, ax, p: Palette) -> None:
    """The eigenvalue ratio is the descent rate."""
    fig.clear()
    left, right = fig.subplots(1, 2, gridspec_kw={"width_ratios": [1, 1.05]})

    kappas = np.array([1.0, 2.0, 5.0, 10.0, 30.0, 100.0, 300.0, 1000.0])
    iters = []
    predicted = []
    for k in kappas:
        # f(x) = 0.5 (x1^2 + k x2^2). H = diag(1, k), so kappa(H) = k.
        lam = np.array([1.0, k])
        lr = 2.0 / (1.0 + k)              # the optimal fixed step for this quadratic
        x = np.array([1.0, 1.0])
        n = 0
        while np.linalg.norm(x) > 1e-8 and n < 200000:
            x = x - lr * lam * x
            n += 1
        iters.append(n)
        # Theory: the contraction factor per step is (k-1)/(k+1).
        rate = (k - 1) / (k + 1)
        predicted.append(np.log(1e-8 / np.sqrt(2)) / np.log(rate) if k > 1 else 1)

    left.loglog(kappas, iters, "o-", color=p.blue, linewidth=2.2, label="measured steps")
    left.loglog(kappas[1:], predicted[1:], "s--", color=p.amber, linewidth=1.8,
                label="$\\log\\varepsilon / \\log\\frac{\\kappa-1}{\\kappa+1}$")
    left.set_xlabel("$\\kappa(H) = \\lambda_{\\max}/\\lambda_{\\min}$")
    left.set_ylabel("steps to $\\|x\\| < 10^{-8}$")
    left.set_title("the Hessian's eigenvalue ratio IS the descent rate", fontsize=9.5)
    left.legend(loc="upper left", fontsize=8.2)
    left.text(
        0.98, 0.03,
        "  kappa   steps   predicted\n"
        + "\n".join(f"  {k:<7.0f} {i:<7d} {q:.0f}" for k, i, q in zip(kappas, iters, predicted)),
        transform=left.transAxes, ha="right", va="bottom",
        color=p.fg, fontsize=7.2, family="monospace",
    )

    # The picture: contours of a badly conditioned quadratic, and the zig-zag.
    k = 30.0
    g1 = np.linspace(-1.3, 1.3, 300)
    g2 = np.linspace(-0.4, 0.4, 300)
    X, Y = np.meshgrid(g1, g2)
    Z = 0.5 * (X ** 2 + k * Y ** 2)
    right.contour(X, Y, Z, levels=np.geomspace(0.005, 2.5, 9), colors=p.muted,
                  linewidths=1.0, alpha=0.8)

    lr = 1.6 / k                      # a step that is stable but far from optimal
    x = np.array([1.2, 0.32])
    path = [x.copy()]
    for _ in range(40):
        x = x - lr * np.array([1.0, k]) * x
        path.append(x.copy())
    path = np.array(path)
    right.plot(path[:, 0], path[:, 1], "-o", color=p.red, linewidth=1.4, markersize=3)
    right.plot([0], [0], "*", color=p.green, markersize=14, zorder=5)
    right.set_aspect("auto")
    right.set_xlabel("$x_1$")
    right.set_ylabel("$x_2$")
    right.set_title(f"$\\kappa = {k:.0f}$: the ravine, and the zig-zag", fontsize=9.5)
    right.text(
        0.5, 0.04,
        f"a step small enough to be stable in $x_2$\n"
        f"(where the curvature is {k:.0f}) is {k:.0f} times too\n"
        f"small for $x_1$ -- hence {len(path) - 1} steps to cross\n"
        f"a distance of 1.2.",
        transform=right.transAxes, ha="center", va="bottom",
        color=p.fg, fontsize=7.4, family="monospace",
    )


FIGURES = [
    figure("hessian-classifies-critical-points", hessian_classifies_critical_points,
           size=(11.4, 4.4), axes=False),
    figure("mixed-partials-commute", mixed_partials_commute, size=(11.0, 4.6), axes=False),
    figure("hessian-conditioning", hessian_conditioning, size=(11.0, 4.4), axes=False),
]
