"""Figures for *Orthonormal Basis*.

1. `gram-schmidt-loses-orthogonality` — the textbook algorithm is not the one
   libraries use, and this is why. Classical Gram-Schmidt, modified
   Gram-Schmidt and NumPy's Householder QR are run on the same increasingly
   ill-conditioned matrices, and the loss of orthogonality is measured as
   ||Q^T Q - I||. Classical GS degrades roughly with the square of the condition
   number; the other two do not. The mathematics in §3.8.3 is exact — the
   arithmetic is not.

2. `parseval-check` — what an orthonormal basis actually buys. The same vector
   is expanded in an ONB and in a skewed basis of the same subspace. Under the
   ONB the squared coordinates add up to the squared length, so coordinates can
   be read off one inner product at a time; under the skewed basis they do not,
   and the panel prints the size of the discrepancy.
"""

from __future__ import annotations

import numpy as np

from _style import Palette, figure


def _classical_gs(A: np.ndarray) -> np.ndarray:
    """Q from classical Gram-Schmidt: every column projected against the original."""
    n, m = A.shape
    Q = np.zeros((n, m))
    for j in range(m):
        v = A[:, j].copy()
        # The classical form: all coefficients taken against the *original* column.
        for i in range(j):
            v = v - (Q[:, i] @ A[:, j]) * Q[:, i]
        Q[:, j] = v / np.linalg.norm(v)
    return Q


def _modified_gs(A: np.ndarray) -> np.ndarray:
    """Q from modified Gram-Schmidt: each subtraction uses the running remainder."""
    n, m = A.shape
    Q = np.zeros((n, m))
    for j in range(m):
        v = A[:, j].copy()
        for i in range(j):
            v = v - (Q[:, i] @ v) * Q[:, i]
        Q[:, j] = v / np.linalg.norm(v)
    return Q


def _conditioned(n: int, kappa: float, seed: int = 5) -> np.ndarray:
    """A square matrix with exactly the requested condition number."""
    rng = np.random.default_rng(seed)
    U, _ = np.linalg.qr(rng.normal(size=(n, n)))
    V, _ = np.linalg.qr(rng.normal(size=(n, n)))
    s = np.logspace(0.0, -np.log10(kappa), n)
    return U @ np.diag(s) @ V.T


def gram_schmidt_loses_orthogonality(fig, ax, p: Palette) -> None:
    """Three ways to build an ONB, and how far each one drifts."""
    kappas = np.logspace(1.0, 14.0, 27)
    n = 8

    rows = {"classical GS": [], "modified GS": [], "NumPy QR (Householder)": []}
    for kappa in kappas:
        A = _conditioned(n, float(kappa))
        for name, Q in (
            ("classical GS", _classical_gs(A)),
            ("modified GS", _modified_gs(A)),
            ("NumPy QR (Householder)", np.linalg.qr(A)[0]),
        ):
            rows[name].append(float(np.linalg.norm(Q.T @ Q - np.eye(n), 2)))

    styles = {
        "classical GS": (p.red, "-"),
        "modified GS": (p.amber, "-"),
        "NumPy QR (Householder)": (p.green, "-"),
    }
    for name, vals in rows.items():
        colour, ls = styles[name]
        ax.plot(kappas, np.maximum(vals, 1e-18), color=colour, linestyle=ls, linewidth=2.2,
                marker="o", markersize=3.0, label=name)

    eps = float(np.finfo(float).eps)
    ax.axhline(eps, color=p.muted, linewidth=1.0, linestyle=":")
    ax.annotate(
        f"machine epsilon, {eps:.2e}",
        xy=(kappas[2], eps),
        xytext=(kappas[1], eps * 30),
        color=p.muted,
        fontsize=8,
    )
    ax.plot(kappas, np.minimum(eps * kappas**2, 1e3), color=p.blue, linewidth=1.4, linestyle="--",
            label=r"$\varepsilon\,\kappa^2$ reference")

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel(r"condition number $\kappa(A)$")
    ax.set_ylabel(r"$\|Q^\top Q - I\|_2$")
    ax.set_title(f"loss of orthogonality, {n} by {n} matrices", fontsize=10.5)
    ax.legend(loc="upper left", fontsize=8.5)

    worst = max(rows["classical GS"])
    best = max(rows["NumPy QR (Householder)"])
    ax.text(
        0.98,
        0.04,
        f"worst classical GS: {worst:.2e}\nworst Householder:  {best:.2e}",
        transform=ax.transAxes,
        color=p.fg,
        fontsize=8.5,
        family="monospace",
        ha="right",
        va="bottom",
    )


def parseval_check(fig, ax, p: Palette) -> None:
    """Squared coordinates that add up, and squared coordinates that do not."""
    fig.clear()
    axes = fig.subplots(1, 2, sharey=True)

    rng = np.random.default_rng(17)
    n, m = 24, 6

    # An ONB of an m-dimensional subspace, and a badly skewed basis of the same
    # subspace — same span, so the projections agree; different basis, so the
    # coordinates do not.
    Q, _ = np.linalg.qr(rng.normal(size=(n, m)))
    mix = np.eye(m) + 0.9 * np.triu(np.ones((m, m)), 1)
    S = Q @ mix

    x = Q @ rng.normal(size=m)  # a vector that lies in the subspace exactly
    len_sq = float(x @ x)

    # ONB: coordinates are m inner products, nothing more.
    c_onb = Q.T @ x
    # Skewed basis: a least-squares solve is unavoidable.
    c_skew = np.linalg.lstsq(S, x, rcond=None)[0]

    for a, c, B, name, colour in (
        (axes[0], c_onb, Q, "orthonormal basis", p.green),
        (axes[1], c_skew, S, "skewed basis, same span", p.red),
    ):
        a.bar(np.arange(1, m + 1), c**2, color=colour, alpha=0.75, width=0.62)
        total = float(np.sum(c**2))
        recon = float(np.linalg.norm(x - B @ c))
        a.axhline(0, color=p.grid, linewidth=0.9)
        a.set_title(
            f"{name}\n"
            + rf"$\sum c_i^2 = {total:.4f}$ vs $\|x\|^2 = {len_sq:.4f}$",
            color=colour,
            fontsize=10,
        )
        a.set_xlabel("basis vector $i$")
        a.text(
            0.5,
            0.94,
            f"gap: {abs(total - len_sq):.2e}\nreconstruction error: {recon:.2e}",
            transform=a.transAxes,
            color=p.fg,
            fontsize=8.5,
            family="monospace",
            ha="center",
            va="top",
        )

    axes[0].set_ylabel("$c_i^2$")
    fig.text(
        0.5,
        -0.03,
        "Both bases reproduce x exactly — they span the same subspace. Only the "
        "orthonormal one has coordinates whose squares add up to the squared length.",
        ha="center",
        va="top",
        color=p.muted,
        fontsize=8.5,
    )


FIGURES = [
    figure("gram-schmidt-loses-orthogonality", gram_schmidt_loses_orthogonality, size=(7.4, 5.0)),
    figure("parseval-check", parseval_check, size=(9.2, 4.2), axes=False),
]
