"""Figures for *Finding Words for Intuitions*.

1. `learning-is-not-memorising` — the sentence the whole book is built to make
   precise, measured. Polynomial fits of rising degree drive training error to
   essentially zero while test error turns and climbs. The degree that memorises
   perfectly is not the degree that predicts.

2. `three-views-of-a-vector` — one triple of numbers drawn as an array, as an
   arrow, and as a point on a fitted line. Nothing about the data changes; only
   which vocabulary is in use.

3. `function-view-versus-distribution-view` — the same least-squares fit read as
   a function and as a distribution. Identical point predictions, but only the
   second one produces error bars. The third panel is the honest correction to
   the usual story: a distribution view does not by itself notice a gap in the
   data. A straight line is most certain at the centroid whether or not any data
   is there. It takes a flexible model for the band to balloon where the data ran
   out, so the model class decides that, not the vocabulary.
"""

from __future__ import annotations

import numpy as np

from _style import Palette, figure


def _truth(x):
    """The process the model is a stand-in for. Nothing sees this but the plot."""
    return np.sin(1.7 * x) + 0.35 * x


def _split(seed=3, n_train=25, n_test=2000, noise=0.25):
    rng = np.random.default_rng(seed)
    xtr = np.sort(rng.uniform(-3, 3, n_train))
    ytr = _truth(xtr) + noise * rng.standard_normal(n_train)
    xte = np.sort(rng.uniform(-3, 3, n_test))
    yte = _truth(xte) + noise * rng.standard_normal(n_test)
    return xtr, ytr, xte, yte


def _rmse(a, b):
    return float(np.sqrt(np.mean((a - b) ** 2)))


def learning_is_not_memorising(fig, ax, p: Palette) -> None:
    """Training error falls to zero; test error turns. The gap is the subject."""
    fig.clear()
    left, right = fig.subplots(1, 2)

    xtr, ytr, xte, yte = _split()
    degrees = np.arange(0, 19)
    tr_err, te_err = [], []
    for d in degrees:
        # Vandermonde in a shifted, scaled variable so high degrees stay solvable.
        V = np.vander(xtr / 3.0, d + 1)
        coef, *_ = np.linalg.lstsq(V, ytr, rcond=None)
        tr_err.append(_rmse(V @ coef, ytr))
        te_err.append(_rmse(np.vander(xte / 3.0, d + 1) @ coef, yte))
    tr_err = np.array(tr_err)
    te_err = np.array(te_err)
    best = int(degrees[np.argmin(te_err)])
    worst = int(degrees[-1])

    left.semilogy(degrees, tr_err, "o-", color=p.blue, linewidth=2.2,
                  markersize=5, label=f"training error, {xtr.size} points")
    left.semilogy(degrees, te_err, "s-", color=p.red, linewidth=2.2,
                  markersize=5, label=f"test error, {xte.size} unseen points")
    left.axvline(best, color=p.green, linestyle="--", linewidth=1.6)
    left.text(best + 0.15, te_err.max() * 0.55,
              f"best on unseen data:\ndegree {best}", fontsize=8.2,
              color=p.green, family="monospace", va="center")
    left.plot([worst], [tr_err[-1]], "o", color=p.amber, markersize=8,
              markerfacecolor="none", markeredgewidth=1.8)
    left.set_xlabel("polynomial degree, i.e. model capacity")
    left.set_ylabel("root-mean-square error")
    left.set_title("The two errors go opposite ways", fontsize=10)
    left.legend(fontsize=8, loc="lower left")
    left.grid(alpha=0.22, linewidth=0.6)
    left.text(
        0.98, 0.97,
        f"training error never stops falling:\n"
        f"  {tr_err[0]:.3f} at degree 0 down to {tr_err[-1]:.3f} at {worst}\n"
        f"test error turns at degree {best} ({te_err[best]:.4f})\n"
        f"and reaches {te_err[-1]:.1f} at degree {worst}\n"
        f"picking on training error costs "
        f"{te_err[-1] / te_err[best]:.0f}x",
        transform=left.transAxes, ha="right", va="top", fontsize=7.8,
        color=p.fg, family="monospace")

    grid = np.linspace(-3.2, 3.2, 600)
    right.plot(grid, _truth(grid), color=p.muted, linewidth=1.6,
               linestyle="--", label="the process being modelled")
    for d, col, style in ((best, p.green, "-"), (worst, p.amber, "-")):
        V = np.vander(xtr / 3.0, d + 1)
        coef, *_ = np.linalg.lstsq(V, ytr, rcond=None)
        right.plot(grid, np.vander(grid / 3.0, d + 1) @ coef, color=col,
                   linewidth=2.2, linestyle=style,
                   label=f"degree {d}, test RMSE {te_err[d]:.3f}")
    right.plot(xtr, ytr, "o", color=p.blue, markersize=6,
               markeredgecolor=p.bg, markeredgewidth=1.0,
               label=f"the {xtr.size} training points", zorder=5)
    right.set_xlabel("$x$")
    right.set_ylabel("$y$")
    right.set_ylim(-3.6, 3.8)
    right.set_title("What memorising looks like", fontsize=10)
    right.legend(fontsize=7.6, loc="upper left")
    right.grid(alpha=0.22, linewidth=0.6)

    fig.suptitle(
        "\"Learning is not memorising\" is a measurable claim, not a slogan",
        y=0.99, fontsize=10, color=p.fg)
    fig.text(
        0.5, 0.005,
        f"Training error falls at every single step from degree 0 to degree "
        f"{worst}, so it can never tell you when to stop. Test error turns at\n"
        f"degree {best}. A model selected by training error alone lands on degree "
        f"{worst}, whose error on unseen data is {te_err[-1] / te_err[best]:.0f} "
        "times worse. Chapter 8 calls this empirical versus expected risk.",
        ha="center", va="bottom", fontsize=8.3, color=p.muted)


def three_views_of_a_vector(fig, ax, p: Palette) -> None:
    """Array, arrow, axiom-satisfier: one object, three vocabularies."""
    fig.clear()
    a1, a2, a3 = fig.subplots(1, 3)
    from matplotlib.patches import Rectangle

    v = np.array([2.0, 3.0])

    a1.axis("off")
    a1.set_xlim(0, 6)
    a1.set_ylim(0, 6)
    for k, val in enumerate(v):
        a1.add_patch(Rectangle((1.6 + k * 1.4, 3.0), 1.3, 1.3,
                               facecolor=p.blue, alpha=0.22,
                               edgecolor=p.blue, linewidth=1.6))
        a1.text(1.6 + k * 1.4 + 0.65, 3.65, f"{val:.0f}", ha="center",
                va="center", fontsize=14, color=p.fg, family="monospace")
        a1.text(1.6 + k * 1.4 + 0.65, 2.82, f"[{k}]", ha="center", va="top",
                fontsize=8.5, color=p.muted, family="monospace")
    a1.text(3.0, 5.1, "computer science", ha="center", fontsize=10, color=p.blue)
    a1.text(3.0, 2.15,
            "an ARRAY of numbers\n`x = np.array([2., 3.])`\n"
            "`x.shape` is `(2,)`\nwhat the code manipulates",
            ha="center", va="top", fontsize=8.4, color=p.muted,
            family="monospace")

    a2.axhline(0, color=p.grid, linewidth=1.1)
    a2.axvline(0, color=p.grid, linewidth=1.1)
    a2.annotate("", xy=(v[0], v[1]), xytext=(0, 0),
                arrowprops=dict(arrowstyle="-|>", color=p.amber, linewidth=2.6,
                                shrinkA=0, shrinkB=0))
    a2.plot([v[0], v[0]], [0, v[1]], color=p.muted, linestyle=":", linewidth=1.0)
    a2.plot([0, v[0]], [v[1], v[1]], color=p.muted, linestyle=":", linewidth=1.0)
    norm = float(np.linalg.norm(v))
    ang = float(np.degrees(np.arctan2(v[1], v[0])))
    a2.text(1.05, 1.75, f"length {norm:.7f}\nangle {ang:.4f}$^\\circ$",
            fontsize=8.6, color=p.amber, family="monospace")
    a2.set_xlim(-0.8, 4.0)
    a2.set_ylim(-0.8, 4.2)
    a2.set_aspect("equal")
    a2.set_title("physics", fontsize=10, color=p.amber)
    a2.grid(alpha=0.15, linewidth=0.6)
    a2.text(1.6, -0.62,
            "an ARROW with direction\nand magnitude: what the\nintuition runs on",
            ha="center", va="top", fontsize=8.4, color=p.muted,
            family="monospace")

    a3.axis("off")
    a3.set_xlim(0, 10)
    a3.set_ylim(0, 10)
    a3.text(5.0, 9.4, "mathematics", ha="center", fontsize=10, color=p.purple)
    checks = [
        ("$\\mathbf{u} + \\mathbf{v}$ is in the set", "closed under addition"),
        ("$\\lambda\\mathbf{v}$ is in the set", "closed under scaling"),
        ("that is the entire definition", "$\\S2.4$"),
    ]
    for k, (line, note) in enumerate(checks):
        y = 7.7 - k * 1.5
        a3.text(0.4, y, "✓", fontsize=13, color=p.green, va="center")
        a3.text(1.3, y, line, fontsize=9.4, color=p.fg, va="center")
        a3.text(1.3, y - 0.62, note, fontsize=8, color=p.muted, va="center",
                family="monospace")
    a3.text(5.0, 2.6,
            "so these are also vectors:\n"
            "polynomials, audio signals,\nfunctions ($\\S3.7$ takes their angle)",
            ha="center", va="top", fontsize=8.6, color=p.purple)
    a3.text(5.0, 0.55,
            "any OBJECT OBEYING THE AXIOMS:\nwhat the proofs need",
            ha="center", va="bottom", fontsize=8.4, color=p.muted,
            family="monospace")

    fig.suptitle(
        "\"Data is vectors\" means three different things, and fluency is switching "
        "without noticing",
        y=0.99, fontsize=10, color=p.fg)
    fig.text(
        0.5, 0.005,
        "The numbers $2$ and $3$ are the same numbers in all three panels. The views "
        "are not rival theories, they are three faces of one\nobject: an array for "
        "the code, an arrow for the intuition, an axiom-satisfier for the proof. The "
        "third is the one Chapter 2 adopts.",
        ha="center", va="bottom", fontsize=8.3, color=p.muted)


def function_view_versus_distribution_view(fig, ax, p: Palette) -> None:
    """Same estimator, two stories — and the honest caveat about the second."""
    fig.clear()
    a1, a2, a3 = fig.subplots(1, 3)

    # One dataset with a deliberate hole in the middle, shared by all three panels.
    rng = np.random.default_rng(5)
    x = np.sort(np.concatenate([rng.uniform(-2.6, -1.2, 4),
                                rng.uniform(1.2, 2.6, 4)]))
    y = 0.9 * x + 0.4 + 0.35 * rng.standard_normal(x.size)

    grid = np.linspace(-4.0, 4.0, 600)

    def band(Phi, Pg, prior_var, sigma2):
        A = Phi.T @ Phi / sigma2 + np.eye(Phi.shape[1]) / prior_var
        cov = np.linalg.inv(A)
        mean = Pg @ (cov @ Phi.T @ y / sigma2)
        ep = np.sqrt(np.einsum("ij,jk,ik->i", Pg, cov, Pg))
        return mean, ep

    def at(arr, q):
        return float(np.interp(q, grid, arr))

    # --- panel 1: the function view -------------------------------------------
    Phi = np.vstack([np.ones_like(x), x]).T
    Pg = np.vstack([np.ones_like(grid), grid]).T
    w, *_ = np.linalg.lstsq(Phi, y, rcond=None)
    resid = y - Phi @ w
    sigma2 = float(resid @ resid / (x.size - 2))

    for axx in (a1, a2, a3):
        axx.axvspan(-1.2, 1.2, color=p.red, alpha=0.09, linewidth=0)
        axx.plot(x, y, "o", color=p.fg, markersize=6, markeredgecolor=p.bg,
                 markeredgewidth=0.8, zorder=5)
        axx.set_xlabel("$x$")
        axx.set_ylim(-4.2, 4.6)
        axx.set_xlim(-4.0, 4.0)
        axx.grid(alpha=0.20, linewidth=0.6)
    a1.set_ylabel("$y$")

    a1.plot(grid, Pg @ w, color=p.blue, linewidth=2.4)
    a1.set_title("Model as a FUNCTION", fontsize=9.6)
    a1.text(0.0, -3.9, "no data in here", ha="center", fontsize=8,
            color=p.red, family="monospace")
    a1.text(0.03, 0.97,
            f"$f(x) = {w[0]:.4f} + {w[1]:.4f}x$\n"
            f"$f(0) = {w[0]:.4f}$\n"
            "uncertainty expressible: none",
            transform=a1.transAxes, ha="left", va="top", fontsize=7.9,
            color=p.blue, family="monospace")

    # --- panel 2: the distribution view, same straight line --------------------
    mean_l, ep_l = band(Phi, Pg, 9.0, sigma2)
    for k, alpha in ((2, 0.13), (1, 0.24)):
        a2.fill_between(grid, mean_l - k * ep_l, mean_l + k * ep_l,
                        color=p.green, alpha=alpha, linewidth=0)
    a2.plot(grid, mean_l, color=p.green, linewidth=2.4)
    a2.set_title("As a DISTRIBUTION, same line", fontsize=9.6)
    a2.text(0.03, 0.97,
            f"sd in the data ($x=-1.9$): {at(ep_l, -1.9):.4f}\n"
            f"sd in the GAP ($x=0$): {at(ep_l, 0.0):.4f}\n"
            f"sd extrapolating ($x=4$): {at(ep_l, 4.0):.4f}",
            transform=a2.transAxes, ha="left", va="top", fontsize=7.9,
            color=p.green, family="monospace")
    a2.text(0.0, -3.9, "narrowest HERE, with no data",
            ha="center", fontsize=8, color=p.amber, family="monospace")

    # --- panel 3: the distribution view with a flexible model ------------------
    centres = np.linspace(-3.2, 3.2, 14)
    scale = 0.55

    def rbf(t):
        return np.exp(-0.5 * ((t[:, None] - centres[None, :]) / scale) ** 2)

    mean_r, ep_r = band(rbf(x), rbf(grid), 1.0, 0.12)
    for k, alpha in ((2, 0.13), (1, 0.24)):
        a3.fill_between(grid, mean_r - k * ep_r, mean_r + k * ep_r,
                        color=p.purple, alpha=alpha, linewidth=0)
    a3.plot(grid, mean_r, color=p.purple, linewidth=2.4)
    a3.set_title("As a DISTRIBUTION, flexible model", fontsize=9.6)
    a3.text(0.03, 0.97,
            f"sd in the data ($x=-1.9$): {at(ep_r, -1.9):.4f}\n"
            f"sd in the GAP ($x=0$): {at(ep_r, 0.0):.4f}\n"
            f"that is {at(ep_r, 0.0) / at(ep_r, -1.9):.2f}x wider",
            transform=a3.transAxes, ha="left", va="top", fontsize=7.9,
            color=p.purple, family="monospace")
    a3.text(0.0, -3.9, "now it says \"I don't know\"", ha="center", fontsize=8,
            color=p.purple, family="monospace")

    fig.suptitle(
        "A model is a function or a distribution, and the choice decides what "
        "questions you may ask",
        y=0.99, fontsize=10, color=p.fg)
    fig.text(
        0.5, 0.005,
        "One dataset with a hole in the middle. The function view gives a number "
        f"and nothing else. Switching to a distribution buys error bars, but for a "
        f"straight line\nthey are NARROWEST in the gap "
        f"({at(ep_l, 0.0):.3f} against {at(ep_l, -1.9):.3f} inside the data) — a "
        f"line is pinned at the centroid whether data is there or not. Only the "
        f"flexible model widens\nwhere the data ran out, by "
        f"{at(ep_r, 0.0) / at(ep_r, -1.9):.1f} times. So the vocabulary lets you "
        "ask about uncertainty; the model class decides the answer. $\\S9.1$ and "
        "$\\S9.2$ are where this is built.",
        ha="center", va="bottom", fontsize=8.1, color=p.muted)


FIGURES = [
    figure("learning-is-not-memorising", learning_is_not_memorising,
           size=(11.8, 4.8), axes=False),
    figure("three-views-of-a-vector", three_views_of_a_vector,
           size=(12.6, 4.5), axes=False),
    figure("function-view-versus-distribution-view",
           function_view_versus_distribution_view, size=(14.0, 4.9),
           axes=False),
]
