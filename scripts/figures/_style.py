"""Shared matplotlib styling for Python Central Hub figures.

Every figure is rendered twice — once for the dark site theme and once for the
light one — and written as SVG under ``public/images/<group>/<slug>/``. The
site's ``Figure.astro`` component swaps the two variants with the theme, so the
plots never sit on the wrong background.

A page-level figure module looks like this::

    from _style import Palette, figure

    def learning_curves(fig, ax, p: Palette):
        ax.plot(x, train, color=p.blue, label="train")
        ax.plot(x, val, color=p.amber, label="validation")
        ax.set_xlabel("training set size")
        ax.legend()

    FIGURES = [figure("learning-curves", learning_curves)]

``build.py`` discovers every module, renders its ``FIGURES`` and writes the SVGs.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Callable

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402  (must follow the Agg switch)

# --------------------------------------------------------------------------- #
# Palette — mirrors src/styles/theme.css so figures match the rest of the site.
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class Palette:
    """Theme-dependent colors handed to every draw function."""

    name: str
    bg: str
    fg: str
    muted: str
    grid: str
    blue: str
    amber: str
    green: str
    purple: str
    red: str

    @property
    def cycle(self) -> list[str]:
        """Categorical series order. Blue leads, amber contrasts, then the rest."""
        return [self.blue, self.amber, self.green, self.purple, self.red, self.muted]


DARK = Palette(
    name="dark",
    bg="#0d1117",
    fg="#c9d1d9",
    muted="#768390",
    grid="#232a33",
    blue="#6ba9dd",
    amber="#ffd343",
    green="#a5d6a4",
    purple="#c599ff",
    red="#e86e6e",
)

LIGHT = Palette(
    name="light",
    bg="#ffffff",
    fg="#1f2328",
    muted="#57606a",
    grid="#e4e8ee",
    blue="#1f6fb2",
    amber="#b98600",
    green="#2f7d32",
    purple="#7c4dbd",
    red="#c0392b",
)

THEMES = (DARK, LIGHT)


def _rc(p: Palette) -> dict:
    """Matplotlib rcParams for one theme. Quiet chrome, readable labels."""
    return {
        "figure.facecolor": p.bg,
        "axes.facecolor": p.bg,
        "savefig.facecolor": p.bg,
        "savefig.transparent": False,
        "text.color": p.fg,
        "axes.labelcolor": p.fg,
        "axes.edgecolor": p.grid,
        "axes.titlecolor": p.fg,
        "axes.grid": True,
        "axes.axisbelow": True,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "grid.color": p.grid,
        "grid.linewidth": 0.8,
        "xtick.color": p.muted,
        "ytick.color": p.muted,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "axes.labelsize": 10,
        "axes.titlesize": 11.5,
        "axes.titleweight": "bold",
        "legend.frameon": False,
        "legend.fontsize": 9,
        "font.family": "sans-serif",
        "font.sans-serif": ["DejaVu Sans", "Arial", "sans-serif"],
        "font.size": 10,
        "lines.linewidth": 2.0,
        "lines.markersize": 5,
        "figure.dpi": 110,
        "svg.fonttype": "path",  # no font dependency in the published SVG
    }


# --------------------------------------------------------------------------- #
# Figure declaration + rendering
# --------------------------------------------------------------------------- #

DrawFn = Callable[[plt.Figure, object, Palette], None]


@dataclass(frozen=True)
class Figure:
    """One output figure: a file name, a draw function and a canvas size."""

    name: str
    draw: DrawFn
    size: tuple[float, float] = (8.0, 4.6)
    #: Passing None means "the draw function creates its own axes layout".
    axes: bool = True


def figure(
    name: str,
    draw: DrawFn,
    size: tuple[float, float] = (8.0, 4.6),
    axes: bool = True,
) -> Figure:
    """Declare a figure. Sugar so page modules read as a flat list."""
    return Figure(name=name, draw=draw, size=size, axes=axes)


def render(fig_spec: Figure, out_dir: str) -> list[str]:
    """Render one figure in both themes. Returns the paths written."""
    os.makedirs(out_dir, exist_ok=True)
    written: list[str] = []

    for palette in THEMES:
        with plt.rc_context(_rc(palette)):
            plt.rcParams["axes.prop_cycle"] = plt.cycler(color=palette.cycle)
            fig = plt.figure(figsize=fig_spec.size)
            ax = fig.add_subplot(111) if fig_spec.axes else None
            fig_spec.draw(fig, ax, palette)
            fig.tight_layout()

            path = os.path.join(out_dir, f"{fig_spec.name}-{palette.name}.svg")
            fig.savefig(path, format="svg", bbox_inches="tight")
            plt.close(fig)
            written.append(path)

    return written
