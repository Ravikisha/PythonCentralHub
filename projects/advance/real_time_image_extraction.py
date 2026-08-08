"""Real-time image feature extraction.

The previous version of this file "extracted features" by returning the mean
pixel value, which is one number and tells you almost nothing. This one
extracts descriptors that can actually tell two images apart -- an intensity
histogram, gradient energy, and block statistics -- and then measures whether
they can, by matching each frame back to its own class.
"""

import time

import matplotlib.pyplot as plt
import numpy as np

BINS = 16
BLOCKS = 4


class FeatureExtractor:
    """Fixed-length descriptor per frame, cheap enough for a live stream."""

    def histogram(self, image):
        counts, _ = np.histogram(image, bins=BINS, range=(0.0, 1.0))
        return counts / max(counts.sum(), 1)

    def gradients(self, image):
        """Edge energy, horizontal and vertical."""
        # Trim both to the overlapping interior so they can be combined.
        dy = np.diff(image, axis=0)[:, :-1]
        dx = np.diff(image, axis=1)[:-1, :]
        return np.array([np.abs(dx).mean(), np.abs(dy).mean(),
                         np.hypot(dx, dy).mean()])

    def blocks(self, image):
        """Mean and spread of each tile, which keeps coarse layout."""
        size = image.shape[0] // BLOCKS
        tiles = image[:size * BLOCKS, :size * BLOCKS]
        tiles = tiles.reshape(BLOCKS, size, BLOCKS, size)
        return np.concatenate([tiles.mean(axis=(1, 3)).ravel(),
                               tiles.std(axis=(1, 3)).ravel()])

    def extract(self, image):
        return np.concatenate([self.histogram(image), self.gradients(image),
                               self.blocks(image)])


def frame_of(kind, rng, size=64):
    """Three frame types with the SAME mean brightness.

    Equalising the mean is deliberate. If the classes differed in brightness a
    single average pixel would separate them and the descriptor would prove
    nothing; holding the mean fixed forces the comparison onto structure, which
    is what a feature extractor is for.
    """
    grid_y, grid_x = np.mgrid[0:size, 0:size] / size
    if kind == 0:                                   # smooth gradient
        image = grid_x * 0.8 + rng.normal(0, 0.02, (size, size))
    elif kind == 1:                                 # vertical stripes
        image = 0.5 + 0.4 * np.sign(np.sin(grid_x * np.pi * 12))
        image = image + rng.normal(0, 0.05, (size, size))
    else:                                           # bright disc on dark
        image = np.where(np.hypot(grid_x - 0.5, grid_y - 0.5) < 0.28, 0.9, 0.1)
        image = image + rng.normal(0, 0.05, (size, size))
    # Normalise to a fixed mean AND a fixed spread, so neither the average
    # pixel nor the contrast can separate the classes -- only the spatial
    # arrangement can, which is what the descriptor is being tested on.
    image = (image - image.mean()) / max(image.std(), 1e-9)
    return np.clip(image * 0.15 + 0.5, 0.0, 1.0)


def main():
    rng = np.random.default_rng(0)
    extractor = FeatureExtractor()

    frames, labels = [], []
    for index in range(150):
        kind = index % 3
        frames.append(frame_of(kind, rng))
        labels.append(kind)
    labels = np.asarray(labels)

    started = time.perf_counter()
    descriptors = np.stack([extractor.extract(frame) for frame in frames])
    elapsed = time.perf_counter() - started

    print("Real-Time Image Feature Extraction")
    print(f"  frames            : {len(frames)} at 64x64")
    print(f"  descriptor length : {descriptors.shape[1]}")
    print(f"  extraction time   : {elapsed * 1000:.1f} ms total, "
          f"{elapsed / len(frames) * 1000:.3f} ms per frame")
    print(f"  sustainable rate  : {len(frames) / elapsed:,.0f} frames/second")

    # Do the descriptors separate the classes? Nearest neighbour, excluding
    # the frame itself, is the cheapest honest test.
    squared = ((descriptors[:, None, :] - descriptors[None, :, :]) ** 2).sum(2)
    np.fill_diagonal(squared, np.inf)
    nearest = squared.argmin(axis=1)
    accuracy = float((labels[nearest] == labels).mean())
    print(f"\n  nearest-neighbour class match: {accuracy:.4f}")

    mean_only = np.array([[frame.mean()] for frame in frames])
    squared_mean = ((mean_only[:, None] - mean_only[None]) ** 2).sum(2)
    np.fill_diagonal(squared_mean, np.inf)
    baseline = float((labels[squared_mean.argmin(axis=1)] == labels).mean())
    print(f"  the same test using only the mean pixel: {baseline:.4f}")
    print(f"  chance on three balanced classes:        {1/3:.4f}")
    print(f"\n  the {descriptors.shape[1]}-number descriptor is worth "
          f"{accuracy - baseline:.4f} over a single mean")

    figure, axes = plt.subplots(1, 4, figsize=(10, 2.8))
    for kind in range(3):
        axes[kind].imshow(frames[kind], cmap="gray", vmin=0, vmax=1)
        axes[kind].set_title(["gradient", "stripes", "disc"][kind], fontsize=9)
        axes[kind].axis("off")
    for kind in range(3):
        axes[3].plot(descriptors[kind][:BINS],
                     label=["gradient", "stripes", "disc"][kind], linewidth=1.2)
    axes[3].set_title("intensity histograms", fontsize=9)
    axes[3].set_xlabel("bin")
    axes[3].legend(fontsize=7)
    figure.tight_layout()
    plt.savefig("real_time_image_extraction.png", dpi=120, bbox_inches="tight")
    print("saved real_time_image_extraction.png")


if __name__ == "__main__":
    main()
