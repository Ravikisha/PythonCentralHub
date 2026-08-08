"""Real-time procedural image generation.

Generating an image is easy. Generating a *stream* of them, fast enough and
varied enough to be worth watching, is the actual problem -- so this measures
both: how many frames per second the generator sustains, and how different
consecutive frames really are.

The variety check matters because a generator that returns almost the same
frame every time still passes any "did it produce an image" test.
"""

import time

import matplotlib.pyplot as plt
import numpy as np


class PatternGenerator:
    """Layered sine interference, animated by a phase that advances per frame."""

    def __init__(self, size=96, layers=3, seed=0):
        self.size = size
        self.layers = layers
        rng = np.random.default_rng(seed)
        self.frequencies = rng.uniform(2.0, 9.0, (layers, 2))
        self.phases = rng.uniform(0, 2 * np.pi, layers)
        self.weights = rng.uniform(0.5, 1.0, layers)
        grid_y, grid_x = np.mgrid[0:size, 0:size] / size
        self.grid_y, self.grid_x = grid_y, grid_x

    def frame(self, step, drift=0.12):
        image = np.zeros((self.size, self.size))
        for layer in range(self.layers):
            fy, fx = self.frequencies[layer]
            phase = self.phases[layer] + drift * step * (layer + 1)
            image += self.weights[layer] * np.sin(
                2 * np.pi * (fy * self.grid_y + fx * self.grid_x) + phase)
        image = image / self.weights.sum()
        return (image + 1.0) / 2.0


def variety(frames):
    """Mean absolute difference between consecutive frames, and overall."""
    stack = np.stack(frames)
    consecutive = np.abs(np.diff(stack, axis=0)).mean()
    flat = stack.reshape(len(stack), -1)
    sample = flat[::max(len(flat) // 24, 1)]
    pairwise = np.abs(sample[:, None, :] - sample[None, :, :]).mean()
    return consecutive, pairwise


def main():
    generator = PatternGenerator()
    frames = []
    started = time.perf_counter()
    for step in range(240):
        frames.append(generator.frame(step))
    elapsed = time.perf_counter() - started

    consecutive, pairwise = variety(frames)
    print("Real-Time Procedural Image Generation")
    print(f"  frames generated   : {len(frames)} at "
          f"{generator.size}x{generator.size}")
    print(f"  total time         : {elapsed * 1000:.1f} ms")
    print(f"  per frame          : {elapsed / len(frames) * 1000:.3f} ms")
    print(f"  sustained rate     : {len(frames) / elapsed:,.0f} frames/second")
    print(f"  budget at 60 fps   : {1000 / 60:.2f} ms/frame — "
          f"{'within' if elapsed / len(frames) * 1000 < 1000 / 60 else 'over'}")

    print(f"\n  mean change between consecutive frames: {consecutive:.4f}")
    print(f"  mean difference between any two frames : {pairwise:.4f}")
    print(f"  ratio: {consecutive / pairwise:.3f}")
    print("  a ratio near zero would mean the stream is barely moving even")
    print("  though it keeps producing output -- the failure mode a")
    print("  frames-per-second number alone would never show")

    print(f"\n  {'drift':>7} {'consecutive change':>20} {'frames/second':>15}")
    for drift in (0.0, 0.02, 0.12, 0.5):
        sample_generator = PatternGenerator()
        started = time.perf_counter()
        sample = [sample_generator.frame(step, drift=drift)
                  for step in range(120)]
        rate = 120 / (time.perf_counter() - started)
        change, _ = variety(sample)
        print(f"  {drift:>7.2f} {change:>20.4f} {rate:>15,.0f}")
    print("  drift 0.00 regenerates the same frame forever at full speed")

    figure, axes = plt.subplots(1, 5, figsize=(11, 2.5))
    for index, step in enumerate((0, 20, 60, 120, 200)):
        axes[index].imshow(frames[step], cmap="twilight", vmin=0, vmax=1)
        axes[index].set_title(f"step {step}", fontsize=9)
        axes[index].axis("off")
    figure.tight_layout()
    plt.savefig("real_time_image_generation.png", dpi=120, bbox_inches="tight")
    print("saved real_time_image_generation.png")


if __name__ == "__main__":
    main()
