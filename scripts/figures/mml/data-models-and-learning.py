"""Figures for *Data, Models, and Learning*.

1. `tables-8-1-to-8-2` — the book's own two tables side by side, with the four
   encoding decisions marked. Turning a spreadsheet into vectors is a sequence of
   choices, and each one is a modelling assumption rather than a formatting step.

2. `function-versus-distribution` — the book's Figures 8.2 and 8.3. The same
   predictor as a function (one number at x = 60) and as a distribution (a
   Gaussian over values). Fitted to Table 8.2's five points, so the numbers are
   the book's data rather than an illustration.

3. `three-algorithmic-phases` — Section 8.1.4's prediction / training / model
   selection, with what is fixed and what is free at each stage, and the naming
   collision the book warns about.
"""

from __future__ import annotations

import numpy as np
from matplotlib.patches import FancyArrowPatch, Rectangle

from _style import Palette, figure

# Table 8.1, verbatim.
RAW = [
    ("Aditya", "M", "MSc", "W21BG", 36, 89563),
    ("Bob", "M", "PhD", "EC1A1BA", 47, 123543),
    ("Chloe", "F", "BEcon", "SW1A1BH", 26, 23989),
    ("Daisuke", "M", "BSc", "SE207AT", 68, 138769),
    ("Elisabeth", "F", "MBA", "SE10AA", 33, 113888),
]
# Table 8.2, verbatim.
NUM = [
    (-1, 2, 51.5073, 0.1290, 36, 89.563),
    (-1, 3, 51.5074, 0.1275, 47, 123.543),
    (+1, 1, 51.5071, 0.1278, 26, 23.989),
    (-1, 1, 51.5075, 0.1281, 68, 138.769),
    (+1, 2, 51.5074, 0.1278, 33, 113.888),
]
AGE = np.array([r[4] for r in NUM], dtype=float)
SAL = np.array([r[5] for r in NUM], dtype=float)


def _fit():
    X = np.column_stack([np.ones_like(AGE), AGE])
    th = np.linalg.lstsq(X, SAL, rcond=None)[0]
    r = SAL - X @ th
    return th, float(np.sqrt(r @ r / len(SAL)))


def tables_8_1_to_8_2(fig, ax, p: Palette) -> None:
    """Table 8.1 to Table 8.2, and the decisions in between."""
    fig.clear()
    top, bot = fig.subplots(2, 1, height_ratios=[1.0, 1.0])

    for axx in (top, bot):
        axx.axis("off")
        axx.set_xlim(0, 10)

    # --- Table 8.1 -------------------------------------------------------
    top.set_ylim(0, 3.4)
    top.text(0.05, 3.15, "Table 8.1 — as it arrives", fontsize=10,
             color=p.red, weight="bold")
    heads1 = ("Name", "Gender", "Degree", "Postcode", "Age", "Salary")
    xs1 = (0.1, 1.5, 2.7, 3.9, 5.6, 6.5)
    for hx, h in zip(xs1, heads1):
        top.text(hx, 2.72, h, fontsize=8.6, color=p.fg, weight="bold")
    top.plot([0.05, 7.8], [2.6, 2.6], color=p.grid, linewidth=1.2)
    for k, row in enumerate(RAW):
        y = 2.25 - k * 0.42
        if k % 2 == 0:
            top.add_patch(Rectangle((0.05, y - 0.11), 7.75, 0.38,
                                    facecolor=p.grid, alpha=0.32,
                                    edgecolor="none"))
        for hx, val in zip(xs1, row):
            top.text(hx, y, str(val), fontsize=8.2, color=p.muted,
                     family="monospace")
    top.text(8.1, 1.9,
             "Not one column of this is\na number a model can use.\n\n"
             "Strings, categories, an\nordinal disguised as text,\n"
             "and a location disguised\nas a string.",
             fontsize=8.0, color=p.red, va="center")

    # --- Table 8.2 -------------------------------------------------------
    bot.set_ylim(0, 3.4)
    bot.text(0.05, 3.15, "Table 8.2 — after four decisions", fontsize=10,
             color=p.green, weight="bold")
    heads2 = ("Gender ID", "Degree", "Latitude", "Longitude", "Age",
              "Salary (k)")
    xs2 = (0.1, 1.5, 2.6, 3.9, 5.2, 6.0)
    for hx, h in zip(xs2, heads2):
        bot.text(hx, 2.72, h, fontsize=8.6, color=p.fg, weight="bold")
    bot.plot([0.05, 7.6], [2.6, 2.6], color=p.grid, linewidth=1.2)
    for k, row in enumerate(NUM):
        y = 2.25 - k * 0.42
        if k % 2 == 0:
            bot.add_patch(Rectangle((0.05, y - 0.11), 7.55, 0.38,
                                    facecolor=p.grid, alpha=0.32,
                                    edgecolor="none"))
        fmt = ("{:+d}", "{:d}", "{:.4f}", "{:.4f}", "{:d}", "{:.3f}")
        for hx, val, f in zip(xs2, row, fmt):
            bot.text(hx, y, f.format(val), fontsize=8.2, color=p.fg,
                     family="monospace")
    decisions = [
        ("1. Name DROPPED", "not informative, and it de-identifies the row",
         p.red),
        ("2. Gender to -1 / +1", "0 / 1 would have done; the choice matters "
                                "to a regulariser", p.amber),
        ("3. Degree to 1 / 2 / 3", "asserts an ORDER, and that BEcon = BSc "
                                   "and MBA = MSc", p.purple),
        ("4. Postcode to two numbers", "a string became a location, using "
                                       "domain knowledge", p.green),
    ]
    for k, (name, why, col) in enumerate(decisions):
        bot.text(8.1, 2.62 - k * 0.62, name, fontsize=8.2, color=col,
                 weight="bold")
        bot.text(8.1, 2.62 - k * 0.62 - 0.24, why, fontsize=7.2,
                 color=p.muted)

    fig.suptitle(
        "Turning a table into vectors is a sequence of modelling decisions, "
        "not a formatting step",
        y=0.985, fontsize=10, color=p.fg)
    fig.text(
        0.5, 0.005,
        "Each of the four decisions is reversible on paper and irreversible in "
        "practice: nothing downstream can recover the postcode from a latitude, "
        "or learn that\nan MBA is not an MSc. The book's own advice for anything "
        "left over is to shift and scale every column to zero mean and unit "
        "variance — which is itself a\nfifth decision, and the one that decides "
        "what a regulariser considers a large parameter.",
        ha="center", va="bottom", fontsize=8.2, color=p.muted)


def function_versus_distribution(fig, ax, p: Palette) -> None:
    """Figures 8.2 and 8.3, fitted to the book's own five points."""
    fig.clear()
    left, right = fig.subplots(1, 2)

    th, resid = _fit()
    grid = np.linspace(0.0, 80.0, 400)
    line = th[0] + th[1] * grid
    at60 = th[0] + th[1] * 60.0

    for axx in (left, right):
        axx.plot(AGE, SAL, "o", color=p.blue, markersize=8,
                 markeredgecolor=p.bg, markeredgewidth=1.0,
                 label="Table 8.2, five points", zorder=6)
        axx.plot(grid, line, color=p.fg, linewidth=2.0,
                 label="least-squares fit")
        axx.axvline(60, color=p.grid, linestyle=":", linewidth=1.3)
        axx.set_xlabel("$x$ = age")
        axx.set_xlim(0, 80)
        axx.set_ylim(0, 175)
        axx.grid(alpha=0.18, linewidth=0.6)
    left.set_ylabel("$y$ = annual salary, thousands")

    left.plot([60], [at60], "s", color=p.amber, markersize=12, zorder=8,
              markeredgecolor=p.bg, markeredgewidth=1.0)
    left.annotate(f"$f(60) = {at60:.4f}$\na single number,\n"
                  "and no way to say\nhow much to trust it",
                  xy=(60, at60), xytext=(-92, 34),
                  textcoords="offset points", fontsize=8.2, color=p.amber,
                  family="monospace",
                  arrowprops=dict(arrowstyle="->", color=p.amber,
                                  linewidth=1.1))
    left.set_title("Eq 8.2, a predictor as a FUNCTION", fontsize=9.8)
    left.legend(fontsize=7.8, loc="upper left")

    ys = np.linspace(0, 175, 400)
    dens = np.exp(-0.5 * ((ys - at60) / resid) ** 2)
    right.fill_betweenx(ys, 60, 60 + 13.0 * dens, color=p.green, alpha=0.30,
                        linewidth=0)
    right.plot(60 + 13.0 * dens, ys, color=p.green, linewidth=1.8)
    for k, col in ((1, p.green), (2, p.green)):
        right.plot([57.5, 62.5], [at60 + k * resid] * 2, color=col,
                   linewidth=1.0, alpha=0.7)
        right.plot([57.5, 62.5], [at60 - k * resid] * 2, color=col,
                   linewidth=1.0, alpha=0.7)
    right.plot([60], [at60], "s", color=p.amber, markersize=10, zorder=8)
    right.annotate(f"$p(y \\mid x=60)$\nmean {at60:.2f}\n"
                   f"std {resid:.4f}\n\nnow \"how confident?\"\nis a question "
                   "with\nan answer",
                   xy=(73, at60), xytext=(-4, -74),
                   textcoords="offset points", fontsize=8.2, color=p.green,
                   family="monospace")
    right.set_title("Section 8.1.3, a predictor as a DISTRIBUTION",
                    fontsize=9.8)
    right.legend(fontsize=7.8, loc="upper left")

    fig.suptitle(
        "One fit, two kinds of answer — and only the second can express doubt",
        y=0.99, fontsize=10, color=p.fg)
    fig.text(
        0.5, 0.005,
        f"Both panels are the same least-squares line through Table 8.2's five "
        f"points: intercept {th[0]:.6f}, slope {th[1]:.6f}. The function view "
        f"returns {at60:.4f} at\nage 60 and stops. The distribution view returns "
        f"a Gaussian of the same mean with standard deviation {resid:.4f}, which "
        "is the residual scale of a fit to FIVE\npoints — so the honest answer "
        "at age 60 is a very wide one. The book's Figure 8.2 draws an "
        "illustrative line with $f(60) = 100$ rather than this fitted one.",
        ha="center", va="bottom", fontsize=8.0, color=p.muted)


def three_algorithmic_phases(fig, ax, p: Palette) -> None:
    """Section 8.1.4's three phases, and what is fixed in each."""
    fig.clear()
    ax = fig.add_subplot(111)
    ax.axis("off")
    ax.set_xlim(0, 10)
    ax.set_ylim(-0.4, 6.6)

    phases = [
        ("3. Model selection", "hyperparameter tuning",
         "the MODEL CLASS and hyperparameters are free",
         "data + a search over classes", "Section 8.6", p.purple),
        ("2. Training", "parameter estimation",
         "the model class is FIXED, the parameters are free",
         "training data", "Sections 8.2, 8.3, 8.4", p.amber),
        ("1. Prediction", "inference, for a probabilistic model",
         "everything is FIXED; only the input is new",
         "one unseen test point", "Chapters 9 to 12", p.green),
    ]
    for k, (name, alias, free, needs, where, col) in enumerate(phases):
        y = 0.5 + k * 1.95
        ax.add_patch(Rectangle((0.3, y), 6.4, 1.55, facecolor=col,
                               alpha=0.14, edgecolor=col, linewidth=1.6))
        ax.text(0.55, y + 1.18, name, fontsize=11, color=col, weight="bold")
        ax.text(0.55, y + 0.84, f"also called: {alias}", fontsize=8.0,
                color=p.muted, family="monospace")
        ax.text(0.55, y + 0.48, free, fontsize=8.8, color=p.fg)
        ax.text(0.55, y + 0.16, f"needs: {needs}", fontsize=8.0,
                color=p.muted, family="monospace")
        ax.text(6.95, y + 0.72, where, fontsize=8.6, color=col)
        if k < 2:
            ax.add_patch(FancyArrowPatch((3.5, y + 1.62), (3.5, y + 1.90),
                                         arrowstyle="-|>", mutation_scale=14,
                                         color=p.muted, linewidth=1.4))

    ax.text(0.3, 6.35,
            "Three phases, outermost last — and each one gets a different "
            "slice of the data",
            fontsize=10, color=p.fg)
    ax.text(
        0.3, -0.3,
        "The book warns about the naming: \"inference\" usually means "
        "PREDICTION with a probabilistic model, but is sometimes used for "
        "parameter estimation\nand occasionally for prediction with a "
        "non-probabilistic one. There is no agreed convention, so the safe move "
        "is to say which phase you mean.",
        fontsize=8.2, color=p.amber, va="top")

    fig.suptitle(
        "Section 8.1.4: learning is finding parameters, and there are three "
        "distinct things people call it",
        y=0.985, fontsize=10, color=p.fg)


FIGURES = [
    figure("tables-8-1-to-8-2", tables_8_1_to_8_2, size=(14.0, 6.4),
           axes=False),
    figure("function-versus-distribution", function_versus_distribution,
           size=(12.2, 5.0), axes=False),
    figure("three-algorithmic-phases", three_algorithmic_phases,
           size=(11.4, 5.4), axes=False),
]
