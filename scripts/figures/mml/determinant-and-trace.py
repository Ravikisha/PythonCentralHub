"""Figures for *Determinant and Trace*.

1. `determinant-is-volume` — the book's Example 4.2 in both dimensions. A
   parallelogram in the plane with its signed area, and beside it the
   parallelepiped spanned by the book's three vectors r, g, b whose volume comes
   out at exactly 186. The two-dimensional panel also shows what happens as the
   columns approach linear dependence: the area, and therefore the determinant,
   goes to zero.

2. `laplace-versus-elimination` — why nobody computes determinants by cofactor
   expansion. Exact multiplication counts for the Laplace recursion against
   Gaussian elimination, over n. The recursion costs about n! and elimination
   about n^3/3, and the ratio at n = 15 is already 2e9 -- rising to 1.6e15 at n = 20. The
   book says numerical methods superseded the explicit determinant; this is the
   size of the reason.

3. `trace-invariant-under-basis-change` — Equation 4.21, measured. One matrix is
   conjugated by two thousand random invertible S. Every individual entry moves
   enormously, and the trace and determinant do not move at all. That is what
   "characteristic of the mapping, not of the representation" means.
"""

from __future__ import annotations

import numpy as np

from _style import Palette, figure

# The book's Example 4.2 vectors.
R = np.array([2.0, 0.0, -8.0])
G = np.array([6.0, 1.0, 0.0])
B = np.array([1.0, 4.0, -1.0])


def determinant_is_volume(fig, ax, p: Palette) -> None:
    """Signed area in the plane, signed volume in space."""
    fig.clear()
    left = fig.add_subplot(1, 2, 1)
    right = fig.add_subplot(1, 2, 2, projection="3d")

    # -- the plane ------------------------------------------------------- #
    b2 = np.array([0.4, 1.6])
    for k, (g2, colour, alpha) in enumerate(
        (
            (np.array([1.9, 0.3]), p.blue, 0.30),
            (np.array([1.4, 1.05]), p.amber, 0.24),
            (np.array([0.55, 2.15]), p.red, 0.20),
        )
    ):
        A = np.stack([b2, g2], axis=1)
        d = float(np.linalg.det(A))
        poly = np.array([[0, 0], b2, b2 + g2, g2, [0, 0]])
        left.fill(poly[:, 0], poly[:, 1], color=colour, alpha=alpha)
        left.plot(poly[:, 0], poly[:, 1], color=colour, linewidth=1.8)
        left.annotate(
            "",
            xy=tuple(g2),
            xytext=(0, 0),
            arrowprops=dict(arrowstyle="->", color=colour, linewidth=2.0),
        )
        left.annotate(
            f"|det| = {abs(d):.4f}",
            xy=tuple(0.5 * (b2 + g2)),
            xytext=(2.35, 2.5 - 0.42 * k),
            color=colour,
            fontsize=9,
            arrowprops=dict(arrowstyle="->", color=colour, linewidth=0.9),
        )

    left.annotate(
        "", xy=tuple(b2), xytext=(0, 0),
        arrowprops=dict(arrowstyle="->", color=p.fg, linewidth=2.4),
    )
    left.annotate("$b$ (fixed)", xy=tuple(b2), xytext=(b2[0] - 0.15, b2[1] + 0.14),
                  color=p.fg, fontsize=9)
    left.text(
        0.03, 0.03,
        "as $g$ turns towards $b$ the area shrinks;\n"
        "at $g = \\lambda b$ it is exactly zero",
        transform=left.transAxes, color=p.muted, fontsize=8.5, va="bottom",
    )
    left.axhline(0, color=p.grid, linewidth=0.9)
    left.axvline(0, color=p.grid, linewidth=0.9)
    left.set_aspect("equal")
    left.set_xlim(-0.4, 4.0)
    left.set_ylim(-0.4, 3.0)
    left.set_xlabel("$x_1$")
    left.set_ylabel("$x_2$")
    left.set_title("$|\\det[b, g]|$ is the area", fontsize=10.5)

    # -- space: the book's Example 4.2 ----------------------------------- #
    A3 = np.stack([R, G, B], axis=1)
    volume = abs(float(np.linalg.det(A3)))

    corners = np.array(
        [i * R + j * G + k * B for i in (0, 1) for j in (0, 1) for k in (0, 1)]
    )
    faces = [
        (0, 1, 3, 2), (4, 5, 7, 6), (0, 1, 5, 4),
        (2, 3, 7, 6), (0, 2, 6, 4), (1, 3, 7, 5),
    ]
    for f in faces:
        quad = corners[list(f) + [f[0]]]
        right.plot(quad[:, 0], quad[:, 1], quad[:, 2], color=p.blue, linewidth=0.9, alpha=0.7)

    for v, colour, name in ((R, p.red, "$r$"), (G, p.green, "$g$"), (B, p.amber, "$b$")):
        right.plot([0, v[0]], [0, v[1]], [0, v[2]], color=colour, linewidth=2.6)
        right.text(v[0] * 1.05, v[1] * 1.05, v[2] * 1.05, name, color=colour, fontsize=10)

    right.set_title(f"$V = |\\det[r, g, b]| = {volume:.0f}$", fontsize=10.5)
    right.set_xlabel("$x_1$", fontsize=8)
    right.set_ylabel("$x_2$", fontsize=8)
    right.set_zlabel("$x_3$", fontsize=8)
    right.view_init(elev=20, azim=-62)
    right.set_facecolor(p.bg)
    for pane in (right.xaxis, right.yaxis, right.zaxis):
        pane.set_pane_color((0, 0, 0, 0))
        pane._axinfo["grid"]["color"] = p.grid
    right.tick_params(labelsize=7, colors=p.muted)

    fig.text(
        0.5, 0.015,
        f"$r = (2, 0, -8)$, $g = (6, 1, 0)$, $b = (1, 4, -1)$   "
        f"$\\Rightarrow$   $\\det = {float(np.linalg.det(A3)):.0f}$, "
        f"Sarrus' rule and Laplace expansion agree",
        ha="center", color=p.muted, fontsize=8.5,
    )


def laplace_versus_elimination(fig, ax, p: Palette) -> None:
    """Exact multiplication counts for the two routes to a determinant."""
    ns = np.arange(2, 21)

    # Laplace expansion, counted honestly: expanding an n x n determinant costs
    # n sub-determinants of size n-1 plus n multiplications by the cofactor
    # entries. L(1) = 0, L(n) = n * L(n-1) + n.
    lap = [0.0]
    for n in range(2, 21):
        lap.append(n * lap[-1] + n)
    laplace = np.array(lap[1:])

    # Gaussian elimination to triangular form: sum over pivots of the
    # multiply-and-subtract work, plus n-1 multiplications for the diagonal.
    gauss = np.array(
        [sum((n - k) * (n - k + 1) for k in range(1, n)) + (n - 1) for n in ns]
    )

    factorial = np.array(
        [float(np.prod(np.arange(1, int(n) + 1), dtype=float)) for n in ns]
    )

    ax.semilogy(ns, laplace, color=p.red, linewidth=2.2, marker="o", markersize=3.4,
                label="Laplace expansion (Thm 4.2)")
    ax.semilogy(ns, gauss, color=p.green, linewidth=2.2, marker="s", markersize=3.4,
                label="Gaussian elimination (Eq 4.8)")
    ax.semilogy(ns, factorial, color=p.muted, linewidth=1.2, linestyle="--", label="$n!$")
    ax.semilogy(ns, ns.astype(float) ** 3 / 3.0, color=p.blue, linewidth=1.2,
                linestyle=":", label="$n^3/3$")

    for n_mark in (10, 15, 20):
        i = int(n_mark - 2)
        ax.annotate(
            f"n={n_mark}: {laplace[i]:.2e} vs {gauss[i]:.0f}\n"
            f"ratio {laplace[i] / gauss[i]:.2e}",
            xy=(n_mark, laplace[i]),
            xytext=(n_mark - 7.2, laplace[i] * 0.02),
            color=p.red, fontsize=8,
            arrowprops=dict(arrowstyle="->", color=p.red, linewidth=0.9),
        )

    ax.set_xlabel("matrix size $n$")
    ax.set_ylabel("multiplications")
    ax.set_title("two routes to the same number", fontsize=10.5)
    ax.set_xticks(ns[::2])
    ax.legend(loc="upper left", fontsize=8.5)


def trace_invariant_under_basis_change(fig, ax, p: Palette) -> None:
    """Equation 4.21: similar matrices share a trace, and a determinant."""
    fig.clear()
    left, right = fig.subplots(1, 2, gridspec_kw={"width_ratios": [1.15, 1.0]})

    rng = np.random.default_rng(19)
    A = np.array([[3.0, 1.0, -2.0], [0.0, 2.0, 1.0], [1.0, -1.0, 4.0]])
    tr0 = float(np.trace(A))
    det0 = float(np.linalg.det(A))

    traces, dets, entry, spread = [], [], [], []
    for _ in range(2000):
        S = rng.normal(size=(3, 3))
        if abs(np.linalg.det(S)) < 0.2:      # keep the conjugation well conditioned
            continue
        B = np.linalg.solve(S, A @ S)
        traces.append(float(np.trace(B)))
        dets.append(float(np.linalg.det(B)))
        entry.append(float(B[0, 0]))
        spread.append(float(np.abs(B).max()))

    traces = np.array(traces)
    dets = np.array(dets)
    entry = np.array(entry)

    left.hist(entry, bins=70, range=(-40, 40), color=p.blue, alpha=0.75,
              label="a single entry $B_{11}$")
    left.axvline(float(A[0, 0]), color=p.muted, linewidth=1.4, linestyle="--",
                 label=f"$A_{{11}} = {A[0, 0]:.0f}$")
    left.set_xlabel("value")
    left.set_ylabel("count")
    left.set_title("individual entries move freely", fontsize=10.5)
    left.legend(loc="upper right", fontsize=8)

    right.scatter(traces, dets, s=8, color=p.amber, alpha=0.6)
    right.scatter([tr0], [det0], s=90, marker="*", color=p.green, zorder=6,
                  label=f"$A$: tr {tr0:.0f}, det {det0:.0f}")
    # Zoom to the actual scatter rather than to a round number, so the reader
    # sees a cloud of floating-point noise instead of one degenerate dot.
    tspan = max(3e-15, float(np.max(np.abs(traces - tr0))) * 1.4)
    dspan = max(3e-13, float(np.max(np.abs(dets - det0))) * 1.4)
    right.set_xlim(tr0 - tspan, tr0 + tspan)
    right.set_ylim(det0 - dspan, det0 + dspan)
    right.ticklabel_format(useOffset=False, style="plain")
    right.set_xlabel("trace($S^{-1}AS$)")
    right.set_ylabel("det($S^{-1}AS$)")
    right.set_title("trace and determinant do not", fontsize=10.5)
    right.legend(loc="upper right", fontsize=8)

    right.text(
        0.03, 0.05,
        f"conjugations: {len(traces)}\n"
        f"largest |trace - {tr0:.0f}|: {np.max(np.abs(traces - tr0)):.2e}\n"
        f"largest |det - {det0:.0f}|:   {np.max(np.abs(dets - det0)):.2e}\n"
        f"largest entry seen anywhere: {max(spread):.1f}",
        transform=right.transAxes, color=p.fg, fontsize=8,
        family="monospace", va="bottom",
    )


FIGURES = [
    figure("determinant-is-volume", determinant_is_volume, size=(9.8, 4.6), axes=False),
    figure("laplace-versus-elimination", laplace_versus_elimination, size=(7.4, 5.2)),
    figure("trace-invariant-under-basis-change", trace_invariant_under_basis_change,
           size=(9.8, 4.2), axes=False),
]
