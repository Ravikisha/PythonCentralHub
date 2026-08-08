"""Figures for *Capstone 3: A Generative Model You Can Defend*.

The generative capstone is not "train a VAE". It is "train a VAE and produce
the evidence that it works", because on the generative pages the second half
was consistently the harder one.

The deliverable this module measures is a report: a floor, three metrics, a
memorisation check, and an uncurated sample grid -- with a deliberately broken
submission scored alongside to show what the report is protecting against.

``report``
    The full evaluation of three models against the real-data floor: a VAE, an
    undertrained VAE, and a "model" that memorised its training set.

``latent``
    What the latent space looks like and whether the aggregate posterior
    actually matches the prior -- the check that decides if sampling works.

``samples``
    Uncurated grids from each model, next to the numbers that describe them.
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
EPOCHS = 25
SHORT_EPOCHS = 2
LATENT = 8
SAMPLES = 1500
GRID = 6


@functools.lru_cache(maxsize=1)
def _data() -> dict:
    return dataset("mnist", limit=LIMIT, flat=True)


@functools.lru_cache(maxsize=1)
def _judge() -> dict:
    """The classifier that scores coverage, and whose features score distance."""
    keras = tf().keras
    data = _data()
    seed_everything(11)
    inputs = keras.layers.Input((784,))
    hidden = keras.layers.Dense(256, activation="relu")(inputs)
    features = keras.layers.Dense(64, activation="relu", name="features")(hidden)
    outputs = keras.layers.Dense(10, activation="softmax")(features)
    model = keras.Model(inputs, outputs)
    model.compile(keras.optimizers.Adam(1e-3),
                  "sparse_categorical_crossentropy", metrics=["accuracy"])
    history = model.fit(data["x_train"], data["y_train"], epochs=14,
                        batch_size=128, verbose=0,
                        validation_data=(data["x_test"], data["y_test"]))
    return {"model": model,
            "extractor": keras.Model(inputs, model.get_layer("features").output),
            "accuracy": float(history.history["val_accuracy"][-1])}


@functools.lru_cache(maxsize=4)
def _vae(epochs: int = EPOCHS) -> dict:
    keras = tf().keras
    tensorflow = tf()
    data = _data()
    seed_everything(3)

    class Sampler(keras.layers.Layer):
        def call(self, pair):
            mean, log_variance = pair
            noise = tensorflow.random.normal(tensorflow.shape(mean))
            return mean + tensorflow.exp(0.5 * log_variance) * noise

    inputs = keras.layers.Input((784,))
    hidden = keras.layers.Dense(256, activation="relu")(inputs)
    mean = keras.layers.Dense(LATENT)(hidden)
    log_variance = keras.layers.Dense(LATENT)(hidden)
    encoder = keras.Model(inputs, [mean, log_variance,
                                   Sampler()([mean, log_variance])])
    latent_inputs = keras.layers.Input((LATENT,))
    decoded = keras.layers.Dense(256, activation="relu")(latent_inputs)
    decoder = keras.Model(latent_inputs,
                          keras.layers.Dense(784, activation="sigmoid")(decoded))

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

    model = VAE()
    model.compile(optimizer=keras.optimizers.Adam(1e-3))
    started = time.perf_counter()
    model.fit(data["x_train"], epochs=epochs, batch_size=128, verbose=0)
    rng = np.random.default_rng(5)
    samples = decoder.predict(
        rng.normal(0, 1, (SAMPLES, LATENT)).astype("float32"), verbose=0)
    means = encoder.predict(data["x_test"][:2000], verbose=0)[0]
    return {"decoder": decoder, "encoder": encoder, "samples": samples,
            "means": means, "epochs": epochs,
            "seconds": time.perf_counter() - started}


def _frechet(a, b) -> float:
    from scipy import linalg

    extractor = _judge()["extractor"]
    fa = extractor.predict(a, verbose=0).astype("float64")
    fb = extractor.predict(b, verbose=0).astype("float64")
    cov_a = np.cov(fa, rowvar=False)
    cov_b = np.cov(fb, rowvar=False)
    covmean, _ = linalg.sqrtm(cov_a @ cov_b, disp=False)
    if np.iscomplexobj(covmean):
        covmean = covmean.real
    return float(((fa.mean(axis=0) - fb.mean(axis=0)) ** 2).sum()
                 + np.trace(cov_a + cov_b - 2 * covmean))


def _coverage(samples) -> dict:
    probabilities = _judge()["model"].predict(samples, verbose=0)
    counts = np.bincount(probabilities.argmax(axis=1), minlength=10)
    share = counts / counts.sum()
    uniform = np.full(10, 0.1)
    return {"share": share,
            "classes": int((counts > len(samples) * 0.01).sum()),
            "divergence": float(np.sum(uniform * np.log(
                uniform / np.clip(share, 1e-9, None)))),
            "confidence": float(probabilities.max(axis=1).mean())}


def _nearest(samples, reference) -> float:
    squared = (np.sum(samples ** 2, axis=1)[:, None]
               + np.sum(reference ** 2, axis=1)[None, :]
               - 2 * samples @ reference.T)
    picked = squared[np.arange(len(samples)), np.argmin(squared, axis=1)]
    return float(np.sqrt(np.maximum(picked, 0)).mean())


@functools.lru_cache(maxsize=1)
def _report() -> dict:
    """The evaluation every generative submission should carry."""
    data = _data()
    train = data["x_train"]
    # The test split is halved. The floor row has to be real data that appears
    # in NEITHER reference, or it scores zero against itself and the whole
    # table is meaningless.
    half = min(SAMPLES, len(data["x_test"]) // 2)
    held_out = data["x_test"][:half]
    other_real = data["x_test"][half:2 * half]
    train_reference = train[:4000]

    rng = np.random.default_rng(0)
    memoriser = np.tile(train[:150], (SAMPLES // 150 + 1, 1))[:SAMPLES]

    sources = {
        "real, held out (the floor)": other_real,
        "VAE (25 epochs)": _vae(EPOCHS)["samples"],
        "VAE (2 epochs)": _vae(SHORT_EPOCHS)["samples"],
        "memorised 150 images": memoriser,
    }
    out = {}
    for label, samples in sources.items():
        out[label] = {
            "frechet": _frechet(held_out, samples),
            **_coverage(samples),
            # TWO memorisation checks, against different splits. The held-out
            # one answers "is this a copy of some real image"; only the
            # training one answers "is this a copy of something the model was
            # SHOWN", and the memoriser below is invisible to the first.
            "nearest_held_out": _nearest(samples[:400], held_out),
            "nearest_train": _nearest(samples[:400], train_reference),
            "grid": samples[:GRID * GRID],
        }
    del rng
    return out


@functools.lru_cache(maxsize=1)
def _latent() -> dict:
    info = _vae(EPOCHS)
    means = info["means"]
    data = _data()
    distances = np.linalg.norm(means, axis=1)
    # For a standard normal in d dimensions the expected radius is
    # sqrt(2) * gamma((d+1)/2) / gamma(d/2); approximate with sqrt(d - 0.5).
    expected = float(np.sqrt(LATENT - 0.5))
    rng = np.random.default_rng(0)
    prior = np.linalg.norm(rng.normal(0, 1, (len(means), LATENT)), axis=1)
    active = int(np.sum(means.std(axis=0) > 0.1))
    return {"means": means, "labels": data["y_test"][:len(means)],
            "distances": distances, "prior": prior,
            "mean_distance": float(distances.mean()),
            "expected": expected,
            "prior_mean": float(prior.mean()),
            "active": active,
            "per_dimension": means.std(axis=0)}


def report(fig, axes, p: Palette) -> None:
    runs = _report()
    labels = list(runs)
    left, right = fig.subplots(1, 2, width_ratios=(1.15, 1.0))
    metrics = (("frechet", "Frechet distance"),
               ("divergence", "KL from uniform"),
               ("nearest_held_out", "nearest HELD-OUT image"),
               ("nearest_train", "nearest TRAINING image"))
    positions = np.arange(len(metrics))
    width = 0.2
    colours = (p.muted, p.green, p.amber, p.red)
    scales = [max(abs(runs[label][key]) for label in labels) or 1.0
              for key, _ in metrics]
    for index, (label, colour) in enumerate(zip(labels, colours)):
        values = [runs[label][key] for key, _ in metrics]
        offset = (index - 1.5) * width
        left.bar(positions + offset, [v / s for v, s in zip(values, scales)],
                 width * 0.9, color=colour, label=label)
        for x, value, scale in zip(positions + offset, values, scales):
            left.annotate(f"{value:.2f}", (x, value / scale), xytext=(0, 3),
                          textcoords="offset points", ha="center",
                          fontsize=6, color=p.fg)
    left.set_xticks(positions)
    left.set_xticklabels([name for _, name in metrics], fontsize=8)
    left.set_ylim(0, 1.4)
    left.set_ylabel("scaled to the largest value per metric")
    left.set_title(f"{SAMPLES:,} samples each, one judge", fontsize=10)
    left.legend(fontsize=6.5, loc="upper center", ncol=2)

    positions = np.arange(10)
    for label, colour in zip(labels, colours):
        right.plot(positions, runs[label]["share"], "o-", ms=4, lw=1.6,
                   color=colour, label=f"{label} ({runs[label]['classes']}/10)")
    right.axhline(0.1, color=p.fg, lw=1.0, ls=":")
    right.set_xticks(positions)
    right.set_xlabel("digit, as judged by an independent classifier")
    right.set_ylabel("share of samples")
    right.set_title("coverage is what the memoriser cannot fake away",
                    fontsize=10)
    right.legend(fontsize=6.5, loc="upper right")


def latent(fig, axes, p: Palette) -> None:
    info = _latent()
    left, right = fig.subplots(1, 2)
    means = info["means"]
    scatter = left.scatter(means[:, 0], means[:, 1], c=info["labels"], s=8,
                           cmap="tab10", alpha=0.75)
    left.set_xlabel("latent dimension 1")
    left.set_ylabel("latent dimension 2")
    left.set_title(f"encoder means, first 2 of {LATENT} dimensions",
                   fontsize=10)
    del scatter

    right.hist(info["distances"], bins=40, alpha=0.7, color=p.blue,
               density=True, label=f"encoder means "
                                   f"(mean {info['mean_distance']:.4f})")
    right.hist(info["prior"], bins=40, alpha=0.55, color=p.muted, density=True,
               label=f"the prior (mean {info['prior_mean']:.4f})")
    right.set_xlabel("distance from the origin")
    right.set_ylabel("density")
    right.set_title(f"{info['active']} of {LATENT} dimensions active",
                    fontsize=10)
    right.legend(fontsize=8, loc="upper right")


def samples(fig, axes, p: Palette) -> None:
    runs = _report()
    labels = [label for label in runs if label != "real, held out (the floor)"]
    grid = fig.subplots(1, len(labels))
    grid = np.atleast_1d(grid)
    for ax, label in zip(grid, labels):
        images = runs[label]["grid"]
        side = max(1, int(np.sqrt(len(images))))
        canvas = np.concatenate([
            np.concatenate([images[row * side + column].reshape(28, 28)
                            for column in range(side)], axis=1)
            for row in range(side)], axis=0)
        ax.imshow(canvas, cmap="gray")
        ax.set_title(f"{label}\nKL {runs[label]['divergence']:.3f}, "
                     f"nearest train {runs[label]['nearest_train']:.2f}",
                     fontsize=8)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.grid(False)


FIGURES = [
    figure("report", report, size=(9.8, 3.6), axes=False),
    figure("latent", latent, size=(9.4, 3.5), axes=False),
    figure("samples", samples, size=(9.0, 3.4), axes=False),
]


if __name__ == "__main__":
    judge = _judge()
    trained = _vae(EPOCHS)
    print("=== the deliverable ===")
    print("not 'a VAE' but 'a VAE and the evidence it works'. The evidence is")
    print("a floor, three metrics, a memorisation check and uncurated samples.")
    print(f"judge classifier: {judge['accuracy']:.4f} validation accuracy")
    print(f"VAE: latent {LATENT}, {trained['epochs']} epochs, "
          f"{trained['seconds']:.0f}s")

    print(f"\n=== the report, {SAMPLES:,} samples per source ===")
    runs = _report()
    print(f"{'source':28s} {'Frechet':>9} {'classes':>8} {'KL unif':>9} "
          f"{'confidence':>11} {'near held-out':>14} {'near TRAIN':>11}")
    for label, entry in runs.items():
        print(f"{label:28s} {entry['frechet']:9.3f} {entry['classes']:8d} "
              f"{entry['divergence']:9.4f} {entry['confidence']:11.4f} "
              f"{entry['nearest_held_out']:14.4f} "
              f"{entry['nearest_train']:11.4f}")
    floor = runs["real, held out (the floor)"]
    vae = runs["VAE (25 epochs)"]
    memoriser = runs["memorised 150 images"]
    print(f"\nthe floor is not zero: two disjoint samples of real data score")
    print(f"{floor['frechet']:.3f}, so the VAE's {vae['frechet']:.3f} is "
          f"{vae['frechet'] - floor['frechet']:.3f} above it")
    print(f"\nthe memoriser scores {memoriser['frechet']:.3f} on Frechet "
          f"distance and {memoriser['divergence']:.4f} on coverage. Both")
    print("respectable, and BOTH better than the VAE's. It generated nothing.")
    print(f"its distance to the nearest HELD-OUT image is "
          f"{memoriser['nearest_held_out']:.4f}, against the VAE's "
          f"{vae['nearest_held_out']:.4f} --")
    print("that check does not catch it either, because copied training images")
    print("are perfectly ordinary digits as far as the test split is concerned")
    print(f"only the distance to the nearest TRAINING image separates them: "
          f"{memoriser['nearest_train']:.4f}")
    print(f"against the VAE's {vae['nearest_train']:.4f} and real held-out "
          f"data's {floor['nearest_train']:.4f}")
    print("the split you compare against IS the experiment; get it wrong and")
    print("the check reports nothing while looking like it ran")

    info = _latent()
    print(f"\n=== does the latent space support sampling? ===")
    print(f"{info['active']} of {LATENT} dimensions have standard deviation "
          f"above 0.1")
    print("per-dimension sd: "
          + ", ".join(f"{value:.3f}" for value in info["per_dimension"]))
    print(f"mean distance from the origin: {info['mean_distance']:.4f}")
    print(f"the prior's own mean distance:  {info['prior_mean']:.4f}")
    print("if those two disagree, prior samples land where the decoder has")
    print("never been trained, and the sample grid will show it")

    print(f"\n=== the undertrained control ===")
    short = runs["VAE (2 epochs)"]
    print(f"{SHORT_EPOCHS} epochs: Frechet {short['frechet']:.3f}, "
          f"{short['classes']} classes, KL {short['divergence']:.4f}")
    print(f"{EPOCHS} epochs: Frechet {vae['frechet']:.3f}, "
          f"{vae['classes']} classes, KL {vae['divergence']:.4f}")
    print("a control that is the same model trained badly is the cheapest way")
    print("to show the metrics respond to quality rather than to noise")
