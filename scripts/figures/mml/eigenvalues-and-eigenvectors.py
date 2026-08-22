"""Figures for *Eigenvalues and Eigenvectors*.

1. `five-mappings` — the book's Figure 4.4, rebuilt. Five 2x2 matrices applied to
   the same grid of colour-coded points, with the real eigenvectors drawn and
   scaled by their eigenvalues, and the determinant printed. The five cases are
   chosen to cover every qualitative possibility: two distinct real eigenvalues,
   a repeated eigenvalue with a one-dimensional eigenspace, a complex pair, a
   zero eigenvalue, and a general shear-and-stretch.

2. `eigenspectrum-s-curve` — the shape of Example 4.7, on a network built here
   rather than loaded. The C. elegans connectivity matrix the book uses is not
   bundled with this site, so the figure builds a synthetic network with the same
   ingredients (local clustering plus a few long-range links), symmetrises it as
   the book does, and shows that the S-shaped eigenspectrum is a property of that
   structure rather than of the worm. A purely random graph is drawn alongside for
   contrast: its spectrum is a semicircle, not an S.

3. `power-iteration-converges` — Example 4.9's PageRank claim, measured. Repeated
   multiplication by a column-stochastic transition matrix converges to the
   eigenvector of eigenvalue 1, and the error falls geometrically at the rate
   |lambda_2 / lambda_1|. The measured slope is compared against that ratio.
"""

from __future__ import annotations

import numpy as np

from _style import Palette, figure

# The book's Figure 4.4 matrices.
A1 = np.array([[0.5, 0.0], [0.0, 2.0]])
A2 = np.array([[1.0, 0.5], [0.0, 1.0]])
A3 = np.array([[np.cos(np.pi / 6), -np.sin(np.pi / 6)], [np.sin(np.pi / 6), np.cos(np.pi / 6)]])
A4 = np.array([[1.0, -1.0], [-1.0, 1.0]])
A5 = np.array([[1.0, 0.5], [0.5, 1.0]])

MAPPINGS = [
    ("$A_1$", A1, "area preserving"),
    ("$A_2$", A2, "shear"),
    ("$A_3$", A3, "rotation by 30°"),
    ("$A_4$", A4, "collapses a dimension"),
    ("$A_5$", A5, "shear and stretch"),
]


def _grid(n: int = 20) -> np.ndarray:
    g = np.linspace(-1.0, 1.0, n)
    X, Y = np.meshgrid(g, g)
    return np.stack([X.ravel(), Y.ravel()], axis=1)


def five_mappings(fig, ax, p: Palette) -> None:
    """The book's Figure 4.4: five linear maps and their eigenstructure."""
    fig.clear()
    axes = fig.subplots(2, 5, sharex=True, sharey=True)
    pts = _grid()
    # Colour by the vertical coordinate, as the book does, so the deformation of
    # the grid is readable rather than a uniform blob.
    colour = pts[:, 1]

    for col, (name, A, note) in enumerate(MAPPINGS):
        top, bot = axes[0][col], axes[1][col]

        top.scatter(pts[:, 0], pts[:, 1], c=colour, cmap="cividis", s=3.5)
        top.set_title(f"{name}\n{note}", fontsize=9.5)

        out = pts @ A.T
        bot.scatter(out[:, 0], out[:, 1], c=colour, cmap="cividis", s=3.5)

        vals, vecs = np.linalg.eig(A)
        real = np.all(np.abs(vals.imag) < 1e-12)
        d = float(np.linalg.det(A))

        if real:
            for i in range(2):
                v = np.real(vecs[:, i])
                lam = float(np.real(vals[i]))
                c = (p.blue, p.red)[i]
                bot.annotate(
                    "", xy=tuple(1.35 * lam * v), xytext=(0, 0),
                    arrowprops=dict(arrowstyle="->", color=c, linewidth=2.0),
                )
            lam_txt = "\n".join(
                f"$\\lambda_{i + 1} = {float(np.real(vals[i])):.2f}$" for i in range(2)
            )
        else:
            lam_txt = (
                f"$\\lambda = {vals[0].real:.2f} \\pm {abs(vals[0].imag):.2f}i$\n"
                "no real eigenvector"
            )

        bot.text(
            0.03, 0.03, f"{lam_txt}\n$\\det = {d:.2f}$",
            transform=bot.transAxes, color=p.fg, fontsize=7.6, va="bottom",
        )

        for a in (top, bot):
            a.axhline(0, color=p.grid, linewidth=0.7)
            a.axvline(0, color=p.grid, linewidth=0.7)
            a.set_aspect("equal")
            a.set_xlim(-2.6, 2.6)
            a.set_ylim(-2.6, 2.6)
            a.set_xticks([])
            a.set_yticks([])
            a.grid(False)

    axes[0][0].set_ylabel("$x$", fontsize=9)
    axes[1][0].set_ylabel("$Ax$", fontsize=9)


def _small_world(n: int = 220, k: int = 4, rewire: float = 0.06, seed: int = 3) -> np.ndarray:
    """A ring lattice with a few rewired links — local clustering plus shortcuts."""
    rng = np.random.default_rng(seed)
    A = np.zeros((n, n))
    for i in range(n):
        for j in range(1, k + 1):
            A[i, (i + j) % n] = 1.0
    for i in range(n):
        for j in range(n):
            if A[i, j] and rng.random() < rewire:
                A[i, j] = 0.0
                A[i, rng.integers(n)] = 1.0
    np.fill_diagonal(A, 0.0)
    return A


def eigenspectrum_s_curve(fig, ax, p: Palette) -> None:
    """The S-shaped spectrum of a clustered network, against a random one."""
    fig.clear()
    gs = fig.add_gridspec(1, 3, width_ratios=[1.0, 1.0, 1.25], wspace=0.32)
    a0, a1, a2 = (fig.add_subplot(gs[0, i]) for i in range(3))

    n = 220
    sw = _small_world(n=n)
    sw_sym = sw + sw.T

    rng = np.random.default_rng(11)
    density = float((sw_sym > 0).mean())
    er = (rng.random((n, n)) < density / 2).astype(float)
    er_sym = er + er.T
    np.fill_diagonal(er_sym, 0.0)

    for a, M, title in ((a0, sw_sym, "clustered network"), (a1, er_sym, "random network")):
        a.imshow(M > 0, cmap="gray", interpolation="nearest")
        a.set_title(f"{title}\n{int((M > 0).sum())} edges", fontsize=9.5)
        a.set_xlabel("node index", fontsize=8)
        a.grid(False)
        a.tick_params(labelsize=7)
    a0.set_ylabel("node index", fontsize=8)

    for M, colour, label in ((sw_sym, p.amber, "clustered"), (er_sym, p.blue, "random")):
        ev = np.sort(np.linalg.eigvalsh(M))[::-1]
        a2.plot(np.arange(1, n + 1), ev, color=colour, linewidth=1.8, label=label)
    a2.axhline(0, color=p.grid, linewidth=0.9)
    a2.set_xlabel("index of sorted eigenvalue", fontsize=8.5)
    a2.set_ylabel("eigenvalue", fontsize=8.5)
    a2.set_title("eigenspectrum", fontsize=9.5)
    a2.legend(loc="upper right", fontsize=8)

    ev_sw = np.sort(np.linalg.eigvalsh(sw_sym))[::-1]
    ev_er = np.sort(np.linalg.eigvalsh(er_sym))[::-1]
    # A shape measurement rather than an assertion: rescale each spectrum to
    # [0, 1] and read its height at fixed index fractions. A straight line gives
    # roughly 0.90, 0.75, 0.50, 0.25, 0.10; a pronounced knee drops much faster
    # at the start and then flattens.
    def profile(ev: np.ndarray) -> list[float]:
        span = ev[0] - ev[-1]
        y = (ev - ev[-1]) / span
        return [float(y[int(f * len(ev))]) for f in (0.10, 0.25, 0.50, 0.75, 0.90)]

    ps, pr = profile(ev_sw), profile(ev_er)
    a2.text(
        0.04, 0.06,
        "normalised height at 10/25/50/75/90%\n"
        + "clustered " + " ".join(f"{v:.2f}" for v in ps) + "\n"
        + "random    " + " ".join(f"{v:.2f}" for v in pr) + "\n"
        + f"clustered {ev_sw[0]:.2f} to {ev_sw[-1]:.2f}\n"
        + f"random    {ev_er[0]:.2f} to {ev_er[-1]:.2f}",
        transform=a2.transAxes, color=p.fg, fontsize=7.2,
        family="monospace", va="bottom",
    )

    fig.text(
        0.5, -0.02,
        "Synthetic networks, not the C. elegans data of the book's Example 4.7 — "
        "the point is that the S-shape follows from local clustering, which the random graph lacks.",
        ha="center", va="top", color=p.muted, fontsize=8,
    )


def power_iteration_converges(fig, ax, p: Palette) -> None:
    """Example 4.9: repeated multiplication finds the dominant eigenvector."""
    fig.clear()
    left, right = fig.subplots(1, 2, gridspec_kw={"width_ratios": [1.0, 1.15]})

    # A small web: 6 pages, a few links each. Column-stochastic, so 1 is an
    # eigenvalue and the dominant eigenvector is the stationary distribution.
    links = {
        0: [1, 2],
        1: [2],
        2: [0, 3],
        3: [2, 4],
        4: [2, 5],
        5: [2, 3],
    }
    n = 6
    A = np.zeros((n, n))
    for src, dsts in links.items():
        for d in dsts:
            A[d, src] = 1.0 / len(dsts)

    vals = np.linalg.eigvals(A)
    order = np.argsort(-np.abs(vals))
    lam1, lam2 = vals[order[0]], vals[order[1]]
    ratio = abs(lam2) / abs(lam1)

    # The true stationary vector, from the eigen decomposition.
    w, V = np.linalg.eig(A)
    star = np.real(V[:, int(np.argmax(np.abs(w)))])
    star = star / star.sum()

    x = np.full(n, 1.0 / n)
    errs, iters = [], []
    for k in range(1, 61):
        x = A @ x
        x = x / x.sum()
        errs.append(float(np.linalg.norm(x - star)))
        iters.append(k)

    left.bar(np.arange(1, n + 1) - 0.2, np.full(n, 1.0 / n), width=0.38,
             color=p.muted, label="uniform start")
    left.bar(np.arange(1, n + 1) + 0.2, star, width=0.38, color=p.amber,
             label="PageRank (eigenvector of $\\lambda = 1$)")
    left.set_xlabel("page")
    left.set_ylabel("importance")
    left.set_title("the fixed point of $Ax = x$", fontsize=10.5)
    left.set_xticks(np.arange(1, n + 1))
    left.legend(loc="upper left", fontsize=8)

    right.semilogy(iters, np.maximum(errs, 1e-18), color=p.blue, linewidth=2.0,
                   marker="o", markersize=2.8, label="measured error")
    ref = errs[0] * ratio ** (np.array(iters) - 1)
    right.semilogy(iters, np.maximum(ref, 1e-18), color=p.red, linewidth=1.4,
                   linestyle="--", label=f"$|\\lambda_2/\\lambda_1|^k$ = ${ratio:.4f}^k$")
    right.set_xlabel("iterations of $x \\leftarrow Ax$")
    right.set_ylabel("distance to the eigenvector")
    right.set_title("geometric convergence at the eigenvalue ratio", fontsize=10.5)
    right.legend(loc="upper right", fontsize=8)

    # The measured decay rate, from a log-linear fit over the clean middle.
    lo, hi = 5, 35
    slope = np.polyfit(iters[lo:hi], np.log(np.maximum(errs[lo:hi], 1e-300)), 1)[0]
    right.text(
        0.04, 0.06,
        f"|lambda_1| = {abs(lam1):.6f}\n"
        f"|lambda_2| = {abs(lam2):.6f}\n"
        f"ratio      = {ratio:.6f}\n"
        f"measured   = {np.exp(slope):.6f}",
        transform=right.transAxes, color=p.fg, fontsize=8,
        family="monospace", va="bottom",
    )


FIGURES = [
    figure("five-mappings", five_mappings, size=(11.2, 4.8), axes=False),
    figure("eigenspectrum-s-curve", eigenspectrum_s_curve, size=(10.4, 3.6), axes=False),
    figure("power-iteration-converges", power_iteration_converges, size=(9.8, 4.2), axes=False),
]
