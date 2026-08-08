"""Figures for *Generative Adversarial Networks (GANs)*.

Two things make GAN pages misleading: the losses are not comparable to anything
(a generator loss of 0.7 means nothing on its own), and cherry-picked samples
hide mode collapse. This module measures both — class coverage via a separately
trained MNIST classifier, and the loss curves next to that coverage so the
relationship is visible.

``training-curves``
    Discriminator and generator loss per epoch, with discriminator accuracy on
    real and fake batches — the only numbers that say whether the game is
    balanced.

``coverage``
    What fraction of the ten digit classes the generator actually produces,
    scored by an independent classifier, against the same measurement for a VAE
    trained on the same data.

``samples``
    An uncurated grid at three points in training, so "improving" is visible
    rather than asserted.
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
EPOCHS = 24
LATENT = 32
BATCH = 128
SNAPSHOTS = (1, 8, 24)
GRID = 8

# The discriminator gets two updates per step (one real batch, one fake batch)
# against the generator's one, which is what most tutorials do and is why the
# first run here ended with D catching 100% of fakes. Each configuration below
# is one way of handing capacity back to the generator.
CONFIGS = {
    "as written (D lr 2e-4)": {"d_lr": 2e-4, "g_steps": 1, "d_dropout": 0.3},
    "D lr 5e-5": {"d_lr": 5e-5, "g_steps": 1, "d_dropout": 0.3},
    "2 generator steps": {"d_lr": 2e-4, "g_steps": 2, "d_dropout": 0.3},
    "D lr 5e-5 + dropout 0.5": {"d_lr": 5e-5, "g_steps": 2, "d_dropout": 0.5},
}


@functools.lru_cache(maxsize=1)
def _data() -> dict:
    return dataset("mnist", limit=LIMIT, flat=True)


@functools.lru_cache(maxsize=1)
def _judge() -> dict:
    """An independent classifier, used only to score what the models produce."""
    keras = tf().keras
    data = _data()
    seed_everything(7)
    model = keras.Sequential([
        keras.layers.Input((784,)),
        keras.layers.Dense(128, activation="relu"),
        keras.layers.Dense(64, activation="relu"),
        keras.layers.Dense(10, activation="softmax"),
    ])
    model.compile(keras.optimizers.Adam(1e-3),
                  "sparse_categorical_crossentropy", metrics=["accuracy"])
    history = model.fit(data["x_train"], data["y_train"], epochs=12,
                        batch_size=128, verbose=0,
                        validation_data=(data["x_test"], data["y_test"]))
    return {"model": model,
            "accuracy": float(history.history["val_accuracy"][-1])}


def _generator(seed: int = 0):
    keras = tf().keras
    seed_everything(seed)
    return keras.Sequential([
        keras.layers.Input((LATENT,)),
        keras.layers.Dense(128),
        keras.layers.LeakyReLU(negative_slope=0.2),
        keras.layers.Dense(256),
        keras.layers.LeakyReLU(negative_slope=0.2),
        keras.layers.Dense(784, activation="sigmoid"),
    ], name="generator")


def _called_real(y_true, y_pred):
    """Share of the batch the discriminator calls real (probability > 0.5).

    Deliberately not `metrics=["accuracy"]`: the real labels are smoothed to
    0.9, and Keras compares the *rounded* prediction with y_true, so 0.9 equals
    neither 0 nor 1 and binary accuracy reads 0.0000 at every epoch no matter
    how the game is going. This metric ignores the label and reports the
    decision, which is what the caller needs.
    """
    del y_true
    tensorflow = tf()
    return tensorflow.reduce_mean(tensorflow.cast(y_pred > 0.5, "float32"))


def _discriminator(seed: int = 0, learning_rate: float = 2e-4,
                   dropout: float = 0.3):
    keras = tf().keras
    seed_everything(seed + 1)
    model = keras.Sequential([
        keras.layers.Input((784,)),
        keras.layers.Dense(256),
        keras.layers.LeakyReLU(negative_slope=0.2),
        keras.layers.Dropout(dropout),
        keras.layers.Dense(128),
        keras.layers.LeakyReLU(negative_slope=0.2),
        keras.layers.Dense(1, activation="sigmoid"),
    ], name="discriminator")
    model.compile(keras.optimizers.Adam(learning_rate), "binary_crossentropy",
                  metrics=[_called_real])
    return model


def _generator_step(combined, discriminator, noise) -> float:
    """Train the generator with the discriminator genuinely frozen.

    The generator's target is "call my fakes real". If the discriminator is
    trainable while that runs, it is dragged towards agreeing -- the opposite of
    its job.
    """
    discriminator.trainable = False
    loss = combined.train_on_batch(noise, np.ones((len(noise), 1), "float32"))
    discriminator.trainable = True
    return float(loss)


@functools.lru_cache(maxsize=8)
def _train(config: str = "as written (D lr 2e-4)") -> dict:
    """A minimal GAN loop, written out so the alternation is visible."""
    keras = tf().keras
    data = _data()
    real = data["x_train"]
    settings = CONFIGS[config]
    generator = _generator()
    discriminator = _discriminator(learning_rate=settings["d_lr"],
                                   dropout=settings["d_dropout"])

    discriminator.trainable = False
    combined_input = keras.layers.Input((LATENT,))
    combined = keras.Model(combined_input,
                           discriminator(generator(combined_input)))
    combined.compile(keras.optimizers.Adam(2e-4), "binary_crossentropy")
    discriminator.trainable = True
    # Keras 3 reads `trainable` when the step RUNS, not when the model was
    # compiled, so the classic Keras 2 idiom (freeze, compile, unfreeze) leaves
    # the discriminator trainable inside the generator step -- which then
    # trains it towards "fakes are real". Measured: 20 generator steps moved
    # the discriminator's weights by 0.0117. The flag has to be toggled around
    # each generator step instead; see `_generator_step`.

    rng = np.random.default_rng(0)
    history = {"d_loss": [], "g_loss": [], "d_real": [], "d_fake": []}
    snapshots = {}
    started = time.perf_counter()
    steps = len(real) // BATCH
    for epoch in range(1, EPOCHS + 1):
        order = rng.permutation(len(real))
        totals = np.zeros(4)
        for step in range(steps):
            batch = real[order[step * BATCH:(step + 1) * BATCH]]
            noise = rng.normal(0, 1, (len(batch), LATENT)).astype("float32")
            fake = generator.predict(noise, verbose=0)
            # One-sided label smoothing on the real labels only.
            d_real = discriminator.train_on_batch(
                batch, np.full((len(batch), 1), 0.9, "float32"))
            d_fake = discriminator.train_on_batch(
                fake, np.zeros((len(fake), 1), "float32"))
            g_losses = [
                _generator_step(combined, discriminator,
                                rng.normal(0, 1, (BATCH, LATENT))
                                .astype("float32"))
                for _ in range(settings["g_steps"])]
            # The metric reports "called real", so accuracy on the fake batch
            # is one minus it.
            totals += (float(d_real[0]) + float(d_fake[0])) / 2, \
                float(np.mean(g_losses)), \
                float(d_real[1]), 1.0 - float(d_fake[1])
        totals /= steps
        history["d_loss"].append(float(totals[0]))
        history["g_loss"].append(float(totals[1]))
        history["d_real"].append(float(totals[2]))
        history["d_fake"].append(float(totals[3]))
        # Snapshot the requested epochs, and always the last one — otherwise a
        # shrunk EPOCHS (smoke.py) leaves the samples figure with no data.
        if epoch in SNAPSHOTS or epoch == EPOCHS:
            noise = np.random.default_rng(1).normal(
                0, 1, (GRID * GRID, LATENT)).astype("float32")
            snapshots[epoch] = generator.predict(noise, verbose=0)
    return {"generator": generator, "history": history,
            "snapshots": snapshots, "config": config,
            "seconds": time.perf_counter() - started}


@functools.lru_cache(maxsize=1)
def _balance_runs() -> dict:
    """Every configuration, scored by the same judge."""
    rng = np.random.default_rng(11)
    noise = rng.normal(0, 1, (2000, LATENT)).astype("float32")
    out = {}
    for config in CONFIGS:
        info = _train(config)
        samples = info["generator"].predict(noise, verbose=0)
        out[config] = {"history": info["history"], "coverage": _coverage(samples),
                       "seconds": info["seconds"]}
    return out


def _best_config() -> str:
    """The configuration that covered the most classes, then lowest KL."""
    runs = _balance_runs()
    return min(runs, key=lambda name: (-runs[name]["coverage"]["classes"],
                                       runs[name]["coverage"]["divergence"]))


@functools.lru_cache(maxsize=1)
def _vae_baseline() -> dict:
    """A VAE on the same data, so coverage has something to compare against."""
    keras = tf().keras
    tensorflow = tf()
    data = _data()
    seed_everything(3)

    inputs = keras.layers.Input((784,))
    x = keras.layers.Dense(256, activation="relu")(inputs)
    mean = keras.layers.Dense(LATENT)(x)
    log_variance = keras.layers.Dense(LATENT)(x)

    class Sampler(keras.layers.Layer):
        def call(self, pair):
            mu, log_var = pair
            noise = tensorflow.random.normal(tensorflow.shape(mu))
            return mu + tensorflow.exp(0.5 * log_var) * noise

    code = Sampler()([mean, log_variance])
    encoder = keras.Model(inputs, [mean, log_variance, code])
    latent_inputs = keras.layers.Input((LATENT,))
    y = keras.layers.Dense(256, activation="relu")(latent_inputs)
    decoder = keras.Model(latent_inputs,
                          keras.layers.Dense(784, activation="sigmoid")(y))

    class VAE(keras.Model):
        def __init__(self, encoder, decoder):
            super().__init__()
            self.encoder, self.decoder = encoder, decoder

        def call(self, inputs):
            return self.decoder(self.encoder(inputs)[2])

        def train_step(self, batch):
            x = batch[0] if isinstance(batch, tuple) else batch
            with tensorflow.GradientTape() as tape:
                mu, log_var, z = self.encoder(x)
                reconstruction = self.decoder(z)
                loss = tensorflow.reduce_mean(
                    keras.losses.binary_crossentropy(x, reconstruction)) * 784
                loss += -0.5 * tensorflow.reduce_mean(
                    tensorflow.reduce_sum(1 + log_var - tensorflow.square(mu)
                                          - tensorflow.exp(log_var), axis=1))
            self.optimizer.apply_gradients(
                zip(tape.gradient(loss, self.trainable_weights),
                    self.trainable_weights))
            return {"loss": loss}

    model = VAE(encoder, decoder)
    model.compile(optimizer=keras.optimizers.Adam(1e-3))
    model.fit(data["x_train"], epochs=EPOCHS, batch_size=BATCH, verbose=0)
    noise = np.random.default_rng(2).normal(0, 1,
                                            (2000, LATENT)).astype("float32")
    return {"samples": decoder.predict(noise, verbose=0)}


def _coverage(samples) -> dict:
    judge = _judge()["model"]
    probabilities = judge.predict(samples, verbose=0)
    predicted = probabilities.argmax(axis=1)
    counts = np.bincount(predicted, minlength=10)
    share = counts / counts.sum()
    # Reverse KL against a uniform target: how far from covering every class.
    uniform = np.full(10, 0.1)
    divergence = float(np.sum(uniform * np.log(uniform
                                               / np.clip(share, 1e-9, None))))
    return {"counts": counts, "share": share,
            "classes": int((counts > len(samples) * 0.01).sum()),
            "divergence": divergence,
            "confidence": float(probabilities.max(axis=1).mean())}


def training_curves(fig, axes, p: Palette) -> None:
    runs = _balance_runs()
    left, right = fig.subplots(1, 2)
    colors = (p.red, p.blue, p.green, p.purple)
    for (config, entry), color in zip(runs.items(), colors):
        history = entry["history"]
        epochs = range(1, len(history["d_loss"]) + 1)
        left.plot(epochs, history["g_loss"], lw=1.9, color=color,
                  label=f"{config} (ends {history['g_loss'][-1]:.2f})")
        right.plot(epochs, history["d_fake"], lw=1.9, color=color,
                   label=f"{config} (ends {history['d_fake'][-1]:.4f})")
    left.set_xlabel("epoch")
    left.set_ylabel("generator loss")
    left.set_title(f"MNIST, {LIMIT:,} images, {EPOCHS} epochs each",
                   fontsize=10)
    left.legend(fontsize=7, loc="upper left")

    right.axhline(0.5, color=p.muted, lw=1.2, ls="--")
    right.annotate("0.5 = equilibrium", (1, 0.52), fontsize=8, color=p.muted)
    right.set_xlabel("epoch")
    right.set_ylabel("D accuracy on fake batches")
    right.set_ylim(0, 1.05)
    right.set_title("a rising generator loss means D is pulling away",
                    fontsize=10)
    right.legend(fontsize=7, loc="lower left")


def coverage(fig, axes, p: Palette) -> None:
    judge = _judge()
    best = _best_config()
    gan = _balance_runs()[best]["coverage"]
    vae = _coverage(_vae_baseline()["samples"])
    data = _data()
    real = _coverage(data["x_test"][:2000])

    left, right = fig.subplots(1, 2)
    positions = np.arange(10)
    width = 0.27
    for offset, label, entry, color in ((-width, "real data", real, p.muted),
                                        (0.0, f"GAN, {best}", gan, p.green),
                                        (width, "VAE", vae, p.blue)):
        left.bar(positions + offset, entry["share"], width * 0.92, color=color,
                 label=label)
    left.axhline(0.1, color=p.amber, lw=1.2, ls="--")
    left.annotate("uniform = 0.10", (9.2, 0.105), fontsize=8, color=p.amber,
                  ha="right")
    left.set_xticks(positions)
    left.set_xlabel("digit, as judged by an independent classifier")
    left.set_ylabel("share of 2,000 samples")
    left.set_title(f"class coverage (judge accuracy "
                   f"{judge['accuracy']:.4f})", fontsize=10)
    left.legend(fontsize=8, loc="upper right")

    labels = ("real data", "GAN (best)", "VAE")
    entries = (real, gan, vae)
    metrics = ("classes covered", "divergence from uniform",
               "judge confidence")
    values = [[entry["classes"] / 10 for entry in entries],
              [entry["divergence"] for entry in entries],
              [entry["confidence"] for entry in entries]]
    positions = np.arange(len(labels))
    for index, (metric, row) in enumerate(zip(metrics, values)):
        offset = (index - 1) * 0.27
        right.bar(positions + offset, row, 0.25,
                  color=(p.green, p.amber, p.purple)[index], label=metric)
        for x, value in zip(positions + offset, row):
            right.annotate(f"{value:.3f}", (x, value),
                           textcoords="offset points", xytext=(0, 3),
                           ha="center", fontsize=7, color=p.fg)
    right.set_xticks(positions)
    right.set_xticklabels(labels)
    right.set_title("three ways to ask 'did it cover the data?'", fontsize=10)
    right.legend(fontsize=7.5, loc="upper left")


def samples(fig, axes, p: Palette) -> None:
    info = _train(_best_config())
    epochs = sorted(info["snapshots"])
    grid = fig.subplots(1, len(epochs))
    grid = np.atleast_1d(grid)
    for ax, epoch in zip(grid, epochs):
        images = info["snapshots"][epoch].reshape(GRID, GRID, 28, 28)
        canvas = np.concatenate([np.concatenate(list(row), axis=1)
                                 for row in images], axis=0)
        ax.imshow(canvas, cmap="gray")
        ax.set_title(f"epoch {epoch} — {info['config']}", fontsize=9)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.grid(False)


FIGURES = [
    figure("training-curves", training_curves, size=(9.4, 3.5), axes=False),
    figure("coverage", coverage, size=(9.6, 3.6), axes=False),
    figure("samples", samples, size=(9.4, 3.4), axes=False),
]


if __name__ == "__main__":
    judge = _judge()
    print(f"=== the judge: an independent classifier, val accuracy "
          f"{judge['accuracy']:.4f} ===")
    runs = _balance_runs()
    print(f"\n=== the balance sweep: {EPOCHS} epochs per configuration ===")
    print("D gets two updates per step (real batch, fake batch) against G's")
    print("one, so 'as written' is the tutorial default, not a neutral choice")
    for config, entry in runs.items():
        history = entry["history"]
        print(f"\n[{config}]  {entry['seconds']:.0f}s")
        print(f"{'epoch':>6} {'D loss':>8} {'G loss':>8} {'D acc real':>11} "
              f"{'D acc fake':>11}")
        for epoch in range(len(history["d_loss"])):
            if epoch < 2 or epoch >= len(history["d_loss"]) - 2:
                print(f"{epoch + 1:6d} {history['d_loss'][epoch]:8.4f} "
                      f"{history['g_loss'][epoch]:8.4f} "
                      f"{history['d_real'][epoch]:11.4f} "
                      f"{history['d_fake'][epoch]:11.4f}")
    print(f"\nthe theoretical equilibrium is D loss log 2 = {np.log(2):.4f} "
          f"with both accuracies at 0.5")

    print("\n=== what each configuration produced (2,000 samples) ===")
    print(f"{'configuration':26s} {'classes':>8} {'KL unif':>9} "
          f"{'confidence':>11} {'D acc fake (last)':>18}")
    for config, entry in runs.items():
        cover = entry["coverage"]
        print(f"{config:26s} {cover['classes']:8d} {cover['divergence']:9.4f} "
              f"{cover['confidence']:11.4f} "
              f"{entry['history']['d_fake'][-1]:18.4f}")
    best = _best_config()
    print(f"best by coverage: {best}")

    gan = runs[best]["coverage"]
    vae = _coverage(_vae_baseline()["samples"])
    real = _coverage(_data()["x_test"][:2000])
    print("\n=== class coverage over 2,000 samples ===")
    print(f"{'source':10s} " + " ".join(f"{d:>5}" for d in range(10))
          + f" {'classes':>8} {'KL vs uniform':>14} {'confidence':>11}")
    for label, entry in (("real", real), (f"GAN", gan), ("VAE", vae)):
        print(f"{label:10s} " + " ".join(f"{v:5.3f}" for v in entry["share"])
              + f" {entry['classes']:8d} {entry['divergence']:14.4f} "
              f"{entry['confidence']:11.4f}")
    print("the GAN row is the BEST configuration of the sweep, not the first")
    print("one tried -- reporting the default alone would have understated")
    print("what the architecture can do and overstated the VAE's margin")
