"""Figures for *Discrete and Continuous Probabilities*.

1. `pmf-versus-pdf` — the book's Figure 6.3, with the y-axis deliberately shared
   so the point survives: the continuous uniform's density is 1.4286, taller than
   any bar a pmf could have, while both objects integrate or sum to exactly one.
   The third panel drives it home by shrinking the support: the height runs off to
   infinity and the area never moves.

2. `joint-marginal-conditional` — Example 6.2 as three heatmaps of the same
   counts. The joint divides by N, the two conditionals divide by a column total
   and a row total, and the panel titles say which axis ends up summing to one.
   That is the distinction Equations 6.13 and 6.14 encode and the one that gets
   transposed in practice.

3. `density-is-not-probability` — two ways of saying it. Left: a Gaussian's peak
   density against sigma, crossing 1 at sigma = 0.3989 and reaching 39.9 by
   sigma = 0.01. Right: the same distribution's cdf, which is bounded by 1 no
   matter what sigma does. The cdf is the object that is always a probability.
"""

from __future__ import annotations

import numpy as np

from _style import Palette, figure

# Example 6.3's two distributions.
Z_STATES = np.array([-1.1, 0.3, 1.5])
Z_PMF = np.full(3, 1 / 3)
A, B = 0.9, 1.6
HEIGHT = 1 / (B - A)

# Example 6.2's counts: X has five states, Y has three.
N_IJ = np.array([
    [12, 30, 18, 8, 4],
    [6, 22, 40, 26, 10],
    [2, 8, 14, 30, 20],
])


def pmf_versus_pdf(fig, ax, p: Palette) -> None:
    """Figure 6.3, plus the reason the shared axis matters."""
    fig.clear()
    axes = fig.subplots(1, 3, gridspec_kw={"width_ratios": [1, 1, 1.15]})
    left, mid, right = axes

    # (a) the discrete uniform.
    left.bar(Z_STATES, Z_PMF, width=0.12, color=p.blue)
    for z in Z_STATES:
        left.text(z, 1 / 3 + 0.05, f"{1/3:.3f}", ha="center", color=p.fg,
                  fontsize=8.5, family="monospace")
    left.set_xlim(-1.6, 2.1)
    left.set_ylim(0, 2.0)
    left.set_xlabel("$z$")
    left.set_ylabel("$P(Z = z)$")
    left.set_title("(a) discrete: a pmf", fontsize=9.5, color=p.blue)
    left.text(0.5, 0.97,
              "every bar is a PROBABILITY,\nso every bar is at most 1",
              transform=left.transAxes, ha="center", va="top",
              color=p.fg, fontsize=8, family="monospace")

    # (b) the continuous uniform, same y-axis.
    xs = np.linspace(-1.6, 2.1, 800)
    dens = np.where((xs >= A) & (xs <= B), HEIGHT, 0.0)
    mid.fill_between(xs, dens, color=p.green, alpha=0.35, step="mid")
    mid.plot(xs, dens, color=p.green, linewidth=2.0)
    mid.axhline(1.0, color=p.red, linestyle="--", linewidth=1.3)
    mid.text(-1.5, 1.04, "the line $p = 1$", color=p.red, fontsize=8,
             family="monospace")
    mid.annotate(f"height {HEIGHT:.4f}", xy=((A + B) / 2, HEIGHT),
                 xytext=((A + B) / 2 - 0.1, HEIGHT + 0.28),
                 ha="center", color=p.green, fontsize=8.5, family="monospace",
                 arrowprops=dict(arrowstyle="-|>", color=p.green, linewidth=1.2))
    mid.set_xlim(-1.6, 2.1)
    mid.set_ylim(0, 2.0)
    mid.set_xlabel("$x$")
    mid.set_ylabel("$p(x)$")
    mid.set_title("(b) continuous: a pdf", fontsize=9.5, color=p.green)
    mid.text(0.5, 0.97,
             f"area = {HEIGHT * (B - A):.4f}\nbut the HEIGHT exceeds 1",
             transform=mid.transAxes, ha="center", va="top",
             color=p.fg, fontsize=8, family="monospace")

    # (c) the height is unbounded.
    widths = np.array([1.0, 0.7, 0.3, 0.1, 0.03, 0.01, 3e-3, 1e-3])
    right.loglog(widths, 1 / widths, "o-", color=p.amber, linewidth=2.0,
                 label="density height $1/(b-a)$")
    right.axhline(1.0, color=p.red, linestyle="--", linewidth=1.3,
                  label="the line $p = 1$")
    right.plot([B - A], [HEIGHT], "o", color=p.green, markersize=9, zorder=5,
               label="Example 6.3")
    right.set_xlabel("width of the support $b - a$")
    right.set_ylabel("height of the density")
    right.invert_xaxis()
    right.set_title("(c) a density has no upper bound", fontsize=9.5,
                    color=p.amber)
    right.legend(loc="upper left", fontsize=7.6)
    right.text(
        0.97, 0.03,
        "the area stays exactly 1\nat every point on this line:\n"
        "height $\\times$ width $= 1$",
        transform=right.transAxes, ha="right", va="bottom",
        color=p.fg, fontsize=8, family="monospace")

    fig.text(
        0.5, -0.06,
        "The two y-axes on (a) and (b) are the same on purpose. A pmf value is a "
        "probability and cannot exceed 1; a pdf value is a density and can be as "
        "large as you like. Equation 6.15 constrains the AREA, not the height.",
        ha="center", va="top", color=p.muted, fontsize=8.4)


def joint_marginal_conditional(fig, ax, p: Palette) -> None:
    """Example 6.2: one table, three normalisations."""
    fig.clear()
    axes = fig.subplots(1, 3)
    N = N_IJ.sum()
    c_i = N_IJ.sum(axis=0)
    r_j = N_IJ.sum(axis=1)

    panels = [
        ("joint, Eq 6.9\n$n_{ij}/N$", N_IJ / N, "everything sums to 1"),
        ("$P(Y|X)$, Eq 6.13\n$n_{ij}/c_i$", N_IJ / c_i[None, :],
         "each COLUMN sums to 1"),
        ("$P(X|Y)$, Eq 6.14\n$n_{ij}/r_j$", N_IJ / r_j[:, None],
         "each ROW sums to 1"),
    ]

    for a, (title, M, note) in zip(axes, panels):
        im = a.imshow(M, cmap="viridis", aspect="auto", vmin=0,
                      vmax=float(M.max()))
        for j in range(M.shape[0]):
            for i in range(M.shape[1]):
                a.text(i, j, f"{M[j, i]:.3f}", ha="center", va="center",
                       color="white" if M[j, i] < 0.6 * M.max() else "black",
                       fontsize=7.4, family="monospace")
        a.set_xticks(range(5), [f"$x_{i+1}$" for i in range(5)])
        a.set_yticks(range(3), [f"$y_{j+1}$" for j in range(3)])
        a.set_title(title, fontsize=9)
        a.text(0.5, -0.16, note, transform=a.transAxes, ha="center", va="top",
               color=p.amber, fontsize=8.4, family="monospace")

    # The marginals, printed under the joint panel.
    axes[0].text(
        0.5, -0.30,
        f"$P(X)$ = {np.array2string(c_i / N, precision=3)}\n"
        f"$P(Y)$ = {np.array2string(r_j / N, precision=3)}",
        transform=axes[0].transAxes, ha="center", va="top",
        color=p.fg, fontsize=7.6, family="monospace")

    fig.text(
        0.5, -0.16,
        "Same 250 counts in all three panels. Only the DIVISOR changes: the total, "
        "a column total, or a row total. Which axis ends up summing to one is the "
        "whole content of Equations 6.13 and 6.14, and it is the thing that gets "
        "transposed.",
        ha="center", va="top", color=p.muted, fontsize=8.4)


def density_is_not_probability(fig, ax, p: Palette) -> None:
    """A density is unbounded; its cdf is not."""
    fig.clear()
    left, right = fig.subplots(1, 2)

    sds = np.geomspace(0.005, 3.0, 400)
    peak = 1 / (sds * np.sqrt(2 * np.pi))
    left.loglog(sds, peak, color=p.blue, linewidth=2.2,
                label="peak density $1/(\\sigma\\sqrt{2\\pi})$")
    left.axhline(1.0, color=p.red, linestyle="--", linewidth=1.4,
                 label="the line $p = 1$")
    cross = 1 / np.sqrt(2 * np.pi)
    left.plot([cross], [1.0], "o", color=p.amber, markersize=8, zorder=5)
    left.annotate(f"crosses 1 at\n$\\sigma = {cross:.4f}$",
                  xy=(cross, 1.0), xytext=(cross * 2.4, 0.35),
                  color=p.amber, fontsize=8, family="monospace",
                  arrowprops=dict(arrowstyle="-|>", color=p.amber, linewidth=1.2))
    for sd in (0.1, 0.01):
        v = 1 / (sd * np.sqrt(2 * np.pi))
        left.plot([sd], [v], "o", color=p.green, markersize=6, zorder=5)
        left.text(sd * 1.25, v, f"$\\sigma={sd}$: {v:.1f}", color=p.green,
                  fontsize=8, family="monospace", va="center")
    left.set_xlabel("$\\sigma$")
    left.set_ylabel("density at the mean")
    left.set_title("a density is not bounded by 1", fontsize=9.5)
    left.legend(loc="lower left", fontsize=8)

    # Right: the cdf of the same family, which is bounded.
    xs = np.linspace(-1.5, 1.5, 1200)
    from math import erf
    erfv = np.vectorize(erf)
    for sd, colour in zip((1.0, 0.3, 0.1, 0.03),
                          (p.muted, p.blue, p.green, p.amber)):
        cdf = 0.5 * (1 + erfv(xs / (sd * np.sqrt(2))))
        right.plot(xs, cdf, color=colour, linewidth=1.9, label=f"$\\sigma={sd}$")
    right.axhline(1.0, color=p.red, linestyle="--", linewidth=1.4)
    right.set_ylim(-0.05, 1.15)
    right.set_xlabel("$x$")
    right.set_ylabel("$F_X(x) = P(X \\leq x)$")
    right.set_title("its cdf always is", fontsize=9.5)
    right.legend(loc="upper left", fontsize=8)
    right.text(
        0.97, 0.05,
        "however tall the density gets,\n"
        "the cdf still runs from 0 to 1.\n"
        "Definition 6.2 is the object that\n"
        "is a probability at every point.",
        transform=right.transAxes, ha="right", va="bottom",
        color=p.fg, fontsize=8, family="monospace")


FIGURES = [
    figure("pmf-versus-pdf", pmf_versus_pdf, size=(12.0, 4.2), axes=False),
    figure("joint-marginal-conditional", joint_marginal_conditional,
           size=(12.0, 4.0), axes=False),
    figure("density-is-not-probability", density_is_not_probability,
           size=(11.0, 4.4), axes=False),
]
