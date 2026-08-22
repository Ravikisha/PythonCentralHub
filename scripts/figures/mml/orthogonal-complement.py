"""Figures for *Orthogonal Complement*.

1. `pythagoras-in-five-dimensions` — the split x = p + q into a component in U
   and a component in U-perp is not merely unique, it is Pythagorean. Four
   thousand random vectors in R^5 are split against a fixed two-dimensional
   subspace and the two squared parts are plotted against the squared whole. The
   points sit on the diagonal, and the panel prints the largest deviation over
   the whole sample, which is at the level of floating-point noise.

2. `plane-and-normal` — the dimension count made concrete. A plane through the
   origin in R^3 with its normal direction drawn, the projection of one vector
   onto both parts, and the distance from the vector to the plane computed twice:
   once by the closed form and once by brute-force search over the plane. The two
   agree, which is what makes the closed form worth trusting.

3. `complement-is-three-pixels` — an orthogonal complement with a completely
   concrete description. The centred handwritten-digit matrix has rank 61 out of
   64, so its orthogonal complement in pixel space is 3-dimensional; and it turns
   out to be spanned exactly by the coordinate axes of the three pixels that are
   zero in every one of the 1797 images. The panel measures the agreement between
   the two projectors rather than asserting it.
"""

from __future__ import annotations

import numpy as np

from _data import digits_dataset
from _style import Palette, figure

# The plane spanned by these two, in R^3, used by the second figure.
B1 = np.array([1.0, 0.6, -0.3])
B2 = np.array([0.2, 1.0, 0.7])
TARGET = np.array([0.9, -0.4, 1.6])


def _onb(vectors: list[np.ndarray]) -> np.ndarray:
    """Columns: an orthonormal basis of the span, by QR."""
    A = np.stack(vectors, axis=1)
    Q, _ = np.linalg.qr(A)
    return Q


def pythagoras_in_five_dimensions(fig, ax, p: Palette) -> None:
    """The squared parts add up to the squared whole, measured 4000 times."""
    rng = np.random.default_rng(23)
    n, m, samples = 5, 2, 4000

    Q, _ = np.linalg.qr(rng.normal(size=(n, m)))
    P = Q @ Q.T  # projector onto U
    Pc = np.eye(n) - P  # projector onto U-perp

    X = rng.normal(size=(samples, n)) * rng.uniform(0.3, 3.0, size=(samples, 1))
    inU = X @ P.T
    inUc = X @ Pc.T

    whole = np.sum(X**2, axis=1)
    parts = np.sum(inU**2, axis=1) + np.sum(inUc**2, axis=1)

    frac = np.sum(inU**2, axis=1) / whole
    sc = ax.scatter(whole, parts, c=frac, cmap="viridis", s=6, alpha=0.6, edgecolor="none")
    cb = fig.colorbar(sc, ax=ax, fraction=0.046, pad=0.03)
    cb.set_label("fraction of the length inside $U$", fontsize=8.5)

    hi = float(whole.max()) * 1.02
    ax.plot([0, hi], [0, hi], color=p.red, linewidth=1.6,
            label=r"$\|p\|^2 + \|q\|^2 = \|x\|^2$")

    dev = float(np.max(np.abs(parts - whole)))
    rel = float(np.max(np.abs(parts - whole) / whole))
    cross = float(np.max(np.abs(np.sum(inU * inUc, axis=1))))

    ax.text(
        0.03,
        0.95,
        f"vectors split: {samples}\n"
        f"largest absolute gap: {dev:.3e}\n"
        f"largest relative gap: {rel:.3e}\n"
        f"largest |<p, q>|:     {cross:.3e}\n"
        f"dim U = {m}, dim U-perp = {n - m}, sum = {n}",
        transform=ax.transAxes,
        color=p.fg,
        fontsize=9,
        family="monospace",
        va="top",
    )

    ax.set_xlabel(r"$\|x\|^2$")
    ax.set_ylabel(r"$\|p\|^2 + \|q\|^2$")
    ax.set_xlim(0, hi)
    ax.set_ylim(0, hi)
    ax.legend(loc="lower right", fontsize=8.5)


def plane_and_normal(fig, ax, p: Palette) -> None:
    """A plane, its normal, and the distance verified two ways."""
    fig.clear()
    a3 = fig.add_subplot(111, projection="3d")

    Q = _onb([B1, B2])
    P = Q @ Q.T
    proj = P @ TARGET
    resid = TARGET - proj

    # The normal direction: the third column of a full QR of [b1 b2].
    full, _ = np.linalg.qr(np.stack([B1, B2, np.cross(B1, B2)], axis=1))
    normal = full[:, 2]
    normal = normal * np.sign(normal @ resid if abs(normal @ resid) > 1e-12 else 1.0)

    # The plane as a patch spanned by the ONB.
    g = np.linspace(-1.9, 1.9, 2)
    S, T = np.meshgrid(g, g)
    surface = S[..., None] * Q[:, 0] + T[..., None] * Q[:, 1]
    a3.plot_surface(
        surface[..., 0], surface[..., 1], surface[..., 2],
        color=p.green, alpha=0.22, edgecolor=p.green, linewidth=0.5,
    )

    def arrow(vec, colour, label, width=2.6):
        a3.plot([0, vec[0]], [0, vec[1]], [0, vec[2]], color=colour, linewidth=width)
        a3.text(vec[0] * 1.06, vec[1] * 1.06, vec[2] * 1.06, label, color=colour, fontsize=9)

    arrow(B1, p.blue, "$b_1$", 2.0)
    arrow(B2, p.blue, "$b_2$", 2.0)
    arrow(TARGET, p.amber, "$x$")
    arrow(proj, p.green, r"$\pi_U(x)$")
    arrow(normal * np.linalg.norm(resid), p.purple, r"$U^\perp$")

    a3.plot(
        [proj[0], TARGET[0]], [proj[1], TARGET[1]], [proj[2], TARGET[2]],
        color=p.red, linewidth=2.2, linestyle="--",
    )

    # The distance, twice. Once from the residual, once by searching the plane.
    closed = float(np.linalg.norm(resid))
    grid = np.linspace(-3.0, 3.0, 1201)
    S2, T2 = np.meshgrid(grid, grid)
    pts = S2.ravel()[:, None] * Q[:, 0] + T2.ravel()[:, None] * Q[:, 1]
    brute = float(np.min(np.linalg.norm(pts - TARGET, axis=1)))

    a3.set_title(
        f"$d(x, U) = {closed:.6f}$ from the residual,  {brute:.6f} by search over the plane",
        fontsize=9.5,
    )
    a3.set_xlabel("$x_1$", fontsize=8)
    a3.set_ylabel("$x_2$", fontsize=8)
    a3.set_zlabel("$x_3$", fontsize=8)
    a3.set_xlim(-2, 2)
    a3.set_ylim(-2, 2)
    a3.set_zlim(-2, 2)
    a3.view_init(elev=20, azim=-58)
    a3.set_facecolor(p.bg)
    for pane in (a3.xaxis, a3.yaxis, a3.zaxis):
        pane.set_pane_color((0, 0, 0, 0))
        pane._axinfo["grid"]["color"] = p.grid
    a3.tick_params(labelsize=7, colors=p.muted)

    fig.text(
        0.5,
        0.02,
        rf"$\langle b_1, x-\pi_U(x)\rangle = {B1 @ resid:.2e}$,   "
        rf"$\langle b_2, x-\pi_U(x)\rangle = {B2 @ resid:.2e}$   "
        "(the residual is orthogonal to the whole plane, not just to one vector)",
        ha="center",
        color=p.muted,
        fontsize=8.5,
    )



def complement_is_three_pixels(fig, ax, p: Palette) -> None:
    """The orthogonal complement of a real dataset, identified exactly."""
    fig.clear()
    left, right = fig.subplots(1, 2, gridspec_kw={"width_ratios": [1.0, 1.25]})

    X, _, source = digits_dataset()
    n, d = X.shape
    Xc = X - X.mean(axis=0)
    rank = int(np.linalg.matrix_rank(Xc))
    _, sv, Vt = np.linalg.svd(Xc, full_matrices=True)

    # The complement of the row space, and the coordinate axes of the pixels that
    # are constant across every image. If the two agree, the complement has a
    # completely concrete description.
    comp = Vt[rank:]
    const = np.where(X.std(axis=0) == 0)[0]
    E = np.zeros((len(const), d))
    E[np.arange(len(const)), const] = 1.0
    gap = float(np.linalg.norm(comp.T @ comp - E.T @ E))

    side = int(round(np.sqrt(d)))
    mask = np.zeros(d)
    mask[const] = 1.0
    left.imshow(mask.reshape(side, side), cmap="inferno", vmin=0, vmax=1)
    for i in const:
        left.text(i % side, i // side, str(i), color=p.bg, fontsize=7,
                  ha="center", va="center", fontweight="bold")
    left.set_title(f"the {len(const)} pixels that are zero" + "\n" + f"in all {n} images",
                   fontsize=10)
    left.set_xticks([])
    left.set_yticks([])
    left.grid(False)

    right.semilogy(np.arange(1, d + 1), np.maximum(sv, 1e-18), color=p.blue,
                   linewidth=1.8, marker="o", markersize=2.6)
    right.axvline(rank + 0.5, color=p.amber, linewidth=1.6, linestyle="--")
    right.annotate(
        f"rank {rank}",
        xy=(rank + 0.5, sv[rank - 1]),
        xytext=(rank - 34, sv[rank - 1] * 40),
        color=p.amber,
        fontsize=9,
        arrowprops=dict(arrowstyle="->", color=p.amber, linewidth=1.1),
    )
    right.set_xlabel("index")
    right.set_ylabel("singular value")
    right.set_title("the last three are exactly zero", fontsize=10)
    right.text(
        0.03,
        0.06,
        "\n".join(
            [
                f"dim U        = {rank}",
                f"dim U-perp   = {d - rank}",
                f"sum          = {d}",
                f"constant pixels: {list(const)}",
                f"|| P_perp - P_pixels || = {gap:.3e}",
            ]
        ),
        transform=right.transAxes,
        color=p.fg,
        fontsize=8.5,
        family="monospace",
        va="bottom",
    )


FIGURES = [
    figure("pythagoras-in-five-dimensions", pythagoras_in_five_dimensions, size=(7.2, 5.2)),
    figure("plane-and-normal", plane_and_normal, size=(7.4, 6.0), axes=False),
    figure("complement-is-three-pixels", complement_is_three_pixels, size=(9.6, 4.2), axes=False),
]
