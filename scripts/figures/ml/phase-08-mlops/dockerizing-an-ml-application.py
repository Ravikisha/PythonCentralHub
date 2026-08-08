"""Figures for *Dockerizing an ML Application*."""

import importlib.util
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _style import Palette, figure  # noqa: E402


def _package_mb(name):
    """Installed size of a package's directory, in MB, or None if absent."""
    spec = importlib.util.find_spec(name)
    if spec is None or not spec.submodule_search_locations:
        return None
    root = list(spec.submodule_search_locations)[0]
    total = 0
    for dirpath, _, files in os.walk(root):
        for f in files:
            try:
                total += os.path.getsize(os.path.join(dirpath, f))
            except OSError:
                pass
    return total / 1024 / 1024


def dependency_footprint(fig, axes, p: Palette) -> None:
    """What actually drives image size: the installed dependency tree.

    These are real measurements of the site-packages directories in the
    environment that built this figure — not of a built image, which would also
    include the base OS layer and the Python runtime. The point is the relative
    weight, which is what your Dockerfile controls.
    """
    packages = ["joblib", "matplotlib", "numpy", "sklearn", "pandas", "scipy",
                "tensorflow"]
    measured = [(n, _package_mb(n)) for n in packages]
    measured = [(n, v) for n, v in measured if v is not None]
    measured.sort(key=lambda t: t[1])

    core = {"numpy", "scipy", "sklearn", "joblib"}
    colors = [p.green if n in core else
              (p.red if n == "tensorflow" else p.amber) for n, _ in measured]

    bars = axes.barh([n for n, _ in measured], [v for _, v in measured],
                     color=colors)
    for b, (_, v) in zip(bars, measured):
        axes.annotate(f"{v:,.0f} MB", (v * 1.05, b.get_y() + b.get_height() / 2),
                      va="center", fontsize=9, color=p.muted)

    serve_only = sum(v for n, v in measured if n in core)
    everything = sum(v for _, v in measured)
    axes.set_xscale("log")
    axes.set_xlim(1, everything * 3)
    axes.set_xlabel("installed size, MB (log scale)")
    axes.set_title(f"Serving stack {serve_only:,.0f} MB · everything installed "
                   f"{everything:,.0f} MB — {everything / serve_only:.1f}x "
                   f"heavier")


def layer_cache(fig, axes, p: Palette) -> None:
    """Why COPY requirements.txt comes before COPY . in every good Dockerfile."""
    axes.axis("off")
    from matplotlib.patches import Rectangle

    layers = ["FROM python:3.11-slim", "COPY requirements.txt",
              "RUN pip install -r ...", "COPY app/ + model.pkl"]

    for col, (title, changed_from) in enumerate(
            [("You changed one line of app code", 3),
             ("You added one dependency", 1)]):
        x0 = 0.04 + col * 0.50
        axes.annotate(title, (x0 + 0.21, 0.90), ha="center", fontsize=10.5,
                      color=p.fg)
        for i, name in enumerate(layers):
            y = 0.72 - i * 0.16
            cached = i < changed_from
            colour = p.green if cached else p.red
            axes.add_patch(Rectangle((x0, y), 0.42, 0.12, facecolor=colour,
                                     alpha=0.22, edgecolor=colour, lw=1.8))
            axes.annotate(name, (x0 + 0.012, y + 0.06), va="center",
                          fontsize=8.5, color=p.fg)
            axes.annotate("cached" if cached else "REBUILT",
                          (x0 + 0.405, y + 0.06), va="center", ha="right",
                          fontsize=8.5, color=colour)
        rebuilt = len(layers) - changed_from
        axes.annotate(f"{rebuilt} of {len(layers)} layers rebuilt",
                      (x0 + 0.21, 0.04), ha="center", fontsize=9.5,
                      color=p.muted)

    axes.set_xlim(0, 1)
    axes.set_ylim(0, 1)
    axes.set_title("Copy the dependency list before the source, and pip install "
                   "stays cached")


FIGURES = [
    figure("dependency-footprint", dependency_footprint, size=(7.8, 3.8)),
    figure("layer-cache", layer_cache, size=(8.8, 3.4)),
]
