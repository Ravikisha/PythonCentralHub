"""Figures for *Object Detection (Bounding Boxes and YOLO)*.

Synthetic 64x64 scenes with one to three rectangles, each with an exact box and
class. Generating the data means every box is known to be correct, and the whole
page runs on a CPU.

``iou-examples``
    Six box pairs with their IoU computed, because "0.5 overlap" is not a
    quantity most people can picture.

``grid-predictions``
    A YOLO-style grid detector's raw output next to the truth.

``nms-effect``
    The same predictions before and after non-max suppression, at three
    thresholds.
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

SIDE = 64
GRID = 8
CELL = SIDE // GRID
TRAIN = 2000
TEST = 400
EPOCHS = 18


def iou(a, b) -> float:
    """a, b are (x1, y1, x2, y2)."""
    left = max(a[0], b[0])
    top = max(a[1], b[1])
    right = min(a[2], b[2])
    bottom = min(a[3], b[3])
    if right <= left or bottom <= top:
        return 0.0
    intersection = (right - left) * (bottom - top)
    area_a = (a[2] - a[0]) * (a[3] - a[1])
    area_b = (b[2] - b[0]) * (b[3] - b[1])
    return float(intersection / (area_a + area_b - intersection))


PAIRS = (
    ("identical", (10, 10, 30, 30), (10, 10, 30, 30)),
    ("shifted 4 px", (10, 10, 30, 30), (14, 10, 34, 30)),
    ("shifted 10 px", (10, 10, 30, 30), (20, 10, 40, 30)),
    ("half the size", (10, 10, 30, 30), (10, 10, 20, 20)),
    ("touching", (10, 10, 30, 30), (30, 10, 50, 30)),
    ("disjoint", (10, 10, 30, 30), (40, 40, 60, 60)),
)


def iou_examples(fig, axes, p: Palette) -> None:
    grid = fig.subplots(1, len(PAIRS))
    for ax, (label, a, b) in zip(grid, PAIRS):
        for box, color in ((a, p.blue), (b, p.amber)):
            ax.add_patch(__import__("matplotlib").patches.Rectangle(
                (box[0], box[1]), box[2] - box[0], box[3] - box[1],
                fill=False, edgecolor=color, lw=2.0))
        score = iou(a, b)
        ax.set_xlim(0, SIDE)
        ax.set_ylim(SIDE, 0)
        ax.set_title(f"{label}\nIoU {score:.4f}", fontsize=8)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.grid(False)


def _scene(rng: np.random.Generator):
    image = rng.normal(0.5, 0.05, (SIDE, SIDE)).astype("float32")
    boxes = []
    for _ in range(rng.integers(1, 4)):
        width = int(rng.integers(10, 20))
        height = int(rng.integers(10, 20))
        x = int(rng.integers(0, SIDE - width))
        y = int(rng.integers(0, SIDE - height))
        bright = float(rng.choice([0.15, 0.9]))
        image[y:y + height, x:x + width] = bright
        boxes.append((x, y, x + width, y + height))
    return np.clip(image, 0, 1)[..., None], boxes


def _encode(boxes) -> np.ndarray:
    """One target per grid cell: objectness, then centre offset and size."""
    target = np.zeros((GRID, GRID, 5), "float32")
    for x1, y1, x2, y2 in boxes:
        cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
        column, row = int(cx // CELL), int(cy // CELL)
        column = min(column, GRID - 1)
        row = min(row, GRID - 1)
        target[row, column] = (1.0,
                               (cx - column * CELL) / CELL,
                               (cy - row * CELL) / CELL,
                               (x2 - x1) / SIDE,
                               (y2 - y1) / SIDE)
    return target


def _decode(prediction: np.ndarray, threshold: float = 0.5):
    out = []
    for row in range(GRID):
        for column in range(GRID):
            objectness = float(prediction[row, column, 0])
            if objectness < threshold:
                continue
            ox, oy, w, h = prediction[row, column, 1:]
            cx = (column + float(ox)) * CELL
            cy = (row + float(oy)) * CELL
            width, height = float(w) * SIDE, float(h) * SIDE
            out.append((objectness, (cx - width / 2, cy - height / 2,
                                     cx + width / 2, cy + height / 2)))
    return sorted(out, key=lambda item: -item[0])


def non_max_suppression(detections, threshold: float):
    kept = []
    for score, box in detections:
        if all(iou(box, other) <= threshold for _, other in kept):
            kept.append((score, box))
    return kept


@functools.lru_cache(maxsize=1)
def _data() -> dict:
    rng = np.random.default_rng(0)
    images, targets, truth = [], [], []
    for _ in range(TRAIN + TEST):
        image, boxes = _scene(rng)
        images.append(image)
        targets.append(_encode(boxes))
        truth.append(boxes)
    images = np.stack(images)
    targets = np.stack(targets)
    return {"x_train": images[:TRAIN], "y_train": targets[:TRAIN],
            "x_test": images[TRAIN:], "y_test": targets[TRAIN:],
            "truth": truth[TRAIN:],
            "boxes_per_scene": float(np.mean([len(b) for b in truth]))}


@functools.lru_cache(maxsize=1)
def _detector() -> dict:
    keras = tf().keras
    data = _data()
    seed_everything(0)
    inputs = keras.layers.Input((SIDE, SIDE, 1))
    x = inputs
    for filters in (16, 32, 64):
        x = keras.layers.Conv2D(filters, 3, padding="same",
                                activation="relu")(x)
        x = keras.layers.MaxPooling2D(2)(x)
    objectness = keras.layers.Conv2D(1, 1, activation="sigmoid")(x)
    geometry = keras.layers.Conv2D(4, 1, activation="sigmoid")(x)
    outputs = keras.layers.Concatenate()([objectness, geometry])
    model = keras.Model(inputs, outputs)

    def loss(y_true, y_pred):
        present = y_true[..., :1]
        objectness_loss = keras.losses.binary_crossentropy(
            y_true[..., :1], y_pred[..., :1])
        geometry_loss = tf().reduce_sum(
            tf().square(y_true[..., 1:] - y_pred[..., 1:]) * present, axis=-1)
        return objectness_loss + 5.0 * geometry_loss

    model.compile(keras.optimizers.Adam(2e-3), loss)
    history = model.fit(data["x_train"], data["y_train"], epochs=EPOCHS,
                        batch_size=32, verbose=0,
                        validation_data=(data["x_test"], data["y_test"]))
    predictions = model.predict(data["x_test"], verbose=0)
    return {"model": model, "predictions": predictions,
            "loss": [float(v) for v in history.history["loss"]],
            "val_loss": [float(v) for v in history.history["val_loss"]],
            "params": int(model.count_params())}


def _draw_boxes(ax, boxes, color, lw=1.8, scores=None):
    patches = __import__("matplotlib").patches
    for index, box in enumerate(boxes):
        ax.add_patch(patches.Rectangle((box[0], box[1]), box[2] - box[0],
                                       box[3] - box[1], fill=False,
                                       edgecolor=color, lw=lw))
        if scores is not None:
            ax.annotate(f"{scores[index]:.2f}", (box[0], box[1] - 1),
                        fontsize=6, color=color)


def grid_predictions(fig, axes, p: Palette) -> None:
    data = _data()
    info = _detector()
    grid = fig.subplots(2, 4)
    for column in range(4):
        image = data["x_test"][column][..., 0]
        raw = _decode(info["predictions"][column], threshold=0.5)
        kept = non_max_suppression(raw, 0.3)
        for row, (title, boxes, scores, color) in enumerate((
                ("truth", data["truth"][column], None, p.green),
                (f"kept {len(kept)} of {len(raw)}",
                 [b for _, b in kept], [s for s, _ in kept], p.amber))):
            ax = grid[row][column]
            ax.imshow(image, cmap="gray")
            for line in range(1, GRID):
                ax.axhline(line * CELL - 0.5, color=p.grid, lw=0.4)
                ax.axvline(line * CELL - 0.5, color=p.grid, lw=0.4)
            _draw_boxes(ax, boxes, color, scores=scores)
            ax.set_title(title, fontsize=8, color=color)
            ax.set_xticks([])
            ax.set_yticks([])
            ax.grid(False)


def nms_effect(fig, axes, p: Palette) -> None:
    data = _data()
    info = _detector()
    thresholds = (1.0, 0.5, 0.3, 0.1)
    grid = fig.subplots(1, len(thresholds))
    sample = 0
    raw = _decode(info["predictions"][sample], threshold=0.4)
    for ax, threshold in zip(grid, thresholds):
        kept = raw if threshold >= 1.0 else non_max_suppression(raw, threshold)
        ax.imshow(data["x_test"][sample][..., 0], cmap="gray")
        _draw_boxes(ax, data["truth"][sample], p.green, lw=2.4)
        _draw_boxes(ax, [b for _, b in kept], p.amber, lw=1.2,
                    scores=[s for s, _ in kept])
        label = "no NMS" if threshold >= 1.0 else f"IoU threshold {threshold:g}"
        ax.set_title(f"{label}\n{len(kept)} boxes for "
                     f"{len(data['truth'][sample])} objects", fontsize=8)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.grid(False)


FIGURES = [
    figure("iou-examples", iou_examples, size=(9.6, 2.0), axes=False),
    figure("grid-predictions", grid_predictions, size=(9.4, 4.6), axes=False),
    figure("nms-effect", nms_effect, size=(9.4, 2.6), axes=False),
]


if __name__ == "__main__":
    print("=== IoU on six box pairs ===")
    print(f"{'case':16s} {'box A':>22} {'box B':>22} {'IoU':>8}")
    for label, a, b in PAIRS:
        print(f"{label:16s} {str(a):>22} {str(b):>22} {iou(a, b):8.4f}")

    data = _data()
    print(f"\n=== synthetic detection data ===")
    print(f"{TRAIN} train / {TEST} test scenes of {SIDE}x{SIDE}, "
          f"{data['boxes_per_scene']:.3f} boxes per scene on average")
    print(f"grid {GRID}x{GRID} of {CELL}x{CELL} cells, 5 numbers per cell "
          f"= {GRID * GRID * 5} targets")
    occupied = float((data["y_train"][..., 0] == 1).mean())
    print(f"only {occupied:.4f} of cells contain an object centre, so the "
          f"objectness target is {1 / occupied:.1f}:1 imbalanced")

    info = _detector()
    print(f"\n=== the detector, {EPOCHS} epochs ===")
    print(f"parameters {info['params']:,}  final loss {info['loss'][-1]:.4f}  "
          f"final val loss {info['val_loss'][-1]:.4f}")

    print("\n=== decoding and NMS on the test split ===")
    for threshold in (0.3, 0.5, 0.7):
        raw_total = kept_total = matched = 0
        truth_total = 0
        for index in range(TEST):
            raw = _decode(info["predictions"][index], threshold=threshold)
            kept = non_max_suppression(raw, 0.3)
            raw_total += len(raw)
            kept_total += len(kept)
            truth = data["truth"][index]
            truth_total += len(truth)
            for _, box in kept:
                if any(iou(box, actual) >= 0.5 for actual in truth):
                    matched += 1
        print(f"objectness threshold {threshold:.1f}: {raw_total:5d} raw -> "
              f"{kept_total:5d} after NMS  ({matched:5d} match a true box at "
              f"IoU 0.5, precision {matched / max(kept_total, 1):.4f}, "
              f"recall {matched / truth_total:.4f})")
    print("raising the objectness threshold trades recall for precision; NMS")
    print("removes duplicates without touching either directly")
