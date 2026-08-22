"""Figures for *Singular Value Decomposition*.

1. `svd-three-stages` — the book's Figures 4.8 and 4.9, rebuilt with the book's
   own matrix from Example 4.12. Four panels following the same anticlockwise
   order: the square grid in the domain, the grid after V-transpose has rotated
   it, the result of Sigma scaling and lifting it into R^3 where the third
   coordinate is still exactly zero, and the final rotation by U out of that
   plane. The panel measures the third coordinate before U to show it really is
   zero.

2. `evd-versus-svd` — the comparison in §4.5.3, drawn. For a non-symmetric matrix
   the eigenvectors are not orthogonal and the eigen-ellipse axes do not line up
   with the singular-value axes; for a symmetric one the two coincide exactly, as
   the spectral theorem demands. The panel measures the angle between the
   eigenvectors in each case.

3. `singular-values-from-both-grams` — the identity the book states twice: the
   nonzero eigenvalues of A-transpose A and of A A-transpose are the same, and
   their square roots are the singular values. Measured on rectangular matrices
   of several shapes, including one with more rows than columns and one with
   fewer, so the padding structure of Sigma is visible.
"""

from __future__ import annotations

import numpy as np

from _style import Palette, figure

# The book's Example 4.12 matrix: 3x2, so the SVD lifts R^2 into R^3.
A = np.array([[1.0, -0.8], [0.0, 1.0], [1.0, 0.0]])


def _grid(n: int = 21) -> np.ndarray:
    g = np.linspace(-1.0, 1.0, n)
    X, Y = np.meshgrid(g, g)
    return np.stack([X.ravel(), Y.ravel()], axis=1)


def svd_three_stages(fig, ax, p: Palette) -> None:
    """Grid, then V-transpose, then Sigma into R^3, then U."""
    fig.clear()
    a0 = fig.add_subplot(1, 4, 1)
    a1 = fig.add_subplot(1, 4, 2)
    a2 = fig.add_subplot(1, 4, 3, projection="3d")
    a3 = fig.add_subplot(1, 4, 4, projection="3d")

    U, s, Vt = np.linalg.svd(A)
    Sigma = np.zeros_like(A)
    np.fill_diagonal(Sigma, s)

    pts = _grid()
    colour = pts[:, 1]

    rot = pts @ Vt.T                       # V-transpose applied to each row
    lifted = rot @ Sigma.T                 # now in R^3
    final = lifted @ U.T

    a0.scatter(pts[:, 0], pts[:, 1], c=colour, cmap="cividis", s=6)
    a0.set_title("$\\mathcal{X} \\subset \\mathbb{R}^2$", fontsize=10)
    a1.scatter(rot[:, 0], rot[:, 1], c=colour, cmap="cividis", s=6)
    a1.set_title("$V^\\top \\mathcal{X}$: a rotation", fontsize=10)
    for a in (a0, a1):
        a.axhline(0, color=p.grid, linewidth=0.8)
        a.axvline(0, color=p.grid, linewidth=0.8)
        a.set_aspect("equal")
        a.set_xlim(-1.6, 1.6)
        a.set_ylim(-1.6, 1.6)
        a.set_xticks([])
        a.set_yticks([])
        a.grid(False)

    for a, data, title in (
        (a2, lifted, "$\\Sigma V^\\top \\mathcal{X}$: scaled,\nstill in the $x_1x_2$ plane"),
        (a3, final, "$U \\Sigma V^\\top \\mathcal{X} = A\\mathcal{X}$:\nrotated out of it"),
    ):
        a.scatter(data[:, 0], data[:, 1], data[:, 2], c=colour, cmap="cividis", s=5)
        a.set_title(title, fontsize=9.5)
        a.set_xlim(-2.0, 2.0)
        a.set_ylim(-2.0, 2.0)
        a.set_zlim(-2.0, 2.0)
        a.view_init(elev=20, azim=-62)
        a.set_facecolor(p.bg)
        for pane in (a.xaxis, a.yaxis, a.zaxis):
            pane.set_pane_color((0, 0, 0, 0))
            pane._axinfo["grid"]["color"] = p.grid
        a.tick_params(labelsize=6, colors=p.muted)

    direct = pts @ A.T
    fig.text(
        0.5, -0.03,
        f"$\\sigma = {s[0]:.4f}, {s[1]:.4f}$   "
        f"largest $|x_3|$ before $U$: {float(np.abs(lifted[:, 2]).max()):.2e}   "
        f"largest $|A\\mathcal{{X}} - U\\Sigma V^\\top\\mathcal{{X}}|$: "
        f"{float(np.abs(direct - final).max()):.2e}   "
        "(the third row of $\\Sigma$ is zero, which is why the third panel is flat)",
        ha="center", va="top", color=p.muted, fontsize=8.5,
    )


def evd_versus_svd(fig, ax, p: Palette) -> None:
    """Eigenvectors need not be orthogonal; singular vectors always are."""
    fig.clear()
    axes = fig.subplots(1, 2, sharex=True, sharey=True)

    cases = [
        (np.array([[3.0, 1.6], [0.4, 2.0]]), "non-symmetric"),
        (np.array([[3.0, 1.0], [1.0, 2.0]]), "symmetric"),
    ]

    th = np.linspace(0, 2 * np.pi, 400)
    circ = np.stack([np.cos(th), np.sin(th)], axis=1)

    for a, (M, label) in zip(axes, cases):
        img = circ @ M.T
        a.plot(circ[:, 0], circ[:, 1], color=p.muted, linewidth=1.2)
        a.plot(img[:, 0], img[:, 1], color=p.fg, linewidth=1.8)

        vals, vecs = np.linalg.eig(M)
        Uu, s, Vt = np.linalg.svd(M)

        for i, colour in enumerate((p.red, p.blue)):
            v = np.real(vecs[:, i])
            a.annotate("", xy=tuple(v * float(np.real(vals[i]))), xytext=(0, 0),
                       arrowprops=dict(arrowstyle="->", color=colour, linewidth=2.4))
        for i, colour in enumerate((p.green, p.amber)):
            u = Uu[:, i] * s[i]
            a.annotate("", xy=tuple(u), xytext=(0, 0),
                       arrowprops=dict(arrowstyle="->", color=colour, linewidth=2.0,
                                       linestyle="dashed"))

        ang_eig = np.degrees(np.arccos(np.clip(
            abs(np.real(vecs[:, 0]) @ np.real(vecs[:, 1])), -1, 1)))
        ang_sing = np.degrees(np.arccos(np.clip(abs(Uu[:, 0] @ Uu[:, 1]), -1, 1)))

        a.set_title(
            f"{label}\n"
            f"eigenvector angle {ang_eig:.2f}°, "
            f"singular vector angle {ang_sing:.2f}°",
            fontsize=9.5,
        )
        a.text(
            0.03, 0.03,
            f"$\\lambda$ = {np.real(vals[0]):.4f}, {np.real(vals[1]):.4f}\n"
            f"$\\sigma$ = {s[0]:.4f}, {s[1]:.4f}\n"
            f"$|\\lambda|$ = $\\sigma$? "
            f"{'yes' if np.allclose(np.sort(np.abs(np.real(vals))), np.sort(s)) else 'no'}",
            transform=a.transAxes, color=p.fg, fontsize=8,
            family="monospace", va="bottom",
        )
        a.axhline(0, color=p.grid, linewidth=0.8)
        a.axvline(0, color=p.grid, linewidth=0.8)
        a.set_aspect("equal")
        a.set_xlim(-4.4, 4.4)
        a.set_ylim(-4.4, 4.4)

    axes[0].set_xlabel("$x_1$")
    axes[1].set_xlabel("$x_1$")
    axes[0].set_ylabel("$x_2$")
    fig.text(
        0.5, -0.02,
        "solid arrows: eigenvectors scaled by their eigenvalues.   "
        "dashed arrows: left-singular vectors scaled by their singular values.   "
        "For a symmetric matrix the two coincide (Theorem 4.15).",
        ha="center", va="top", color=p.muted, fontsize=8.5,
    )


def singular_values_from_both_grams(fig, ax, p: Palette) -> None:
    """The nonzero spectra of A-transpose A and A A-transpose coincide."""
    rng = np.random.default_rng(13)
    shapes = [(2, 5), (3, 3), (5, 2), (6, 4), (4, 9)]

    rows = []
    for m, n in shapes:
        M = rng.normal(size=(m, n))
        ata = np.sort(np.linalg.eigvalsh(M.T @ M))[::-1]
        aat = np.sort(np.linalg.eigvalsh(M @ M.T))[::-1]
        s = np.linalg.svd(M, compute_uv=False)
        k = min(m, n)
        gap_pair = float(np.abs(ata[:k] - aat[:k]).max())
        gap_sing = float(np.abs(np.sqrt(np.maximum(ata[:k], 0)) - s).max())
        rows.append((m, n, k, ata, aat, s, gap_pair, gap_sing))

    for i, (m, n, k, ata, aat, s, gp, gs) in enumerate(rows):
        xs = np.arange(1, max(m, n) + 1)
        base = i * 3.0
        ax.plot(xs[: len(ata)], base + ata / max(ata[0], 1e-12), color=p.blue,
                linewidth=1.8, marker="o", markersize=3.6,
                label=r"eig($A^\top A$)" if i == 0 else None)
        ax.plot(xs[: len(aat)], base + aat / max(ata[0], 1e-12), color=p.amber,
                linewidth=1.2, linestyle="--", marker="s", markersize=3.0,
                label=r"eig($AA^\top$)" if i == 0 else None)
        ax.axhline(base, color=p.grid, linewidth=0.8)
        ax.text(
            max(m, n) + 0.35, base + 0.35,
            f"{m}×{n}: rank ≤ {k}\n"
            f"nonzero spectra agree to {gp:.1e}\n"
            f"$\\sqrt{{\\cdot}}$ matches $\\sigma$ to {gs:.1e}",
            color=p.fg, fontsize=7.8, va="center",
        )

    ax.set_xlabel("index of sorted eigenvalue")
    ax.set_ylabel("eigenvalue, rescaled and offset per shape")
    ax.set_xlim(0.6, 13.5)
    ax.set_yticks([i * 3.0 for i in range(len(rows))],
                  [f"{m}×{n}" for m, n, *_ in rows], fontsize=8.5)
    ax.set_title(
        "the two Gram matrices differ in size and share every nonzero eigenvalue",
        fontsize=10.5,
    )
    ax.legend(loc="upper right", fontsize=8.5)


FIGURES = [
    figure("svd-three-stages", svd_three_stages, size=(11.4, 3.4), axes=False),
    figure("evd-versus-svd", evd_versus_svd, size=(9.4, 4.6), axes=False),
    figure("singular-values-from-both-grams", singular_values_from_both_grams, size=(8.6, 5.4)),
]
