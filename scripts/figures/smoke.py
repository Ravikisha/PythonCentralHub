"""Draw every figure in a module on tiny data, in seconds instead of an hour.

A figure module has two kinds of code that fail for unrelated reasons: expensive
measurement functions, and cheap drawing functions. Discovering a KeyError in a
legend *after* an hour of training is the worst possible way to find one — and it
happened, when a hardcoded style key stopped matching a changed depth constant.

This runs the module's real code path with its size constants shrunk to almost
nothing and its dataset capped at a few hundred rows, then renders every figure
to a throwaway file. Shape mistakes, missing dictionary keys, bad unpacking and
label typos all surface within seconds.

    python scripts/figures/smoke.py dl/phase-03-vision/famous-architectures

It proves only that the figures *draw*. Numbers from a smoke run are meaningless
— preview the real module before trusting any of them.
"""

from __future__ import annotations

import argparse
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from _style import DARK, _rc  # noqa: E402
from preview import load  # noqa: E402

# Module-level constants worth shrinking, and what to shrink them to. Anything
# not present in a given module is simply skipped.
SCALARS = {
    "EPOCHS": 1, "PRETRAIN_EPOCHS": 1, "LIMIT": 256, "TRAIN": 48, "TEST": 16,
    "PRETRAIN_ROWS": 256, "SPLITS": 2, "DEPTH": 3, "BLOCKS": 1, "SUBSET": 120,
    # sequence pages
    "MAXLEN": 24, "COPY_ROWS": 128, "COPY_EPOCHS": 1, "COPY_DISTANCE": 12,
    "ROWS": 256, "TIMESTEPS": 12, "UNITS": 8, "VOCAB": 512,
    # text pages
    "DOCUMENTS": 200, "MERGES": 60, "PRETOKENS": 400,
    # generative pages: corpus size, layer width, sample counts
    "REVIEWS": 40, "WINDOW": 16, "STRIDE": 8, "LENGTH": 24, "WIDTH": 16,
    "SAMPLES": 64, "SCORED": 32, "GRID": 4, "SIDE": 8,
    # reinforcement learning: episodes and frames dominate the wall-clock
    "EPISODES": 20, "EVAL": 8, "STEPS": 32, "SEEDS": 3, "FRAMES": 120,
    "ENVS": 4, "BUFFER": 200, "WARMUP": 32, "TARGET_SYNC": 16, "DQN_SEEDS": 1,
    "ROLLOUTS": 8, "BATCH_EPISODES": 4, "UPDATES": 6, "PPO_EPOCHS": 2,
}
SEQUENCES = {
    "SIZES": (64, 96), "BATCHES": (32,), "RATES": (0.1,), "DEPTHS": (2, 3),
    "WIDTHS": (8, 16), "DROPOUTS": (0.0, 0.5), "PENALTIES": (0.0, 1e-3),
    "MAGNITUDES": (1.0, 10.0), "DISTANCES": (4, 8), "HORIZONS": (1, 3),
    "CANDIDATES": (8, 16), "WINDOWS": (4, 8), "MERGE_STEPS": (0, 20, 60),
    "WORD_CAPS": (50, 200),
}
CAP = 256


def shrink(module) -> list[str]:
    """Rewrite the module's size knobs in place. Returns what was changed."""
    changed = []
    for name, value in SCALARS.items():
        if hasattr(module, name) and isinstance(getattr(module, name), int):
            if getattr(module, name) > value:
                setattr(module, name, value)
                changed.append(f"{name}={value}")
    for name, value in SEQUENCES.items():
        current = getattr(module, name, None)
        if not isinstance(current, (tuple, list)) or not current:
            continue
        # A sequence of pairs (say DROPOUTS = ((0.0, 0.0), (0.3, 0.0))) means
        # something different to the module than a sequence of numbers, and
        # replacing one with the other breaks the unpacking rather than the
        # cost. Leave those alone.
        if isinstance(current[0], (tuple, list)):
            continue
        setattr(module, name, type(current)(value))
        changed.append(f"{name}={value}")

    # Constants derived from a sequence have to be re-derived, or a figure will
    # look up a key the shrunk measurement never produced.
    if hasattr(module, "SWEEP_SIZE") and hasattr(module, "SIZES"):
        sizes = module.SIZES
        module.SWEEP_SIZE = sizes[len(sizes) // 2]
        changed.append(f"SWEEP_SIZE={module.SWEEP_SIZE}")

    if hasattr(module, "dataset"):
        original = module.dataset

        def small(name="mnist", limit=CAP, flat=True, _original=original):
            return _original(name, min(limit, CAP), flat)

        module.dataset = small
        changed.append(f"dataset capped at {CAP} rows")

    if hasattr(module, "imdb"):
        original_imdb = module.imdb

        def small_imdb(vocab=512, maxlen=24, limit=CAP, truncating="pre",
                       _original=original_imdb):
            return _original(min(vocab, 512), min(maxlen, 24),
                             min(limit, CAP), truncating)

        module.imdb = small_imdb
        changed.append(f"imdb capped at {CAP} rows / 24 tokens")

    if hasattr(module, "waves"):
        original_waves = module.waves

        def small_waves(rows=CAP, timesteps=12, horizon=1, noise=0.1, seed=0,
                        trend=0.0, _original=original_waves):
            return _original(min(rows, CAP), min(timesteps, 12), horizon,
                             noise, seed, trend)

        module.waves = small_waves
        changed.append(f"waves capped at {CAP} rows / 12 timesteps")
    return changed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("module", help="group/slug of the figure module")
    args = parser.parse_args()

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    module = load(args.module)
    for note in shrink(module):
        print(f"  shrunk {note}")
    print()

    palette = DARK
    target = os.path.join(tempfile.mkdtemp(prefix="pch-smoke-"), "out.png")
    failures = []
    for spec in module.FIGURES:
        try:
            with plt.rc_context(_rc(palette)):
                plt.rcParams["axes.prop_cycle"] = plt.cycler(color=palette.cycle)
                fig = plt.figure(figsize=spec.size)
                ax = fig.add_subplot(111) if spec.axes else None
                spec.draw(fig, ax, palette)
                fig.tight_layout()
                fig.savefig(target, format="png", dpi=40)
                plt.close(fig)
            print(f"  ok    {spec.name}")
        except Exception as error:                      # noqa: BLE001
            failures.append(spec.name)
            print(f"  FAIL  {spec.name}: {type(error).__name__}: {error}")

    print()
    if failures:
        print(f"{len(failures)} of {len(module.FIGURES)} figure(s) failed: "
              f"{', '.join(failures)}")
        return 1
    print(f"all {len(module.FIGURES)} figure(s) drew (on tiny data — the numbers "
          f"mean nothing)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
