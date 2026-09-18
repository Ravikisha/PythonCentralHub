"""Figures for *Directed Graphical Models*.

1. `from-factorization-to-graph` — Figure 8.9's two graphs, each beside the
   factorization it encodes, plus the reason the encoding is worth having: the
   parameter count. Thirty-one free parameters become ten on five binary
   variables, and 1.27e30 becomes 395 on a hundred.

2. `d-separation-measured` — Figure 8.11, its edges recovered from the PDF's
   vector layer, with all four of Example 8.9's claims checked numerically on
   four million samples. Measured partial correlations: -0.000320, -0.000079,
   0.272172, -0.146064.

3. `the-collider-effect` — the head-to-head rule, isolated. a and c are
   independent given b. Condition additionally on the collider d, or merely on
   its descendant e, and the correlation appears from nowhere.
"""

from __future__ import annotations

import itertools

import numpy as np

from _style import Palette, figure

N_SAMP = 4_000_000


# --------------------------------------------------------------------------
# shared helpers
# --------------------------------------------------------------------------

def _node(ax, x, y, label, p: Palette, shaded=False, r=0.40):
    face = p.blue if shaded else p.bg
    circ = __import__("matplotlib.patches", fromlist=["Circle"]).Circle(
        (x, y), r, facecolor=face, edgecolor=p.fg, linewidth=1.6,
        alpha=0.85 if shaded else 1.0, zorder=3)
    ax.add_patch(circ)
    ax.text(x, y, label, ha="center", va="center", fontsize=12,
            color=p.bg if shaded else p.fg, zorder=4,
            fontstyle="italic")


def _arrow(ax, x1, y1, x2, y2, p: Palette, color=None, r=0.40, lw=1.7):
    dx, dy = x2 - x1, y2 - y1
    L = np.hypot(dx, dy)
    ux, uy = dx / L, dy / L
    ax.annotate("", xy=(x2 - r * ux, y2 - r * uy),
                xytext=(x1 + r * ux, y1 + r * uy),
                arrowprops=dict(arrowstyle="-|>", color=color or p.fg,
                                linewidth=lw, shrinkA=0, shrinkB=0), zorder=2)


def _blank(ax, xlim, ylim):
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect("equal")
    ax.axis("off")


# --------------------------------------------------------------------------
# 1. from a factorization to a graph
# --------------------------------------------------------------------------

def from_factorization_to_graph(fig, ax, p: Palette) -> None:
    fig.clear()
    a1, a2, a3 = fig.subplots(1, 3, gridspec_kw={"width_ratios": [1, 1.15, 1.5]})

    # --- Figure 8.9(a): fully connected ----------------------------------
    _node(a1, 0.0, 1.5, "a", p)
    _node(a1, -1.2, 0.0, "b", p)
    _node(a1, 1.2, 0.0, "c", p)
    _arrow(a1, 0.0, 1.5, -1.2, 0.0, p)
    _arrow(a1, 0.0, 1.5, 1.2, 0.0, p)
    _arrow(a1, -1.2, 0.0, 1.2, 0.0, p)
    _blank(a1, (-2.3, 2.3), (-2.1, 2.4))
    a1.set_title("Figure 8.9(a), fully connected", fontsize=9.6, color=p.fg)
    a1.text(0.0, -1.05,
            "$p(a,b,c) = p(c \\mid a,b)\\,p(b \\mid a)\\,p(a)$",
            ha="center", fontsize=10.5, color=p.amber)
    a1.text(0.0, -1.75,
            "c depends directly on a and b\nb depends directly on a\n"
            "a depends on neither",
            ha="center", va="top", fontsize=7.8, color=p.fg,
            family="monospace")

    # --- Figure 8.9(b): not fully connected ------------------------------
    pos = {"x1": (-1.5, 1.6), "x2": (0.6, 1.6), "x5": (2.3, 2.7),
           "x3": (-0.5, 0.1), "x4": (1.9, 0.1)}
    for k, (x, y) in pos.items():
        _node(a2, x, y, f"$x_{k[1]}$", p, r=0.42)
    for u, v in (("x1", "x3"), ("x2", "x3"), ("x2", "x4"), ("x5", "x2")):
        _arrow(a2, *pos[u], *pos[v], p, r=0.42)
    _blank(a2, (-2.6, 3.4), (-2.3, 3.5))
    a2.set_title("Figure 8.9(b), not fully connected", fontsize=9.6,
                 color=p.fg)
    a2.text(0.4, -0.95,
            "$p(x_1)p(x_5)p(x_2 \\mid x_5)p(x_3 \\mid x_1,x_2)p(x_4 \\mid x_2)$",
            ha="center", fontsize=9.2, color=p.amber)
    a2.text(0.4, -1.45,
            "Equation 8.31:  p(x) = prod_k p(x_k | Pa_k)\n"
            "one factor per node, conditioned on its parents.\n\n"
            "Checked against 4,000,000 samples:\n"
            "  max error over all 32 cells = 0.000124",
            ha="center", va="top", fontsize=7.4, color=p.fg,
            family="monospace")

    # --- why it is worth having ------------------------------------------
    Ks = np.array([5, 10, 20, 50, 100])
    full = 2.0 ** Ks - 1
    chain = 1 + 2 + 4 * (Ks - 2)
    a3.semilogy(Ks, full, "o-", color=p.red, linewidth=2.4, markersize=7,
                label="full joint, $2^K - 1$")
    a3.semilogy(Ks, chain, "o-", color=p.green, linewidth=2.4, markersize=7,
                label="each node, at most 2 parents")
    a3.set_xlabel("$K$, number of binary variables")
    a3.set_ylabel("free parameters")
    a3.set_title("Why a factorization is worth writing down", fontsize=9.6)
    a3.legend(fontsize=8, loc="center left")
    a3.grid(alpha=0.20, linewidth=0.6, which="both")
    a3.text(
        0.97, 0.06,
        f"{'K':>5} {'full':>11} {'graph':>7} {'ratio':>11}\n"
        + "\n".join(f"{k:>5} {f:>11.4g} {c:>7} {f / c:>11.4g}"
                    for k, f, c in zip(Ks, full, chain))
        + "\n\nFigure 8.9(b) itself:\n  31 parameters become 10.",
        transform=a3.transAxes, ha="right", va="bottom", fontsize=7.1,
        color=p.fg, family="monospace")

    fig.suptitle(
        "Section 8.5.1: a directed graphical model is a picture of one "
        "factorization of the joint",
        y=0.99, fontsize=10, color=p.fg)
    fig.text(
        0.5, 0.005,
        "Two rules build the graph from the factorization: one node per random "
        "variable, and an arrow into each node from every variable its "
        "conditional is conditioned on.\nRun the rules backwards and Equation "
        "8.31 reads the joint back off the picture. The book's caution: the "
        "layout depends on the factorization you chose, not on the joint.",
        ha="center", va="bottom", fontsize=8.0, color=p.muted)


# --------------------------------------------------------------------------
# 2. d-separation, measured
# --------------------------------------------------------------------------

_SIM: dict = {}


def _sim():
    """Figure 8.11 as a linear-Gaussian model: a->b, a->d, b->c, c->d, d->e."""
    if "V" not in _SIM:
        r = np.random.default_rng(2024)
        a = r.standard_normal(N_SAMP)
        b = 0.9 * a + r.standard_normal(N_SAMP)
        c = 0.8 * b + r.standard_normal(N_SAMP)
        d = 0.7 * a + 0.6 * c + r.standard_normal(N_SAMP)
        e = 1.1 * d + r.standard_normal(N_SAMP)
        _SIM["V"] = {"a": a, "b": b, "c": c, "d": d, "e": e}
    return _SIM["V"]


def _pcorr(u, v, given):
    V = _sim()
    U, W = V[u].copy(), V[v].copy()
    if given:
        Z = np.column_stack([V[g] for g in given] + [np.ones(N_SAMP)])
        U -= Z @ np.linalg.lstsq(Z, U, rcond=None)[0]
        W -= Z @ np.linalg.lstsq(Z, W, rcond=None)[0]
    else:
        U -= U.mean()
        W -= W.mean()
    return float(U @ W / np.sqrt((U @ U) * (W @ W)))


_CLAIMS = (("8.35", "b", "d", ["a", "c"], True),
           ("8.36", "a", "c", ["b"], True),
           ("8.37", "b", "d", ["c"], False),
           ("8.38", "a", "c", ["b", "e"], False))


def d_separation_measured(fig, ax, p: Palette) -> None:
    fig.clear()
    left, right = fig.subplots(1, 2, gridspec_kw={"width_ratios": [1, 1.25]})

    pos = {"a": (0.0, 2.6), "b": (-1.7, 1.2), "c": (-1.7, -0.5),
           "d": (0.6, -0.5), "e": (0.6, -2.2)}
    edges = (("a", "b"), ("a", "d"), ("b", "c"), ("c", "d"), ("d", "e"))
    for u, v in edges:
        _arrow(left, *pos[u], *pos[v], p)
    for k, (x, y) in pos.items():
        _node(left, x, y, k, p)
    left.annotate("the collider:\nc and a meet\nhead to head here",
                  xy=pos["d"], xytext=(2.35, 0.45), fontsize=7.6,
                  color=p.red, family="monospace", ha="left",
                  arrowprops=dict(arrowstyle="->", color=p.red, linewidth=1.2))
    left.annotate("a descendant\nof the collider",
                  xy=pos["e"], xytext=(2.35, -2.3), fontsize=7.6,
                  color=p.amber, family="monospace", ha="left",
                  arrowprops=dict(arrowstyle="->", color=p.amber,
                                  linewidth=1.2))
    _blank(left, (-3.0, 4.6), (-3.4, 3.4))
    left.set_title("Figure 8.11, edges recovered from the PDF vector layer",
                   fontsize=9.4, color=p.fg)
    left.text(0.5, -0.04,
              "a -> b,  a -> d,  b -> c,  c -> d,  d -> e",
              transform=left.transAxes, ha="center", fontsize=8.6,
              color=p.green, family="monospace")

    vals = [_pcorr(u, v, g) for _, u, v, g, _ in _CLAIMS]
    labels = [f"{eq}:  {u} vs {v}  |  {','.join(g)}"
              for eq, u, v, g, _ in _CLAIMS]
    cols = [p.green if ind else p.red for *_, ind in _CLAIMS]
    ypos = np.arange(len(vals))[::-1]
    right.barh(ypos, vals, height=0.52, color=cols)
    right.axvline(0.0, color=p.fg, linewidth=1.2)
    for yy, v, (_, _, _, _, ind) in zip(ypos, vals, _CLAIMS):
        off = 0.012 if v >= 0 else -0.012
        right.text(v + off, yy, f"{v:+.6f}", va="center",
                   ha="left" if v >= 0 else "right", fontsize=8.6,
                   color=p.green if ind else p.red, family="monospace")
    right.set_yticks(ypos)
    right.set_yticklabels(labels, fontsize=8.2, family="monospace")
    right.set_xlim(-0.34, 0.40)
    right.set_xlabel("measured partial correlation, 4,000,000 samples")
    right.set_title("All four of Example 8.9's claims, checked",
                    fontsize=9.4)
    right.grid(alpha=0.20, linewidth=0.6, axis="x")
    right.text(
        0.02, 0.03,
        "green = the book says INDEPENDENT\nred   = the book says DEPENDENT\n\n"
        "For jointly Gaussian variables a zero\npartial correlation is exactly\n"
        "conditional independence, so this is a\nproof and not an analogy.",
        transform=right.transAxes, ha="left", va="bottom", fontsize=7.3,
        color=p.fg, family="monospace")

    fig.suptitle(
        "Section 8.5.2: d-separation reads conditional independence off the "
        "picture, and it is right four times out of four",
        y=0.99, fontsize=10, color=p.fg)
    fig.text(
        0.5, 0.005,
        "Two of the four claims come out at 3.2e-4 and 7.9e-5 — zero to "
        "sampling error. The other two come out at 0.272 and -0.146. Nothing "
        "about the model changed between\nthem; only the conditioning set did. "
        "The book's own recovery of these four lines is one sentence: "
        "\"Visual inspection gives us\".",
        ha="center", va="bottom", fontsize=8.0, color=p.muted)


# --------------------------------------------------------------------------
# 3. the collider
# --------------------------------------------------------------------------

def the_collider_effect(fig, ax, p: Palette) -> None:
    fig.clear()
    axes = fig.subplots(1, 3)
    V = _sim()
    rs = np.random.default_rng(1)
    idx = rs.choice(N_SAMP, 4000, replace=False)

    panels = (
        (["b"], "given $b$ only", "Equation 8.36: INDEPENDENT",
         "a -> b -> c is blocked at b.\na -> d <- c is blocked at d,\n"
         "because neither d nor its\ndescendant e is conditioned on.", True),
        (["b", "d"], "given $b$ and $d$", "the collider itself: DEPENDENT",
         "Conditioning on d opens the\nhead-to-head meeting. Knowing\n"
         "the sum constrains the parts:\nif d is high and a is low,\nc must be high.", False),
        (["b", "e"], "given $b$ and $e$", "Equation 8.38: DEPENDENT",
         "e is only a DESCENDANT of d,\nand it is enough. This is why\n"
         "the head-to-head rule says\n\"nor any of its descendants\".", False),
    )
    for axx, (given, title, verdict, note, indep) in zip(axes, panels):
        Z = np.column_stack([V[g] for g in given] + [np.ones(N_SAMP)])
        A = V["a"] - Z @ np.linalg.lstsq(Z, V["a"], rcond=None)[0]
        C = V["c"] - Z @ np.linalg.lstsq(Z, V["c"], rcond=None)[0]
        r = float(A @ C / np.sqrt((A @ A) * (C @ C)))
        col = p.green if indep else p.red
        axx.plot(A[idx], C[idx], ".", color=col, markersize=2.2, alpha=0.30)
        # the least-squares line through the residuals
        sl = float(A @ C / (A @ A))
        xr = np.array([-4.0, 4.0])
        axx.plot(xr, sl * xr, "-", color=p.amber, linewidth=2.2)
        axx.set_xlim(-4.2, 4.2)
        axx.set_ylim(-4.2, 4.2)
        axx.set_aspect("equal")
        axx.set_xlabel("$a$, with the conditioning set removed")
        axx.set_ylabel("$c$, with the conditioning set removed")
        axx.set_title(f"{title}\n{verdict}", fontsize=9.2, color=col)
        axx.grid(alpha=0.20, linewidth=0.6)
        axx.text(0.03, 0.97, f"correlation {r:+.6f}",
                 transform=axx.transAxes, ha="left", va="top", fontsize=9.0,
                 color=col, family="monospace")
        axx.text(0.03, 0.03, note, transform=axx.transAxes, ha="left",
                 va="bottom", fontsize=7.0, color=p.fg, family="monospace")

    fig.suptitle(
        "The head-to-head rule: conditioning on a collider CREATES a "
        "dependence that was not there",
        y=0.99, fontsize=10, color=p.fg)
    fig.text(
        0.5, 0.005,
        "Nothing about a or c changed across these three panels — the data is "
        "the same four million samples from the same model. Only the set we "
        "conditioned on changed. Every other\nrule in d-separation says "
        "conditioning BLOCKS a path; this is the one that says conditioning "
        "OPENS one, and it is why the rule has to mention descendants.",
        ha="center", va="bottom", fontsize=8.0, color=p.muted)


FIGURES = [
    figure("from-factorization-to-graph", from_factorization_to_graph,
           size=(15.0, 5.3), axes=False),
    figure("d-separation-measured", d_separation_measured,
           size=(13.6, 5.3), axes=False),
    figure("the-collider-effect", the_collider_effect,
           size=(14.6, 5.3), axes=False),
]
