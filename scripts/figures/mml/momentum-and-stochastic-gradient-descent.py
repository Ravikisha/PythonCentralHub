"""Figures for *Momentum and Stochastic Gradient Descent*.

1. `momentum-beats-conditioning` — the reason momentum exists. Plain gradient
   descent needs O(kappa) iterations; heavy ball needs O(sqrt(kappa)). Measured
   over four decades of condition number, and the speedup grows exactly as the
   theory says it should.

2. `what-momentum-does-to-the-path` — the same trajectory with and without a
   memory term, plus a sweep over alpha showing that momentum has its own
   sweet spot and its own instability. The headline: the heavy-ball step size is
   16% ABOVE the ceiling where plain gradient descent diverges.

3. `minibatch-noise` — the claim SGD rests on. A mini-batch gradient is an
   unbiased estimate of the full gradient, and the spread of a single estimate
   falls as 1/sqrt(B) — but only with the finite-population correction, which is
   what makes the noise hit exactly zero at B = N rather than merely small.
"""

from __future__ import annotations

import numpy as np

from _style import Palette, figure

A7 = np.array([[2.0, 1.0], [1.0, 20.0]])
B7 = np.array([5.0, 3.0])
XSTAR = np.linalg.solve(A7, B7)
MU, L = (float(v) for v in np.linalg.eigvalsh(A7))


def _heavy(A, b, xstar, x0, gamma, alpha, tol=1e-8, cap=200000):
    """Equations 7.11 and 7.12. alpha = 0 recovers plain gradient descent."""
    x = np.asarray(x0, dtype=float).copy()
    dx = np.zeros_like(x)
    for k in range(cap):
        if np.linalg.norm(x - xstar) < tol:
            return k
        dx = alpha * dx - gamma * (A @ x - b)
        x = x + dx
        if not np.all(np.isfinite(x)) or np.linalg.norm(x) > 1e12:
            return -1
    return cap


def _hb_params(mu, ell):
    gamma = 4.0 / (np.sqrt(mu) + np.sqrt(ell)) ** 2
    alpha = ((np.sqrt(ell) - np.sqrt(mu)) / (np.sqrt(ell) + np.sqrt(mu))) ** 2
    return gamma, alpha


def _scaling_sweep():
    """Steps to tolerance for GD and heavy ball across condition numbers."""
    if getattr(_scaling_sweep, "_memo", None) is not None:
        return _scaling_sweep._memo
    kappas = np.array([3.0, 10.0, 30.0, 100.0, 300.0, 1000.0, 3000.0, 10000.0])
    gd, hb = [], []
    for kap in kappas:
        A = np.diag([1.0, kap])
        b = np.zeros(2)
        zero = np.zeros(2)
        x0 = np.array([1.0, 1.0])
        gd.append(_heavy(A, b, zero, x0, 2.0 / (1.0 + kap), 0.0))
        g, a = _hb_params(1.0, kap)
        hb.append(_heavy(A, b, zero, x0, g, a))
    _scaling_sweep._memo = (kappas, np.array(gd), np.array(hb))
    return _scaling_sweep._memo


def _noise_sweep():
    """Spread of a mini-batch gradient against batch size, sampled without
    replacement so the finite-population correction is visible."""
    if getattr(_noise_sweep, "_memo", None) is not None:
        return _noise_sweep._memo
    rng = np.random.default_rng(0)
    N, D = 2000, 5
    X = rng.standard_normal((N, D))
    w = rng.standard_normal(D)
    y = X @ w + 0.5 * rng.standard_normal(N)
    theta = rng.standard_normal(D)
    g_full = 2 * X.T @ (X @ theta - y)
    sizes = np.array([1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 1600, 2000])
    sds, biases = [], []
    for bsz in sizes:
        trials = 3000
        acc = np.zeros(D)
        sq = 0.0
        for _ in range(trials):
            idx = rng.choice(N, int(bsz), replace=False)
            gb = 2 * (N / bsz) * X[idx].T @ (X[idx] @ theta - y[idx])
            acc += gb
            sq += float(np.linalg.norm(gb - g_full) ** 2)
        sds.append(np.sqrt(sq / trials))
        biases.append(float(np.linalg.norm(acc / trials - g_full)))
    _noise_sweep._memo = (N, sizes, np.array(sds), np.array(biases),
                          float(np.linalg.norm(g_full)))
    return _noise_sweep._memo


def momentum_beats_conditioning(fig, ax, p: Palette) -> None:
    """O(kappa) against O(sqrt kappa), measured over four decades."""
    fig.clear()
    left, right = fig.subplots(1, 2)

    kappas, gd, hb = _scaling_sweep()

    left.loglog(kappas, gd, "-o", color=p.blue, linewidth=2.3, markersize=5,
                label="gradient descent, $\\gamma = 2/(\\mu+L)$")
    left.loglog(kappas, hb, "-s", color=p.green, linewidth=2.3, markersize=5,
                label="heavy ball, Eq 7.11 with $\\gamma, \\alpha$ from $\\kappa$")
    ref_k = kappas / kappas[0] * gd[0]
    ref_s = np.sqrt(kappas / kappas[0]) * hb[0]
    left.loglog(kappas, ref_k, ":", color=p.blue, linewidth=1.4,
                label="slope $\\kappa$")
    left.loglog(kappas, ref_s, ":", color=p.green, linewidth=1.4,
                label="slope $\\sqrt{\\kappa}$")
    left.set_xlabel("condition number $\\kappa = L/\\mu$")
    left.set_ylabel("iterations to $10^{-8}$")
    left.set_title("Two different scaling laws", fontsize=10)
    left.legend(fontsize=7.6, loc="upper left")
    left.grid(alpha=0.20, linewidth=0.6, which="both")

    right.semilogx(kappas, gd / np.maximum(hb, 1), "-o", color=p.amber,
                   linewidth=2.4, markersize=5.5, label="measured speedup")
    right.semilogx(kappas, np.sqrt(kappas), ":", color=p.muted, linewidth=1.8,
                   label="$\\sqrt{\\kappa}$")
    for k, g_, h_ in zip(kappas, gd, hb):
        if k in (10.0, 1000.0, 10000.0):
            right.annotate(f"$\\kappa={k:.0f}$: {g_} vs {h_}",
                           xy=(k, g_ / h_), xytext=(0, -16),
                           textcoords="offset points", ha="center",
                           fontsize=7.6, color=p.fg, family="monospace")
    right.set_xlabel("condition number $\\kappa$")
    right.set_ylabel("iterations saved, as a factor")
    right.set_title("What the memory term buys", fontsize=10)
    right.legend(fontsize=8, loc="upper left")
    right.grid(alpha=0.20, linewidth=0.6, which="both")

    fig.suptitle(
        "Momentum does not tweak gradient descent — it changes its complexity",
        y=0.99, fontsize=10, color=p.fg)
    fig.text(
        0.5, 0.005,
        f"Plain gradient descent on a quadratic needs iterations proportional to "
        f"$\\kappa$; heavy ball needs $\\sqrt{{\\kappa}}$. Measured at "
        f"$\\kappa = 10^4$: {gd[-1]} iterations against {hb[-1]}, a factor of "
        f"{gd[-1] / hb[-1]:.0f}.\nThe two dotted reference lines are pure slopes "
        "anchored at the left-hand point, so the agreement is in the exponent "
        "rather than a fitted constant.",
        ha="center", va="bottom", fontsize=8.2, color=p.muted)


def what_momentum_does_to_the_path(fig, ax, p: Palette) -> None:
    """The path, the alpha sweep, and the step size GD cannot survive."""
    fig.clear()
    a1, a2, a3 = fig.subplots(1, 3)

    ceiling = 2.0 / L
    g_hb, a_hb = _hb_params(MU, L)
    x0 = np.array([-3.0, -1.0])

    def path(gamma, alpha, n=42):
        x = x0.copy()
        dx = np.zeros(2)
        pts = [x.copy()]
        for _ in range(n):
            dx = alpha * dx - gamma * (A7 @ x - B7)
            x = x + dx
            if not np.all(np.isfinite(x)) or np.linalg.norm(x) > 50:
                break
            pts.append(x.copy())
        return np.array(pts)

    g1 = np.linspace(-4.3, 4.3, 240)
    g2 = np.linspace(-2.5, 2.5, 180)
    G1, G2 = np.meshgrid(g1, g2)
    Z = G1 ** 2 + G1 * G2 + 10.0 * G2 ** 2 - 5.0 * G1 - 3.0 * G2
    for axx in (a1, a2):
        axx.contour(G1, G2, Z, levels=16, colors=p.grid, linewidths=0.85)
        axx.plot([XSTAR[0]], [XSTAR[1]], "*", color=p.green, markersize=14,
                 zorder=6)
        axx.set_xlabel("$x_1$")
        axx.set_xlim(-4.3, 4.3)
        axx.set_ylim(-2.5, 2.5)
    a1.set_ylabel("$x_2$")

    pg = path(2.0 / (MU + L), 0.0)
    a1.plot(pg[:, 0], pg[:, 1], "-o", color=p.blue, linewidth=1.5,
            markersize=3.0)
    n_gd = _heavy(A7, B7, XSTAR, x0, 2.0 / (MU + L), 0.0)
    a1.set_title(f"No memory: {n_gd} iterations", fontsize=9.6)
    a1.text(0.03, 0.97,
            f"$\\alpha = 0$\n$\\gamma = {2 / (MU + L):.6f}$\n"
            "the best plain descent can do",
            transform=a1.transAxes, ha="left", va="top", fontsize=7.6,
            color=p.blue, family="monospace")

    pm = path(g_hb, a_hb)
    a2.plot(pm[:, 0], pm[:, 1], "-o", color=p.green, linewidth=1.5,
            markersize=3.0)
    n_hb = _heavy(A7, B7, XSTAR, x0, g_hb, a_hb)
    a2.set_title(f"With memory: {n_hb} iterations", fontsize=9.6)
    a2.text(0.03, 0.97,
            f"$\\alpha = {a_hb:.6f}$\n$\\gamma = {g_hb:.6f}$\n"
            f"that $\\gamma$ is {100 * (g_hb / ceiling - 1):.1f}% ABOVE $2/L$",
            transform=a2.transAxes, ha="left", va="top", fontsize=7.6,
            color=p.green, family="monospace")
    a2.text(0.03, 0.06,
            "plain descent DIVERGES\nat this step size",
            transform=a2.transAxes, ha="left", va="bottom", fontsize=7.8,
            color=p.red, family="monospace")

    alphas = np.linspace(0.0, 0.99, 199)
    counts = np.array([_heavy(A7, B7, XSTAR, x0, g_hb, a) for a in alphas])
    ok = counts > 0
    a3.plot(alphas[ok], counts[ok], color=p.green, linewidth=2.2)
    if (~ok).any():
        a3.axvspan(0, alphas[ok][0], color=p.red, alpha=0.13, linewidth=0)
        a3.text(alphas[ok][0] / 2, counts[ok].max() * 0.5,
                "diverges:\ntoo little\nmomentum for\nthis $\\gamma$",
                ha="center", va="center", fontsize=7.4, color=p.red,
                family="monospace")
    best_i = int(np.argmin(counts[ok]))
    a3.plot([alphas[ok][best_i]], [counts[ok][best_i]], "o", color=p.amber,
            markersize=9, markerfacecolor="none", markeredgewidth=1.9)
    a3.axvline(a_hb, color=p.muted, linestyle="--", linewidth=1.4)
    a3.set_yscale("log")
    a3.set_xlabel("momentum coefficient $\\alpha$")
    a3.set_ylabel("iterations to $10^{-8}$")
    a3.set_title("Momentum has its own sweet spot", fontsize=9.6)
    a3.grid(alpha=0.20, linewidth=0.6, which="both")
    a3.text(
        0.97, 0.96,
        f"measured best $\\alpha = {alphas[ok][best_i]:.4f}$\n"
        f"  in {counts[ok][best_i]} iterations\n"
        f"theory $\\alpha = {a_hb:.6f}$ (dashed)\n"
        f"  gives {_heavy(A7, B7, XSTAR, x0, g_hb, a_hb)}\n"
        f"$\\alpha = 0.99$ gives "
        f"{_heavy(A7, B7, XSTAR, x0, g_hb, 0.99)}\n"
        "$\\alpha \\geq 1$ never converges",
        transform=a3.transAxes, ha="right", va="top", fontsize=7.4,
        color=p.fg, family="monospace")

    fig.suptitle(
        "One extra term, and the step-size ceiling moves",
        y=0.99, fontsize=10, color=p.fg)
    fig.text(
        0.5, 0.005,
        f"Left and middle are the same objective from the same start. Momentum "
        f"cuts {n_gd} iterations to {n_hb} — and it does so at "
        f"$\\gamma = {g_hb:.6f}$, which is\n"
        f"{100 * (g_hb / ceiling - 1):.1f}% past the $2/L = {ceiling:.6f}$ where "
        "plain descent blows up. Right: too little momentum at that step size "
        "diverges, too much oscillates,\nand the useful band is neither wide nor "
        "centred on the popular default of $0.9$.",
        ha="center", va="bottom", fontsize=8.2, color=p.muted)


def minibatch_noise(fig, ax, p: Palette) -> None:
    """Unbiased in the mean, noisy in a single draw, and the 1/sqrt(B) law."""
    fig.clear()
    left, right = fig.subplots(1, 2)

    N, sizes, sds, biases, gnorm = _noise_sweep()

    finite = sizes < N
    left.loglog(sizes[finite], sds[finite], "-o", color=p.blue, linewidth=2.3,
                markersize=5, label="measured spread of one estimate")
    naive = sds[0] / np.sqrt(sizes[finite])
    fpc = sds[0] * np.sqrt((N - sizes[finite]) / (N - 1)) / np.sqrt(sizes[finite])
    left.loglog(sizes[finite], naive, ":", color=p.muted, linewidth=1.7,
                label="$1/\\sqrt{B}$ alone")
    left.loglog(sizes[finite], fpc, "--", color=p.green, linewidth=1.9,
                label="$\\sqrt{(N-B)/(N-1)}\\,/\\,\\sqrt{B}$")
    left.plot([sizes[-1]], [max(sds[-1], 1e-9)], "v", color=p.amber,
              markersize=10)
    left.annotate(f"at $B = N = {N}$ the noise is\nexactly zero, not merely small",
                  xy=(sizes[-1], max(sds[-1], 1e-9)), xytext=(0.30, 0.10),
                  textcoords="axes fraction", fontsize=7.8, color=p.amber,
                  family="monospace",
                  arrowprops=dict(arrowstyle="->", color=p.amber, linewidth=1.1))
    left.set_xlabel("mini-batch size $B$")
    left.set_ylabel("$\\|\\hat{g}_B - \\nabla L\\|$, root mean square")
    left.set_title("How noisy is one mini-batch gradient?", fontsize=10)
    left.legend(fontsize=7.6, loc="lower left")
    left.grid(alpha=0.20, linewidth=0.6, which="both")

    rel = biases / gnorm
    right.loglog(sizes, np.maximum(rel, 1e-17), "-o", color=p.green,
                 linewidth=2.3, markersize=5,
                 label="$\\|$mean over 3000 draws $-\\ \\nabla L\\|\\,/\\,\\|\\nabla L\\|$")
    right.loglog(sizes, np.maximum(sds / gnorm, 1e-17), "-s", color=p.red,
                 linewidth=2.0, markersize=4.5,
                 label="spread of a SINGLE draw, same scale")
    right.set_xlabel("mini-batch size $B$")
    right.set_ylabel("relative to $\\|\\nabla L\\|$")
    right.set_title("Unbiased, and yet wildly noisy", fontsize=10)
    right.legend(fontsize=7.4, loc="lower left")
    right.grid(alpha=0.20, linewidth=0.6, which="both")
    right.text(
        0.97, 0.96,
        f"at $B = 1$ a single gradient is\n{sds[0] / gnorm:.1f} times the size of "
        f"the true one,\nyet its average over 3000 draws is\nwithin "
        f"{rel[0]:.1e} of it.\n\nThat gap is the entire design space:\nbias is what "
        "breaks convergence,\nvariance only slows it down.",
        transform=right.transAxes, ha="right", va="top", fontsize=7.4,
        color=p.fg, family="monospace")

    fig.suptitle(
        "Why a gradient computed from one example is good enough to descend with",
        y=0.99, fontsize=10, color=p.fg)
    fig.text(
        0.5, 0.005,
        f"Convergence needs the estimate to be UNBIASED, not accurate. At $B = 1$ "
        f"the typical error of a single mini-batch gradient is "
        f"{sds[0] / gnorm:.1f}$\\times$ the norm of the\ntrue gradient — and its "
        f"mean is right to {rel[0]:.0e}. The spread follows $1/\\sqrt{{B}}$ only "
        "once the finite-population factor is included, which is also\nwhat forces "
        "it to vanish exactly at $B = N$: a full batch is not a very good sample, "
        "it is the whole population.",
        ha="center", va="bottom", fontsize=8.2, color=p.muted)


FIGURES = [
    figure("momentum-beats-conditioning", momentum_beats_conditioning,
           size=(11.8, 4.8), axes=False),
    figure("what-momentum-does-to-the-path", what_momentum_does_to_the_path,
           size=(14.0, 4.9), axes=False),
    figure("minibatch-noise", minibatch_noise, size=(12.0, 4.9), axes=False),
]
