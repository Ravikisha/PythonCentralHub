"""Figures for *Attention Before Transformers (Bahdanau)*.

The task is date normalisation: a messily written date in, an ISO date out.
Synthetic, so there is no corpus to download, and the alignment is known in
advance — which is what makes the attention weights checkable rather than
merely decorative.

``bottleneck``
    Exact-match accuracy against encoder width for a plain encoder-decoder and
    for the same model with additive attention. The plain model's accuracy is a
    function of how much state it has; the attention model's is much less so,
    which is the whole argument for attention.

``by-position``
    Per-character accuracy for each of the ten output positions. The plain
    model's 0.73 is not spread evenly: it gets the parts of the answer that a
    single fixed-size state can hold and misses the rest. Bucketing by source
    length, which is what this figure originally did, showed nothing -- the
    plain model scores the same at 8 characters as at 40 -- so the split that
    does carry information replaced it.

``alignment``
    The attention matrix for one decoded example, with the output characters on
    one axis and the input characters on the other.
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

from _dl import seed_everything, tf  # noqa: E402
from _style import Palette, figure  # noqa: E402

ROWS = 6000
TEST = 1200
SOURCE_LEN = 30
TARGET_LEN = 10
UNITS = 64
EPOCHS = 12
WIDTHS = (8, 16, 32, 64)

MONTHS = ("january", "february", "march", "april", "may", "june", "july",
          "august", "september", "october", "november", "december")
DAYS = ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday",
        "sunday")
SOURCE_ALPHABET = " -/,0123456789abcdefghijklmnopqrstuvwxyz"
TARGET_ALPHABET = "0123456789-^$"          # ^ start, $ pad


def _formats(rng, day, month, year):
    """Six ways a human writes the same date, some of them long."""
    name = MONTHS[month - 1]
    weekday = DAYS[rng.integers(0, len(DAYS))]
    return (
        f"{day}/{month}/{year}",
        f"{day} {name} {year}",
        f"{name} {day}, {year}",
        f"{weekday} {day} {name} {year}",
        f"the {day} of {name}, {year}",
        f"{day}-{month:02d}-{year}",
    )


@functools.lru_cache(maxsize=1)
def _data() -> dict:
    rng = np.random.default_rng(0)
    source_index = {character: number
                    for number, character in enumerate(SOURCE_ALPHABET)}
    target_index = {character: number
                    for number, character in enumerate(TARGET_ALPHABET)}

    sources, targets, lengths = [], [], []
    for _ in range(ROWS + TEST):
        year = int(rng.integers(1970, 2030))
        month = int(rng.integers(1, 13))
        day = int(rng.integers(1, 29))
        options = _formats(rng, day, month, year)
        text = options[rng.integers(0, len(options))]
        iso = f"{year:04d}-{month:02d}-{day:02d}"
        lengths.append(len(text))
        row = [source_index[character] for character in text[:SOURCE_LEN]]
        row += [0] * (SOURCE_LEN - len(row))
        sources.append(row)
        targets.append([target_index[character] for character in iso])

    sources = np.array(sources, dtype="int32")
    targets = np.array(targets, dtype="int32")
    lengths = np.array(lengths)
    # The decoder input is the target shifted right behind a start symbol.
    start = target_index["^"]
    shifted = np.concatenate(
        [np.full((len(targets), 1), start, dtype="int32"), targets[:, :-1]],
        axis=1)
    return {"x_train": sources[:ROWS], "y_train": targets[:ROWS],
            "shift_train": shifted[:ROWS],
            "x_test": sources[ROWS:], "y_test": targets[ROWS:],
            "shift_test": shifted[ROWS:],
            "lengths_test": lengths[ROWS:],
            "source_index": source_index, "target_index": target_index,
            "start": start}


def _build(units: int, attention: bool):
    """Encoder-decoder over characters, with or without additive attention."""
    keras = tf().keras
    tensorflow = tf()

    class Decoder(keras.layers.Layer):
        """An unrolled GRU decoder. With attention it recomputes a context
        vector at every step from the previous state; without, it sees the
        encoder's final state once and nothing else."""

        def __init__(self, units, attention, vocabulary, **kwargs):
            super().__init__(**kwargs)
            self.cell = keras.layers.GRUCell(units)
            self.embedding = keras.layers.Embedding(len(TARGET_ALPHABET), 16)
            self.output_layer = keras.layers.Dense(vocabulary)
            self.attention = attention
            if attention:
                # score = v . tanh(W_enc h_j + W_dec s_{t-1})  -- additive.
                self.encoder_projection = keras.layers.Dense(units,
                                                             use_bias=False)
                self.state_projection = keras.layers.Dense(units,
                                                           use_bias=False)
                self.score = keras.layers.Dense(1, use_bias=False)

        def call(self, inputs):
            encoded, final_state, tokens = inputs
            state = final_state
            embedded = self.embedding(tokens)
            projected = (self.encoder_projection(encoded)
                         if self.attention else None)
            outputs, weights = [], []
            for step in range(TARGET_LEN):
                if self.attention:
                    query = self.state_projection(state)[:, None, :]
                    scores = self.score(
                        tensorflow.nn.tanh(projected + query))[..., 0]
                    alpha = tensorflow.nn.softmax(scores, axis=1)
                    context = tensorflow.reduce_sum(
                        alpha[..., None] * encoded, axis=1)
                    weights.append(alpha)
                    cell_input = tensorflow.concat(
                        [embedded[:, step, :], context], axis=-1)
                else:
                    cell_input = embedded[:, step, :]
                output, [state] = self.cell(cell_input, [state])
                outputs.append(self.output_layer(output))
            stacked = tensorflow.stack(outputs, axis=1)
            if self.attention:
                return stacked, tensorflow.stack(weights, axis=1)
            zeros = tensorflow.zeros(
                (tensorflow.shape(stacked)[0], TARGET_LEN, SOURCE_LEN))
            return stacked, zeros

    source = keras.layers.Input((SOURCE_LEN,), dtype="int32")
    tokens = keras.layers.Input((TARGET_LEN,), dtype="int32")
    embedded = keras.layers.Embedding(len(SOURCE_ALPHABET), 32)(source)
    encoded, final_state = keras.layers.GRU(
        units, return_sequences=True, return_state=True)(embedded)
    logits, weights = Decoder(units, attention,
                              len(TARGET_ALPHABET))([encoded, final_state,
                                                     tokens])
    model = keras.Model([source, tokens], logits)
    weight_model = keras.Model([source, tokens], weights)
    model.compile(optimizer="adam",
                  loss=keras.losses.SparseCategoricalCrossentropy(
                      from_logits=True))
    return model, weight_model


def _greedy(model, data, rows):
    """Decode without teacher forcing: the model eats its own predictions."""
    sources = data["x_test"][:rows]
    tokens = np.full((len(sources), TARGET_LEN), data["start"], dtype="int32")
    for step in range(TARGET_LEN):
        logits = model.predict([sources, tokens], verbose=0)
        chosen = logits[:, step, :].argmax(axis=1)
        if step + 1 < TARGET_LEN:
            tokens[:, step + 1] = chosen
        if step == 0:
            predictions = np.zeros((len(sources), TARGET_LEN), dtype="int32")
        predictions[:, step] = chosen
    return predictions


def _score(predictions, truth):
    """Exact match is the honest headline; per-character accuracy is what
    shows whether a model that never gets a whole date right has learned
    anything at all."""
    matched = predictions == truth
    exact = matched.all(axis=1)
    return float(exact.mean()), exact, matched.mean(axis=1)


@functools.lru_cache(maxsize=1)
def _sweep() -> dict:
    data = _data()
    out = {}
    for attention in (False, True):
        row = []
        for units in WIDTHS:
            seed_everything(0)
            model, _ = _build(units, attention)
            start = time.perf_counter()
            model.fit([data["x_train"], data["shift_train"]], data["y_train"],
                      epochs=EPOCHS, batch_size=128, verbose=0)
            seconds = time.perf_counter() - start
            predictions = _greedy(model, data, TEST)
            accuracy, exact, per_row = _score(predictions,
                                              data["y_test"][:TEST])
            row.append({"units": units, "accuracy": accuracy,
                        "characters": float(per_row.mean()),
                        "seconds": seconds,
                        "parameters": int(model.count_params()),
                        "exact": exact})
        out["attention" if attention else "plain"] = row
    return out


@functools.lru_cache(maxsize=1)
def _detail() -> dict:
    """The widest pair again, kept so the length buckets and the alignment
    come from a model whose accuracy is already in the sweep."""
    data = _data()
    result = {}
    for attention in (False, True):
        seed_everything(0)
        model, weight_model = _build(UNITS, attention)
        model.fit([data["x_train"], data["shift_train"]], data["y_train"],
                  epochs=EPOCHS, batch_size=128, verbose=0)
        predictions = _greedy(model, data, TEST)
        accuracy, exact, per_row = _score(predictions, data["y_test"][:TEST])
        result["attention" if attention else "plain"] = {
            "accuracy": accuracy, "exact": exact, "characters": per_row,
            "mean_characters": float(per_row.mean()),
            "predictions": predictions}
        if attention:
            index = int(np.argmax(data["lengths_test"][:TEST]))
            sample = data["x_test"][index: index + 1]
            tokens = predictions[index: index + 1].copy()
            tokens = np.concatenate(
                [np.full((1, 1), data["start"], dtype="int32"),
                 tokens[:, :-1]], axis=1)
            weights = weight_model.predict([sample, tokens], verbose=0)[0]
            reverse = {number: character
                       for character, number in data["source_index"].items()}
            text = "".join(reverse[token] for token in sample[0]).rstrip()
            result["alignment"] = {
                "weights": weights[:, :max(len(text), 1)],
                "source": text,
                "output": "".join(
                    TARGET_ALPHABET[token] for token in predictions[index]),
            }

    lengths = data["lengths_test"][:TEST]
    edges = ((0, 12), (12, 18), (18, 24), (24, 60))
    buckets = []
    for low, high in edges:
        mask = (lengths >= low) & (lengths < high)
        if mask.sum() < 20:
            continue
        buckets.append({
            "label": f"{low}-{high}",
            "n": int(mask.sum()),
            "plain": float(result["plain"]["characters"][mask].mean()),
            "attention": float(
                result["attention"]["characters"][mask].mean()),
            "plain_exact": float(result["plain"]["exact"][mask].mean()),
            "attention_exact": float(
                result["attention"]["exact"][mask].mean()),
            "plain_sd": float(result["plain"]["characters"][mask].std()),
        })
    result["buckets"] = buckets
    truth = data["y_test"][:TEST]
    result["positions"] = {
        key: (result[key]["predictions"] == truth).mean(axis=0).tolist()
        for key in ("plain", "attention")}
    result["labels"] = ["Y", "Y", "Y", "Y", "-", "M", "M", "-", "D", "D"]
    return result


def bottleneck(fig, axes, p: Palette) -> None:
    sweep = _sweep()
    ax = fig.subplots(1, 1)
    positions = np.arange(len(WIDTHS))
    width = 0.36
    for offset, key, colour, label in (
            (-width / 2, "plain", p.muted, "encoder-decoder"),
            (width / 2, "attention", p.blue, "+ additive attention")):
        values = [row["accuracy"] for row in sweep[key]]
        ax.bar(positions + offset, values, width * 0.92, color=colour,
               label=label)
        for position, value in zip(positions + offset, values):
            ax.annotate(f"{value:.3f}", (position, value), xytext=(0, 3),
                        textcoords="offset points", ha="center", fontsize=7.5,
                        color=p.fg)
    ax.set_xticks(positions)
    ax.set_xticklabels([f"{units} units" for units in WIDTHS])
    ax.set_ylim(0, 1.08)
    ax.set_xlabel("encoder width — the size of the vector the plain model "
                  "must fit the whole input into")
    ax.set_ylabel("exact-match accuracy")
    ax.set_title(f"date normalisation, {TEST:,} held-out strings, "
                 f"{EPOCHS} epochs each", fontsize=10)
    ax.legend(fontsize=8, loc="upper left")


def by_position(fig, axes, p: Palette) -> None:
    info = _detail()
    ax = fig.subplots(1, 1)
    labels = info["labels"]
    positions = np.arange(len(labels))
    width = 0.36
    plain = info["positions"]["plain"]
    attention = info["positions"]["attention"]
    ax.bar(positions - width / 2, plain, width * 0.92, color=p.muted,
           label="encoder-decoder")
    ax.bar(positions + width / 2, attention, width * 0.92, color=p.blue,
           label="+ additive attention")
    for position, value in zip(positions - width / 2, plain):
        ax.annotate(f"{value:.2f}", (position, value), xytext=(0, 3),
                    textcoords="offset points", ha="center", fontsize=7,
                    color=p.fg)
    ax.set_xticks(positions)
    ax.set_xticklabels([f"{label}\n{index}"
                        for index, label in enumerate(labels)], fontsize=8)
    ax.set_ylim(0, 1.12)
    ax.set_xlabel("output position — YYYY-MM-DD")
    ax.set_ylabel("accuracy at that position")
    ax.set_title(f"both models at {UNITS} units, {TEST:,} held-out strings",
                 fontsize=10)
    ax.legend(fontsize=8, loc="lower left")


def alignment(fig, axes, p: Palette) -> None:
    info = _detail()["alignment"]
    ax = fig.subplots(1, 1)
    weights = info["weights"]
    mesh = ax.imshow(weights, cmap="magma", aspect="auto",
                     vmin=0, vmax=max(float(weights.max()), 1e-6))
    fig.colorbar(mesh, ax=ax, fraction=0.03, label="attention weight")
    ax.set_xticks(range(len(info["source"])))
    ax.set_xticklabels(list(info["source"]), fontsize=7)
    ax.set_yticks(range(len(info["output"])))
    ax.set_yticklabels(list(info["output"]), fontsize=8)
    ax.set_xlabel("input characters")
    ax.set_ylabel("output characters")
    ax.set_title("where the decoder looked, one step per output character",
                 fontsize=10)


FIGURES = [
    figure("bottleneck", bottleneck, size=(8.4, 4.4), axes=False),
    figure("by-position", by_position, size=(8.8, 4.4), axes=False),
    figure("alignment", alignment, size=(9.0, 4.4), axes=False),
]


if __name__ == "__main__":
    sweep = _sweep()
    print("=== encoder width sweep ===")
    print(f"{'units':>6} {'plain':>9} {'attention':>11} {'plain ch':>10} "
          f"{'attn ch':>9} {'plain s':>9} {'attn s':>8}")
    for plain, attention in zip(sweep["plain"], sweep["attention"]):
        print(f"{plain['units']:6d} {plain['accuracy']:9.4f} "
              f"{attention['accuracy']:11.4f} {plain['characters']:10.4f} "
              f"{attention['characters']:9.4f} "
              f"{plain['seconds']:9.1f} {attention['seconds']:8.1f}")
    print(f"\nparameters at {UNITS} units: plain "
          f"{sweep['plain'][-1]['parameters']:,}, attention "
          f"{sweep['attention'][-1]['parameters']:,}")

    detail = _detail()
    print("\n=== by source length ===")
    print(f"{'bucket':>8} {'n':>6} {'plain ch':>10} {'attn ch':>9}")
    for bucket in detail["buckets"]:
        print(f"{bucket['label']:>8} {bucket['n']:6d} {bucket['plain']:10.4f} "
              f"{bucket['attention']:9.4f}")
    spread = [bucket["plain"] for bucket in detail["buckets"]]
    print(f"the plain model varies by only {max(spread) - min(spread):.4f} "
          f"across the length buckets -- length is not the axis that matters")

    print("\n=== by output position ===")
    print(f"{'position':>9} {'plain':>9} {'attention':>11}")
    for index, label in enumerate(detail["labels"]):
        print(f"{label + str(index):>9} "
              f"{detail['positions']['plain'][index]:9.4f} "
              f"{detail['positions']['attention'][index]:11.4f}")
    print(f"\noverall: plain {detail['plain']['accuracy']:.4f}, "
          f"attention {detail['attention']['accuracy']:.4f}")
    print(f"\nalignment example: {detail['alignment']['source']!r} -> "
          f"{detail['alignment']['output']!r}")
    peaks = detail["alignment"]["weights"].argmax(axis=1)
    print("peak input position per output character:")
    for character, peak in zip(detail["alignment"]["output"], peaks):
        source = detail["alignment"]["source"]
        print(f"  {character} -> position {peak} ({source[peak]!r})")
