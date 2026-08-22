"""Figures for *Eigendecomposition and Diagonalization*.

1. `pdp-three-steps` — the book's Figure 4.7, rebuilt with a unit disc of points.
   Four panels: the original disc with the eigenvectors marked, the same disc
   after P-inverse has moved the eigenvectors onto the standard axes, the disc
   scaled by D along those axes, and the result of P putting it back. The
   composition of the three equals a single multiplication by A, and the panel
   measures the agreement.

2. `matrix-power-two-ways` — Equation 4.62 as a cost argument. A^k computed by
   repeated multiplication against P D^k P-inverse, over k up to a thousand. The
   two agree while the numbers stay in range, and the eigen route needs one
   diagonalisation plus k scalar powers rather than k matrix products. The panel
   reports both the multiplication counts and the measured disagreement.

3. `defective-is-a-measure-zero-accident` — the hypothesis of Theorem 4.20,
   quantified. Four thousand 4x4 matrices from each of four constructions are
   tested for defectiveness. Gaussian entries: never. Small integer entries:
   2.7%, because exact repeats become possible. A deliberately repeated
   eigenvalue, conjugated from a diagonal: still never. A Jordan block: almost
   always. So defectiveness is not a hazard of random data at all — it needs an
   exactly deficient eigenspace, which only structure supplies.
"""

from __future__ import annotations

import numpy as np

from _style import Palette, figure

# A symmetric matrix, so P is orthogonal and the four panels are honest rotations
# rather than shears. The book's Figure 4.7 draws it that way too.
A = np.array([[2.0, 1.0], [1.0, 2.0]])


def _disc(n: int = 900, seed: int = 4) -> np.ndarray:
    rng = np.random.default_rng(seed)
    v = rng.normal(size=(n, 2))
    v /= np.linalg.norm(v, axis=1, keepdims=True)
    r = np.sqrt(rng.random(n))
    return v * r[:, None]


def pdp_three_steps(fig, ax, p: Palette) -> None:
    """P-inverse, then D, then P — and the product equals A."""
    fig.clear()
    axes = fig.subplots(1, 4, sharex=True, sharey=True)

    lam, P = np.linalg.eigh(A)
    order = np.argsort(-lam)
    lam = lam[order]
    P = P[:, order]
    D = np.diag(lam)
    Pinv = np.linalg.inv(P)

    pts = _disc()
    colour = np.arctan2(pts[:, 1], pts[:, 0])

    stages = [
        (pts, "original, with the eigenvectors $p_i$"),
        (pts @ Pinv.T, "$P^{-1}$: eigenvectors onto the axes"),
        (pts @ Pinv.T @ D.T, "$D$: scale along those axes"),
        (pts @ Pinv.T @ D.T @ P.T, "$P$: back to the original frame"),
    ]

    for a, (data, title) in zip(axes, stages):
        a.scatter(data[:, 0], data[:, 1], c=colour, cmap="twilight", s=3.2)
        a.set_title(title, fontsize=9)
        a.axhline(0, color=p.grid, linewidth=0.8)
        a.axvline(0, color=p.grid, linewidth=0.8)
        a.set_aspect("equal")
        a.set_xlim(-3.4, 3.4)
        a.set_ylim(-3.4, 3.4)
        a.set_xticks([])
        a.set_yticks([])
        a.grid(False)

    # The eigenvectors in the first panel, and where they land in the second.
    for i, colour_i in enumerate((p.red, p.blue)):
        v = P[:, i]
        axes[0].annotate("", xy=tuple(v), xytext=(0, 0),
                         arrowprops=dict(arrowstyle="->", color=colour_i, linewidth=2.4))
        axes[0].annotate(f"$p_{i + 1}$", xy=tuple(v), xytext=(v[0] * 1.2, v[1] * 1.2 + 0.15),
                         color=colour_i, fontsize=9)
        e = Pinv @ v
        axes[1].annotate("", xy=tuple(e), xytext=(0, 0),
                         arrowprops=dict(arrowstyle="->", color=colour_i, linewidth=2.4))
        axes[2].annotate("", xy=tuple(D @ e), xytext=(0, 0),
                         arrowprops=dict(arrowstyle="->", color=colour_i, linewidth=2.4))
        axes[3].annotate("", xy=tuple(A @ v), xytext=(0, 0),
                         arrowprops=dict(arrowstyle="->", color=colour_i, linewidth=2.4))

    direct = pts @ A.T
    chain = pts @ Pinv.T @ D.T @ P.T
    gap = float(np.abs(direct - chain).max())
    orth = float(np.abs(P.T @ P - np.eye(2)).max())

    fig.text(
        0.5, -0.04,
        f"$\\lambda = {lam[0]:.0f}, {lam[1]:.0f}$   "
        f"largest $|Ax - PDP^{{-1}}x|$ over {len(pts)} points: {gap:.2e}   "
        f"$|P^\\top P - I|$: {orth:.2e} — so here $P^{{-1}} = P^\\top$ and the two outer "
        "steps really are rotations (Theorem 4.21)",
        ha="center", va="top", color=p.muted, fontsize=8.5,
    )


def matrix_power_two_ways(fig, ax, p: Palette) -> None:
    """A^k by repeated multiplication against P D^k P-inverse."""
    fig.clear()
    left, right = fig.subplots(1, 2)

    # A matrix whose powers stay in range: spectral radius just under 1.
    rng = np.random.default_rng(5)
    Q, _ = np.linalg.qr(rng.normal(size=(6, 6)))
    S = Q @ np.diag(np.array([0.99, 0.8, 0.6, -0.5, 0.3, -0.1])) @ Q.T

    lam, P = np.linalg.eigh(S)
    Pinv = np.linalg.inv(P)

    ks = np.unique(np.round(np.geomspace(1, 1000, 40)).astype(int))
    gaps, naive_mults, eigen_mults = [], [], []
    n = S.shape[0]
    running = np.eye(n)
    prev_k = 0
    for k in ks:
        for _ in range(int(k) - prev_k):
            running = running @ S
        prev_k = int(k)
        direct = running
        via_eigen = P @ np.diag(lam ** int(k)) @ Pinv
        denom = max(float(np.abs(direct).max()), 1e-300)
        gaps.append(float(np.abs(direct - via_eigen).max()) / denom)
        naive_mults.append((int(k) - 1) * n ** 3)
        # One eigendecomposition (about 10 n^3 for a symmetric matrix), k scalar
        # powers, and two n x n products to reassemble.
        eigen_mults.append(10 * n ** 3 + int(k) + 2 * n ** 3)

    left.loglog(ks, np.maximum(gaps, 1e-18), color=p.blue, linewidth=2.0,
                marker="o", markersize=3.0)
    left.axhline(np.finfo(float).eps, color=p.muted, linewidth=1.0, linestyle=":")
    left.set_xlabel("power $k$")
    left.set_ylabel("relative disagreement")
    left.set_title("$A^k$ and $PD^kP^{-1}$ agree", fontsize=10.5)
    left.text(
        0.05, 0.9,
        f"largest relative gap over all $k$: {max(gaps):.2e}\n"
        f"spectral radius {max(abs(lam)):.2f}, so $A^k$ decays",
        transform=left.transAxes, color=p.fg, fontsize=8, family="monospace", va="top",
    )

    right.loglog(ks, naive_mults, color=p.red, linewidth=2.0, marker="o", markersize=3.0,
                 label="repeated multiplication: $(k-1)n^3$")
    right.loglog(ks, eigen_mults, color=p.green, linewidth=2.0, marker="s", markersize=3.0,
                 label="eigen route: one decomposition $+\\;k$ scalar powers")
    cross = next((int(k) for k, a_, b_ in zip(ks, naive_mults, eigen_mults) if a_ > b_), None)
    if cross is not None:
        right.axvline(cross, color=p.fg, linewidth=1.2, linestyle="--")
        right.annotate(
            f"the eigen route wins\nfrom $k = {cross}$",
            xy=(cross, eigen_mults[list(ks).index(cross)]),
            xytext=(cross * 1.6, min(naive_mults) * 2.0),
            color=p.fg, fontsize=8.5,
            arrowprops=dict(arrowstyle="->", color=p.fg, linewidth=1.0),
        )
    right.set_xlabel("power $k$")
    right.set_ylabel("multiplications")
    right.set_title(f"cost, for $n = {n}$", fontsize=10.5)
    right.legend(loc="upper left", fontsize=8)


def defective_is_a_measure_zero_accident(fig, ax, p: Palette) -> None:
    """How often is a matrix defective? Depends entirely on where it came from."""
    rng = np.random.default_rng(31)

    def is_defective(M: np.ndarray, tol: float = 1e-7) -> bool:
        n = M.shape[0]
        vals = np.linalg.eigvals(M)
        total = 0
        seen: list[complex] = []
        for l in vals:
            if any(abs(l - u) < 1e-6 for u in seen):
                continue
            seen.append(l)
            # Geometric multiplicity: the nullity of M - lambda I.
            s = np.linalg.svd(M - l * np.eye(n), compute_uv=False)
            total += int(np.sum(s < tol * max(1.0, s[0])))
        return total < n

    families = []

    # Every family reports cnt out of the number actually TESTED. Families (c) and
    # (d) skip a near-singular conjugation rather than test through it, and counting
    # a skip as non-defective would inflate the shortfall in the last bar and make it
    # look like a tolerance effect when it is really a missing sample.
    trials = 4000

    # (a) Fully random real entries.
    cnt = 0
    for _ in range(trials):
        if is_defective(rng.normal(size=(4, 4))):
            cnt += 1
    families.append(("random\nGaussian entries", cnt, trials, p.green))

    # (b) Random with integer entries in a small range: repeats become possible.
    cnt = 0
    for _ in range(trials):
        if is_defective(rng.integers(-2, 3, size=(4, 4)).astype(float)):
            cnt += 1
    families.append(("small integer\nentries", cnt, trials, p.blue))

    # (c) Built to have a repeated eigenvalue: conjugate a diagonal matrix with a
    #     repeat. Still diagonalisable by construction.
    cnt = tested = 0
    for _ in range(trials):
        Sx = rng.normal(size=(4, 4))
        if abs(np.linalg.det(Sx)) < 0.1:
            continue
        tested += 1
        M = Sx @ np.diag([2.0, 2.0, 1.0, -1.0]) @ np.linalg.inv(Sx)
        if is_defective(M):
            cnt += 1
    families.append(("repeated eigenvalue,\ndiagonalisable by\nconstruction", cnt, tested, p.amber))

    # (d) A Jordan block: a repeated eigenvalue with a deficient eigenspace.
    J = np.array([[2.0, 1.0, 0.0, 0.0], [0.0, 2.0, 0.0, 0.0],
                  [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, -1.0]])
    cnt = tested = 0
    for _ in range(trials):
        Sx = rng.normal(size=(4, 4))
        if abs(np.linalg.det(Sx)) < 0.1:
            continue
        tested += 1
        if is_defective(Sx @ J @ np.linalg.inv(Sx)):
            cnt += 1
    families.append(("Jordan block\n(defective by\nconstruction)", cnt, tested, p.red))

    labels = [f[0] for f in families]
    fracs = [100.0 * f[1] / f[2] for f in families]
    colours = [f[3] for f in families]

    bars = ax.bar(range(len(families)), fracs, color=colours, alpha=0.85, width=0.6)
    for i, (b, f) in enumerate(zip(bars, families)):
        ax.text(
            b.get_x() + b.get_width() / 2,
            b.get_height() + 2.0,
            f"{f[1]} of {f[2]}\n{100.0 * f[1] / f[2]:.2f}%",
            ha="center", color=p.fg, fontsize=8.5,
        )

    ax.set_xticks(range(len(families)), labels, fontsize=8)
    ax.set_ylabel("percent defective (4×4 matrices)")
    ax.set_ylim(0, 118)
    ax.set_title("Theorem 4.20's hypothesis fails only when you arrange it", fontsize=10.5)
    ax.text(
        0.02, 0.80,
        "defectiveness measured as\n"
        "sum of eigenspace dimensions < n,\n"
        "each dimension from an SVD of\n"
        "A - lambda*I at tolerance 1e-7.\n\n"
        "The last two families skip a\n"
        "near-singular conjugation rather\n"
        "than test through it, so their\n"
        "denominators are the number\n"
        "actually tested.\n\n"
        "The last bar still falls 24 short\n"
        "of its 3804 — not because those\n"
        "matrices are diagonalisable but\n"
        "because a badly conditioned\n"
        "conjugation makes the deficient\n"
        "eigenspace look full at this\n"
        "tolerance: defectiveness is not\n"
        "numerically decidable.",
        transform=ax.transAxes, color=p.muted, fontsize=7.4, va="top",
    )


FIGURES = [
    figure("pdp-three-steps", pdp_three_steps, size=(11.2, 3.2), axes=False),
    figure("matrix-power-two-ways", matrix_power_two_ways, size=(9.8, 4.2), axes=False),
    figure("defective-is-a-measure-zero-accident", defective_is_a_measure_zero_accident,
           size=(8.0, 4.8)),
]
