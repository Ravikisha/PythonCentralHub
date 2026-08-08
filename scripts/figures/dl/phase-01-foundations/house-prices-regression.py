"""Figures for *First Example: Predicting House Prices (Regression)*.

``feature-scales``
    The thirteen input features on one axis, before and after standardisation.
    The spread across three orders of magnitude is why scaling is not optional.

``kfold-spread``
    Four validation folds trained identically. The spread between them is large
    enough that a single split would be a coin toss.

``residuals``
    Predicted against actual price for the test set, plus the residual
    distribution — where a mean absolute error of about 2.6 actually lands.
"""

from __future__ import annotations

import functools
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "..", ".."))

from _dl import seed_everything, tf  # noqa: E402
from _style import Palette, figure  # noqa: E402

EPOCHS = 80
FOLDS = 4


@functools.lru_cache(maxsize=1)
def _data() -> dict:
    (x_train, y_train), (x_test, y_test) = \
        tf().keras.datasets.boston_housing.load_data()
    mean = x_train.mean(axis=0)
    std = x_train.std(axis=0)
    return {
        "x_train": x_train, "y_train": y_train,
        "x_test": x_test, "y_test": y_test,
        "x_train_scaled": (x_train - mean) / std,
        "x_test_scaled": (x_test - mean) / std,
    }


def _model(features: int):
    keras = tf().keras
    model = keras.Sequential([
        keras.layers.Input((features,)),
        keras.layers.Dense(64, activation="relu"),
        keras.layers.Dense(64, activation="relu"),
        keras.layers.Dense(1),
    ])
    model.compile("rmsprop", "mse", metrics=["mae"])
    return model


@functools.lru_cache(maxsize=1)
def _kfold() -> dict:
    data = _data()
    x, y = data["x_train_scaled"], data["y_train"]
    size = len(x) // FOLDS
    scores, curves = [], []
    for fold in range(FOLDS):
        val_x = x[fold * size:(fold + 1) * size]
        val_y = y[fold * size:(fold + 1) * size]
        part_x = np.concatenate([x[:fold * size], x[(fold + 1) * size:]])
        part_y = np.concatenate([y[:fold * size], y[(fold + 1) * size:]])
        seed_everything(fold)
        model = _model(x.shape[1])
        history = model.fit(part_x, part_y, epochs=EPOCHS, batch_size=16,
                            verbose=0, validation_data=(val_x, val_y))
        scores.append(float(model.evaluate(val_x, val_y, verbose=0)[1]))
        curves.append([float(v) for v in history.history["val_mae"]])
    return {"scores": scores, "curves": curves}


@functools.lru_cache(maxsize=1)
def _final() -> dict:
    data = _data()
    seed_everything(0)
    model = _model(data["x_train_scaled"].shape[1])
    model.fit(data["x_train_scaled"], data["y_train"], epochs=EPOCHS,
              batch_size=16, verbose=0)
    predictions = model.predict(data["x_test_scaled"], verbose=0).ravel()
    mse, mae = model.evaluate(data["x_test_scaled"], data["y_test"], verbose=0)
    return {"predictions": predictions, "mse": float(mse), "mae": float(mae)}


def feature_scales(fig, axes, p: Palette) -> None:
    data = _data()
    left, right = fig.subplots(1, 2)
    positions = np.arange(data["x_train"].shape[1])

    # How wide is each feature's range, in its own units? Plotted on a log
    # axis because the answer spans three orders of magnitude.
    widths = data["x_train"].max(axis=0) - data["x_train"].min(axis=0)
    order = np.argsort(widths)
    left.barh(positions, widths[order], 0.65, color=p.blue)
    for y, index in zip(positions, order):
        left.annotate(f"{widths[index]:,.2f}", (widths[index], y),
                      textcoords="offset points", xytext=(5, -3), fontsize=7,
                      color=p.fg)
    left.set_xscale("log")
    left.set_xlim(0.2, widths.max() * 6)
    left.set_yticks(positions)
    left.set_yticklabels([f"feature {i}" for i in order], fontsize=7.5)
    left.set_xlabel("max - min, in the feature's own units (log scale)")
    left.set_title(f"widest range is {widths.max() / widths.min():,.0f}x the "
                   f"narrowest", fontsize=10)

    scaled = data["x_train_scaled"]
    right.vlines(positions, scaled.min(axis=0), scaled.max(axis=0),
                 color=p.blue, lw=6, alpha=0.75)
    right.plot(positions, scaled.mean(axis=0), "o", ms=4, color=p.amber,
               label="mean (now 0)")
    right.axhline(0, color=p.grid, lw=1.0)
    right.set_xticks(positions)
    right.set_xticklabels([str(i) for i in positions], fontsize=7.5)
    right.set_xlabel("feature index")
    right.set_ylabel("standard deviations")
    worst = int(np.argmax(scaled.max(axis=0)))
    right.set_title(f"after (x - mean) / std — feature {worst} still reaches "
                    f"{scaled.max():.1f} sd", fontsize=10)
    right.legend(fontsize=7.5)


def kfold_spread(fig, axes, p: Palette) -> None:
    result = _kfold()
    left, right = fig.subplots(1, 2)
    epochs = range(1, EPOCHS + 1)

    for fold, (curve, color) in enumerate(zip(result["curves"], p.cycle)):
        left.plot(epochs, curve, lw=1.4, color=color, label=f"fold {fold + 1}")
    left.set_xlabel("epoch")
    left.set_ylabel("validation MAE")
    left.set_ylim(1.5, 8.0)
    left.set_title("same configuration, four different held-out folds",
                   fontsize=10)
    left.legend(fontsize=7.5)

    scores = result["scores"]
    positions = np.arange(FOLDS)
    right.bar(positions, scores, 0.55, color=p.blue)
    for x, value in zip(positions, scores):
        right.annotate(f"{value:.4f}", (x, value), textcoords="offset points",
                       xytext=(0, 4), ha="center", fontsize=8, color=p.fg)
    mean = float(np.mean(scores))
    right.axhline(mean, color=p.amber, lw=1.8, ls="--",
                  label=f"mean {mean:.4f}, spread "
                        f"{max(scores) - min(scores):.4f}")
    right.set_xticks(positions)
    right.set_xticklabels([f"fold {i + 1}" for i in positions])
    right.set_ylabel("final validation MAE")
    right.set_ylim(0, max(scores) * 1.35)
    right.set_title("the number you would have reported", fontsize=10)
    right.legend(fontsize=7.5)


def residuals(fig, axes, p: Palette) -> None:
    data = _data()
    final = _final()
    left, right = fig.subplots(1, 2)
    actual = data["y_test"]
    predicted = final["predictions"]

    limits = (0, 55)
    left.plot(limits, limits, color=p.grid, lw=1.2, ls="--", label="perfect")
    left.scatter(actual, predicted, s=22, color=p.blue, alpha=0.8)
    left.set_xlim(*limits)
    left.set_ylim(*limits)
    left.set_xlabel("actual price ($1000s)")
    left.set_ylabel("predicted price ($1000s)")
    left.set_title(f"test MAE {final['mae']:.4f}", fontsize=10)
    left.legend(fontsize=7.5)

    errors = predicted - actual
    worst = int(np.argmax(np.abs(errors)))
    left.annotate(f"actual {actual[worst]:.1f}, predicted "
                  f"{predicted[worst]:.1f}",
                  (actual[worst], predicted[worst]),
                  textcoords="offset points", xytext=(26, -34), fontsize=7.5,
                  color=p.red,
                  arrowprops=dict(arrowstyle="->", color=p.red, lw=1.0))
    capped = actual >= 49.9
    left.annotate(f"{int(capped.sum())} houses sit at the 50.0 cap",
                  (49.5, 43), textcoords="offset points", xytext=(-4, -46),
                  ha="right", fontsize=7.5, color=p.amber,
                  arrowprops=dict(arrowstyle="->", color=p.amber, lw=1.0))

    right.hist(np.clip(errors, -11.5, 11.5), bins=24, range=(-12, 12),
               color=p.blue, alpha=0.85)
    right.axvline(0, color=p.grid, lw=1.2)
    right.axvline(float(np.median(errors)), color=p.amber, lw=1.8,
                  label=f"median error {np.median(errors):+.2f}")
    right.set_xlim(-12, 12)
    right.set_xlabel("predicted - actual ($1000s)")
    right.set_ylabel("houses")
    right.set_title(f"{int((errors > 0).sum())} of {len(errors)} houses "
                    f"over-predicted", fontsize=10)
    right.annotate(f"1 house at {errors[worst]:+.2f}\n(clipped)",
                   (11.5, 1), textcoords="offset points", xytext=(-16, 34),
                   ha="right", fontsize=7, color=p.red,
                   arrowprops=dict(arrowstyle="->", color=p.red, lw=1.0))
    right.legend(fontsize=7.5, loc="upper left")


FIGURES = [
    figure("feature-scales", feature_scales, size=(9.2, 3.4), axes=False),
    figure("kfold-spread", kfold_spread, size=(9.2, 3.4), axes=False),
    figure("residuals", residuals, size=(9.2, 3.4), axes=False),
]


if __name__ == "__main__":
    data = _data()
    print(f"train {data['x_train'].shape}  test {data['x_test'].shape}")
    widths = data["x_train"].max(axis=0) - data["x_train"].min(axis=0)
    print(f"feature range widths: min {widths.min():.4f}  max {widths.max():.4f}"
          f"  ratio {widths.max() / widths.min():,.0f}x")
    result = _kfold()
    print(f"\nper-fold MAE {[round(s, 4) for s in result['scores']]}")
    print(f"mean {np.mean(result['scores']):.4f}  "
          f"spread {max(result['scores']) - min(result['scores']):.4f}")
    best_epochs = [int(np.argmin(c)) + 1 for c in result["curves"]]
    print(f"epoch of best val MAE per fold: {best_epochs}")
    final = _final()
    errors = final["predictions"] - data["y_test"]
    print(f"\ntest MSE {final['mse']:.4f}  MAE {final['mae']:.4f}")
    print(f"median residual {np.median(errors):+.4f}  "
          f"worst {errors[np.argmax(np.abs(errors))]:+.4f}")
    over = int((errors > 0).sum())
    print(f"over-predicted {over} of {len(errors)} houses")
    within = float((np.abs(errors) <= 2.0).mean())
    print(f"within $2,000: {within:.4f}")
