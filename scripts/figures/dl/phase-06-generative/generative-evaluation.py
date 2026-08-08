"""Figures for *Evaluating Generative Models (FID, Coverage and Memorisation)*.

Sample grids are not evidence. This module implements the three measurements
that are — a Frechet distance in a feature space, class coverage, and a
nearest-neighbour check for memorisation — and then breaks each one on purpose,
because every generative metric has a cheap adversarial example.

``metric-behaviour``
    How the Frechet distance responds to blur, noise, class dropping and
    duplication, so the number has a scale attached.

``model-comparison``
    A VAE, a GAN and the training set itself scored on all three metrics.

``memorisation``
    Nearest training neighbours for generated samples, and the distance
    distribution — a model that copies scores perfectly on the other two.
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
SAMPLES = 2000
LATENT = 32
EPOCHS = 24
SHOW = 6


@functools.lru_cache(maxsize=1)
def _data() -> dict:
    return dataset("mnist", limit=LIMIT, flat=True)


@functools.lru_cache(maxsize=1)
def _features() -> dict:
    """A classifier trained on this data; its penultimate layer is the metric space.

    This is the honest version of "Inception features": a network trained on the
    same domain, used only to score. The page says so, because FID numbers from
    different feature extractors are not comparable.
    """
    keras = tf().keras
    data = _data()
    seed_everything(11)
    inputs = keras.layers.Input((784,))
    x = keras.layers.Dense(256, activation="relu")(inputs)
    x = keras.layers.Dense(64, activation="relu", name="features")(x)
    outputs = keras.layers.Dense(10, activation="softmax")(x)
    model = keras.Model(inputs, outputs)
    model.compile(keras.optimizers.Adam(1e-3),
                  "sparse_categorical_crossentropy", metrics=["accuracy"])
    history = model.fit(data["x_train"], data["y_train"], epochs=14,
                        batch_size=128, verbose=0,
                        validation_data=(data["x_test"], data["y_test"]))
    extractor = keras.Model(inputs, model.get_layer("features").output)
    return {"model": model, "extractor": extractor,
            "accuracy": float(history.history["val_accuracy"][-1])}


def _frechet(a, b) -> float:
    """The Frechet distance between two Gaussians fitted in feature space."""
    from scipy import linalg

    extractor = _features()["extractor"]
    fa = extractor.predict(a, verbose=0).astype("float64")
    fb = extractor.predict(b, verbose=0).astype("float64")
    mu_a, mu_b = fa.mean(axis=0), fb.mean(axis=0)
    cov_a = np.cov(fa, rowvar=False)
    cov_b = np.cov(fb, rowvar=False)
    covmean, _ = linalg.sqrtm(cov_a @ cov_b, disp=False)
    if np.iscomplexobj(covmean):
        covmean = covmean.real
    return float(((mu_a - mu_b) ** 2).sum()
                 + np.trace(cov_a + cov_b - 2 * covmean))


def _coverage(samples) -> dict:
    judge = _features()["model"]
    probabilities = judge.predict(samples, verbose=0)
    counts = np.bincount(probabilities.argmax(axis=1), minlength=10)
    share = counts / counts.sum()
    uniform = np.full(10, 0.1)
    return {"share": share,
            "classes": int((counts > len(samples) * 0.01).sum()),
            "divergence": float(np.sum(uniform * np.log(
                uniform / np.clip(share, 1e-9, None)))),
            "confidence": float(probabilities.max(axis=1).mean())}


def _memorisation(samples, reference) -> dict:
    """Nearest training neighbour for each sample, in pixel space."""
    squared = (np.sum(samples ** 2, axis=1)[:, None]
               + np.sum(reference ** 2, axis=1)[None, :]
               - 2 * samples @ reference.T)
    nearest = np.argmin(squared, axis=1)
    distance = np.sqrt(np.maximum(squared[np.arange(len(samples)), nearest], 0))
    return {"nearest": nearest, "distance": distance,
            "mean": float(distance.mean()),
            "duplicates": int((distance < 1.0).sum())}


@functools.lru_cache(maxsize=1)
def _corruptions() -> dict:
    """Break a real sample set in four ways and watch the metric respond."""
    data = _data()
    rng = np.random.default_rng(0)
    real = data["x_test"][:SAMPLES]
    other = data["x_train"][:SAMPLES]

    images = real.reshape(-1, 28, 28)
    padded = np.pad(images, ((0, 0), (2, 2), (2, 2)), mode="edge")
    blurred = sum(padded[:, i:i + 28, j:j + 28] for i in range(5)
                  for j in range(5)) / 25.0
    labels = data["y_test"][:SAMPLES * 3]
    dropped_pool = data["x_test"][:SAMPLES * 3][labels < 5]

    # Tile rather than np.repeat with a computed count: SAMPLES // 200 is zero
    # for any sample budget under 200 and would hand `predict` an empty array.
    base = real[:max(1, min(200, len(real) // 2))]
    copies = int(np.ceil(len(real) / len(base)))
    out = {
        "real (held out)": other,
        "blurred 5x5": blurred.reshape(len(images), -1).astype("float32"),
        "noise added": np.clip(real + rng.normal(0, 0.25, real.shape),
                               0, 1).astype("float32"),
        "5 of 10 classes": dropped_pool[:SAMPLES],
        f"{len(base)} images repeated": np.tile(base, (copies, 1))[:len(real)],
        "pure noise": rng.uniform(0, 1, real.shape).astype("float32"),
    }
    scores = {}
    for label, candidate in out.items():
        scores[label] = {
            "frechet": _frechet(real, candidate),
            **_coverage(candidate),
            **{"memorisation": _memorisation(candidate[:400], real)["mean"]},
        }
    return {"scores": scores, "real": real}


@functools.lru_cache(maxsize=1)
def _models() -> dict:
    """A VAE and a GAN on the same data, both deliberately small."""
    keras = tf().keras
    tensorflow = tf()
    data = _data()
    real = data["x_train"]

    # --- VAE ---------------------------------------------------------------
    seed_everything(3)

    class Sampler(keras.layers.Layer):
        def call(self, pair):
            mu, log_var = pair
            return mu + tensorflow.exp(0.5 * log_var) * tensorflow.random.normal(
                tensorflow.shape(mu))

    inputs = keras.layers.Input((784,))
    h = keras.layers.Dense(256, activation="relu")(inputs)
    mean = keras.layers.Dense(LATENT)(h)
    log_variance = keras.layers.Dense(LATENT)(h)
    encoder = keras.Model(inputs, [mean, log_variance,
                                   Sampler()([mean, log_variance])])
    latent_inputs = keras.layers.Input((LATENT,))
    d = keras.layers.Dense(256, activation="relu")(latent_inputs)
    decoder = keras.Model(latent_inputs,
                          keras.layers.Dense(784, activation="sigmoid")(d))

    class VAE(keras.Model):
        def __init__(self):
            super().__init__()
            self.encoder, self.decoder = encoder, decoder

        def call(self, x):
            return self.decoder(self.encoder(x)[2])

        def train_step(self, batch):
            x = batch[0] if isinstance(batch, tuple) else batch
            with tensorflow.GradientTape() as tape:
                mu, log_var, z = self.encoder(x)
                reconstruction = self.decoder(z)
                loss = tensorflow.reduce_mean(
                    keras.losses.binary_crossentropy(x, reconstruction)) * 784
                loss += -0.5 * tensorflow.reduce_mean(tensorflow.reduce_sum(
                    1 + log_var - tensorflow.square(mu)
                    - tensorflow.exp(log_var), axis=1))
            self.optimizer.apply_gradients(
                zip(tape.gradient(loss, self.trainable_weights),
                    self.trainable_weights))
            return {"loss": loss}

    vae = VAE()
    vae.compile(optimizer=keras.optimizers.Adam(1e-3))
    vae.fit(real, epochs=EPOCHS, batch_size=128, verbose=0)
    rng = np.random.default_rng(5)
    vae_samples = decoder.predict(
        rng.normal(0, 1, (SAMPLES, LATENT)).astype("float32"), verbose=0)

    # --- GAN ---------------------------------------------------------------
    seed_everything(4)
    generator = keras.Sequential([
        keras.layers.Input((LATENT,)),
        keras.layers.Dense(128), keras.layers.LeakyReLU(negative_slope=0.2),
        keras.layers.Dense(256), keras.layers.LeakyReLU(negative_slope=0.2),
        keras.layers.Dense(784, activation="sigmoid"),
    ])
    discriminator = keras.Sequential([
        keras.layers.Input((784,)),
        keras.layers.Dense(256), keras.layers.LeakyReLU(negative_slope=0.2),
        keras.layers.Dropout(0.3),
        keras.layers.Dense(1, activation="sigmoid"),
    ])
    discriminator.compile(keras.optimizers.Adam(2e-4), "binary_crossentropy")
    discriminator.trainable = False
    gan_input = keras.layers.Input((LATENT,))
    combined = keras.Model(gan_input, discriminator(generator(gan_input)))
    combined.compile(keras.optimizers.Adam(2e-4), "binary_crossentropy")
    discriminator.trainable = True

    batch = 128
    for _ in range(EPOCHS):
        order = rng.permutation(len(real))
        for step in range(len(real) // batch):
            chunk = real[order[step * batch:(step + 1) * batch]]
            noise = rng.normal(0, 1, (len(chunk), LATENT)).astype("float32")
            fake = generator.predict(noise, verbose=0)
            discriminator.train_on_batch(
                chunk, np.full((len(chunk), 1), 0.9, "float32"))
            discriminator.train_on_batch(
                fake, np.zeros((len(fake), 1), "float32"))
            # Keras 3 checks `trainable` at run time, so the flag has to be off
            # while the generator step executes or that step trains the
            # discriminator towards calling fakes real.
            discriminator.trainable = False
            combined.train_on_batch(
                rng.normal(0, 1, (batch, LATENT)).astype("float32"),
                np.ones((batch, 1), "float32"))
            discriminator.trainable = True
    gan_samples = generator.predict(
        rng.normal(0, 1, (SAMPLES, LATENT)).astype("float32"), verbose=0)
    return {"vae": vae_samples, "gan": gan_samples}


@functools.lru_cache(maxsize=1)
def _comparison() -> dict:
    data = _data()
    real = data["x_test"][:SAMPLES]
    models = _models()
    sources = {"real (held out)": data["x_train"][:SAMPLES],
               "VAE": models["vae"], "GAN": models["gan"]}
    out = {}
    for label, samples in sources.items():
        # Memorisation is scored against the TEST split for every row. Using
        # x_train would let the "real (held out)" row find itself -- it is drawn
        # from x_train -- and report a distance of 0.0031, which reads as
        # catastrophic copying when it is really a self-match.
        out[label] = {"frechet": _frechet(real, samples),
                      **_coverage(samples),
                      "memorisation": _memorisation(samples[:400],
                                                    data["x_test"])["mean"],
                      "samples": samples[:SHOW]}
    return out


def metric_behaviour(fig, axes, p: Palette) -> None:
    info = _corruptions()["scores"]
    left, right = fig.subplots(1, 2)
    labels = list(info)
    frechet = [info[label]["frechet"] for label in labels]
    positions = np.arange(len(labels))
    left.barh(positions, frechet, 0.55, color=p.blue)
    for y, value in zip(positions, frechet):
        left.annotate(f"{value:.2f}", (value, y), xytext=(6, 0),
                      textcoords="offset points", va="center", fontsize=8,
                      color=p.fg)
    left.set_yticks(positions)
    left.set_yticklabels(labels, fontsize=8.5)
    left.invert_yaxis()
    left.set_xscale("symlog")
    left.set_xlim(0, max(frechet) * 3)
    left.set_xlabel("Frechet distance to the real set (log)")
    left.set_title(f"{SAMPLES:,} samples each", fontsize=10)

    coverage = [info[label]["divergence"] for label in labels]
    right.barh(positions, coverage, 0.55, color=p.amber)
    for y, value, label in zip(positions, coverage, labels):
        right.annotate(f"{value:.3f}  ({info[label]['classes']}/10 classes)",
                       (value, y), xytext=(6, 0),
                       textcoords="offset points", va="center", fontsize=8,
                       color=p.fg)
    right.set_yticks(positions)
    right.set_yticklabels([])
    right.set_xlim(0, max(coverage) * 2.2)
    right.set_xlabel("KL from uniform class coverage")
    right.set_title("the two metrics disagree about which failure is worse",
                    fontsize=10)


def model_comparison(fig, axes, p: Palette) -> None:
    info = _comparison()
    labels = list(info)
    left, right = fig.subplots(1, 2)
    metrics = (("frechet", "Frechet distance"),
               ("divergence", "KL from uniform"),
               ("confidence", "judge confidence"),
               ("memorisation", "mean distance to nearest\nheld-out real image"))
    positions = np.arange(len(labels))
    width = 0.8 / len(metrics)
    colors = (p.blue, p.amber, p.purple, p.green)
    for index, ((key, name), color) in enumerate(zip(metrics, colors)):
        offset = (index - (len(metrics) - 1) / 2) * width
        values = [info[label][key] for label in labels]
        scale = max(values) or 1.0
        left.bar(positions + offset, [v / scale for v in values], width * 0.9,
                 color=color, label=f"{name} (max {scale:.2f})")
        for x, value in zip(positions + offset, values):
            left.annotate(f"{value:.2f}", (x, value / scale),
                          textcoords="offset points", xytext=(0, 3),
                          ha="center", fontsize=6.5, color=p.fg)
    left.set_xticks(positions)
    left.set_xticklabels(labels, fontsize=8.5)
    left.set_ylim(0, 1.35)
    left.set_ylabel("each metric scaled to its own maximum")
    left.set_title("three models, four numbers", fontsize=10)
    left.legend(fontsize=6.5, loc="upper center", ncol=2)

    right.axis("off")
    canvas = np.concatenate([
        np.concatenate([info[label]["samples"][i].reshape(28, 28)
                        for i in range(SHOW)], axis=1)
        for label in labels], axis=0)
    right.imshow(canvas, cmap="gray")
    right.set_title(" / ".join(labels), fontsize=9)
    right.grid(False)


def memorisation(fig, axes, p: Palette) -> None:
    data = _data()
    info = _comparison()
    corruptions = _corruptions()["scores"]
    top, bottom = fig.subplots(2, 1, height_ratios=(1.0, 1.1))

    generated = _models()["gan"][:SHOW]
    found = _memorisation(generated, data["x_train"])
    strip = np.concatenate([
        np.concatenate([image.reshape(28, 28) for image in generated], axis=1),
        np.concatenate([data["x_train"][index].reshape(28, 28)
                        for index in found["nearest"]], axis=1)], axis=0)
    top.imshow(strip, cmap="gray")
    top.set_title("GAN samples (top) and their nearest training images "
                  "(bottom)", fontsize=10)
    top.set_xticks([])
    top.set_yticks([])
    top.grid(False)

    for label, color in (("real (held out)", p.muted), ("VAE", p.blue),
                         ("GAN", p.green)):
        distances = _memorisation(
            (data["x_train"][:400] if label == "real (held out)"
             else _models()["vae" if label == "VAE" else "gan"][:400]),
            data["x_test"])["distance"]
        bottom.hist(distances, bins=40, alpha=0.55, color=color, label=label)
    duplicated = next(key for key in corruptions if key.endswith("repeated"))
    copied = corruptions[duplicated]["memorisation"]
    bottom.axvline(copied, color=p.red, lw=1.6, ls="--",
                   label=f"{duplicated} ({copied:.2f})")
    bottom.set_xlabel("distance to the nearest image in the other split")
    bottom.set_ylabel("samples")
    bottom.set_title("a model that copies its training data scores perfectly "
                     "on the other metrics", fontsize=10)
    bottom.legend(fontsize=7.5, loc="upper right")


FIGURES = [
    figure("metric-behaviour", metric_behaviour, size=(9.6, 3.6), axes=False),
    figure("model-comparison", model_comparison, size=(9.6, 3.6), axes=False),
    figure("memorisation", memorisation, size=(9.0, 5.0), axes=False),
]


if __name__ == "__main__":
    features = _features()
    print(f"=== the feature extractor: a classifier at "
          f"{features['accuracy']:.4f} accuracy ===")
    print("FID-style numbers depend entirely on this network, so they are not")
    print("comparable with published Inception-based figures")

    print(f"\n=== how each metric responds to a known corruption "
          f"({SAMPLES:,} samples) ===")
    scores = _corruptions()["scores"]
    print(f"{'source':22s} {'Frechet':>9} {'classes':>8} {'KL unif':>9} "
          f"{'confidence':>11} {'dist to real':>13}")
    for label, entry in scores.items():
        print(f"{label:22s} {entry['frechet']:9.3f} {entry['classes']:8d} "
              f"{entry['divergence']:9.4f} {entry['confidence']:11.4f} "
              f"{entry['memorisation']:13.4f}")
    print("note the row that repeats 200 images: near-perfect Frechet distance")
    print("and coverage, because copying the data matches its statistics")

    print(f"\n=== three models on the same metrics ===")
    comparison = _comparison()
    print(f"{'model':18s} {'Frechet':>9} {'classes':>8} {'KL unif':>9} "
          f"{'confidence':>11} {'nearest held-out':>17}")
    for label, entry in comparison.items():
        print(f"{label:18s} {entry['frechet']:9.3f} {entry['classes']:8d} "
              f"{entry['divergence']:9.4f} {entry['confidence']:11.4f} "
              f"{entry['memorisation']:19.4f}")
    print("the 'real (held out)' row is the floor: a perfect model should")
    print("score like a second sample of the same distribution, not like zero")
