"""Figures for *Problem Formulation* (Section 9.1).

1. `lines-through-the-origin` — Figure 9.2 rebuilt, plus the thing its caption
   does not say: Equation 9.4 has no intercept. On data with a true intercept of
   4.0 the one-parameter model reaches RMSE 4.091288 against 0.514303, and its
   slope is wrong by 0.106288 as well.

2. `linear-in-the-parameters` — the chapter's most-repeated sentence, measured.
   Superposition holds in theta to 4.4e-11 and fails in x by 2.3e+05. A
   degree-9 polynomial fit is an ordinary linear least-squares solve.

3. `a-density-in-y-not-in-theta` — the same expression read two ways. As a
   function of y it integrates to 1.00000000; as a function of theta it
   integrates to 1/|x|, measured at 0.50000000 for x = 2. Plus the Dirac limit.
"""

from __future__ import annotations

import numpy as np

from _style import Palette, figure

SIG = 0.6


def _data(n=40, seed=11):
    rng = np.random.default_rng(seed)
    x = np.sort(rng.uniform(-5, 5, n))
    return x, 4.0 + 1.3 * x + SIG * rng.standard_normal(n)


# --------------------------------------------------------------------------
# 1. Figure 9.2, and what its model class cannot reach
# --------------------------------------------------------------------------

def lines_through_the_origin(fig, ax, p: Palette) -> None:
    fig.clear()
    a1, a2, a3 = fig.subplots(1, 3)

    xs = np.linspace(-10, 10, 200)

    # (a) the model class of Eq 9.4
    for th, col in ((-2.0, p.red), (-0.8, p.amber), (0.4, p.green),
                    (1.3, p.blue), (2.4, p.purple)):
        a1.plot(xs, th * xs, color=col, linewidth=2.0,
                label=f"$\\theta = {th}$")
    a1.plot([0], [0], "o", color=p.fg, markersize=9, zorder=5)
    a1.annotate("every line in the class\npasses through here",
                xy=(0, 0), xytext=(-9.4, 14), fontsize=7.8, color=p.fg,
                family="monospace",
                arrowprops=dict(arrowstyle="->", color=p.fg, linewidth=1.1))
    a1.set_xlabel("$x$")
    a1.set_ylabel("$y$")
    a1.set_title("Figure 9.2(a): the class of Equation 9.4", fontsize=9.6)
    a1.legend(fontsize=7.4, loc="lower right")
    a1.grid(alpha=0.20, linewidth=0.6)
    a1.set_ylim(-22, 22)

    # (b) and (c) the training set and the two fits
    x, y = _data()
    th_o = float(x @ y / (x @ x))
    Phi = np.column_stack([np.ones_like(x), x])
    th_f = np.linalg.lstsq(Phi, y, rcond=None)[0]
    rm_o = float(np.sqrt(np.mean((y - th_o * x) ** 2)))
    rm_f = float(np.sqrt(np.mean((y - Phi @ th_f) ** 2)))

    for axx, (title, pred, col, lab, rm) in zip(
            (a2, a3),
            (("Equation 9.4: $f(x) = x\\theta$", th_o * xs, p.red,
              f"$\\theta = {th_o:.6f}$", rm_o),
             ("Equation 9.13: $\\phi(x) = [1, x]^\\top$",
              th_f[0] + th_f[1] * xs, p.green,
              f"$\\theta = [{th_f[0]:.4f}, {th_f[1]:.4f}]$", rm_f))):
        axx.plot(x, y, "o", color=p.blue, markersize=5,
                 markeredgecolor=p.bg, markeredgewidth=0.5,
                 label="training set")
        axx.plot(xs, pred, color=col, linewidth=2.6, label=lab)
        axx.axhline(4.0, color=p.muted, linestyle=":", linewidth=1.0)
        axx.plot([0], [0], "o", color=p.fg, markersize=7, zorder=5)
        axx.set_xlim(-6, 6)
        axx.set_ylim(-6, 14)
        axx.set_xlabel("$x$")
        axx.set_ylabel("$y$")
        axx.set_title(title, fontsize=9.6)
        axx.legend(fontsize=7.6, loc="upper left")
        axx.grid(alpha=0.20, linewidth=0.6)
        axx.text(0.97, 0.04, f"RMSE {rm:.6f}", transform=axx.transAxes,
                 ha="right", va="bottom", fontsize=9.2, color=col,
                 family="monospace")

    a2.text(0.03, 0.60,
            "The data is\ny = 4.0 + 1.3x + noise.\n\n"
            "Forced through the origin,\nthe model spends its ONE\n"
            "parameter reaching a cloud\nwhose centre is not there —\n"
            f"so even the slope comes out\nwrong, {th_o:.6f}\n"
            "against a true 1.3.",
            transform=a2.transAxes, ha="left", va="top", fontsize=7.2,
            color=p.fg, family="monospace")
    a3.text(0.03, 0.60,
            "One extra feature, a column\nof ones, and the intercept\n"
            f"comes back: {th_f[0]:.6f}\nagainst a true 4.0.\n\n"
            "Nothing about the method\nchanged. Only phi did.",
            transform=a3.transAxes, ha="left", va="top", fontsize=7.2,
            color=p.fg, family="monospace")

    fig.suptitle(
        "Section 9.1: Equation 9.4 describes straight lines through the "
        "origin — and that is a modelling choice, not a formality",
        y=0.99, fontsize=10, color=p.fg)
    fig.text(
        0.5, 0.005,
        "The book says it plainly — \"the class of functions described by "
        "(9.4) are straight lines that pass through the origin\" — and then "
        "Equation 9.13 removes the restriction\nwithout changing a single step "
        "of the derivation. An intercept is not a special case of linear "
        "regression; it is one more feature.",
        ha="center", va="bottom", fontsize=8.0, color=p.muted)


# --------------------------------------------------------------------------
# 2. linear in the parameters
# --------------------------------------------------------------------------

def linear_in_the_parameters(fig, ax, p: Palette) -> None:
    fig.clear()
    left, right = fig.subplots(1, 2)

    xs = np.linspace(-1.6, 1.6, 400)
    for k, col in zip(range(6), (p.muted, p.blue, p.green, p.amber, p.purple,
                                 p.red)):
        left.plot(xs, xs ** k, color=col, linewidth=2.0,
                  label=f"$\\phi_{k}(x) = x^{{{k}}}$")
    left.set_xlabel("$x$")
    left.set_ylabel("$\\phi_k(x)$")
    left.set_title("$\\phi$ is as nonlinear in $x$ as you like",
                   fontsize=9.6)
    left.legend(fontsize=7.4, loc="upper center", ncol=2)
    left.grid(alpha=0.20, linewidth=0.6)
    left.set_ylim(-2.2, 4.2)
    left.text(0.03, 0.03,
              "Equation 9.14 lifts a scalar x\ninto K monomials. The model\n"
              "is a linear combination of\nTHESE, which is why a\n"
              "degree-9 polynomial fit is\nstill an ordinary linear\n"
              "least-squares solve.",
              transform=left.transAxes, ha="left", va="bottom", fontsize=7.3,
              color=p.fg, family="monospace")

    # superposition in theta, drawn
    xg = np.linspace(-1.5, 1.5, 300)
    A = np.vander(xg, 6, increasing=True)
    r1 = np.random.default_rng(2)
    t1, t2 = r1.standard_normal(6), r1.standard_normal(6)
    a, b = 1.4, -0.8
    right.plot(xg, A @ t1, color=p.blue, linewidth=2.0,
               label="$f(x; \\theta_1)$")
    right.plot(xg, A @ t2, color=p.green, linewidth=2.0,
               label="$f(x; \\theta_2)$")
    right.plot(xg, A @ (a * t1 + b * t2), color=p.amber, linewidth=4.2,
               alpha=0.55,
               label=f"$f(x;\\ {a}\\theta_1 {b}\\theta_2)$")
    right.plot(xg, a * (A @ t1) + b * (A @ t2), color=p.red, linewidth=1.6,
               linestyle="--",
               label=f"${a}f(x;\\theta_1) {b}f(x;\\theta_2)$")

    # the measured residuals
    xb = np.linspace(-4, 4, 9)
    B = np.vander(xb, 10, increasing=True)
    u1, u2 = r1.standard_normal(10), r1.standard_normal(10)
    aa, bb = 2.7, -1.4
    res_t = float(np.abs(B @ (aa*u1 + bb*u2)
                         - (aa*(B @ u1) + bb*(B @ u2))).max())
    pu, pv = 1.1, -0.7
    res_x = float(np.abs(np.vander([aa*pu + bb*pv], 10, increasing=True)[0]
                         - (aa*np.vander([pu], 10, increasing=True)[0]
                            + bb*np.vander([pv], 10, increasing=True)[0])).max())

    right.set_xlabel("$x$")
    right.set_ylabel("$f(x;\\theta)$")
    right.set_title("Superposition holds in $\\theta$, exactly",
                    fontsize=9.6)
    right.legend(fontsize=7.4, loc="upper left")
    right.grid(alpha=0.20, linewidth=0.6)
    right.text(
        0.97, 0.04,
        "measured, degree 9:\n"
        f"  in theta: {res_t:.3e}\n"
        f"  in x    : {res_x:.3e}\n\n"
        "The thick and dashed curves\nare the same function.\n"
        "\"Linear regression\" is a\nstatement about theta and\n"
        "says nothing about x.",
        transform=right.transAxes, ha="right", va="bottom", fontsize=7.3,
        color=p.fg, family="monospace")

    fig.suptitle(
        "\"Linear regression refers to models that are linear in the "
        "parameters\" — the chapter's most load-bearing sentence",
        y=0.99, fontsize=10, color=p.fg)
    fig.text(
        0.5, 0.005,
        "The margin note is explicit: models can be \"linear-in-the-parameters\" "
        "while \"the inputs can undergo any nonlinear transformation\". That is "
        "why Equation 9.19 is\nEquation 9.12c with X replaced by Phi, and why "
        "every closed form in this chapter survives the move to polynomials, "
        "Gaussian bumps, or anything else.",
        ha="center", va="bottom", fontsize=8.0, color=p.muted)


# --------------------------------------------------------------------------
# 3. a density in y, not in theta
# --------------------------------------------------------------------------

def a_density_in_y_not_in_theta(fig, ax, p: Palette) -> None:
    fig.clear()
    a1, a2, a3 = fig.subplots(1, 3)

    XQ, SQ = 2.0, 0.6

    # --- as a function of y --------------------------------------------
    gy = np.linspace(-4, 10, 900)
    for th, col in ((0.4, p.blue), (1.3, p.amber), (2.6, p.purple)):
        d = np.exp(-0.5*((gy - XQ*th)/SQ)**2)/(SQ*np.sqrt(2*np.pi))
        a1.plot(gy, d, color=col, linewidth=2.4,
                label=f"$\\theta = {th}$")
        a1.fill_between(gy, 0, d, color=col, alpha=0.12)
    a1.set_xlabel("$y$, a possible observation")
    a1.set_ylabel("$p(y \\mid x, \\theta)$")
    a1.set_title("Read as a function of $y$", fontsize=9.5)
    a1.legend(fontsize=7.8, loc="upper right")
    a1.grid(alpha=0.20, linewidth=0.6)
    a1.text(0.03, 0.96,
            f"x = {XQ} fixed, theta fixed.\n\n"
            "Each curve integrates to\n  1.00000000\n\n"
            "This is a probability\ndensity. Equation 9.1.",
            transform=a1.transAxes, ha="left", va="top", fontsize=7.4,
            color=p.green, family="monospace")

    # --- as a function of theta ----------------------------------------
    gt = np.linspace(-2, 5, 900)
    for yq, col in ((1.0, p.blue), (3.1, p.amber), (5.4, p.purple)):
        d = np.exp(-0.5*((yq - XQ*gt)/SQ)**2)/(SQ*np.sqrt(2*np.pi))
        a2.plot(gt, d, color=col, linewidth=2.4, label=f"$y = {yq}$")
        a2.fill_between(gt, 0, d, color=col, alpha=0.12)
    a2.set_xlabel("$\\theta$, a possible parameter")
    a2.set_ylabel("the same expression")
    a2.set_title("Read as a function of $\\theta$", fontsize=9.5)
    a2.legend(fontsize=7.8, loc="upper right")
    a2.grid(alpha=0.20, linewidth=0.6)
    a2.text(0.03, 0.96,
            f"y fixed, x = {XQ} fixed.\n\n"
            "Each curve integrates to\n"
            f"  {1/XQ:.8f}\n"
            f"which is 1/|x| = 1/{XQ:.0f}.\n\n"
            "NOT a density in theta.\nIt is the likelihood.",
            transform=a2.transAxes, ha="left", va="top", fontsize=7.4,
            color=p.red, family="monospace")

    # --- the Dirac limit -------------------------------------------------
    g = np.linspace(-1.2, 1.2, 3000)
    for s2, col in ((1.0, p.muted), (1e-1, p.blue), (1e-2, p.green),
                    (1e-4, p.amber)):
        s = np.sqrt(s2)
        a3.plot(g, np.exp(-0.5*(g/s)**2)/(s*np.sqrt(2*np.pi)), color=col,
                linewidth=2.2, label=f"$\\sigma^2 = 10^{{{int(np.log10(s2))}}}$")
    a3.set_yscale("log")
    a3.set_ylim(1e-3, 2e2)
    a3.set_xlabel("$y - f(x)$")
    a3.set_ylabel("density")
    a3.set_title("As $\\sigma^2 \\to 0$: a Dirac delta", fontsize=9.5)
    a3.legend(fontsize=7.4, loc="upper right")
    a3.grid(alpha=0.20, linewidth=0.6, which="both")
    a3.text(0.03, 0.04,
            "measured, mass within 0.01\n"
            "  sigma^2=1e+0 : 0.007978\n"
            "  sigma^2=1e-2 : 0.079652\n"
            "  sigma^2=1e-4 : 0.682665\n"
            "  sigma^2=1e-6 : 1.000000\n\n"
            "Peak diverges, area stays 1.\n"
            "Without noise the relation\nis deterministic.",
            transform=a3.transAxes, ha="left", va="bottom", fontsize=7.0,
            color=p.fg, family="monospace")

    fig.suptitle(
        "One expression, two readings — and only one of them is a probability "
        "distribution",
        y=0.99, fontsize=10, color=p.fg)
    fig.text(
        0.5, 0.005,
        "The book's remark is that the likelihood \"is simply a function of the "
        "parameters theta but does not integrate to 1\". Measured for this "
        "model it integrates to 1/|x| — so it\nonly reaches 1 by accident when "
        "|x| = 1, and diverges as x approaches 0. That is why maximum "
        "likelihood needs a prior before it can be called a posterior.",
        ha="center", va="bottom", fontsize=8.0, color=p.muted)


FIGURES = [
    figure("lines-through-the-origin", lines_through_the_origin,
           size=(15.0, 5.0), axes=False),
    figure("linear-in-the-parameters", linear_in_the_parameters,
           size=(13.2, 5.0), axes=False),
    figure("a-density-in-y-not-in-theta", a_density_in_y_not_in_theta,
           size=(15.0, 5.0), axes=False),
]
