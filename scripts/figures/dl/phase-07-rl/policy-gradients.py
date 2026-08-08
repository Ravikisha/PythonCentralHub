"""Figures for *Policy Gradients (Intro)*.

REINFORCE optimises the policy directly, which removes the value function and
introduces a new problem in its place: the gradient estimate is extremely
noisy. This module measures that noise instead of describing it, and measures
what a baseline does to it.

``baseline``
    Learning curves with and without a baseline, over several seeds, plus the
    measured variance of the gradient estimate in each case.

``variance``
    Where the variance actually comes from -- return scale, episode length and
    batch size -- with the reduction each fix buys.

``reinforce-settings``
    Every configuration on one axis, with the episode budget each one spent,
    against the random baseline and the episode cap.
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
from _rl import CartPole, discounted_returns  # noqa: E402
from _style import Palette, figure  # noqa: E402

GAMMA = 0.99
BATCH_EPISODES = 16          # episodes per gradient step
UPDATES = 120
SEEDS = 3
LEARNING_RATE = 5e-3
BATCH_SIZES = (4, 16, 48)


def _policy(seed: int = 0):
    keras = tf().keras
    seed_everything(seed)
    model = keras.Sequential([
        keras.layers.Input((4,)),
        keras.layers.Dense(64, activation="relu"),
        keras.layers.Dense(2, activation="softmax"),
    ])
    model.compile(keras.optimizers.Adam(LEARNING_RATE))
    return model


def _act(model):
    """Compiled forward pass -- see the DQN page for why this matters."""
    tensorflow = tf()

    @tensorflow.function(reduce_retracing=True)
    def forward(batch):
        return model(batch, training=False)

    return lambda batch: np.array(forward(tensorflow.constant(batch)))


def _gradient_step(model):
    tensorflow = tf()
    optimizer = model.optimizer

    @tensorflow.function(reduce_retracing=True)
    def step(states, actions, weights):
        with tensorflow.GradientTape() as tape:
            probabilities = model(states, training=True)
            chosen = tensorflow.reduce_sum(
                probabilities * tensorflow.one_hot(actions, 2), axis=1)
            log_probability = tensorflow.math.log(chosen + 1e-8)
            # The REINFORCE objective: maximise log pi(a|s) * weight, so the
            # loss is its negative.
            loss = -tensorflow.reduce_mean(log_probability * weights)
        gradients = tape.gradient(loss, model.trainable_variables)
        optimizer.apply_gradients(zip(gradients, model.trainable_variables))
        flat = tensorflow.concat([tensorflow.reshape(g, [-1])
                                  for g in gradients], axis=0)
        return loss, tensorflow.norm(flat)

    return step


def _collect(env, act, rng, episodes: int) -> dict:
    """Run whole episodes -- REINFORCE needs complete returns -- in parallel.

    All `episodes` run simultaneously in one vectorised environment, so a batch
    costs one model call per timestep instead of one per timestep per episode.
    Running them serially measured at roughly 16x this cost for a batch of 16.
    """
    env.reset()
    alive = np.ones(episodes, dtype=bool)
    states = [[] for _ in range(episodes)]
    actions = [[] for _ in range(episodes)]
    rewards = [[] for _ in range(episodes)]
    for _ in range(CartPole.MAX_STEPS):
        state = env.state.copy()
        probabilities = act(state)
        chosen = (rng.random(episodes) < probabilities[:, 1]).astype("int32")
        _, reward, done = env.step(chosen)
        for index in np.flatnonzero(alive):
            states[index].append(state[index])
            actions[index].append(int(chosen[index]))
            rewards[index].append(float(reward[index]))
        alive &= ~done
        if not alive.any():
            break
    flat_states, flat_actions, weights, lengths = [], [], [], []
    for index in range(episodes):
        if not rewards[index]:
            continue
        returns = discounted_returns(rewards[index], GAMMA)
        flat_states.extend(states[index])
        flat_actions.extend(actions[index])
        weights.extend(returns.tolist())
        lengths.append(len(rewards[index]))
    return {"states": np.array(flat_states, "float32"),
            "actions": np.array(flat_actions, "int32"),
            "weights": np.array(weights, "float32"),
            "lengths": lengths}


def _train(baseline: bool, seed: int = 0, episodes: int = None,
           updates: int = None) -> dict:
    episodes = BATCH_EPISODES if episodes is None else int(episodes)
    updates = UPDATES if updates is None else int(updates)
    model = _policy(seed)
    act = _act(model)
    step = _gradient_step(model)
    env = CartPole(count=episodes, seed=seed)
    rng = np.random.default_rng(seed + 99)
    curve = []
    norms = []
    started = time.perf_counter()
    for update in range(1, updates + 1):
        batch = _collect(env, act, rng, episodes)
        weights = batch["weights"]
        if baseline:
            # Subtract the mean return and scale: the classic variance
            # reduction. It does not change the gradient in expectation.
            weights = (weights - weights.mean()) / (weights.std() + 1e-8)
        _, norm = step(batch["states"], batch["actions"], weights)
        norms.append(float(norm))
        curve.append({"update": update,
                      "length": float(np.mean(batch["lengths"])),
                      "episodes": update * episodes})
    recent = [point["length"] for point in curve[-10:]]
    return {"curve": curve, "final": float(np.mean(recent)),
            "gradient_norm": float(np.mean(norms)),
            "norm_sd": float(np.std(norms)),
            "seconds": time.perf_counter() - started,
            "total_episodes": updates * episodes}


@functools.lru_cache(maxsize=1)
def _baseline_runs() -> dict:
    out = {}
    for label, baseline in (("no baseline", False), ("with baseline", True)):
        runs = [_train(baseline, seed) for seed in range(SEEDS)]
        finals = [run["final"] for run in runs]
        out[label] = {
            "curves": [run["curve"] for run in runs],
            "mean": float(np.mean(finals)),
            "sd": float(np.std(finals)),
            "best": float(np.max(finals)),
            "worst": float(np.min(finals)),
            "gradient_norm": float(np.mean([r["gradient_norm"]
                                            for r in runs])),
            "norm_sd": float(np.mean([r["norm_sd"] for r in runs])),
            "seconds": float(np.mean([r["seconds"] for r in runs])),
            "episodes": runs[0]["total_episodes"],
        }
    return out


@functools.lru_cache(maxsize=1)
def _batch_runs() -> dict:
    """Batch size against the noise in the gradient estimate."""
    out = {}
    for size in BATCH_SIZES:
        # Hold the episode budget roughly constant across batch sizes.
        updates = max(4, int(UPDATES * BATCH_EPISODES / size))
        run = _train(True, seed=0, episodes=size, updates=updates)
        out[size] = {"final": run["final"],
                     "gradient_norm": run["gradient_norm"],
                     "norm_sd": run["norm_sd"],
                     "updates": updates,
                     "episodes": run["total_episodes"],
                     "seconds": run["seconds"]}
    return out


@functools.lru_cache(maxsize=1)
def _return_scale() -> dict:
    """What the weights look like before and after the baseline."""
    model = _policy(0)
    act = _act(model)
    env = CartPole(count=BATCH_EPISODES, seed=0)
    rng = np.random.default_rng(1)
    batch = _collect(env, act, rng, BATCH_EPISODES)
    raw = batch["weights"]
    centred = (raw - raw.mean()) / (raw.std() + 1e-8)
    return {"raw": raw, "centred": centred,
            "raw_mean": float(raw.mean()), "raw_sd": float(raw.std()),
            "centred_mean": float(centred.mean()),
            "centred_sd": float(centred.std()),
            "positive_share": float((raw > 0).mean()),
            "centred_positive": float((centred > 0).mean())}


@functools.lru_cache(maxsize=1)
def _random_baseline() -> dict:
    env = CartPole(count=200, seed=7)
    running = np.zeros(200)
    alive = np.ones(200, bool)
    rng = np.random.default_rng(7)
    for _ in range(CartPole.MAX_STEPS):
        _, _, done = env.step(rng.integers(0, 2, 200))
        running += alive
        alive &= ~done
        if not alive.any():
            break
    return {"mean": float(running.mean())}


def baseline(fig, axes, p: Palette) -> None:
    runs = _baseline_runs()
    random = _random_baseline()
    left, right = fig.subplots(1, 2, width_ratios=(1.15, 1.0))
    for (label, entry), color in zip(runs.items(), (p.red, p.green)):
        for index, curve in enumerate(entry["curves"]):
            episodes = [point["episodes"] for point in curve]
            lengths = [point["length"] for point in curve]
            left.plot(episodes, lengths, lw=1.6, color=color,
                      alpha=0.9 if index == 0 else 0.35,
                      label=label if index == 0 else None)
    left.axhline(random["mean"], color=p.muted, lw=1.2, ls=":",
                 label=f"random ({random['mean']:.2f})")
    left.axhline(CartPole.MAX_STEPS, color=p.muted, lw=1.0, ls="--")
    left.set_xlabel("episodes of experience")
    left.set_ylabel("mean episode length")
    left.set_title(f"REINFORCE on CartPole, {SEEDS} seeds each", fontsize=10)
    left.legend(fontsize=8, loc="upper left")

    labels = list(runs)
    positions = np.arange(len(labels))
    finals = [runs[label]["mean"] for label in labels]
    spread = [runs[label]["sd"] for label in labels]
    right.bar(positions - 0.2, finals, 0.38, yerr=spread, color=p.blue,
              error_kw={"ecolor": p.muted, "capsize": 3},
              label="final episode length")
    norms = [runs[label]["gradient_norm"] for label in labels]
    scale = max(finals) / max(norms) if max(norms) else 1.0
    right.bar(positions + 0.2, [n * scale for n in norms], 0.38, color=p.amber,
              label="mean gradient norm (scaled)")
    for x, value in zip(positions - 0.2, finals):
        right.annotate(f"{value:.1f}", (x, value), xytext=(0, 4),
                       textcoords="offset points", ha="center", fontsize=8,
                       color=p.fg)
    for x, value in zip(positions + 0.2, norms):
        right.annotate(f"{value:.3f}", (x, value * scale), xytext=(0, 4),
                       textcoords="offset points", ha="center", fontsize=8,
                       color=p.fg)
    right.set_xticks(positions)
    right.set_xticklabels(labels)
    right.set_title("the baseline changes the gradient, not the objective",
                    fontsize=10)
    right.legend(fontsize=7.5, loc="upper left")


def variance(fig, axes, p: Palette) -> None:
    scale = _return_scale()
    batches = _batch_runs()
    left, right = fig.subplots(1, 2)
    left.hist(scale["raw"], bins=40, alpha=0.75, color=p.red,
              label=f"raw returns (mean {scale['raw_mean']:.2f}, "
                    f"sd {scale['raw_sd']:.2f})")
    twin = left.twiny()
    twin.hist(scale["centred"], bins=40, alpha=0.6, color=p.green,
              label=f"after the baseline (mean {scale['centred_mean']:.2f}, "
                    f"sd {scale['centred_sd']:.2f})")
    twin.set_xlabel("standardised weight", color=p.green)
    left.set_xlabel("raw discounted return", color=p.red)
    left.set_ylabel("state-action pairs")
    left.set_title(f"every raw weight is positive "
                   f"({scale['positive_share']:.0%}), so every action is "
                   f"reinforced", fontsize=9.5)
    handles = left.get_legend_handles_labels()[0] + \
        twin.get_legend_handles_labels()[0]
    labels = left.get_legend_handles_labels()[1] + \
        twin.get_legend_handles_labels()[1]
    left.legend(handles, labels, fontsize=7, loc="upper right")

    sizes = list(batches)
    norms = [batches[size]["gradient_norm"] for size in sizes]
    sds = [batches[size]["norm_sd"] for size in sizes]
    right.errorbar(sizes, norms, yerr=sds, fmt="o-", ms=7, lw=2.0, capsize=4,
                   color=p.blue, label="gradient norm (mean ± sd)")
    for size, value in zip(sizes, norms):
        right.annotate(f"{value:.3f}", (size, value), xytext=(0, 10),
                       textcoords="offset points", ha="center", fontsize=7.5,
                       color=p.blue)
    twin2 = right.twinx()
    twin2.plot(sizes, [batches[size]["final"] for size in sizes], "s--", ms=6,
               lw=1.8, color=p.green, label="final episode length")
    twin2.set_ylabel("final episode length")
    right.set_xlabel("episodes per gradient step")
    right.set_ylabel("gradient norm")
    right.set_title("a bigger batch is a less noisy estimate", fontsize=9.5)
    lines = right.get_lines() + twin2.get_lines()
    right.legend(lines, [line.get_label() for line in lines], fontsize=7.5,
                 loc="upper center")


def settings(fig, axes, p: Palette) -> None:
    runs = _baseline_runs()
    batches = _batch_runs()
    random = _random_baseline()
    entry = runs["with baseline"]
    rows = [("REINFORCE, no baseline", runs["no baseline"]["mean"],
             runs["no baseline"]["sd"], runs["no baseline"]["episodes"],
             runs["no baseline"]["seconds"]),
            ("REINFORCE, with baseline", entry["mean"], entry["sd"],
             entry["episodes"], entry["seconds"])]
    for size in batches:
        rows.append((f"REINFORCE, batch {size}", batches[size]["final"], 0.0,
                     batches[size]["episodes"], batches[size]["seconds"]))
    labels = [row[0] for row in rows]
    positions = np.arange(len(rows))
    values = [row[1] for row in rows]
    errors = [row[2] for row in rows]
    axes.barh(positions, values, 0.55, xerr=errors, color=p.blue,
              error_kw={"ecolor": p.muted, "capsize": 3})
    for y, row in zip(positions, rows):
        axes.annotate(f"{row[1]:.1f}   ({row[3]} episodes, {row[4]:.0f}s)",
                      (row[1] + row[2], y), xytext=(6, 0),
                      textcoords="offset points", va="center", fontsize=7.5,
                      color=p.fg)
    axes.axvline(random["mean"], color=p.muted, lw=1.2, ls=":")
    axes.annotate(f"random {random['mean']:.1f}", (random["mean"], -0.7),
                  xytext=(4, 0), textcoords="offset points", fontsize=7.5,
                  color=p.muted)
    axes.axvline(CartPole.MAX_STEPS, color=p.green, lw=1.0, ls="--")
    axes.annotate(f"cap {CartPole.MAX_STEPS}", (CartPole.MAX_STEPS, -0.7),
                  xytext=(-46, 0), textcoords="offset points", fontsize=7.5,
                  color=p.green)
    axes.set_yticks(positions)
    axes.set_yticklabels(labels, fontsize=8.5)
    axes.invert_yaxis()
    axes.set_xlim(0, CartPole.MAX_STEPS * 1.12)
    axes.set_xlabel("final mean episode length")
    axes.set_title("every REINFORCE setting, on the same axis", fontsize=10)


FIGURES = [
    figure("baseline", baseline, size=(9.6, 3.6), axes=False),
    figure("variance", variance, size=(9.6, 3.7), axes=False),
    figure("reinforce-settings", settings, size=(8.6, 3.4)),
]


if __name__ == "__main__":
    random = _random_baseline()
    print("=== REINFORCE on CartPole ===")
    print(f"random policy: mean episode length {random['mean']:.2f}, "
          f"cap {CartPole.MAX_STEPS}")

    scale = _return_scale()
    print(f"\n=== the weights, before and after a baseline ===")
    print(f"raw discounted returns: mean {scale['raw_mean']:.4f}, "
          f"sd {scale['raw_sd']:.4f}, "
          f"{scale['positive_share']:.1%} positive")
    print(f"after standardising:    mean {scale['centred_mean']:.4f}, "
          f"sd {scale['centred_sd']:.4f}, "
          f"{scale['centred_positive']:.1%} positive")
    print("with every weight positive, every action taken is made MORE likely")
    print("and the only thing separating good from bad is how much -- which is")
    print("what makes the raw estimator so noisy")

    print(f"\n=== with and without a baseline ({SEEDS} seeds, "
          f"{UPDATES} updates of {BATCH_EPISODES} episodes) ===")
    print(f"{'setting':18s} {'final length':>13} {'sd':>7} {'worst':>7} "
          f"{'best':>7} {'grad norm':>10} {'seconds':>9}")
    for label, entry in _baseline_runs().items():
        print(f"{label:18s} {entry['mean']:13.2f} {entry['sd']:7.2f} "
              f"{entry['worst']:7.2f} {entry['best']:7.2f} "
              f"{entry['gradient_norm']:10.4f} {entry['seconds']:9.0f}")

    print(f"\n=== batch size (episode budget held roughly constant) ===")
    print(f"{'episodes/step':>14} {'updates':>8} {'total episodes':>15} "
          f"{'final length':>13} {'grad norm':>10} {'norm sd':>9}")
    for size, entry in _batch_runs().items():
        print(f"{size:14d} {entry['updates']:8d} {entry['episodes']:15d} "
              f"{entry['final']:13.2f} {entry['gradient_norm']:10.4f} "
              f"{entry['norm_sd']:9.4f}")
    print("a bigger batch averages more episodes into one gradient, so the")
    print("estimate is less noisy -- at the cost of fewer updates for the")
    print("same amount of experience")
