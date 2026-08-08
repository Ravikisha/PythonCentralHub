"""Figures for *Autoencoders*.

The comparison that makes this page honest is PCA. An autoencoder with linear
activations and a squared-error loss *is* PCA, so any claim about autoencoders
learning useful compression has to beat the linear method it generalises —
which takes two lines of scikit-learn and no training at all.

``bottleneck-sweep``
    Reconstruction error against bottleneck size for a deep autoencoder and for
    PCA at the same number of components.

``reconstructions``
    The same digits reconstructed at several bottleneck sizes, with the
    per-image error printed, so "blurry" has a number attached.

``denoising``
    A denoising autoencoder against the identity and against a simple blur —
    the baseline nobody runs.
"""

from __future__ import annotations

import functools
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "..", ".."))

from _dl import dataset, seed_everything, tf  # noqa: E402
from _style import Palette, figure  # noqa: E402

LIMIT = 12000
EPOCHS = 20
BOTTLENECKS = (2, 8, 32, 128)
SHOW = 4
NOISE = 0.4


@functools.lru_cache(maxsize=1)
def _data() -> dict:
    return dataset("mnist", limit=LIMIT, flat=True)


def _autoencoder(bottleneck: int, seed: int = 0):
    keras = tf().keras
    seed_everything(seed)
    inputs = keras.layers.Input((784,))
    x = keras.layers.Dense(256, activation="relu")(inputs)
    x = keras.layers.Dense(64, activation="relu")(x)
    code = keras.layers.Dense(bottleneck, activation="relu", name="code")(x)
    x = keras.layers.Dense(64, activation="relu")(code)
    x = keras.layers.Dense(256, activation="relu")(x)
    outputs = keras.layers.Dense(784, activation="sigmoid")(x)
    model = keras.Model(inputs, outputs)
    model.compile(keras.optimizers.Adam(1e-3), "mse")
    return model


@functools.lru_cache(maxsize=1)
def _runs() -> dict:
    from sklearn.decomposition import PCA

    data = _data()
    out = {}
    for bottleneck in BOTTLENECKS:
        model = _autoencoder(bottleneck)
        started = time.perf_counter()
        history = model.fit(data["x_train"], data["x_train"], epochs=EPOCHS,
                            batch_size=128, verbose=0,
                            validation_data=(data["x_test"], data["x_test"]))
        reconstructed = model.predict(data["x_test"], verbose=0)
        pca = PCA(n_components=bottleneck).fit(data["x_train"])
        pca_reconstructed = np.clip(
            pca.inverse_transform(pca.transform(data["x_test"])), 0, 1)
        out[bottleneck] = {
            "mse": float(np.mean((reconstructed - data["x_test"]) ** 2)),
            "pca_mse": float(np.mean((pca_reconstructed
                                      - data["x_test"]) ** 2)),
            "explained": float(pca.explained_variance_ratio_.sum()),
            "params": int(model.count_params()),
            "seconds": time.perf_counter() - started,
            "reconstructed": reconstructed[:SHOW],
            "pca_reconstructed": pca_reconstructed[:SHOW],
            "curve": [float(v) for v in history.history["val_loss"]],
        }
    return out


def bottleneck_sweep(fig, axes, p: Palette) -> None:
    runs = _runs()
    left, right = fig.subplots(1, 2)
    mse = [runs[b]["mse"] for b in BOTTLENECKS]
    pca_mse = [runs[b]["pca_mse"] for b in BOTTLENECKS]
    left.plot(BOTTLENECKS, mse, "o-", ms=6, lw=2.0, color=p.green,
              label="autoencoder")
    left.plot(BOTTLENECKS, pca_mse, "o-", ms=6, lw=2.0, color=p.amber,
              label="PCA, same components")
    for bottleneck, a, b in zip(BOTTLENECKS, mse, pca_mse):
        left.annotate(f"{a:.4f}", (bottleneck, a), textcoords="offset points",
                      xytext=(0, -14), ha="center", fontsize=7.5,
                      color=p.green)
        left.annotate(f"{b:.4f}", (bottleneck, b), textcoords="offset points",
                      xytext=(0, 8), ha="center", fontsize=7.5, color=p.amber)
    left.set_xscale("log")
    left.minorticks_off()
    left.set_xticks(list(BOTTLENECKS))
    left.set_xticklabels([str(b) for b in BOTTLENECKS])
    left.set_xlabel("bottleneck size")
    left.set_ylabel("test reconstruction MSE")
    left.set_title(f"MNIST, {LIMIT:,} images, {EPOCHS} epochs", fontsize=10)
    left.legend(fontsize=8, loc="upper right")

    gains = [(b - a) / b for a, b in zip(mse, pca_mse)]
    positions = np.arange(len(BOTTLENECKS))
    right.bar(positions, gains, 0.55,
              color=[p.green if value > 0 else p.red for value in gains])
    for x, value in zip(positions, gains):
        right.annotate(f"{value:+.1%}", (x, value),
                       textcoords="offset points",
                       xytext=(0, 4 if value > 0 else -12), ha="center",
                       fontsize=8.5, color=p.fg)
    right.axhline(0, color=p.muted, lw=1.1)
    right.set_xticks(positions)
    # The explained-variance figure goes in the tick label: annotated inside
    # the axes it collided with the percentage labels.
    right.set_xticklabels([f"{b}\n(PCA keeps\n{runs[b]['explained']:.1%})"
                           for b in BOTTLENECKS], fontsize=8)
    right.set_xlabel("bottleneck size")
    right.set_ylabel("error reduction against PCA")
    right.set_title("what the nonlinearity actually buys", fontsize=10)


def reconstructions(fig, axes, p: Palette) -> None:
    runs = _runs()
    data = _data()
    rows = 1 + 2 * len(BOTTLENECKS)
    grid = fig.subplots(rows, SHOW)
    for column in range(SHOW):
        grid[0][column].imshow(data["x_test"][column].reshape(28, 28),
                               cmap="gray")
        if column == 0:
            grid[0][column].set_ylabel("original", fontsize=7.5)
    for index, bottleneck in enumerate(BOTTLENECKS):
        run = runs[bottleneck]
        for column in range(SHOW):
            ax = grid[1 + 2 * index][column]
            ax.imshow(run["reconstructed"][column].reshape(28, 28),
                      cmap="gray")
            error = float(np.mean((run["reconstructed"][column]
                                   - data["x_test"][column]) ** 2))
            ax.set_title(f"{error:.4f}", fontsize=6.5)
            if column == 0:
                ax.set_ylabel(f"AE {bottleneck}", fontsize=7.5)
            ax = grid[2 + 2 * index][column]
            ax.imshow(run["pca_reconstructed"][column].reshape(28, 28),
                      cmap="gray")
            error = float(np.mean((run["pca_reconstructed"][column]
                                   - data["x_test"][column]) ** 2))
            ax.set_title(f"{error:.4f}", fontsize=6.5)
            if column == 0:
                ax.set_ylabel(f"PCA {bottleneck}", fontsize=7.5)
    for row in grid:
        for ax in row:
            ax.set_xticks([])
            ax.set_yticks([])
            ax.grid(False)


@functools.lru_cache(maxsize=1)
def _denoising() -> dict:
    keras = tf().keras
    data = _data()
    rng = np.random.default_rng(0)
    noisy_train = np.clip(data["x_train"]
                          + rng.normal(0, NOISE, data["x_train"].shape), 0, 1)
    noisy_test = np.clip(data["x_test"]
                         + rng.normal(0, NOISE, data["x_test"].shape), 0, 1)
    model = _autoencoder(32, seed=1)
    model.fit(noisy_train, data["x_train"], epochs=EPOCHS, batch_size=128,
              verbose=0, validation_data=(noisy_test, data["x_test"]))
    cleaned = model.predict(noisy_test, verbose=0)

    # The baselines nobody runs: do nothing, and blur.
    identity = noisy_test
    kernel = np.ones((3, 3), "float32") / 9.0
    images = noisy_test.reshape(-1, 28, 28)
    blurred = np.zeros_like(images)
    padded = np.pad(images, ((0, 0), (1, 1), (1, 1)), mode="edge")
    for i in range(3):
        for j in range(3):
            blurred += kernel[i, j] * padded[:, i:i + 28, j:j + 28]
    blurred = blurred.reshape(len(images), -1)
    return {"noisy": noisy_test[:SHOW], "cleaned": cleaned[:SHOW],
            "blurred": blurred[:SHOW],
            "mse": {
                "noisy input": float(np.mean((identity
                                              - data["x_test"]) ** 2)),
                "3x3 blur": float(np.mean((blurred - data["x_test"]) ** 2)),
                "denoising AE": float(np.mean((cleaned
                                               - data["x_test"]) ** 2)),
            }}


def denoising(fig, axes, p: Palette) -> None:
    info = _denoising()
    data = _data()
    left, right = fig.subplots(1, 2, width_ratios=(1.35, 1.0))
    left.axis("off")
    strip = np.concatenate(
        [np.concatenate([info["noisy"][i].reshape(28, 28) for i in range(SHOW)],
                        axis=1),
         np.concatenate([info["blurred"][i].reshape(28, 28)
                         for i in range(SHOW)], axis=1),
         np.concatenate([info["cleaned"][i].reshape(28, 28)
                         for i in range(SHOW)], axis=1),
         np.concatenate([data["x_test"][i].reshape(28, 28)
                         for i in range(SHOW)], axis=1)], axis=0)
    left.imshow(strip, cmap="gray")
    left.set_title("noisy / 3x3 blur / denoising AE / clean", fontsize=9.5)
    left.grid(False)

    labels = list(info["mse"])
    values = [info["mse"][label] for label in labels]
    best = min(values)
    positions = np.arange(len(labels))
    right.bar(positions, values, 0.55,
              color=[p.green if abs(v - best) < 1e-12 else p.blue
                     for v in values])
    for x, value in zip(positions, values):
        right.annotate(f"{value:.4f}", (x, value),
                       textcoords="offset points", xytext=(0, 4), ha="center",
                       fontsize=8.5, color=p.fg)
    right.set_xticks(positions)
    right.set_xticklabels([label.replace(" ", "\n") for label in labels],
                          fontsize=8)
    right.set_ylabel("MSE against the clean image")
    right.set_title(f"noise sd {NOISE}", fontsize=10)


FIGURES = [
    figure("bottleneck-sweep", bottleneck_sweep, size=(9.4, 3.5), axes=False),
    figure("reconstructions", reconstructions, size=(6.4, 8.2), axes=False),
    figure("denoising", denoising, size=(9.6, 3.4), axes=False),
]


if __name__ == "__main__":
    runs = _runs()
    print(f"=== MNIST, {LIMIT:,} images, {EPOCHS} epochs ===")
    print(f"{'bottleneck':>11} {'AE params':>10} {'AE MSE':>9} {'PCA MSE':>9} "
          f"{'AE vs PCA':>10} {'PCA variance':>13} {'seconds':>9}")
    for bottleneck in BOTTLENECKS:
        run = runs[bottleneck]
        gain = (run["pca_mse"] - run["mse"]) / run["pca_mse"]
        print(f"{bottleneck:11d} {run['params']:10,} {run['mse']:9.4f} "
              f"{run['pca_mse']:9.4f} {gain:+9.1%} "
              f"{run['explained']:13.1%} {run['seconds']:9.1f}")
    print("a linear autoencoder with a squared-error loss *is* PCA, so the")
    print("nonlinear version has to beat it to have earned its training time")

    info = _denoising()
    print(f"\n=== denoising, noise sd {NOISE} ===")
    print(f"{'method':16s} {'MSE against clean':>18}")
    for label, value in info["mse"].items():
        print(f"{label:16s} {value:18.4f}")
    best = min(info["mse"], key=info["mse"].get)
    print(f"best: {best}")
    print("the blur is the baseline that makes a denoiser's number meaningful:")
    print("averaging nine pixels removes a lot of independent noise for free")
