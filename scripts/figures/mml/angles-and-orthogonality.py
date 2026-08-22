"""Figures for *Angles and Orthogonality*.

1. `two-inner-products-two-angles` — the book's Example 3.7, drawn. The vectors
   (1, 1) and (-1, 1) are at ninety degrees under the dot product and at 109.5
   degrees under x^T diag(2, 1) y. Both angles are drawn on the same pair of
   arrows, with the unit set of each inner product behind them, because the arc
   is the only place where "the angle depends on the inner product" stops
   sounding like a technicality.

2. `cosine-similarity-matrix` — why the cosine and not the dot product. Nine
   short documents over a small vocabulary, with the raw dot products beside the
   cosine similarities. The dot product ranks the long documents first no matter
   what they are about; the cosine puts the topical pairs first. The two
   orderings are printed underneath, measured from the matrices above.
"""

from __future__ import annotations

import numpy as np

from _style import Palette, figure

X = np.array([1.0, 1.0])
Y = np.array([-1.0, 1.0])
DOT = np.eye(2)
DIAG = np.array([[2.0, 0.0], [0.0, 1.0]])

TERMS = ["model", "train", "loss", "recipe", "oven", "flour"]

# Three ML notes, three baking notes, and three of mixed length so that document
# length and topic are not confounded.
DOCS: list[tuple[str, list[float]]] = [
    ("ml-short", [2, 1, 1, 0, 0, 0]),
    ("ml-long", [9, 7, 6, 0, 0, 1]),
    ("ml-tiny", [1, 0, 1, 0, 0, 0]),
    ("bake-short", [0, 0, 0, 2, 1, 2]),
    ("bake-long", [0, 1, 0, 8, 6, 9]),
    ("bake-tiny", [0, 0, 0, 1, 0, 1]),
    ("mixed", [3, 2, 1, 3, 1, 2]),
    ("ml-huge", [20, 15, 14, 1, 0, 2]),
    ("bake-huge", [1, 0, 1, 18, 14, 20]),
]


def two_inner_products_two_angles(fig, ax, p: Palette) -> None:
    """The same two arrows, two different angles between them."""
    th = np.linspace(0.0, 2.0 * np.pi, 721)
    dirs = np.stack([np.cos(th), np.sin(th)], axis=1)

    for A, colour, label in (
        (DOT, p.muted, "unit set of the dot product"),
        (DIAG, p.purple, r"unit set of $\mathbf{x}^\top\mathrm{diag}(2,1)\mathbf{y}$"),
    ):
        q = np.einsum("ij,jk,ik->i", dirs, A, dirs)
        pts = dirs / np.sqrt(q)[:, None]
        ax.plot(pts[:, 0], pts[:, 1], color=colour, linewidth=1.5, linestyle="--", label=label)

    for v, name, colour in ((X, r"$\mathbf{x} = (1,1)$", p.amber), (Y, r"$\mathbf{y} = (-1,1)$", p.blue)):
        ax.annotate("", xy=tuple(v), xytext=(0, 0),
                    arrowprops=dict(arrowstyle="->", color=colour, linewidth=2.6))
        ax.annotate(name, xy=tuple(v), xytext=(v[0] + 0.06, v[1] + 0.12), color=colour, fontsize=10)

    rows = []
    for A, name, colour, radius in (
        (DOT, "dot product", p.green, 0.52),
        (DIAG, "diag(2, 1)", p.red, 0.74),
    ):
        num = float(X @ A @ Y)
        cos = num / np.sqrt((X @ A @ X) * (Y @ A @ Y))
        omega = float(np.arccos(cos))

        # The arc, drawn between the two arrow directions the long way round if
        # the angle is obtuse — which for diag(2, 1) it is.
        a0 = np.arctan2(X[1], X[0])
        arc = np.linspace(a0, a0 + omega, 200)
        ax.plot(radius * np.cos(arc), radius * np.sin(arc), color=colour, linewidth=2.0)
        mid = a0 + omega / 2.0
        ax.annotate(
            rf"$\omega = {np.degrees(omega):.1f}^\circ$",
            xy=(radius * np.cos(mid), radius * np.sin(mid)),
            xytext=((radius + 0.34) * np.cos(mid) - 0.28, (radius + 0.34) * np.sin(mid)),
            color=colour,
            fontsize=9.5,
        )
        rows.append(f"  {name:<12} cos = {cos:+.4f}   {np.degrees(omega):7.2f} deg")

    ax.text(
        0.02,
        0.03,
        "same two vectors:\n" + "\n".join(rows),
        transform=ax.transAxes,
        color=p.fg,
        fontsize=9,
        family="monospace",
        va="bottom",
    )

    ax.axhline(0, color=p.grid, linewidth=0.9)
    ax.axvline(0, color=p.grid, linewidth=0.9)
    ax.set_aspect("equal")
    ax.set_xlim(-1.75, 1.75)
    ax.set_ylim(-1.15, 1.75)
    ax.set_xlabel("$x_1$")
    ax.set_ylabel("$x_2$")
    ax.legend(loc="lower right", fontsize=8)


def cosine_similarity_matrix(fig, ax, p: Palette) -> None:
    """Raw dot products beside cosines, with both rankings measured."""
    fig.clear()
    axes = fig.subplots(1, 2)

    names = [d[0] for d in DOCS]
    V = np.array([d[1] for d in DOCS], dtype=float)
    lengths = np.linalg.norm(V, axis=1)

    gram = V @ V.T
    cosine = gram / np.outer(lengths, lengths)

    for a, M, title, cmap in (
        (axes[0], gram, r"raw dot product $\mathbf{x}^\top\mathbf{y}$", "magma"),
        (axes[1], cosine, r"cosine $\frac{\mathbf{x}^\top\mathbf{y}}{\|\mathbf{x}\|\|\mathbf{y}\|}$", "viridis"),
    ):
        im = a.imshow(M, cmap=cmap)
        a.set_xticks(range(len(names)), names, rotation=90, fontsize=7.5)
        a.set_yticks(range(len(names)), names, fontsize=7.5)
        a.set_title(title, fontsize=10)
        a.grid(False)
        fig.colorbar(im, ax=a, fraction=0.046, pad=0.03)

    # The top off-diagonal pair under each measure. If the dot product were a
    # good similarity, both would name the same pair.
    def top_pair(M: np.ndarray) -> tuple[str, str, float]:
        Mm = M.copy()
        np.fill_diagonal(Mm, -np.inf)
        i, j = np.unravel_index(int(np.argmax(Mm)), Mm.shape)
        return names[i], names[j], float(Mm[i, j])

    gi, gj, gv = top_pair(gram)
    ci, cj, cv = top_pair(cosine)

    # And the cross-topic worst case: does either measure rank an ml/bake pair
    # above a same-topic pair?
    ml = [i for i, n in enumerate(names) if n.startswith("ml")]
    bake = [i for i, n in enumerate(names) if n.startswith("bake")]
    cross_gram = max(gram[i, j] for i in ml for j in bake)
    same_gram = min(
        [gram[i, j] for i in ml for j in ml if i != j] + [gram[i, j] for i in bake for j in bake if i != j]
    )
    cross_cos = max(cosine[i, j] for i in ml for j in bake)
    same_cos = min(
        [cosine[i, j] for i in ml for j in ml if i != j]
        + [cosine[i, j] for i in bake for j in bake if i != j]
    )

    fig.text(
        0.5,
        -0.02,
        f"top pair by dot product: {gi} + {gj} ({gv:.0f})        "
        f"top pair by cosine: {ci} + {cj} ({cv:.3f})\n"
        f"dot product: worst same-topic {same_gram:.0f} vs best cross-topic {cross_gram:.0f}"
        f"  ->  {'OVERLAP' if cross_gram > same_gram else 'clean split'}\n"
        f"cosine:      worst same-topic {same_cos:.3f} vs best cross-topic {cross_cos:.3f}"
        f"  ->  {'OVERLAP' if cross_cos > same_cos else 'clean split'}",
        ha="center",
        va="top",
        color=p.fg,
        fontsize=8.5,
        family="monospace",
    )


FIGURES = [
    figure("two-inner-products-two-angles", two_inner_products_two_angles, size=(6.6, 5.4)),
    figure("cosine-similarity-matrix", cosine_similarity_matrix, size=(10.0, 4.4), axes=False),
]
