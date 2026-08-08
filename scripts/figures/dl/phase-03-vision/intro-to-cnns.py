"""Figures for *Intro to Convolutional Neural Networks (CNN) for Images*.

``kernels-on-an-image``
    Four hand-written 3x3 kernels applied to a real Fashion-MNIST image, so
    "convolution detects edges" becomes something you can look at.

``parameter-comparison``
    The same input through a Dense layer and a Conv2D layer with the same number
    of output units. The parameter counts differ by orders of magnitude.

``receptive-field``
    How far back into the input each layer can see, for two kernel sizes and
    with and without stride.
"""

from __future__ import annotations

import functools
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "..", ".."))

from _dl import dataset, seed_everything, tf  # noqa: E402
from _style import Palette, figure  # noqa: E402

KERNELS = {
    "vertical edges": np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], "float32"),
    "horizontal edges": np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]], "float32"),
    "sharpen": np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]], "float32"),
    "blur (3x3 mean)": np.ones((3, 3), "float32") / 9.0,
}


def _convolve(image: np.ndarray, kernel: np.ndarray) -> np.ndarray:
    """Valid-padding 2-D convolution, written out so nothing is hidden."""
    height, width = image.shape
    size = kernel.shape[0]
    out = np.zeros((height - size + 1, width - size + 1), "float32")
    for row in range(out.shape[0]):
        for column in range(out.shape[1]):
            patch = image[row:row + size, column:column + size]
            out[row, column] = float((patch * kernel).sum())
    return out


@functools.lru_cache(maxsize=1)
def _sample() -> dict:
    data = dataset("fashion", limit=200, flat=False)
    image = data["x_train"][7]
    grey = image[..., 0]
    return {"image": image, "grey": grey,
            "responses": {name: _convolve(grey, kernel)
                          for name, kernel in KERNELS.items()}}


def kernels_on_an_image(fig, axes, p: Palette) -> None:
    info = _sample()
    grid = fig.subplots(1, 5)
    grid[0].imshow(info["grey"], cmap="gray")
    grid[0].set_title("input 28x28x1", fontsize=9)
    for ax, (name, response) in zip(grid[1:], info["responses"].items()):
        ax.imshow(response, cmap="gray")
        ax.set_title(f"{name}\nrange {response.min():.2f} to "
                     f"{response.max():.2f}", fontsize=8.5)
    for ax in grid:
        ax.set_xticks([])
        ax.set_yticks([])
        ax.grid(False)


def _dense_params(inputs: int, units: int) -> int:
    return inputs * units + units


def _conv_params(kernel: int, in_channels: int, out_channels: int) -> int:
    return kernel * kernel * in_channels * out_channels + out_channels


CASES = (
    ("Fashion-MNIST\n28x28x1", 28, 1),
    ("small colour\n32x32x3", 32, 3),
    ("photo\n224x224x3", 224, 3),
)


def parameter_comparison(fig, axes, p: Palette) -> None:
    ax = fig.subplots(1, 1)
    labels = [c[0] for c in CASES]
    positions = np.arange(len(CASES))
    dense, conv = [], []
    for _, side, channels in CASES:
        # 32 outputs either way: a Dense layer with 32 units, or a Conv2D with
        # 32 filters of 3x3.
        dense.append(_dense_params(side * side * channels, 32))
        conv.append(_conv_params(3, channels, 32))

    ax.bar(positions - 0.2, dense, 0.38, color=p.red, label="Dense(32)")
    ax.bar(positions + 0.2, conv, 0.38, color=p.green,
           label="Conv2D(32, 3x3)")
    for x, value in zip(positions - 0.2, dense):
        ax.annotate(f"{value:,}", (x, value), textcoords="offset points",
                    xytext=(0, 4), ha="center", fontsize=8, color=p.fg)
    for x, value, d in zip(positions + 0.2, conv, dense):
        ax.annotate(f"{value:,}\n{d / value:,.0f}x fewer", (x, value),
                    textcoords="offset points", xytext=(0, 4), ha="center",
                    fontsize=8, color=p.green)
    ax.set_yscale("log")
    ax.set_xticks(positions)
    ax.set_xticklabels(labels, fontsize=8.5)
    ax.set_ylabel("parameters in the first layer (log scale)")
    ax.set_ylim(10, max(dense) * 12)
    ax.set_title("Same 32 outputs, two ways of connecting them", fontsize=10.5)
    ax.legend(fontsize=8)


def receptive_field(fig, axes, p: Palette) -> None:
    ax = fig.subplots(1, 1)
    depths = np.arange(0, 9)
    # stride 2 and "conv + 2x2 pool" grow identically, so only one is drawn.
    recipes = (
        ("3x3, stride 1", 3, 1, p.blue),
        ("5x5, stride 1", 5, 1, p.green),
        ("3x3, stride 2 (or 3x3 + 2x2 pool)", 3, 2, p.amber),
    )
    for label, kernel, stride, color in recipes:
        field, jump = 1, 1
        sizes = [field]
        for _ in depths[1:]:
            field = field + (kernel - 1) * jump
            jump = jump * stride
            sizes.append(field)
        ax.plot(depths, sizes, "o-", ms=5, lw=1.9, color=color,
                label=f"{label} — layer 8 sees {sizes[-1]}x{sizes[-1]}")
    ax.axhline(28, color=p.grid, lw=1.4, ls="--")
    ax.annotate("a whole Fashion-MNIST image (28 px)", (0.2, 30), fontsize=8,
                color=p.muted)
    ax.set_yscale("log", base=2)
    ax.set_xlabel("layers stacked")
    ax.set_ylabel("receptive field, pixels on a side (log scale)")
    ax.set_title("How far back into the input each layer can see",
                 fontsize=10.5)
    ax.legend(fontsize=8)


FIGURES = [
    figure("kernels-on-an-image", kernels_on_an_image, size=(9.6, 2.4),
           axes=False),
    figure("parameter-comparison", parameter_comparison, size=(7.6, 3.8),
           axes=False),
    figure("receptive-field", receptive_field, size=(7.8, 3.8), axes=False),
]


if __name__ == "__main__":
    info = _sample()
    print("=== hand-written kernels on one Fashion-MNIST image ===")
    print(f"grey input range {info['grey'].min():.4f} to "
          f"{info['grey'].max():.4f}, mean {info['grey'].mean():.4f}")
    for name, response in info["responses"].items():
        print(f"{name:18s} shape {response.shape}  "
              f"range {response.min():8.4f} to {response.max():7.4f}  "
              f"mean |response| {np.abs(response).mean():.4f}")

    print("\n=== checking one output against Keras ===")
    tensorflow = tf()
    grey = info["grey"][None, :, :, None]
    kernel = KERNELS["vertical edges"][:, :, None, None]
    keras_out = tensorflow.nn.conv2d(grey, kernel, strides=1,
                                     padding="VALID").numpy()[0, :, :, 0]
    mine = info["responses"]["vertical edges"]
    print(f"max |mine - tf.nn.conv2d| = {np.abs(mine - keras_out).max():.2e}")

    print("\n=== parameters: Dense(32) against Conv2D(32, 3x3) ===")
    print(f"{'input':16s} {'Dense(32)':>14} {'Conv2D(32,3x3)':>16} {'ratio':>10}")
    for label, side, channels in CASES:
        d = _dense_params(side * side * channels, 32)
        c = _conv_params(3, channels, 32)
        print(f"{label.replace(chr(10), ' '):16s} {d:14,} {c:16,} "
              f"{d / c:9,.0f}x")

    print("\n=== receptive field by depth ===")
    for label, kernel_size, stride in (("3x3 s1", 3, 1), ("5x5 s1", 5, 1),
                                       ("3x3 s2", 3, 2)):
        field, jump = 1, 1
        for _ in range(8):
            field = field + (kernel_size - 1) * jump
            jump = jump * stride
        print(f"{label:8s} after 8 layers: {field}x{field} pixels")
