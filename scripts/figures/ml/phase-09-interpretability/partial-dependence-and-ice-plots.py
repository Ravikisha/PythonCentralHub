"""Figures for *Partial Dependence and ICE Plots*."""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _data import sign_flip_interaction  # noqa: E402
from _style import Palette, figure  # noqa: E402


def pdp_hides_interaction(fig, axes, p: Palette) -> None:
    """The average of +2.5x and -2.5x is a flat line."""
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.inspection import partial_dependence

    X, y = sign_flip_interaction()
    model = RandomForestRegressor(n_estimators=300, random_state=0).fit(X, y)

    # method="brute" throughout: it is the only setting under which the PDP is
    # exactly the mean of the ICE curves. sklearn's default for forests is
    # "recursion", which computes something subtly different.
    both = partial_dependence(model, X, features=["x"], grid_resolution=25,
                              kind="both", method="brute")
    grid = both["grid_values"][0]
    pdp = both["average"][0]
    ind = both["individual"][0]

    axs = fig.subplots(1, 2, sharey=True)

    axs[0].plot(grid, pdp, "o-", color=p.amber, lw=2.6)
    axs[0].axhline(0, color=p.muted, lw=1, ls="--")
    axs[0].set_xlabel("x")
    axs[0].set_ylabel("partial dependence")
    axs[0].set_title(f"PDP: total range {pdp.max() - pdp.min():.3f}\n"
                     f"'x barely matters'", fontsize=10.5)

    g = X["group"].to_numpy()
    for i in range(0, len(ind), 7):
        axs[1].plot(grid, ind[i], color=p.blue if g[i] == 1 else p.green,
                    lw=0.7, alpha=0.30)
    axs[1].plot(grid, ind[g == 1].mean(axis=0), color=p.blue, lw=3,
                label="group = 1 mean")
    axs[1].plot(grid, ind[g == 0].mean(axis=0), color=p.green, lw=3,
                label="group = 0 mean")
    axs[1].plot(grid, pdp, color=p.amber, lw=2.6, ls="--", label="the PDP")
    slopes = ind[:, -1] - ind[:, 0]
    axs[1].set_xlabel("x")
    axs[1].set_title(f"ICE: slopes from {slopes.min():+.2f} to "
                     f"{slopes.max():+.2f}\n'x matters enormously'",
                     fontsize=10.5)
    axs[1].legend(loc="upper center", fontsize=8.5)

    fig.suptitle("Averaging two opposite effects gives you neither of them",
                 fontsize=10.5, color=p.muted)


def centred_ice(fig, axes, p: Palette) -> None:
    """Centred ICE separates the shape of each curve from its starting level."""
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.inspection import partial_dependence

    X, y = sign_flip_interaction()
    model = RandomForestRegressor(n_estimators=300, random_state=0).fit(X, y)
    ind = partial_dependence(model, X, features=["x"], grid_resolution=25,
                             kind="individual", method="brute")
    grid = ind["grid_values"][0]
    curves = ind["individual"][0]
    g = X["group"].to_numpy()

    axs = fig.subplots(1, 2, sharex=True)

    for i in range(0, len(curves), 7):
        axs[0].plot(grid, curves[i], color=p.blue if g[i] == 1 else p.green,
                    lw=0.7, alpha=0.30)
    axs[0].set_title("Raw ICE — curves start at different levels", fontsize=10.5)
    axs[0].set_ylabel("prediction")

    centred = curves - curves[:, [0]]
    for i in range(0, len(centred), 7):
        axs[1].plot(grid, centred[i], color=p.blue if g[i] == 1 else p.green,
                    lw=0.7, alpha=0.30)
    axs[1].axhline(0, color=p.muted, lw=1, ls="--")
    axs[1].set_title("Centred ICE — every curve starts at 0", fontsize=10.5)
    axs[1].set_ylabel("change from x at its minimum")

    for ax in axs:
        ax.set_xlabel("x")

    fig.suptitle("Two clean fans instead of one cloud: the interaction is now "
                 "unmistakable", fontsize=10.5, color=p.muted)


FIGURES = [
    figure("pdp-hides-interaction", pdp_hides_interaction, size=(8.8, 3.8),
           axes=False),
    figure("centred-ice", centred_ice, size=(8.8, 3.6), axes=False),
]
