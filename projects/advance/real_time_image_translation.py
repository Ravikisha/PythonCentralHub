"""Real-time image translation (geometric).

Shifting an image is trivial when the shift is a whole number of pixels: it is
a roll. It stops being trivial the moment the shift is fractional, because then
every output pixel has to be interpolated from neighbours that do not line up,
and the picture loses detail every time you do it.

This measures that loss, by translating an image away and back and comparing
with the original.
"""

import matplotlib.pyplot as plt
import numpy as np


class ImageTranslator:
    def roll(self, image, shift):
        """Integer shift: exact, reversible, and wraps at the edges."""
        dy, dx = int(round(shift[0])), int(round(shift[1]))
        return np.roll(np.roll(image, dy, axis=0), dx, axis=1)

    def bilinear(self, image, shift):
        """Fractional shift: each output pixel is a blend of four inputs."""
        dy, dx = shift
        rows, columns = image.shape
        grid_y, grid_x = np.mgrid[0:rows, 0:columns]
        source_y = (grid_y - dy) % rows
        source_x = (grid_x - dx) % columns
        y0, x0 = np.floor(source_y).astype(int), np.floor(source_x).astype(int)
        y1, x1 = (y0 + 1) % rows, (x0 + 1) % columns
        weight_y = (source_y - y0)[..., None][..., 0]
        weight_x = (source_x - x0)[..., None][..., 0]
        top = image[y0, x0] * (1 - weight_x) + image[y0, x1] * weight_x
        bottom = image[y1, x0] * (1 - weight_x) + image[y1, x1] * weight_x
        return top * (1 - weight_y) + bottom * weight_y

    def round_trip(self, image, shift, method):
        there = method(image, shift)
        return method(there, (-shift[0], -shift[1]))


def checkerboard(size=64, period=8, rng=None):
    grid_y, grid_x = np.mgrid[0:size, 0:size]
    image = ((grid_y // period + grid_x // period) % 2).astype(float)
    if rng is not None:
        image = np.clip(image + rng.normal(0, 0.03, image.shape), 0, 1)
    return image


def main():
    rng = np.random.default_rng(0)
    image = checkerboard(rng=rng)
    translator = ImageTranslator()

    print("Real-Time Image Translation")
    print(f"  {'shift':>12} {'method':>10} {'round-trip RMSE':>17} "
          f"{'detail kept':>12}")

    original_energy = np.abs(np.diff(image, axis=1)).mean()
    rows = []
    for shift in ((5.0, 5.0), (0.5, 0.5), (2.5, 1.5), (0.25, 0.75)):
        for name, method in (("roll", translator.roll),
                             ("bilinear", translator.bilinear)):
            back = translator.round_trip(image, shift, method)
            rmse = float(np.sqrt(((back - image) ** 2).mean()))
            energy = np.abs(np.diff(back, axis=1)).mean()
            rows.append((shift, name, rmse, energy / original_energy))
            print(f"  {str(shift):>12} {name:>10} {rmse:>17.6f} "
                  f"{energy / original_energy:>11.2%}")

    print("\n  a whole-pixel shift is exact both ways: RMSE is 0 and every")
    print("  edge survives. A fractional shift blends four pixels each time,")
    print("  so going there and back is NOT the identity -- the round trip")
    print("  costs real detail, and it costs it twice.")

    repeated = image.copy()
    losses = []
    for step in range(1, 21):
        repeated = translator.bilinear(repeated, (0.5, 0.5))
        losses.append(np.abs(np.diff(repeated, axis=1)).mean()
                      / original_energy)
    print(f"\n  after 20 successive half-pixel shifts, edge energy is "
          f"{losses[-1]:.2%} of the original")

    figure, axes = plt.subplots(1, 4, figsize=(10, 2.9))
    axes[0].imshow(image, cmap="gray", vmin=0, vmax=1)
    axes[0].set_title("original", fontsize=9)
    axes[1].imshow(translator.round_trip(image, (5.0, 5.0), translator.roll),
                   cmap="gray", vmin=0, vmax=1)
    axes[1].set_title("roll, there and back", fontsize=9)
    axes[2].imshow(repeated, cmap="gray", vmin=0, vmax=1)
    axes[2].set_title("20 half-pixel shifts", fontsize=9)
    for axis in axes[:3]:
        axis.axis("off")
    axes[3].plot(range(1, 21), losses, marker="o", markersize=3)
    axes[3].set_xlabel("successive shifts")
    axes[3].set_ylabel("edge energy kept")
    axes[3].set_title("interpolation is lossy", fontsize=9)
    figure.tight_layout()
    plt.savefig("real_time_image_translation.png", dpi=120,
                bbox_inches="tight")
    print("saved real_time_image_translation.png")


if __name__ == "__main__":
    main()
