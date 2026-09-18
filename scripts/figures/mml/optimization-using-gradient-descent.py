"""Figures for *Optimization Using Gradient Descent*.

1. `stationary-points-and-basins` — the chapter's opening example, Equation 7.1.
   Three stationary points found exactly rather than read off the plot, the two
   basins of attraction shaded, and the watershed marked where it actually is:
   at the maximum, not at the book's conservative "x > -1".

2. `step-size-decides-everything` — iterations to reach 1e-8 against the step
   size, on Example 7.1's quadratic. The curve is a U, not a slide: the optimum
   sits at 2/(mu+L) and the count climbs steeply again just below the divergence
   threshold 2/L. Bigger is not faster.

3. `zigzag-and-conditioning` — Example 7.1's trajectory on its contours, the
   angle between successive steps (which shows the zigzag is a transient, not the
   asymptotic behaviour), and what conditioning costs on a least-squares problem.
"""

from __future__ import annotations

import numpy as np

from _style import Palette, figure

# Example 7.1's quadratic, used by two of the three figures.
A = np.array([[2.0, 1.0], [1.0, 20.0]])
B = np.array([5.0, 3.0])
XSTAR = np.linalg.solve(A, B)
EV = np.linalg.eigvalsh(A)


def _f(x):
    return 0.5 * x @ A @ x - B @ x


def _grad(x):
    return A @ x - B


def _cond_sweep(marks=(100, 1000, 10000, 100000)):
    """Example 7.2 at four condition numbers. Cached on the function object:
    `render` calls each draw once per theme, and this loop is the whole cost."""
    if getattr(_cond_sweep, "_memo", None) is not None:
        return _cond_sweep._memo
    rng = np.random.default_rng(7)
    out = []
    for kap_t in (1.0, 10.0, 100.0, 1000.0):
        m, n = 40, 8
        U, _ = np.linalg.qr(rng.standard_normal((m, n)))
        V, _ = np.linalg.qr(rng.standard_normal((n, n)))
        M = U @ np.diag(np.geomspace(1.0, 1.0 / kap_t, n)) @ V.T
        rhs = rng.standard_normal(m)
        exact = np.linalg.lstsq(M, rhs, rcond=None)[0]
        lr = 1.0 / (2 * np.linalg.eigvalsh(M.T @ M)[-1])
        x = np.zeros(n)
        xs_, ys_ = [], []
        for k in range(1, max(marks) + 1):
            x = x - lr * 2 * (M.T @ (M @ x - rhs))
            if k in marks:
                xs_.append(k)
                ys_.append(float(np.linalg.norm(x - exact)
                                 / np.linalg.norm(exact)))
        out.append((float(np.linalg.cond(M)), xs_, ys_))
    _cond_sweep._memo = out
    return out


def _quartic():
    """Equation 7.1 and its two derivatives, as polynomial objects."""
    ell = np.polynomial.Polynomial([3.0, -17.0, 5.0, 7.0, 1.0])
    return ell, ell.deriv(1), ell.deriv(2)


def stationary_points_and_basins(fig, ax, p: Palette) -> None:
    """Equation 7.1: three stationary points, two basins, one watershed."""
    fig.clear()
    left, right = fig.subplots(1, 2, width_ratios=[1.25, 1.0])

    ell, d1, d2 = _quartic()
    roots = np.sort(d1.roots().real)
    xs = np.linspace(-6.2, 2.2, 1400)

    left.plot(xs, ell(xs), color=p.blue, linewidth=2.4,
              label="$\\ell(x) = x^4 + 7x^3 + 5x^2 - 17x + 3$")
    left.axhline(0, color=p.grid, linewidth=1.0)

    watershed = float(roots[1])
    left.axvspan(-6.2, watershed, color=p.green, alpha=0.10, linewidth=0)
    left.axvspan(watershed, 2.2, color=p.amber, alpha=0.10, linewidth=0)

    names = ["global minimum", "maximum", "local minimum"]
    cols = [p.green, p.red, p.amber]
    for r, nm, col in zip(roots, names, cols):
        left.plot([r], [ell(r)], "o", color=col, markersize=8,
                  markeredgecolor=p.bg, markeredgewidth=1.0, zorder=6)
        va = "top" if d2(r) < 0 else "bottom"
        off = 5 if d2(r) < 0 else -5
        left.annotate(f"{nm}\n$x = {r:.6f}$\n$\\ell = {ell(r):.4f}$",
                      xy=(r, ell(r)), xytext=(0, -off * 5),
                      textcoords="offset points", ha="center", va=va,
                      fontsize=7.8, color=col, family="monospace")

    left.axvline(watershed, color=p.red, linestyle="--", linewidth=1.5)
    left.set_xlabel("value of the parameter $x$")
    left.set_ylabel("objective $\\ell(x)$")
    left.set_ylim(-62, 62)
    left.set_title("Equation 7.1, with its stationary points solved exactly",
                   fontsize=9.8)
    left.legend(fontsize=8, loc="upper left")
    left.grid(alpha=0.20, linewidth=0.6)
    left.text(-6.0, -55, "descend from anywhere here\nand you reach $-47.0748$",
              fontsize=7.8, color=p.green, family="monospace", va="bottom")
    left.text(2.0, -55, "from anywhere here\nyou reach $-3.8399$",
              fontsize=7.8, color=p.amber, family="monospace", va="bottom",
              ha="right")

    # Which basin does each start land in? Measured, not assumed. All 321 starts
    # are advanced together — a scalar loop here costs minutes per theme.
    starts = np.linspace(-6.0, 2.0, 321)
    finals = starts.copy()
    for _ in range(20000):
        finals -= 0.001 * d1(finals)
    left_basin = finals < -2

    right.scatter(starts[left_basin], finals[left_basin], s=9, color=p.green,
                  edgecolors="none", label="lands on the global minimum")
    right.scatter(starts[~left_basin], finals[~left_basin], s=9, color=p.amber,
                  edgecolors="none", label="lands on the local minimum")
    right.axvline(watershed, color=p.red, linestyle="--", linewidth=1.6)
    right.axvline(-1.0, color=p.muted, linestyle=":", linewidth=1.4)
    right.set_xlabel("starting point $x_0$")
    right.set_ylabel("where gradient descent ends up")
    right.set_title("The basin boundary, measured", fontsize=9.8)
    right.legend(fontsize=7.8, loc="center left")
    right.grid(alpha=0.20, linewidth=0.6)
    n_left = int(left_basin.sum())
    right.text(
        0.97, 0.42,
        f"the book says the right minimum wins\nfor $x > -1$ (dotted), which is "
        f"true\nbut not tight. The sharp boundary is\nthe MAXIMUM at "
        f"{watershed:.6f} (dashed).\n\n{n_left} of {starts.size} starts sampled "
        f"reach\nthe global minimum.",
        transform=right.transAxes, ha="right", va="center", fontsize=7.6,
        color=p.fg, family="monospace")

    fig.suptitle(
        "A gradient tells you which way is downhill, never which valley you are in",
        y=0.99, fontsize=10, color=p.fg)
    fig.text(
        0.5, 0.005,
        "Setting the derivative to zero gives three stationary points, and the "
        "second derivative sorts them: $\\ell'' > 0$ at the two minima, "
        "$\\ell'' < 0$ at\nthe maximum between them. The maximum is exactly the "
        "watershed — start on its left and you reach $-47.0748$, start on its right "
        "and you stop at $-3.8399$,\nwhich is $43.23$ higher. Nothing local about "
        "the gradient at either point reveals that the other exists.",
        ha="center", va="bottom", fontsize=8.2, color=p.muted)


def step_size_decides_everything(fig, ax, p: Palette) -> None:
    """Iterations against step size: a U, with a cliff on the right."""
    fig.clear()
    left, right = fig.subplots(1, 2)

    mu, L = float(EV[0]), float(EV[-1])
    ceiling = 2.0 / L
    optimum = 2.0 / (mu + L)
    x0 = np.array([-3.0, -1.0])

    def steps_to(lr, tol=1e-8, cap=200000):
        x = x0.copy()
        for k in range(cap):
            if np.linalg.norm(x - XSTAR) < tol:
                return k
            x = x - lr * _grad(x)
            if not np.all(np.isfinite(x)) or np.linalg.norm(x) > 1e12:
                return -1
        return cap

    lrs = np.concatenate([np.geomspace(2e-4, 0.0985, 90),
                          np.linspace(0.0986, 0.1035, 46)])
    counts = np.array([steps_to(lr) for lr in lrs])
    good = counts > 0

    left.loglog(lrs[good], counts[good], color=p.blue, linewidth=2.2,
                marker="o", markersize=2.6)
    left.axvline(ceiling, color=p.red, linestyle="--", linewidth=1.7)
    left.axvline(optimum, color=p.green, linestyle="--", linewidth=1.7)
    best_k = int(counts[good].min())
    best_lr = float(lrs[good][int(np.argmin(counts[good]))])
    left.plot([best_lr], [best_k], "o", color=p.green, markersize=8,
              markerfacecolor="none", markeredgewidth=1.8)
    left.text(optimum * 0.92, best_k * 4.5,
              f"optimum\n$2/(\\mu+L) = {optimum:.6f}$\n{best_k} steps",
              ha="right", fontsize=7.8, color=p.green, family="monospace")
    left.text(ceiling * 1.03, 3000,
              f"$2/L = {ceiling:.6f}$\ndiverges past here",
              ha="left", fontsize=7.8, color=p.red, family="monospace")
    left.set_xlabel("step size $\\gamma$")
    left.set_ylabel("iterations to reach $\\|x - x^*\\| < 10^{-8}$")
    left.set_title("Bigger is not faster", fontsize=9.8)
    left.grid(alpha=0.20, linewidth=0.6, which="both")

    near = 0.0997
    near_k = steps_to(near)
    left.annotate(
        f"$\\gamma = {near}$: {near_k} steps,\n"
        f"{near_k / best_k:.0f}$\\times$ the optimum",
        xy=(near, near_k), xytext=(0.02, 0.86), textcoords="axes fraction",
        fontsize=7.8, color=p.amber, family="monospace",
        arrowprops=dict(arrowstyle="->", color=p.amber, linewidth=1.1))

    # The right panel: what the iterates actually do at four step sizes.
    picks = [(0.01, p.muted, "too small"), (optimum, p.green, "optimal"),
             (near, p.amber, "just inside the ceiling"),
             (0.105, p.red, "past the ceiling")]
    for lr, col, lab in picks:
        x = x0.copy()
        errs = []
        for _ in range(60):
            errs.append(np.linalg.norm(x - XSTAR))
            x = x - lr * _grad(x)
            if not np.all(np.isfinite(x)):
                break
        errs = np.array(errs)
        right.semilogy(np.arange(errs.size), np.maximum(errs, 1e-16),
                       color=col, linewidth=2.0,
                       label=f"$\\gamma = {lr:.4f}$, {lab}")
    right.set_xlabel("iteration")
    right.set_ylabel("$\\|x_i - x^*\\|$")
    right.set_title("The same four step sizes, iterate by iterate", fontsize=9.8)
    right.legend(fontsize=7.6, loc="lower left")
    right.grid(alpha=0.20, linewidth=0.6)
    right.text(
        0.97, 0.97,
        f"$\\mu = {mu:.6f}$\n$L = {L:.6f}$\n$\\kappa = {L / mu:.6f}$\n"
        f"predicted rate $(\\kappa-1)/(\\kappa+1) = {(L / mu - 1) / (L / mu + 1):.6f}$",
        transform=right.transAxes, ha="right", va="top", fontsize=7.6,
        color=p.fg, family="monospace")

    fig.suptitle(
        "Step size on Example 7.1's quadratic: two ways to be slow and one "
        "way to fail",
        y=0.99, fontsize=10, color=p.fg)
    fig.text(
        0.5, 0.005,
        f"The theoretical optimum $2/(\\mu+L) = {optimum:.6f}$ reaches tolerance "
        f"in {best_k} iterations, and the measured best over 136 sampled step "
        f"sizes agrees.\nAt $\\gamma = {near}$ — only "
        f"{100 * (1 - near / ceiling):.1f}% below the divergence threshold — it "
        f"takes {near_k}, or {near_k / best_k:.0f} times as long. The window "
        "between fastest and\nbroken is narrow, and the failure is not gradual.",
        ha="center", va="bottom", fontsize=8.2, color=p.muted)


def zigzag_and_conditioning(fig, ax, p: Palette) -> None:
    """The trajectory, the angle between steps, and the price of conditioning."""
    fig.clear()
    a1, a2, a3 = fig.subplots(1, 3)

    gamma = 0.085
    x0 = np.array([-3.0, -1.0])
    path = [x0.copy()]
    for _ in range(40):
        path.append(path[-1] - gamma * _grad(path[-1]))
    path = np.array(path)

    g1 = np.linspace(-4.2, 4.2, 260)
    g2 = np.linspace(-2.4, 2.4, 200)
    G1, G2 = np.meshgrid(g1, g2)
    # 0.5 x^T A x - b^T x written out, so the grid is one vectorised expression
    # rather than 52000 two-by-two matmuls in a Python loop.
    Z = (G1 ** 2 + G1 * G2 + 10.0 * G2 ** 2 - 5.0 * G1 - 3.0 * G2)
    assert abs(Z[0, 0] - _f(np.array([G1[0, 0], G2[0, 0]]))) < 1e-12
    a1.contour(G1, G2, Z, levels=18, colors=p.grid, linewidths=0.9)
    a1.contour(G1, G2, Z, levels=[_f(XSTAR) + 1e-9], colors=[p.muted],
               linewidths=0.8)
    a1.plot(path[:, 0], path[:, 1], "-o", color=p.amber, linewidth=1.5,
            markersize=3.2, label=f"$\\gamma = {gamma}$")
    a1.plot([XSTAR[0]], [XSTAR[1]], "*", color=p.green, markersize=15,
            label="$x^*$", zorder=6)
    for k in range(3):
        a1.annotate(f"$x_{k}$", xy=path[k], xytext=(6, 6),
                    textcoords="offset points", fontsize=8, color=p.fg,
                    family="monospace")
    a1.set_xlabel("$x_1$")
    a1.set_ylabel("$x_2$")
    a1.set_title("Example 7.1, reproduced", fontsize=9.6)
    a1.legend(fontsize=7.8, loc="lower right")
    a1.text(
        0.03, 0.97,
        f"$x_0 = [-3, -1]$\n$x_1 = [{path[1][0]:.2f}, {path[1][1]:.2f}]$\n"
        f"$x_2 = [{path[2][0]:.2f}, {path[2][1]:.2f}]$\n"
        f"$x^* = [{XSTAR[0]:.6f}, {XSTAR[1]:.6f}]$",
        transform=a1.transAxes, ha="left", va="top", fontsize=7.4,
        color=p.fg, family="monospace")

    steps = np.diff(path, axis=0)
    angs = []
    for k in range(1, len(steps)):
        u, v = steps[k], steps[k - 1]
        c = u @ v / (np.linalg.norm(u) * np.linalg.norm(v))
        angs.append(np.degrees(np.arccos(np.clip(c, -1, 1))))
    angs = np.array(angs)
    a2.plot(np.arange(1, angs.size + 1), angs, "-o", color=p.blue,
            linewidth=2.0, markersize=3.4)
    a2.axhline(90, color=p.red, linestyle="--", linewidth=1.4)
    a2.text(angs.size * 0.97, 93, "orthogonal", ha="right", fontsize=7.8,
            color=p.red, family="monospace")
    a2.set_xlabel("iteration")
    a2.set_ylabel("angle between successive steps, degrees")
    a2.set_ylim(-6, 150)
    a2.set_title("The zigzag is a transient", fontsize=9.6)
    a2.grid(alpha=0.20, linewidth=0.6)
    a2.text(
        0.97, 0.96,
        f"first angle {angs[0]:.2f}$^\\circ$ — steps nearly reverse\n"
        f"crosses 90$^\\circ$ at iteration "
        f"{int(np.argmax(angs < 90)) + 1}\n"
        f"mean of the last 20: {angs[-20:].mean():.3f}$^\\circ$\n"
        "asymptotically the steps ALIGN, along\nthe slow eigendirection",
        transform=a2.transAxes, ha="right", va="top", fontsize=7.4,
        color=p.fg, family="monospace")

    # Example 7.2's least-squares problem at four condition numbers.
    sweep = _cond_sweep()
    worst = sweep[-1][2][-1]
    for (kap, xs_, ys_), col in zip(sweep,
                                    (p.green, p.blue, p.amber, p.red)):
        a3.loglog(xs_, np.maximum(ys_, 1e-17), "-o", color=col, linewidth=2.0,
                  markersize=4.5, label=f"$\\kappa = {kap:.0f}$")
    a3.set_xlabel("gradient descent iterations")
    a3.set_ylabel("relative error against `lstsq`")
    a3.set_title("Conditioning is the whole story", fontsize=9.6)
    a3.legend(fontsize=7.8, loc="lower left")
    a3.grid(alpha=0.20, linewidth=0.6, which="both")
    a3.text(0.97, 0.97,
            "`lstsq` solves every one of\nthese exactly, in one call",
            transform=a3.transAxes, ha="right", va="top", fontsize=7.6,
            color=p.muted, family="monospace")

    fig.suptitle(
        "Why gradient descent is slow near a minimum, and what makes it slower",
        y=0.99, fontsize=10, color=p.fg)
    fig.text(
        0.5, 0.005,
        f"Left: the book's Example 7.1 to the digit. Middle: successive steps "
        f"start almost reversed ({angs[0]:.1f}$^\\circ$) but end almost parallel "
        f"({angs[-20:].mean():.2f}$^\\circ$)\n— the famous zigzag is the opening "
        "phase, after which the iterates crawl along the flattest eigendirection. "
        "Right: at $\\kappa = 1000$ gradient descent is\nstill 84% wrong after "
        "100000 iterations of a problem `lstsq` closes exactly. This is the "
        "motivation for both momentum and the second-order methods of $\\S7.4$.",
        ha="center", va="bottom", fontsize=8.0, color=p.muted)


FIGURES = [
    figure("stationary-points-and-basins", stationary_points_and_basins,
           size=(12.6, 5.0), axes=False),
    figure("step-size-decides-everything", step_size_decides_everything,
           size=(12.2, 4.9), axes=False),
    figure("zigzag-and-conditioning", zigzag_and_conditioning,
           size=(14.2, 4.9), axes=False),
]
