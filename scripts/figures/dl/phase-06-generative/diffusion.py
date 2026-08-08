"""Figures for *Diffusion Models (Introduction)*.

A diffusion model is trained to remove a known amount of noise. That makes it
the easiest generative family to verify: the forward process has a closed form,
so every claim about it can be checked with arithmetic rather than trained.

This module tests two hypotheses about why its first samples were blobs, and
keeps both results because only one of them was right.

The first schedule written here ran 1e-4 to 0.02 over 200 steps, leaving the
image contributing 0.3636 of the signal at the *last* timestep -- so sampling
starts from pure noise the model never trained on. That is a real, published
failure (the terminal signal-to-noise problem), so it looked like the cause.
Fixing it (beta to 0.06, final signal weight 0.0466) did **not** fix the
samples: still 2 of 10 classes and mean ink 0.4731 against 0.1206 for real
digits. The actual bottleneck was the architecture -- a dense network has no
spatial structure to denoise with. Both findings are on the page.

``forward-process``
    Both schedules in closed form, with the signal-to-noise ratio -- the point
    being that the last timestep must actually destroy the image.

``what-fixed-it``
    Three runs -- the original schedule, the fixed schedule, and the fixed
    schedule with a convolutional denoiser -- scored on the same metrics, with
    their sample grids.

``sampling-steps``
    Sample quality against the number of reverse steps, scored by an
    independent classifier, plus the wall-clock each setting costs.

``denoising-targets``
    What the network predicts at three noise levels against what it should
    predict -- the noise, not the image.
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
EPOCHS = 40
STEPS = 200
WIDTH = 256
TIME_FEATURES = 16
SHOW_TIMESTEPS = (0, 20, 60, 120, 199)
SAMPLE_STEPS = (2, 5, 20, 50, 200)
# Sampling dominates the wall-clock: every reverse step is a full forward pass
# over the whole batch, so this count multiplies straight into the runtime.
SCORED = 250
GRID = 8

# beta_max per schedule; the first value is what this module originally used.
SCHEDULES = {"as first written": 0.02, "terminal-SNR fixed": 0.06}
FIXED = "terminal-SNR fixed"

# The three runs the page compares: (label, schedule, architecture).
RUNS = (
    ("dense, original schedule", "as first written", "dense"),
    ("dense, terminal-SNR fixed", FIXED, "dense"),
    ("convolutional, terminal-SNR fixed", FIXED, "conv"),
)
BEST = RUNS[-1]


@functools.lru_cache(maxsize=1)
def _data() -> dict:
    return dataset("mnist", limit=LIMIT, flat=True)


def _timesteps() -> int:
    """STEPS, but never below the number of timesteps the figures index."""
    return max(int(STEPS), 8)


@functools.lru_cache(maxsize=8)
def _schedule(kind: str = FIXED) -> dict:
    """A linear beta schedule, and everything derived from it in closed form."""
    steps = _timesteps()
    beta = np.linspace(1e-4, SCHEDULES[kind], steps)
    alpha_bar = np.cumprod(1.0 - beta)
    return {"beta": beta, "alpha_bar": alpha_bar,
            "sqrt_alpha_bar": np.sqrt(alpha_bar),
            "sqrt_one_minus": np.sqrt(1.0 - alpha_bar),
            "snr": alpha_bar / (1.0 - alpha_bar)}


def _shown_timesteps() -> tuple:
    steps = _timesteps()
    return tuple(sorted({min(int(t), steps - 1) for t in SHOW_TIMESTEPS}))


def _sample_steps() -> tuple:
    steps = _timesteps()
    return tuple(sorted({max(1, min(int(s), steps)) for s in SAMPLE_STEPS}))


def _embed(timesteps) -> np.ndarray:
    """Sinusoidal timestep features: the network must know the noise level.

    Handing the raw integer to a dense layer works badly -- one input among 784
    pixels barely moves the first activation.
    """
    position = np.asarray(timesteps, "float32")[:, None] / _timesteps()
    frequency = 2.0 ** np.arange(TIME_FEATURES // 2, dtype="float32")
    angles = position * frequency[None, :] * np.pi
    return np.concatenate([np.sin(angles), np.cos(angles)],
                          axis=1).astype("float32")


def _noise(x, timesteps, rng, kind=FIXED):
    """The forward process in one step: x_t = sqrt(a_bar) x + sqrt(1-a_bar) e."""
    schedule = _schedule(kind)
    noise = rng.normal(0, 1, x.shape).astype("float32")
    a = schedule["sqrt_alpha_bar"][timesteps][:, None]
    b = schedule["sqrt_one_minus"][timesteps][:, None]
    return (a * x + b * noise).astype("float32"), noise


@functools.lru_cache(maxsize=1)
def _judge() -> dict:
    """An independent classifier, used only to score what the model produces."""
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


def _dense_denoiser(keras):
    image_input = keras.layers.Input((784,))
    time_input = keras.layers.Input((TIME_FEATURES,))
    x = keras.layers.Concatenate()([image_input, time_input])
    for _ in range(3):
        x = keras.layers.Dense(WIDTH, activation="relu")(x)
    return keras.Model([image_input, time_input],
                       keras.layers.Dense(784)(x))


def _conv_denoiser(keras):
    """A small U-Net: the same job, but with somewhere for locality to live.

    Noise removal is a local operation. A dense layer has to learn every pixel's
    neighbourhood from scratch out of a flat vector of 784 inputs; a convolution
    is handed it.
    """
    image_input = keras.layers.Input((784,))
    time_input = keras.layers.Input((TIME_FEATURES,))
    x = keras.layers.Reshape((28, 28, 1))(image_input)

    def add_time(tensor, channels):
        bias = keras.layers.Dense(channels)(time_input)
        return keras.layers.Add()([tensor,
                                   keras.layers.Reshape((1, 1, channels))(bias)])

    first = keras.layers.Conv2D(32, 3, padding="same", activation="relu")(x)
    first = add_time(first, 32)
    down = keras.layers.MaxPooling2D()(first)                      # 14x14
    second = keras.layers.Conv2D(64, 3, padding="same",
                                 activation="relu")(down)
    second = add_time(second, 64)
    bottom = keras.layers.MaxPooling2D()(second)                   # 7x7
    bottom = keras.layers.Conv2D(64, 3, padding="same",
                                 activation="relu")(bottom)
    bottom = add_time(bottom, 64)

    up = keras.layers.UpSampling2D()(bottom)                       # 14x14
    up = keras.layers.Concatenate()([up, second])
    up = keras.layers.Conv2D(64, 3, padding="same", activation="relu")(up)
    up = keras.layers.UpSampling2D()(up)                           # 28x28
    up = keras.layers.Concatenate()([up, first])
    up = keras.layers.Conv2D(32, 3, padding="same", activation="relu")(up)
    outputs = keras.layers.Conv2D(1, 3, padding="same")(up)
    return keras.Model([image_input, time_input],
                       keras.layers.Reshape((784,))(outputs))


@functools.lru_cache(maxsize=8)
def _model(kind: str = FIXED, architecture: str = "conv") -> dict:
    """Predict the noise that was added, conditioned on the timestep."""
    keras = tf().keras
    data = _data()
    seed_everything(0)
    model = (_conv_denoiser(keras) if architecture == "conv"
             else _dense_denoiser(keras))
    model.compile(keras.optimizers.Adam(1e-3), "mse")

    rng = np.random.default_rng(0)
    clean = data["x_train"]
    started = time.perf_counter()
    losses = []
    for _ in range(EPOCHS):
        timesteps = rng.integers(0, _timesteps(), len(clean))
        noisy, noise = _noise(clean, timesteps, rng, kind)
        history = model.fit([noisy, _embed(timesteps)], noise, epochs=1,
                            batch_size=128, verbose=0)
        losses.append(float(history.history["loss"][0]))
    return {"model": model, "losses": losses,
            "seconds": time.perf_counter() - started}


def _sample(count: int, steps: int, kind: str = FIXED,
            architecture: str = "conv", seed: int = 0):
    """Reverse the process with `steps` evenly spaced timesteps."""
    schedule = _schedule(kind)
    model = _model(kind, architecture)["model"]
    rng = np.random.default_rng(seed)
    x = rng.normal(0, 1, (count, 784)).astype("float32")
    timeline = np.unique(
        np.linspace(_timesteps() - 1, 0, steps).astype(int))[::-1]
    for index, t in enumerate(timeline):
        predicted_noise = model.predict([x, _embed(np.full(count, t))],
                                        verbose=0)
        alpha_bar = schedule["alpha_bar"][t]
        x0 = np.clip((x - np.sqrt(1 - alpha_bar) * predicted_noise)
                     / np.sqrt(alpha_bar), 0.0, 1.0)
        if index + 1 < len(timeline):
            next_alpha_bar = schedule["alpha_bar"][timeline[index + 1]]
            noise = rng.normal(0, 1, x.shape).astype("float32")
            x = (np.sqrt(next_alpha_bar) * x0
                 + np.sqrt(1 - next_alpha_bar) * noise).astype("float32")
        else:
            x = x0.astype("float32")
    return x


def _score(samples) -> dict:
    judge = _judge()["model"]
    probabilities = judge.predict(samples, verbose=0)
    counts = np.bincount(probabilities.argmax(axis=1), minlength=10)
    share = counts / counts.sum()
    uniform = np.full(10, 0.1)
    return {"confidence": float(probabilities.max(axis=1).mean()),
            "classes": int((counts > len(samples) * 0.01).sum()),
            "divergence": float(np.sum(uniform * np.log(
                uniform / np.clip(share, 1e-9, None)))),
            "ink": float(samples.mean())}


@functools.lru_cache(maxsize=1)
def _schedule_runs() -> dict:
    """The three runs the page compares, sampled with the full step count."""
    out = {}
    for label, kind, architecture in RUNS:
        schedule = _schedule(kind)
        info = _model(kind, architecture)
        samples = _sample(SCORED, _timesteps(), kind, architecture, seed=1)
        out[label] = {**_score(samples), "samples": samples[:GRID * GRID],
                      "terminal": float(schedule["sqrt_alpha_bar"][-1]),
                      "terminal_snr": float(schedule["snr"][-1]),
                      "parameters": int(info["model"].count_params()),
                      "seconds": info["seconds"],
                      "loss": info["losses"][-1]}
    return out


@functools.lru_cache(maxsize=1)
def _sampling_runs() -> dict:
    data = _data()
    _, kind, architecture = BEST
    _model(kind, architecture)            # train before timing anything
    _sample(8, 2, kind, architecture)     # warm the predict graph
    out = {}
    for steps in _sample_steps():
        started = time.perf_counter()
        samples = _sample(SCORED, steps, kind, architecture, seed=1)
        out[steps] = {"seconds": time.perf_counter() - started,
                      **_score(samples)}
    out["real"] = _score(data["x_test"][:SCORED])
    return out


def forward_process(fig, axes, p: Palette) -> None:
    data = _data()
    top, bottom = fig.subplots(2, 1, height_ratios=(1.0, 1.15))
    rng = np.random.default_rng(0)
    shown = _shown_timesteps()
    strips = []
    for timestep in shown:
        noisy, _ = _noise(data["x_test"][:6], np.full(6, timestep), rng, FIXED)
        strips.append(np.concatenate([image.reshape(28, 28)
                                      for image in noisy], axis=1))
    top.imshow(np.concatenate(strips, axis=0), cmap="gray", vmin=-1, vmax=2)
    top.set_title(f"{FIXED}: t = " + ", ".join(str(t) for t in shown)
                  + "  (top row to bottom row)", fontsize=10)
    top.set_xticks([])
    top.set_yticks([])
    top.grid(False)

    steps = np.arange(_timesteps())
    twin = bottom.twinx()
    for kind, color in zip(SCHEDULES, (p.red, p.green)):
        schedule = _schedule(kind)
        bottom.plot(steps, schedule["alpha_bar"], lw=2.0, color=color,
                    label=f"{kind}: alpha-bar ends "
                          f"{schedule['alpha_bar'][-1]:.4f}")
        twin.plot(steps, schedule["snr"], lw=1.4, ls="--", color=color)
    twin.set_yscale("log")
    twin.set_ylabel("SNR (dashed, log)")
    bottom.set_xlabel("timestep")
    bottom.set_ylabel("alpha-bar (signal weight squared)")
    bottom.set_title("sampling starts at the last step, so alpha-bar must end "
                     "near zero", fontsize=10)
    bottom.legend(fontsize=8, loc="upper right")


def what_fixed_it(fig, axes, p: Palette) -> None:
    runs = _schedule_runs()
    real = _sampling_runs()["real"]
    labels = list(runs)
    top = fig.subplots(2, 1, height_ratios=(1.0, 0.9))
    strip, bars = top
    grids = []
    for label in labels:
        samples = runs[label]["samples"]
        side = max(1, int(np.sqrt(len(samples))))
        grids.append(np.concatenate([
            np.concatenate([samples[row * side + col].reshape(28, 28)
                            for col in range(side)], axis=1)
            for row in range(side)], axis=0))
    strip.imshow(np.concatenate(grids, axis=1), cmap="gray")
    strip.set_title("  |  ".join(labels), fontsize=8.5)
    strip.set_xticks([])
    strip.set_yticks([])
    strip.grid(False)

    metrics = (("ink", "mean pixel value"), ("classes", "classes produced"),
               ("divergence", "KL from uniform"))
    positions = np.arange(len(metrics))
    width = 0.22
    scales = [max([abs(runs[label][key]) for label in labels]
                  + [abs(real[key])]) or 1.0 for key, _ in metrics]
    series = [(label, [runs[label][key] for key, _ in metrics], color)
              for label, color in zip(labels, (p.red, p.amber, p.green))]
    series.append(("real digits", [real[key] for key, _ in metrics], p.muted))
    for index, (label, values, color) in enumerate(series):
        offset = (index - 1.5) * width
        scaled = [value / scale for value, scale in zip(values, scales)]
        bars.bar(positions + offset, scaled, width * 0.9, color=color,
                 label=label)
        for x, y, value in zip(positions + offset, scaled, values):
            bars.annotate(f"{value:.3f}", (x, y), xytext=(0, 3),
                          textcoords="offset points", ha="center",
                          fontsize=6.5, color=p.fg)
    bars.set_xticks(positions)
    bars.set_xticklabels([name for _, name in metrics], fontsize=8.5)
    bars.set_ylim(0, 1.35)
    bars.set_ylabel("scaled to the largest value in each group")
    bars.set_title(f"{SCORED} samples each — the schedule fix moved nothing; "
                   f"the architecture did", fontsize=9)
    bars.legend(fontsize=7, loc="upper center", ncol=2)


def sampling_steps(fig, axes, p: Palette) -> None:
    runs = _sampling_runs()
    left, right = fig.subplots(1, 2)
    steps = list(_sample_steps())
    confidence = [runs[s]["confidence"] for s in steps]
    seconds = [runs[s]["seconds"] for s in steps]
    left.plot(steps, confidence, "o-", ms=6, lw=2.0, color=p.green,
              label="judge confidence in the sample")
    left.axhline(runs["real"]["confidence"], color=p.muted, lw=1.2, ls="--",
                 label=f"real digits ({runs['real']['confidence']:.4f})")
    for step, value in zip(steps, confidence):
        left.annotate(f"{value:.3f}", (step, value),
                      textcoords="offset points", xytext=(0, 8), ha="center",
                      fontsize=7.5, color=p.green)
    for ax in (left, right):
        ax.set_xscale("log")
        ax.minorticks_off()
        ax.set_xticks(steps)
        ax.set_xticklabels([str(s) for s in steps])
        ax.set_xlabel("reverse steps")
    left.set_ylabel("mean classifier confidence")
    left.set_title("more steps, better samples -- up to a point", fontsize=10)
    left.legend(fontsize=8, loc="lower right")

    right.plot(steps, seconds, "o-", ms=6, lw=2.0, color=p.red,
               label=f"seconds for {SCORED} samples")
    for step, value in zip(steps, seconds):
        right.annotate(f"{value:.1f}s", (step, value),
                       textcoords="offset points", xytext=(0, 8), ha="center",
                       fontsize=7.5, color=p.red)
    right.set_yscale("log")
    right.set_ylabel("seconds (log)")
    right.set_title("every step is a full forward pass", fontsize=10)
    right.legend(fontsize=8, loc="upper left")


def denoising_targets(fig, axes, p: Palette) -> None:
    data = _data()
    _, best_kind, best_arch = BEST
    model = _model(best_kind, best_arch)["model"]
    schedule = _schedule(best_kind)
    rng = np.random.default_rng(3)
    steps = _timesteps()
    levels = sorted({min(int(steps * f), steps - 1) for f in (0.1, 0.4, 0.9)})
    grid = fig.subplots(len(levels), 4)
    rows = grid if len(levels) > 1 else [grid]
    for row, timestep in zip(rows, levels):
        noisy, noise = _noise(data["x_test"][:1], np.full(1, timestep), rng,
                              FIXED)
        predicted = model.predict([noisy, _embed(np.full(1, timestep))],
                                  verbose=0)
        alpha_bar = schedule["alpha_bar"][timestep]
        estimate = np.clip((noisy - np.sqrt(1 - alpha_bar) * predicted)
                           / np.sqrt(alpha_bar), 0, 1)
        error = float(np.mean((predicted[0] - noise[0]) ** 2))
        panels = ((noisy[0], f"x_t (t={timestep})"),
                  (noise[0], "the true noise"),
                  (predicted[0], "predicted noise"),
                  (estimate[0], "implied clean image"))
        for column, (ax, (image, title)) in enumerate(zip(row, panels)):
            ax.imshow(image.reshape(28, 28), cmap="gray")
            if timestep == levels[0]:
                ax.set_title(title, fontsize=8.5)
            if column == 0:
                ax.set_ylabel(f"MSE {error:.3f}", fontsize=7.5)
            ax.set_xticks([])
            ax.set_yticks([])
            ax.grid(False)


FIGURES = [
    figure("forward-process", forward_process, size=(9.0, 5.4), axes=False),
    figure("what-fixed-it", what_fixed_it, size=(9.6, 5.2), axes=False),
    figure("sampling-steps", sampling_steps, size=(9.4, 3.5), axes=False),
    figure("denoising-targets", denoising_targets, size=(7.2, 5.4), axes=False),
]


if __name__ == "__main__":
    print(f"=== the forward process, {_timesteps()} steps, linear beta ===")
    for kind, beta_max in SCHEDULES.items():
        schedule = _schedule(kind)
        print(f"\n{kind} (beta from 1e-4 to {beta_max})")
        print(f"{'t':>5} {'beta':>9} {'alpha-bar':>11} {'signal weight':>14} "
              f"{'noise weight':>13} {'SNR':>10}")
        for t in _shown_timesteps():
            print(f"{t:5d} {schedule['beta'][t]:9.5f} "
                  f"{schedule['alpha_bar'][t]:11.5f} "
                  f"{schedule['sqrt_alpha_bar'][t]:14.4f} "
                  f"{schedule['sqrt_one_minus'][t]:13.4f} "
                  f"{schedule['snr'][t]:10.4f}")
        print(f"at the last step the image still contributes "
              f"{schedule['sqrt_alpha_bar'][-1]:.4f} of the signal "
              f"(SNR {schedule['snr'][-1]:.4f})")

    judge = _judge()
    print(f"\n=== three runs, {SCORED} samples each, judge accuracy "
          f"{judge['accuracy']:.4f} ===")
    runs = _schedule_runs()
    real = _sampling_runs()["real"]
    print(f"{'run':36s} {'params':>9} {'train s':>8} {'loss':>7} "
          f"{'last sig wt':>12} {'mean ink':>9} {'classes':>8} {'KL unif':>9} "
          f"{'confidence':>11}")
    for label, entry in runs.items():
        print(f"{label:36s} {entry['parameters']:9,} {entry['seconds']:8.0f} "
              f"{entry['loss']:7.4f} {entry['terminal']:12.4f} "
              f"{entry['ink']:9.4f} {entry['classes']:8d} "
              f"{entry['divergence']:9.4f} {entry['confidence']:11.4f}")
    print(f"{'real digits':36s} {'-':>9} {'-':>8} {'-':>7} {'-':>12} "
          f"{real['ink']:9.4f} {real['classes']:8d} {real['divergence']:9.4f} "
          f"{real['confidence']:11.4f}")
    print("\nthe terminal-SNR fix was the obvious suspect and it was WRONG:")
    print("row 2 barely moves from row 1. Mean pixel value is the tell -- the")
    print("dense runs put four times as much ink on the canvas as real digits")
    print("do, which is a model that cannot localise, not a bad schedule")

    print(f"\n=== sampling cost against reverse steps ({BEST[0]}) ===")
    sampling = _sampling_runs()
    print(f"{'steps':>6} {'seconds':>9} {'confidence':>11} {'classes':>8} "
          f"{'KL vs uniform':>14} {'mean ink':>9}")
    for count in _sample_steps():
        run = sampling[count]
        print(f"{count:6d} {run['seconds']:9.1f} {run['confidence']:11.4f} "
              f"{run['classes']:8d} {run['divergence']:14.4f} "
              f"{run['ink']:9.4f}")
    print("the model is trained and warmed up before this loop is timed --")
    print("otherwise the first row absorbs training time and reads as though")
    print("two steps were the slowest setting (it did, at 56.3s against 1.0s)")
    print("every reverse step is a full forward pass, so cost is linear in")
    print("steps, which is the whole reason DDIM and distillation exist")
