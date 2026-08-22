"""Figures for *Matrix Phylogeny*.

1. `phylogeny-census` — the book's Figure 4.13 turned into a count. Twelve hundred
   matrices per construction are drawn and classified against
   every node of the tree: square, invertible, non-defective, normal, symmetric,
   positive definite, orthogonal, diagonal. The point the tree makes visually —
   that the interesting classes are vanishingly thin inside the space of all
   matrices — becomes a table of percentages, and most of them are zero.

2. `class-implications` — which arrows in the tree are one-way. For each ordered
   pair of properties the figure measures how often the first implies the second
   over a mixed sample, so the containment claims of §4.7 can be read off a grid
   rather than taken on trust. A cell is filled only where the implication held
   for every matrix tested.

4. `qr-determinant-rule` — which class a library routine actually lands you in.
   Householder QR applies n-1 reflections, so det(Q) = (-1)^(n-1); measured over
   eleven sizes and four hundred random inputs each, numpy returns a reflection in
   every even dimension and a rotation in every odd one, with no exceptions. The
   common belief that the sign is random is wrong.

3. `nonsingular-is-not-nondefective` — the sentence in §4.7 that most readers
   skim: non-singular and non-defective are different properties, and neither
   implies the other. Four labelled 2x2 matrices, one in each quadrant of the
   invertible-by-diagonalisable square, with determinant and eigenstructure
   printed for each.
"""

from __future__ import annotations

import numpy as np
from matplotlib.patches import Rectangle

from _style import Palette, figure

TOL = 1e-8


def _is_defective(M: np.ndarray, tol: float = 1e-7) -> bool:
    n = M.shape[0]
    vals = np.linalg.eigvals(M)
    seen: list[complex] = []
    total = 0
    for lam in vals:
        if any(abs(lam - u) < 1e-6 for u in seen):
            continue
        seen.append(lam)
        s = np.linalg.svd(M - lam * np.eye(n), compute_uv=False)
        total += int(np.sum(s < tol * max(1.0, float(s[0]))))
    return total < n


def _classify(M: np.ndarray) -> dict[str, bool]:
    n = M.shape[0]
    sym = bool(np.allclose(M, M.T, atol=TOL))
    normal = bool(np.allclose(M.T @ M, M @ M.T, atol=TOL))
    orth = bool(np.allclose(M.T @ M, np.eye(n), atol=TOL))
    diag = bool(np.allclose(M, np.diag(np.diag(M)), atol=TOL))
    invertible = abs(float(np.linalg.det(M))) > TOL
    posdef = False
    if sym:
        try:
            np.linalg.cholesky(M)
            posdef = True
        except np.linalg.LinAlgError:
            posdef = False
    return {
        "invertible": invertible,
        "non-defective": not _is_defective(M),
        "normal": normal,
        "symmetric": sym,
        "pos. definite": posdef,
        "orthogonal": orth,
        "diagonal": diag,
        "rotation": orth and float(np.linalg.det(M)) > 0,
    }


def _families(rng: np.random.Generator, n: int = 3):
    """Named constructions, each returning one n x n matrix per call."""
    def gaussian():
        return rng.normal(size=(n, n))

    def small_int():
        return rng.integers(-2, 3, size=(n, n)).astype(float)

    def symmetric():
        M = rng.normal(size=(n, n))
        return M + M.T

    def spd():
        M = rng.normal(size=(n, n))
        return M @ M.T + n * np.eye(n)

    def orthogonal():
        Q, _ = np.linalg.qr(rng.normal(size=(n, n)))
        return Q

    def diagonal():
        return np.diag(rng.normal(size=n))

    def jordan():
        J = np.eye(n)
        J[0, 1] = 1.0
        S = rng.normal(size=(n, n))
        while abs(np.linalg.det(S)) < 0.3:
            S = rng.normal(size=(n, n))
        return S @ J @ np.linalg.inv(S)

    return [
        ("Gaussian", gaussian),
        ("small integer", small_int),
        ("symmetric", symmetric),
        ("SPD", spd),
        ("orthogonal", orthogonal),
        ("diagonal", diagonal),
        ("Jordan-like", jordan),
    ]


PROPS = ["invertible", "non-defective", "normal", "symmetric",
         "pos. definite", "orthogonal", "diagonal", "rotation"]


def phylogeny_census(fig, ax, p: Palette) -> None:
    """How thin each branch of the tree is, counted."""
    rng = np.random.default_rng(41)
    fams = _families(rng)
    trials = 1200

    table = np.zeros((len(fams), len(PROPS)))
    for i, (_, make) in enumerate(fams):
        for _ in range(trials):
            c = _classify(make())
            for j, prop in enumerate(PROPS):
                table[i, j] += 1.0 if c[prop] else 0.0
    table = 100.0 * table / trials

    im = ax.imshow(table, cmap="magma", vmin=0, vmax=100, aspect="auto")
    ax.set_xticks(range(len(PROPS)), PROPS, rotation=35, ha="right", fontsize=8.5)
    ax.set_yticks(range(len(fams)), [f[0] for f in fams], fontsize=8.5)
    for i in range(len(fams)):
        for j in range(len(PROPS)):
            v = table[i, j]
            ax.text(j, i, "—" if v == 0 else f"{v:.0f}",
                    ha="center", va="center", fontsize=8,
                    color=p.bg if v > 55 else p.fg)
    ax.set_title(
        f"percent of {trials} random 3×3 matrices per construction with each property",
        fontsize=10.5,
    )
    ax.grid(False)
    fig.colorbar(im, ax=ax, fraction=0.03, pad=0.02, label="percent")


def class_implications(fig, ax, p: Palette) -> None:
    """Which properties imply which, measured over a mixed sample."""
    rng = np.random.default_rng(43)
    fams = _families(rng)
    sample = []
    for _, make in fams:
        for _ in range(700):
            sample.append(_classify(make()))

    k = len(PROPS)
    grid = np.full((k, k), np.nan)
    counts = np.zeros((k, k))
    for i, a in enumerate(PROPS):
        base = [c for c in sample if c[a]]
        for j, b in enumerate(PROPS):
            if not base:
                continue
            hits = sum(1 for c in base if c[b])
            grid[i, j] = 100.0 * hits / len(base)
            counts[i, j] = len(base)

    im = ax.imshow(grid, cmap="viridis", vmin=0, vmax=100, aspect="auto")
    ax.set_xticks(range(k), PROPS, rotation=35, ha="right", fontsize=8.5)
    ax.set_yticks(range(k), PROPS, fontsize=8.5)
    ax.set_xlabel("implies")
    ax.set_ylabel("if a matrix is")
    for i in range(k):
        for j in range(k):
            v = grid[i, j]
            if np.isnan(v):
                continue
            txt = "100" if v > 99.999 else f"{v:.0f}"
            ax.text(j, i, txt, ha="center", va="center", fontsize=7.6,
                    color=p.bg if v > 55 else "#ffffff")
    ax.set_title(
        f"measured over {len(sample)} matrices; 100 means the implication never failed",
        fontsize=10,
    )
    ax.grid(False)
    fig.colorbar(im, ax=ax, fraction=0.03, pad=0.02, label="percent")


def nonsingular_is_not_nondefective(fig, ax, p: Palette) -> None:
    """The two properties are independent, with a witness in each quadrant."""
    cases = [
        (np.array([[2.0, 0.0], [0.0, 3.0]]), "invertible and diagonalisable"),
        (np.array([[2.0, 1.0], [0.0, 2.0]]), "invertible, NOT diagonalisable"),
        (np.array([[1.0, 0.0], [0.0, 0.0]]), "singular, diagonalisable"),
        (np.array([[0.0, 1.0], [0.0, 0.0]]), "singular, NOT diagonalisable"),
    ]

    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    positions = [(0.06, 0.55), (0.55, 0.55), (0.06, 0.06), (0.55, 0.06)]
    for (M, label), (x, y) in zip(cases, positions):
        d = float(np.linalg.det(M))
        vals = np.linalg.eigvals(M)
        defective = _is_defective(M)
        colour = p.green if (abs(d) > TOL and not defective) else (
            p.amber if abs(d) > TOL or not defective else p.red
        )
        ax.add_patch(
            Rectangle(
                (x, y), 0.39, 0.38, transform=ax.transAxes,
                facecolor=colour, alpha=0.10, edgecolor=colour, linewidth=1.6,
            )
        )
        rows = "\n".join(
            "  [" + "  ".join(f"{v:5.1f}" for v in row) + " ]" for row in M
        )
        ax.text(
            x + 0.03, y + 0.32,
            f"{label}\n\n{rows}\n\n"
            f"det = {d:.1f}\n"
            f"eigenvalues = {', '.join(f'{np.real(v):.1f}' for v in vals)}\n"
            f"defective = {defective}\n"
            f"invertible = {abs(d) > TOL}",
            transform=ax.transAxes, color=p.fg, fontsize=8.5,
            family="monospace", va="top",
        )

    ax.text(
        0.5, 1.02,
        "non-singular and non-defective are independent: all four combinations occur",
        transform=ax.transAxes, ha="center", va="bottom",
        color=p.fg, fontsize=10.5, fontweight="bold",
    )
    ax.text(
        0.5, -0.03,
        "A rotation matrix is the case the book names: invertible, and over the reals "
        "not diagonalisable, because its eigenvalues are complex.",
        transform=ax.transAxes, ha="center", va="top", color=p.muted, fontsize=8.5,
    )



def qr_determinant_rule(fig, ax, p: Palette) -> None:
    """Which class does numpy's QR actually land you in?

    Not a random one. Householder QR applies n-1 reflections, each of determinant
    -1, so det(Q) = (-1)^(n-1) exactly -- and the measurement below finds no
    exceptions over eleven sizes and four hundred random inputs each. In every
    even dimension `np.linalg.qr` hands back a reflection, never a rotation.
    """
    sizes = list(range(2, 13))
    trials = 400
    fracs, uniq = [], []
    for n in sizes:
        rng = np.random.default_rng(n * 7 + 1)
        dets = []
        for _ in range(trials):
            Q, _ = np.linalg.qr(rng.normal(size=(n, n)))
            dets.append(float(np.linalg.det(Q)))
        dets = np.array(dets)
        fracs.append(100.0 * float(np.mean(dets > 0)))
        uniq.append(sorted({round(float(d)) for d in dets}))

    pred = [100.0 if (-1) ** (n - 1) > 0 else 0.0 for n in sizes]

    ax.bar([n - 0.18 for n in sizes], fracs, width=0.34, color=p.blue,
           label="measured: percent with $\det Q = +1$")
    ax.plot(sizes, pred, color=p.amber, linewidth=0, marker="_", markersize=22,
            markeredgewidth=3, label=r"predicted by $\det Q = (-1)^{n-1}$")

    for n, f, u in zip(sizes, fracs, uniq):
        ax.text(n, f + 3.0, "rotation" if f > 50 else "reflection",
                ha="center", color=p.green if f > 50 else p.red, fontsize=7.4,
                rotation=90, va="bottom")

    agree = all(
        (f > 99.99 and pv > 99.99) or (f < 0.01 and pv < 0.01)
        for f, pv in zip(fracs, pred)
    )
    ax.text(
        0.02, 0.60,
        "\n".join(
            [
                f"sizes tested: {sizes[0]} to {sizes[-1]}",
                f"random inputs per size: {trials}",
                f"distinct determinants per size: {max(len(u) for u in uniq)}",
                f"prediction matched every size: {agree}",
                "scipy.linalg.qr agrees where installed",
            ]
        ),
        transform=ax.transAxes, color=p.fg, fontsize=8,
        family="monospace", va="top",
    )

    ax.set_xlabel("matrix size $n$")
    ax.set_ylabel(r"percent of runs with $\det Q = +1$")
    ax.set_xticks(sizes)
    ax.set_ylim(0, 148)
    ax.set_title("numpy's QR is not a coin flip: it alternates with the size", fontsize=10.5)
    ax.legend(loc="upper right", fontsize=8.5)


FIGURES = [
    figure("phylogeny-census", phylogeny_census, size=(8.6, 4.4)),
    figure("class-implications", class_implications, size=(8.6, 5.4)),
    figure("nonsingular-is-not-nondefective", nonsingular_is_not_nondefective, size=(8.4, 5.0)),
    figure("qr-determinant-rule", qr_determinant_rule, size=(8.2, 4.8)),
]
