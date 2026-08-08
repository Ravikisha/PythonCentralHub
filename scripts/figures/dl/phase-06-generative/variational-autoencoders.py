"""Figures for *Variational Autoencoders (VAE)*.

A VAE is an autoencoder with two changes: the encoder outputs a distribution
rather than a point, and the loss adds a KL term pulling that distribution
towards a standard normal. Both changes are measurable, and the second one has
a failure mode — posterior collapse — that this module measures directly rather
than describing.

``beta-sweep``
    Reconstruction error and KL divergence against the weight on the KL term,
    including the value where the latent stops carrying information at all.

``latent-structure``
    The 2-D latent space: where the classes land, and how close the aggregate
    posterior actually is to the prior it is being pulled towards.

``samples-and-interpolation``
    Decoded samples from the prior, and an interpolation between two encoded
    digits — the thing a plain autoencoder cannot do.
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

LIMIT = 12000
EPOCHS = 25
LATENT = 2
BETAS = (0.0, 0.5, 1.0, 4.0, 20.0)
SWEEP_BETA = 1.0
GRID = 12


@functools.lru_cache(maxsize=1)
def _data() -> dict:
    return dataset("mnist", limit=LIMIT, flat=True)


def _build(beta: float, latent: int = LATENT, seed: int = 0):
    """A VAE written with an explicit loss, so both terms stay visible."""
    keras = tf().keras
    tensorflow = tf()
    seed_everything(seed)

    class Sampler(keras.layers.Layer):
        def call(self, inputs):
            mean, log_variance = inputs
            noise = tensorflow.random.normal(tensorflow.shape(mean))
            return mean + tensorflow.exp(0.5 * log_variance) * noise

    class VAE(keras.Model):
        def __init__(self, encoder, decoder, beta):
            super().__init__()
            self.encoder = encoder
            self.decoder = decoder
            self.beta = beta
            self.reconstruction_tracker = keras.metrics.Mean(name="reconstruction")
            self.kl_tracker = keras.metrics.Mean(name="kl")

        # Keras 3 owns `metrics` (it is a TrackedList), so overriding it as a
        # property breaks the model at call time. The trackers below are read
        # directly from train_step's return value instead.

        def call(self, inputs):
            mean, log_variance, code = self.encoder(inputs)
            return self.decoder(code)

        def _compute_losses(self, x):
            # Not `_losses`: Keras 3's Model already owns that attribute (a
            # TrackedList), and shadowing it fails at the first train step.
            mean, log_variance, code = self.encoder(x)
            reconstruction = self.decoder(code)
            per_pixel = keras.losses.binary_crossentropy(x, reconstruction)
            reconstruction_loss = tensorflow.reduce_mean(per_pixel) * 784
            kl = -0.5 * tensorflow.reduce_mean(
                tensorflow.reduce_sum(
                    1 + log_variance - tensorflow.square(mean)
                    - tensorflow.exp(log_variance), axis=1))
            return reconstruction_loss, kl

        def train_step(self, data):
            x = data[0] if isinstance(data, tuple) else data
            with tensorflow.GradientTape() as tape:
                reconstruction_loss, kl = self._compute_losses(x)
                loss = reconstruction_loss + self.beta * kl
            self.optimizer.apply_gradients(
                zip(tape.gradient(loss, self.trainable_weights),
                    self.trainable_weights))
            self.reconstruction_tracker.update_state(reconstruction_loss)
            self.kl_tracker.update_state(kl)
            return {"reconstruction": self.reconstruction_tracker.result(),
                    "kl": self.kl_tracker.result()}

        def test_step(self, data):
            x = data[0] if isinstance(data, tuple) else data
            reconstruction_loss, kl = self._compute_losses(x)
            self.reconstruction_tracker.update_state(reconstruction_loss)
            self.kl_tracker.update_state(kl)
            return {"reconstruction": self.reconstruction_tracker.result(),
                    "kl": self.kl_tracker.result()}

    inputs = keras.layers.Input((784,))
    x = keras.layers.Dense(256, activation="relu")(inputs)
    x = keras.layers.Dense(64, activation="relu")(x)
    mean = keras.layers.Dense(latent, name="mean")(x)
    log_variance = keras.layers.Dense(latent, name="log_variance")(x)
    code = Sampler()([mean, log_variance])
    encoder = keras.Model(inputs, [mean, log_variance, code], name="encoder")

    latent_inputs = keras.layers.Input((latent,))
    y = keras.layers.Dense(64, activation="relu")(latent_inputs)
    y = keras.layers.Dense(256, activation="relu")(y)
    outputs = keras.layers.Dense(784, activation="sigmoid")(y)
    decoder = keras.Model(latent_inputs, outputs, name="decoder")

    model = VAE(encoder, decoder, beta)
    model.compile(optimizer=keras.optimizers.Adam(1e-3))
    return model


@functools.lru_cache(maxsize=1)
def _runs() -> dict:
    data = _data()
    out = {}
    for beta in BETAS:
        model = _build(beta)
        model.fit(data["x_train"], epochs=EPOCHS, batch_size=128, verbose=0)
        mean, log_variance, code = model.encoder.predict(data["x_test"],
                                                         verbose=0)
        reconstruction = model.decoder.predict(code, verbose=0)
        per_pixel = float(np.mean((reconstruction - data["x_test"]) ** 2))
        kl = float(np.mean(-0.5 * np.sum(1 + log_variance - mean ** 2
                                         - np.exp(log_variance), axis=1)))
        # Posterior collapse: the latent stops depending on the input, so the
        # means shrink towards zero and the variances towards one.
        out[beta] = {
            "mse": per_pixel, "kl": kl,
            "mean_std": float(mean.std()),
            "mean_variance": float(np.exp(log_variance).mean()),
            "active": int((mean.std(axis=0) > 0.1).sum()),
            "mean": mean, "code": code, "model": model,
        }
    return out


def beta_sweep(fig, axes, p: Palette) -> None:
    runs = _runs()
    left, right = fig.subplots(1, 2)
    mse = [runs[b]["mse"] for b in BETAS]
    kl = [runs[b]["kl"] for b in BETAS]
    positions = np.arange(len(BETAS))
    left.plot(positions, mse, "o-", ms=6, lw=2.0, color=p.green,
              label="reconstruction MSE")
    for x, value in zip(positions, mse):
        left.annotate(f"{value:.4f}", (x, value), textcoords="offset points",
                      xytext=(0, 8), ha="center", fontsize=7.5, color=p.green)
    left.set_xticks(positions)
    left.set_xticklabels([f"{b:g}" for b in BETAS])
    left.set_xlabel("weight on the KL term (beta)")
    left.set_ylabel("test reconstruction MSE")
    left.set_title(f"MNIST, {LATENT}-D latent, {EPOCHS} epochs", fontsize=10)
    left.legend(fontsize=8, loc="upper left")

    twin = right.twinx()
    right.plot(positions, kl, "o-", ms=6, lw=2.0, color=p.amber,
               label="KL divergence")
    twin.plot(positions, [runs[b]["mean_std"] for b in BETAS], "o--", ms=6,
              lw=1.8, color=p.blue, label="spread of the latent means")
    for x, value in zip(positions, kl):
        right.annotate(f"{value:.2f}", (x, value), textcoords="offset points",
                       xytext=(0, 8), ha="center", fontsize=7.5, color=p.amber)
    right.set_xticks(positions)
    right.set_xticklabels([f"{b:g}" for b in BETAS])
    right.set_xlabel("weight on the KL term (beta)")
    right.set_ylabel("KL divergence (nats)")
    twin.set_ylabel("std of the encoder means")
    right.set_title("at high beta the latent stops carrying information",
                    fontsize=10)
    lines = right.get_lines() + twin.get_lines()
    right.legend(lines, [line.get_label() for line in lines], fontsize=8,
                 loc="upper right")


def latent_structure(fig, axes, p: Palette) -> None:
    runs = _runs()
    data = _data()
    left, right = fig.subplots(1, 2)
    mean = runs[SWEEP_BETA]["mean"]
    labels = data["y_test"]
    scatter = left.scatter(mean[:, 0], mean[:, 1], c=labels, s=6, alpha=0.6,
                           cmap="tab10")
    left.set_xlabel("latent dimension 1")
    left.set_ylabel("latent dimension 2")
    left.set_title(f"encoder means, beta = {SWEEP_BETA:g}", fontsize=10)
    fig.colorbar(scatter, ax=left, pad=0.01, fraction=0.04, label="digit")

    # How close is the aggregate posterior to the prior it is pulled towards?
    radius = np.linalg.norm(mean, axis=1)
    prior = np.linalg.norm(np.random.default_rng(0).standard_normal(
        (len(mean), LATENT)), axis=1)
    right.hist(radius, bins=50, alpha=0.75, color=p.blue,
               label=f"encoder means (sd {mean.std():.3f})")
    right.hist(prior, bins=50, alpha=0.6, color=p.amber,
               label="standard normal")
    right.set_xlabel("distance from the origin")
    right.set_ylabel("images")
    right.set_title("the aggregate posterior against the prior", fontsize=10)
    right.legend(fontsize=8, loc="upper right")


def samples_and_interpolation(fig, axes, p: Palette) -> None:
    runs = _runs()
    data = _data()
    model = runs[SWEEP_BETA]["model"]
    top, bottom = fig.subplots(2, 1, height_ratios=(2.4, 1.0))

    # A grid over the prior, decoded.
    span = np.linspace(-2.5, 2.5, GRID)
    codes = np.array([[a, b] for b in span[::-1] for a in span], "float32")
    decoded = model.decoder.predict(codes, verbose=0).reshape(GRID, GRID, 28, 28)
    canvas = np.concatenate([np.concatenate(list(row), axis=1)
                             for row in decoded], axis=0)
    top.imshow(canvas, cmap="gray")
    top.set_title(f"the decoder over a {GRID}x{GRID} grid of the prior",
                  fontsize=10)
    top.set_xticks([])
    top.set_yticks([])
    top.grid(False)

    # Interpolate between two encoded digits.
    mean, _, _ = model.encoder.predict(data["x_test"][:2], verbose=0)
    steps = np.linspace(0, 1, 10)[:, None]
    path = (1 - steps) * mean[0] + steps * mean[1]
    walk = model.decoder.predict(path.astype("float32"), verbose=0)
    strip = np.concatenate([image.reshape(28, 28) for image in walk], axis=1)
    bottom.imshow(strip, cmap="gray")
    bottom.set_title("interpolating between two encoded digits", fontsize=10)
    bottom.set_xticks([])
    bottom.set_yticks([])
    bottom.grid(False)


FIGURES = [
    figure("beta-sweep", beta_sweep, size=(9.4, 3.5), axes=False),
    figure("latent-structure", latent_structure, size=(9.4, 3.6), axes=False),
    figure("samples-and-interpolation", samples_and_interpolation,
           size=(7.6, 6.4), axes=False),
]


if __name__ == "__main__":
    runs = _runs()
    print(f"=== MNIST, {LIMIT:,} images, {LATENT}-D latent, {EPOCHS} epochs ===")
    print(f"{'beta':>6} {'recon MSE':>10} {'KL (nats)':>10} "
          f"{'std of means':>13} {'mean posterior var':>19} {'active dims':>12}")
    for beta in BETAS:
        run = runs[beta]
        print(f"{beta:6g} {run['mse']:10.4f} {run['kl']:10.3f} "
              f"{run['mean_std']:13.4f} {run['mean_variance']:19.4f} "
              f"{run['active']:12d} of {LATENT}")
    print("beta = 0 is a plain autoencoder with a noisy encoder: no pressure")
    print("towards the prior, so sampling from the prior is meaningless.")
    print("At large beta the KL term wins and the latent carries nothing -")
    print("posterior collapse, visible as means with almost no spread")

    data = _data()
    run = runs[SWEEP_BETA]
    mean = run["mean"]
    print(f"\n=== the latent at beta = {SWEEP_BETA:g} ===")
    print(f"per-dimension std of the encoder means: "
          f"{np.round(mean.std(axis=0), 4).tolist()}")
    print(f"aggregate posterior: mean {mean.mean():.4f}, sd {mean.std():.4f} "
          f"(the prior is mean 0, sd 1)")
    print(f"mean distance from the origin {np.linalg.norm(mean, axis=1).mean():.4f}"
          f" against {np.sqrt(np.pi / 2) * 1.0:.4f} expected under the prior")
    for digit in range(10):
        rows = mean[data["y_test"] == digit]
        if len(rows):
            print(f"  digit {digit}: centre "
                  f"({rows[:, 0].mean():+.2f}, {rows[:, 1].mean():+.2f})  "
                  f"spread {rows.std():.2f}")
