"""Figures for *Model Compression: Pruning, Quantisation and Distillation*.

Three ways to make a model smaller, measured against the same baseline on the
same test set. Quantisation has its own page; here it is included only so the
three can be compared on one axis.

``pruning``
    Magnitude pruning at several sparsity levels, with and without fine-tuning
    afterwards -- the fine-tuning step is what the technique actually depends
    on, and skipping it is the usual reason pruning "does not work".

``distillation``
    A small student trained alone against the same student trained from the
    teacher's soft predictions, at matched size and budget.

``frontier``
    Every compressed model on one accuracy-against-size plot, so the three
    families can be compared rather than described.
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
EPOCHS = 8
FINETUNE_EPOCHS = 3
STUDENT_EPOCHS = 12
SPARSITIES = (0.0, 0.5, 0.7, 0.9, 0.95, 0.99)
TEMPERATURE = 4.0
ALPHA = 0.7                    # weight on the teacher's soft targets


@functools.lru_cache(maxsize=1)
def _data() -> dict:
    return dataset("mnist", limit=LIMIT, flat=False)


def _teacher_network(keras):
    return keras.Sequential([
        keras.layers.Input((28, 28, 1)),
        keras.layers.Conv2D(32, 3, activation="relu"),
        keras.layers.MaxPooling2D(),
        keras.layers.Conv2D(64, 3, activation="relu"),
        keras.layers.MaxPooling2D(),
        keras.layers.Flatten(),
        keras.layers.Dense(256, activation="relu"),
        keras.layers.Dense(10),
    ], name="teacher")


def _student_network(keras):
    """Roughly a tenth of the teacher's parameters."""
    return keras.Sequential([
        keras.layers.Input((28, 28, 1)),
        keras.layers.Conv2D(8, 3, activation="relu"),
        keras.layers.MaxPooling2D(),
        keras.layers.Flatten(),
        keras.layers.Dense(32, activation="relu"),
        keras.layers.Dense(10),
    ], name="student")


def _compile(keras, model, rate: float = 1e-3):
    model.compile(keras.optimizers.Adam(rate),
                  keras.losses.SparseCategoricalCrossentropy(from_logits=True),
                  metrics=["accuracy"])
    return model


@functools.lru_cache(maxsize=1)
def _teacher() -> dict:
    keras = tf().keras
    data = _data()
    seed_everything(0)
    model = _compile(keras, _teacher_network(keras))
    started = time.perf_counter()
    history = model.fit(data["x_train"], data["y_train"], epochs=EPOCHS,
                        batch_size=128, verbose=0,
                        validation_data=(data["x_test"], data["y_test"]))
    return {"model": model,
            "accuracy": float(history.history["val_accuracy"][-1]),
            "parameters": int(model.count_params()),
            "seconds": time.perf_counter() - started}


def _weight_bytes(model, sparsity: float = 0.0) -> float:
    """Dense float32 bytes, or a simple sparse estimate when pruned.

    The sparse figure assumes value plus 16-bit index per surviving weight,
    which is what a CSR-style format costs. It is an estimate, and labelled as
    one on the page -- Keras itself always writes the dense array.
    """
    total = sum(int(np.prod(w.shape)) for w in model.weights)
    if sparsity <= 0:
        return total * 4.0
    surviving = total * (1.0 - sparsity)
    return surviving * 6.0


def _prune(model, sparsity: float):
    """Zero the smallest weights, layer by layer, by magnitude."""
    keras = tf().keras
    clone = keras.models.clone_model(model)
    clone.set_weights([w.copy() for w in model.get_weights()])
    if sparsity <= 0:
        return clone
    weights = clone.get_weights()
    pruned = []
    for array in weights:
        if array.ndim < 2:                 # leave biases alone
            pruned.append(array)
            continue
        threshold = np.quantile(np.abs(array), sparsity)
        pruned.append(np.where(np.abs(array) < threshold, 0.0, array))
    clone.set_weights(pruned)
    return clone


def _masks(model) -> list:
    return [(np.abs(w) > 0).astype("float32") if w.ndim >= 2 else None
            for w in model.get_weights()]


@functools.lru_cache(maxsize=1)
def _pruning_runs() -> dict:
    """Prune, score, then fine-tune while keeping the pruned weights at zero."""
    keras = tf().keras
    data = _data()
    teacher = _teacher()["model"]
    out = {}
    for sparsity in SPARSITIES:
        clone = _prune(teacher, sparsity)
        _compile(keras, clone)
        immediate = clone.evaluate(data["x_test"], data["y_test"],
                                   verbose=0)[1]
        masks = _masks(clone)
        if sparsity > 0:
            for _ in range(FINETUNE_EPOCHS):
                clone.fit(data["x_train"], data["y_train"], epochs=1,
                          batch_size=128, verbose=0)
                # Re-apply the mask: gradient descent would otherwise refill
                # the pruned weights and quietly undo the sparsity.
                restored = [w * m if m is not None else w
                            for w, m in zip(clone.get_weights(), masks)]
                clone.set_weights(restored)
        recovered = clone.evaluate(data["x_test"], data["y_test"], verbose=0)[1]
        actual = float(np.mean([(w == 0).mean() for w in clone.get_weights()
                                if w.ndim >= 2]))
        out[sparsity] = {"immediate": float(immediate),
                         "recovered": float(recovered),
                         "actual_sparsity": actual,
                         "bytes": _weight_bytes(clone, sparsity)}
    return out


@functools.lru_cache(maxsize=1)
def _students() -> dict:
    """The same small network, trained alone and trained from the teacher."""
    keras = tf().keras
    tensorflow = tf()
    data = _data()
    teacher = _teacher()["model"]
    logits = teacher.predict(data["x_train"], verbose=0)
    soft = tensorflow.nn.softmax(logits / TEMPERATURE).numpy()

    out = {}
    seed_everything(1)
    plain = _compile(keras, _student_network(keras))
    started = time.perf_counter()
    plain_history = plain.fit(data["x_train"], data["y_train"],
                              epochs=STUDENT_EPOCHS, batch_size=128, verbose=0,
                              validation_data=(data["x_test"], data["y_test"]))
    out["student, alone"] = {
        "model": plain,
        "accuracy": float(plain_history.history["val_accuracy"][-1]),
        "curve": [float(v) for v in plain_history.history["val_accuracy"]],
        "seconds": time.perf_counter() - started,
    }

    seed_everything(1)
    distilled = _student_network(keras)
    optimizer = keras.optimizers.Adam(1e-3)

    @tensorflow.function(reduce_retracing=True)
    def step(images, hard, soft_targets):
        with tensorflow.GradientTape() as tape:
            student_logits = distilled(images, training=True)
            hard_loss = tensorflow.reduce_mean(
                keras.losses.sparse_categorical_crossentropy(
                    hard, student_logits, from_logits=True))
            # The temperature-scaled cross-entropy against the teacher, with
            # the T^2 factor that keeps the gradient magnitude comparable.
            soft_loss = tensorflow.reduce_mean(
                keras.losses.categorical_crossentropy(
                    soft_targets,
                    student_logits / TEMPERATURE,
                    from_logits=True)) * (TEMPERATURE ** 2)
            loss = (1 - ALPHA) * hard_loss + ALPHA * soft_loss
        optimizer.apply_gradients(
            zip(tape.gradient(loss, distilled.trainable_variables),
                distilled.trainable_variables))
        return loss

    rng = np.random.default_rng(0)
    images = data["x_train"]
    labels = data["y_train"]
    curve = []
    started = time.perf_counter()
    scorer = _compile(keras, distilled)
    for _ in range(STUDENT_EPOCHS):
        order = rng.permutation(len(images))
        for begin in range(0, len(order) - 127, 128):
            index = order[begin:begin + 128]
            step(images[index], labels[index], soft[index])
        curve.append(float(scorer.evaluate(data["x_test"], data["y_test"],
                                           verbose=0)[1]))
    out["student, distilled"] = {
        "model": distilled,
        "accuracy": curve[-1],
        "curve": curve,
        "seconds": time.perf_counter() - started,
    }
    out["_soft"] = soft
    out["_logits"] = logits
    return out


@functools.lru_cache(maxsize=1)
def _frontier() -> dict:
    teacher = _teacher()
    students = _students()
    pruned = _pruning_runs()
    out = {
        "teacher": {"accuracy": teacher["accuracy"],
                    "bytes": _weight_bytes(teacher["model"]),
                    "family": "baseline"},
    }
    for sparsity in SPARSITIES:
        if sparsity == 0:
            continue
        entry = pruned[sparsity]
        out[f"pruned {sparsity:.0%}"] = {"accuracy": entry["recovered"],
                                         "bytes": entry["bytes"],
                                         "family": "pruning"}
    for label in ("student, alone", "student, distilled"):
        model = students[label]["model"]
        out[label] = {"accuracy": students[label]["accuracy"],
                      "bytes": _weight_bytes(model),
                      "family": "distillation"}
    return out


def pruning(fig, axes, p: Palette) -> None:
    runs = _pruning_runs()
    teacher = _teacher()
    left, right = fig.subplots(1, 2)
    sparsities = list(runs)
    immediate = [runs[s]["immediate"] for s in sparsities]
    recovered = [runs[s]["recovered"] for s in sparsities]
    left.plot(sparsities, immediate, "o-", ms=6, lw=2.0, color=p.red,
              label="pruned, no fine-tuning")
    left.plot(sparsities, recovered, "s-", ms=6, lw=2.0, color=p.green,
              label=f"+ {FINETUNE_EPOCHS} epochs of fine-tuning")
    left.axhline(teacher["accuracy"], color=p.muted, lw=1.2, ls="--",
                 label=f"teacher ({teacher['accuracy']:.4f})")
    for sparsity in sparsities:
        left.annotate(f"{runs[sparsity]['recovered']:.3f}",
                      (sparsity, runs[sparsity]["recovered"]), xytext=(0, 8),
                      textcoords="offset points", ha="center", fontsize=7,
                      color=p.green)
    left.set_xlabel("share of weights set to zero")
    left.set_ylabel("test accuracy")
    left.set_ylim(0, 1.1)
    left.set_title("fine-tuning is the technique, not the pruning",
                   fontsize=10)
    left.legend(fontsize=7.5, loc="lower left")

    gaps = [runs[s]["recovered"] - runs[s]["immediate"] for s in sparsities]
    right.bar(np.arange(len(sparsities)), gaps, 0.5, color=p.amber)
    for x, (sparsity, gap) in enumerate(zip(sparsities, gaps)):
        right.annotate(f"{gap:+.4f}", (x, gap), xytext=(0, 4),
                       textcoords="offset points", ha="center", fontsize=7.5,
                       color=p.fg)
    right.set_xticks(np.arange(len(sparsities)))
    right.set_xticklabels([f"{s:.0%}" for s in sparsities])
    right.set_xlabel("sparsity")
    right.set_ylabel("accuracy recovered by fine-tuning")
    right.set_title("what the recovery step is worth at each level",
                    fontsize=10)


def distillation(fig, axes, p: Palette) -> None:
    students = _students()
    teacher = _teacher()
    left, right = fig.subplots(1, 2)
    for label, color in (("student, alone", p.blue),
                         ("student, distilled", p.green)):
        curve = students[label]["curve"]
        left.plot(range(1, len(curve) + 1), curve, lw=2.0, color=color,
                  label=f"{label} ({curve[-1]:.4f})")
    left.axhline(teacher["accuracy"], color=p.muted, lw=1.2, ls="--",
                 label=f"teacher ({teacher['accuracy']:.4f})")
    left.set_xlabel("epoch")
    left.set_ylabel("test accuracy")
    left.set_title(f"same architecture, same budget, "
                   f"{students['student, alone']['model'].count_params():,} "
                   f"parameters", fontsize=10)
    left.legend(fontsize=8, loc="lower right")

    logits = students["_logits"]
    hard = np.zeros_like(logits)
    hard[np.arange(len(logits)), logits.argmax(axis=1)] = 1.0
    soft = students["_soft"]
    index = int(np.argmax(soft.max(axis=1) < 0.9))       # an ambiguous example
    positions = np.arange(10)
    width = 0.38
    right.bar(positions - width / 2, hard[index], width * 0.9, color=p.muted,
              label="hard label (one-hot)")
    right.bar(positions + width / 2, soft[index], width * 0.9, color=p.green,
              label=f"teacher at T={TEMPERATURE:g}")
    for x, value in zip(positions + width / 2, soft[index]):
        if value > 0.01:
            right.annotate(f"{value:.2f}", (x, value), xytext=(0, 3),
                           textcoords="offset points", ha="center",
                           fontsize=6.5, color=p.fg)
    right.set_xticks(positions)
    right.set_xlabel("class")
    right.set_ylabel("target probability")
    right.set_title("the soft target carries what the teacher was unsure about",
                    fontsize=10)
    right.legend(fontsize=8, loc="upper right")


def frontier(fig, axes, p: Palette) -> None:
    points = _frontier()
    colors = {"baseline": p.muted, "pruning": p.blue,
              "distillation": p.green}
    seen = set()
    for label, entry in points.items():
        family = entry["family"]
        axes.scatter(entry["bytes"] / 1024, entry["accuracy"], s=90,
                     color=colors[family],
                     label=family if family not in seen else None)
        seen.add(family)
        axes.annotate(label, (entry["bytes"] / 1024, entry["accuracy"]),
                      xytext=(0, 9), textcoords="offset points", ha="center",
                      fontsize=7, color=p.fg)
    axes.set_xscale("log")
    axes.set_xlabel("estimated weight storage (KB, log)")
    axes.set_ylabel("test accuracy")
    axes.set_title("accuracy against size, all three families", fontsize=10)
    axes.legend(fontsize=8, loc="lower right")


FIGURES = [
    figure("pruning", pruning, size=(9.4, 3.5), axes=False),
    figure("distillation", distillation, size=(9.6, 3.5), axes=False),
    figure("frontier", frontier, size=(8.6, 3.6)),
]


if __name__ == "__main__":
    teacher = _teacher()
    print("=== the teacher ===")
    print(f"{teacher['parameters']:,} parameters, {EPOCHS} epochs, "
          f"{teacher['seconds']:.0f}s, test accuracy {teacher['accuracy']:.4f}")

    print(f"\n=== magnitude pruning (fine-tuned for {FINETUNE_EPOCHS} epochs) ===")
    runs = _pruning_runs()
    print(f"{'sparsity':>9} {'measured':>9} {'no fine-tune':>13} "
          f"{'fine-tuned':>11} {'recovered':>10} {'est. KB':>9}")
    for sparsity, entry in runs.items():
        print(f"{sparsity:9.0%} {entry['actual_sparsity']:9.2%} "
              f"{entry['immediate']:13.4f} {entry['recovered']:11.4f} "
              f"{entry['recovered'] - entry['immediate']:+10.4f} "
              f"{entry['bytes'] / 1024:9.1f}")
    print("the mask is re-applied after every fine-tuning epoch: without that,")
    print("gradient descent refills the pruned weights and the sparsity is")
    print("silently lost while the accuracy looks fine")

    print(f"\n=== distillation (T={TEMPERATURE:g}, alpha={ALPHA:g}) ===")
    students = _students()
    student_params = students["student, alone"]["model"].count_params()
    print(f"student has {student_params:,} parameters, "
          f"{teacher['parameters'] / student_params:.1f}x smaller than the "
          f"teacher")
    print(f"{'model':22s} {'accuracy':>9} {'vs teacher':>11} {'seconds':>9}")
    for label in ("student, alone", "student, distilled"):
        entry = students[label]
        print(f"{label:22s} {entry['accuracy']:9.4f} "
              f"{entry['accuracy'] - teacher['accuracy']:+11.4f} "
              f"{entry['seconds']:9.0f}")
    gain = (students["student, distilled"]["accuracy"]
            - students["student, alone"]["accuracy"])
    print(f"distillation was worth {gain:+.4f} at identical size and budget")

    print("\n=== the frontier ===")
    print(f"{'model':22s} {'est. KB':>9} {'accuracy':>9}")
    for label, entry in _frontier().items():
        print(f"{label:22s} {entry['bytes'] / 1024:9.1f} "
              f"{entry['accuracy']:9.4f}")
    print("pruned sizes assume a sparse format (value + 16-bit index per")
    print("surviving weight). Keras writes the dense array regardless, so that")
    print("saving is only real if the deployment format supports sparsity")
