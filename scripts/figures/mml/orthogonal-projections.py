"""Figures for *Orthogonal Projections*.

1. `least-squares-is-a-projection` — the claim at the end of §3.8.2 made
   visible. A line fitted to data by least squares, with the residual of each
   point drawn as a vertical segment, and the measured statement that X^T r is
   zero: the residual vector is orthogonal to every column of the design matrix.
   Solving an unsolvable system and projecting b onto the column space of A are
   the same computation.

2. `projection-error-vs-dimension` — the projection error of §3.8.2 as an
   objective rather than a by-product. The handwritten-digit images are projected
   onto their own best k-dimensional subspace for every k, and the measured
   reconstruction error is plotted with a reconstructed digit at four values of
   k. This is Chapter 10 in one figure, and it is built from nothing but the
   projection matrix of this section.

3. `projection-spectrum` — why P^2 = P forces the eigenvalues to be zeros and
   ones, checked numerically for a projector onto a 3-dimensional subspace of
   R^8. The rank equals the dimension of the subspace, and the trace equals the
   rank, both measured.
"""

from __future__ import annotations

import numpy as np

from _data import digits_dataset, linear_data
from _style import Palette, figure


def least_squares_is_a_projection(fig, ax, p: Palette) -> None:
    """Residuals perpendicular to the column space, measured."""
    x, y = linear_data()
    X = np.stack([np.ones_like(x), x], axis=1)

    # The projection matrix of this section, applied to the target vector.
    P = X @ np.linalg.inv(X.T @ X) @ X.T
    fitted = P @ y
    resid = y - fitted
    beta = np.linalg.lstsq(X, y, rcond=None)[0]

    ax.scatter(x, y, s=34, color=p.blue, zorder=5, label="data")
    order = np.argsort(x)
    ax.plot(x[order], fitted[order], color=p.amber, linewidth=2.4,
            label=rf"$\pi_U(y)$: fit $ {beta[0]:.4f} + {beta[1]:.4f}\,x$")
    for xi, yi, fi in zip(x, y, fitted):
        ax.plot([xi, xi], [yi, fi], color=p.red, linewidth=1.2, alpha=0.85)
    ax.scatter(x, fitted, s=18, color=p.amber, zorder=6)

    normal_eq = X.T @ resid
    ax.text(
        0.03,
        0.95,
        f"points: {len(x)}\n"
        f"squared error: {float(resid @ resid):.6f}\n"
        f"X^T r = [{normal_eq[0]:.2e}, {normal_eq[1]:.2e}]\n"
        f"||P@P - P|| = {np.linalg.norm(P @ P - P):.2e}\n"
        f"rank P = {np.linalg.matrix_rank(P)}, trace P = {np.trace(P):.6f}",
        transform=ax.transAxes,
        color=p.fg,
        fontsize=9,
        family="monospace",
        va="top",
    )

    ax.set_xlabel("$x$")
    ax.set_ylabel("$y$")
    ax.set_title("the fit is a projection; the residuals are the part it cannot reach", fontsize=10.5)
    ax.legend(loc="lower right", fontsize=8.5)


def projection_error_vs_dimension(fig, ax, p: Palette) -> None:
    """Reconstruction error against subspace dimension, on real images."""
    fig.clear()
    gs = fig.add_gridspec(2, 4, height_ratios=[1.5, 1.0], hspace=0.35, wspace=0.12)
    curve = fig.add_subplot(gs[0, :])

    X, _, source = digits_dataset()
    n, d = X.shape
    mean = X.mean(axis=0)
    Xc = X - mean

    # The best k-dimensional subspace is spanned by the leading right singular
    # vectors; the projection onto it is the same B(B^T B)^-1 B^T as everywhere
    # else in this section, which for an orthonormal B collapses to B B^T.
    _, sv, Vt = np.linalg.svd(Xc, full_matrices=False)

    ks = np.arange(0, d + 1)
    total = float(np.sum(Xc**2))
    tail = np.concatenate([[total], total - np.cumsum(sv**2)])
    errs = np.maximum(tail, 0.0) / n  # mean squared reconstruction error per image

    curve.plot(ks, errs, color=p.blue, linewidth=2.2)
    curve.set_yscale("symlog", linthresh=1e-12)
    curve.set_xlabel("dimension $k$ of the subspace projected onto")
    curve.set_ylabel("mean squared\nprojection error")
    curve.set_title(f"projection error against subspace dimension ({n} images, {d} pixels, {source})",
                    fontsize=10.5)

    picks = [1, 4, 12, 40]
    for k, colour in zip(picks, (p.red, p.amber, p.green, p.purple)):
        curve.axvline(k, color=colour, linewidth=1.2, linestyle=":")
        curve.annotate(f"k = {k}", xy=(k, errs[k]), xytext=(k + 1.5, errs[k] * 3.0),
                       color=colour, fontsize=8.5)

    # How many components to reach 90% of the variance.
    frac = np.cumsum(sv**2) / np.sum(sv**2)
    k90 = int(np.searchsorted(frac, 0.90) + 1)
    rank = int(np.linalg.matrix_rank(Xc))
    curve.text(
        0.98,
        0.92,
        f"rank of the centred data: {rank} of {d}\n"
        f"components for 90% of the variance: {k90}\n"
        f"error at k = {rank}: {errs[rank]:.2e}",
        transform=curve.transAxes,
        color=p.fg,
        fontsize=8.5,
        family="monospace",
        ha="right",
        va="top",
    )

    side = int(round(np.sqrt(d)))
    image = X[17]
    for i, (k, colour) in enumerate(zip(picks, (p.red, p.amber, p.green, p.purple))):
        a = fig.add_subplot(gs[1, i])
        B = Vt[:k].T
        recon = mean + B @ (B.T @ (image - mean))
        a.imshow(recon.reshape(side, side), cmap="gray")
        a.set_title(f"k = {k}", color=colour, fontsize=9)
        a.set_xticks([])
        a.set_yticks([])
        a.grid(False)


def projection_spectrum(fig, ax, p: Palette) -> None:
    """Eigenvalues of a projector: ones and zeros, nothing between."""
    rng = np.random.default_rng(29)
    n, m = 8, 3
    B = rng.normal(size=(n, m))
    P = B @ np.linalg.inv(B.T @ B) @ B.T

    eig = np.linalg.eigvalsh(P)[::-1]
    ax.stem(np.arange(1, n + 1), eig, linefmt="-", markerfmt="o", basefmt=" ")
    for line in ax.get_lines():
        line.set_color(p.blue)
    ax.axhline(1.0, color=p.green, linewidth=1.2, linestyle="--", label="eigenvalue 1")
    ax.axhline(0.0, color=p.red, linewidth=1.2, linestyle="--", label="eigenvalue 0")

    ax.text(
        0.5,
        0.55,
        f"P is {n} by {n}, projecting onto a {m}-dimensional subspace\n"
        f"eigenvalues: {np.array2string(eig, precision=12, suppress_small=False)}\n"
        f"how many equal 1 (to 1e-12): {int(np.sum(np.abs(eig - 1) < 1e-12))}\n"
        f"rank P = {np.linalg.matrix_rank(P)}   trace P = {np.trace(P):.12f}\n"
        f"||P - P^T|| = {np.linalg.norm(P - P.T):.2e}   "
        f"||P@P - P|| = {np.linalg.norm(P @ P - P):.2e}",
        transform=ax.transAxes,
        color=p.fg,
        fontsize=8,
        family="monospace",
        ha="center",
        va="center",
    )

    ax.set_xlabel("index")
    ax.set_ylabel("eigenvalue")
    ax.set_ylim(-0.25, 1.35)
    ax.set_title(r"$P^2 = P$ leaves no room for any other eigenvalue", fontsize=10.5)
    ax.legend(loc="upper right", fontsize=8.5)


FIGURES = [
    figure("least-squares-is-a-projection", least_squares_is_a_projection, size=(7.6, 5.0)),
    figure("projection-error-vs-dimension", projection_error_vs_dimension, size=(9.6, 5.6), axes=False),
    figure("projection-spectrum", projection_spectrum, size=(7.4, 4.4)),
]
