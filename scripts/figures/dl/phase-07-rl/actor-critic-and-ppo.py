"""Figures for *Actor-Critic and PPO*.

REINFORCE works and is unusably noisy. This module measures the two standard
fixes on the same CartPole, the same seeds and the same episode budget: a
learned critic in place of a batch-mean baseline, and a clipped objective that
makes it safe to take several gradient steps on one batch of experience.

``learning-curves``
    Mean episode length against update number for four methods, averaged over
    seeds with a spread band.

``sample-efficiency``
    Episodes of environment interaction spent to first reach a target length,
    and the wall clock each method paid for it.

``clipping``
    Where the clip starts to matter. At four gradient steps per batch the
    policy barely drifts and removing the clip costs nothing measurable; the
    figure sweeps the number of steps until it does, which is the honest
    version of "PPO clips for stability".
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
BATCH_EPISODES = 16
UPDATES = 120
SEEDS = 3
LEARNING_RATE = 5e-3
CRITIC_RATE = 1e-2
PPO_EPOCHS = 4
EPOCH_SWEEP = (1, 4, 16, 32)
CLIP = 0.2
TARGET_LENGTH = 150

METHODS = ("reinforce", "whitened", "actor-critic", "ppo")
LABELS = {
    "reinforce": "REINFORCE (raw returns)",
    "whitened": "+ batch-mean baseline",
    "actor-critic": "+ learned critic",
    "ppo": "PPO (clipped, 4 epochs per batch)",
}


def _networks(seed: int):
    keras = tf().keras
    seed_everything(seed)
    actor = keras.Sequential([
        keras.layers.Input((4,)),
        keras.layers.Dense(64, activation="relu"),
        keras.layers.Dense(2, activation="softmax"),
    ])
    actor.compile(keras.optimizers.Adam(LEARNING_RATE))
    critic = keras.Sequential([
        keras.layers.Input((4,)),
        keras.layers.Dense(64, activation="relu"),
        keras.layers.Dense(1),
    ])
    critic.compile(keras.optimizers.Adam(CRITIC_RATE))
    return actor, critic


def _act(model):
    """Traced forward pass. `predict` in a loop costs roughly 400x this."""
    tensorflow = tf()

    @tensorflow.function(reduce_retracing=True)
    def forward(batch):
        return model(batch, training=False)

    return lambda batch: np.array(forward(tensorflow.constant(batch)))


def _policy_step(actor):
    tensorflow = tf()
    optimizer = actor.optimizer

    @tensorflow.function(reduce_retracing=True)
    def step(states, actions, weights):
        with tensorflow.GradientTape() as tape:
            probabilities = actor(states, training=True)
            chosen = tensorflow.reduce_sum(
                probabilities * tensorflow.one_hot(actions, 2), axis=1)
            loss = -tensorflow.reduce_mean(
                tensorflow.math.log(chosen + 1e-8) * weights)
        gradients = tape.gradient(loss, actor.trainable_variables)
        optimizer.apply_gradients(zip(gradients, actor.trainable_variables))
        return loss

    return step


def _ppo_step(actor, clip: float, epochs: int = PPO_EPOCHS):
    """One clipped update. `clip` of zero means no clipping at all."""
    tensorflow = tf()
    optimizer = actor.optimizer

    @tensorflow.function(reduce_retracing=True)
    def step(states, actions, advantages, old_log):
        with tensorflow.GradientTape() as tape:
            probabilities = actor(states, training=True)
            chosen = tensorflow.reduce_sum(
                probabilities * tensorflow.one_hot(actions, 2), axis=1)
            log_probability = tensorflow.math.log(chosen + 1e-8)
            ratio = tensorflow.exp(log_probability - old_log)
            if clip > 0:
                clipped = tensorflow.clip_by_value(ratio, 1 - clip, 1 + clip)
                loss = -tensorflow.reduce_mean(
                    tensorflow.minimum(ratio * advantages,
                                       clipped * advantages))
            else:
                loss = -tensorflow.reduce_mean(ratio * advantages)
        gradients = tape.gradient(loss, actor.trainable_variables)
        optimizer.apply_gradients(zip(gradients, actor.trainable_variables))
        outside = tensorflow.reduce_mean(tensorflow.cast(
            tensorflow.abs(ratio - 1.0) > clip if clip > 0
            else tensorflow.abs(ratio - 1.0) > CLIP, "float32"))
        return loss, outside

    return step


def _critic_step(critic):
    tensorflow = tf()
    optimizer = critic.optimizer

    @tensorflow.function(reduce_retracing=True)
    def step(states, returns):
        with tensorflow.GradientTape() as tape:
            predicted = critic(states, training=True)[:, 0]
            loss = tensorflow.reduce_mean((predicted - returns) ** 2)
        gradients = tape.gradient(loss, critic.trainable_variables)
        optimizer.apply_gradients(zip(gradients, critic.trainable_variables))
        return loss

    return step


def _collect(env, act, rng, episodes: int) -> dict:
    """Run `episodes` complete episodes at once in the vectorised world."""
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
    flat_states, flat_actions, returns, lengths = [], [], [], []
    for index in range(episodes):
        if not rewards[index]:
            continue
        flat_states.extend(states[index])
        flat_actions.extend(actions[index])
        returns.extend(discounted_returns(rewards[index], GAMMA).tolist())
        lengths.append(len(rewards[index]))
    return {"states": np.array(flat_states, "float32"),
            "actions": np.array(flat_actions, "int32"),
            "returns": np.array(returns, "float32"),
            "lengths": lengths}


def _log_probability(actor, states, actions):
    probabilities = actor(states, training=False).numpy()
    chosen = probabilities[np.arange(len(actions)), actions]
    return np.log(chosen + 1e-8).astype("float32")


def _train(method: str, seed: int, updates: int = None,
           clip: float = CLIP, epochs: int = PPO_EPOCHS) -> dict:
    updates = UPDATES if updates is None else int(updates)
    actor, critic = _networks(seed)
    act = _act(actor)
    policy_step = _policy_step(actor)
    critic_step = _critic_step(critic)
    ppo_step = _ppo_step(actor, clip) if method == "ppo" else None
    env = CartPole(count=BATCH_EPISODES, seed=seed)
    rng = np.random.default_rng(seed + 99)

    curve, episodes_used, clipped_share = [], 0, []
    started = time.perf_counter()
    reached = None
    for update in range(1, updates + 1):
        batch = _collect(env, act, rng, BATCH_EPISODES)
        episodes_used += len(batch["lengths"])
        mean_length = float(np.mean(batch["lengths"]))
        curve.append(mean_length)
        if reached is None and mean_length >= TARGET_LENGTH:
            reached = episodes_used

        returns = batch["returns"]
        if method == "reinforce":
            policy_step(batch["states"], batch["actions"], returns)
        elif method == "whitened":
            weights = (returns - returns.mean()) / (returns.std() + 1e-8)
            policy_step(batch["states"], batch["actions"], weights)
        else:
            baseline = critic(batch["states"], training=False).numpy()[:, 0]
            advantages = returns - baseline
            advantages = ((advantages - advantages.mean())
                          / (advantages.std() + 1e-8)).astype("float32")
            if method == "actor-critic":
                policy_step(batch["states"], batch["actions"], advantages)
            else:
                old_log = _log_probability(actor, batch["states"],
                                           batch["actions"])
                for _ in range(epochs):
                    _, outside = ppo_step(batch["states"], batch["actions"],
                                          advantages, old_log)
                    clipped_share.append(float(outside))
            critic_step(batch["states"], returns)

    return {"curve": curve, "seconds": time.perf_counter() - started,
            "episodes": episodes_used, "reached": reached,
            "final": float(np.mean(curve[-10:])),
            "clipped": clipped_share}


@functools.lru_cache(maxsize=1)
def _runs() -> dict:
    out = {}
    for method in METHODS:
        seeds = [_train(method, seed) for seed in range(SEEDS)]
        curves = np.array([run["curve"] for run in seeds])
        reached = [run["reached"] for run in seeds if run["reached"]]
        out[method] = {
            "mean": curves.mean(axis=0),
            "low": curves.min(axis=0),
            "high": curves.max(axis=0),
            "final": float(np.mean([run["final"] for run in seeds])),
            "seconds": float(np.mean([run["seconds"] for run in seeds])),
            "episodes": int(np.mean([run["episodes"] for run in seeds])),
            "reached": int(np.mean(reached)) if reached else None,
            "solved": len(reached),
            "clipped": seeds[0]["clipped"],
        }
    return out


@functools.lru_cache(maxsize=1)
def _clip_study() -> dict:
    """How many gradient steps can one batch of experience support?

    The original version of this figure compared clip against no-clip at four
    epochs and found nothing: 199.9 against 199.4. That is a real result, and
    the reason is in the drift numbers -- at four epochs only 6.6% of samples
    leave the trust region even unclipped, so there is nothing for the clip to
    bound. The sweep below raises the reuse until there is.
    """
    rows = []
    for epochs in EPOCH_SWEEP:
        entry = {"epochs": epochs}
        for label, clip in (("clipped", CLIP), ("unclipped", 0.0)):
            runs = [_train("ppo", seed, clip=clip, epochs=epochs)
                    for seed in range(SEEDS)]
            entry[label] = {
                "final": float(np.mean([run["final"] for run in runs])),
                "worst": float(min(run["final"] for run in runs)),
                "drift": float(np.mean(runs[0]["clipped"][-epochs:])),
            }
        rows.append(entry)
    return {"rows": rows}


def learning_curves(fig, axes, p: Palette) -> None:
    runs = _runs()
    ax = fig.subplots(1, 1)
    colours = {"reinforce": p.muted, "whitened": p.amber,
               "actor-critic": p.blue, "ppo": p.green}
    for method in METHODS:
        info = runs[method]
        x = np.arange(1, len(info["mean"]) + 1)
        ax.plot(x, info["mean"], color=colours[method], lw=1.7,
                label=f"{LABELS[method]} (final {info['final']:.0f})")
        ax.fill_between(x, info["low"], info["high"], color=colours[method],
                        alpha=0.12)
    ax.axhline(TARGET_LENGTH, color=p.fg, lw=1.0, ls=":")
    ax.annotate(f"target {TARGET_LENGTH}", (1, TARGET_LENGTH),
                xytext=(2, 4), textcoords="offset points", fontsize=7.5,
                color=p.fg)
    ax.set_xlabel(f"update ({BATCH_EPISODES} episodes each)")
    ax.set_ylabel("mean episode length")
    ax.set_title(f"CartPole, {SEEDS} seeds, band is min to max", fontsize=10)
    ax.legend(fontsize=7.5, loc="upper left")


def sample_efficiency(fig, axes, p: Palette) -> None:
    runs = _runs()
    left, right = fig.subplots(1, 2)
    positions = np.arange(len(METHODS))
    colours = [p.muted, p.amber, p.blue, p.green]

    reached = [runs[method]["reached"] or 0 for method in METHODS]
    left.bar(positions, reached, color=colours, width=0.6)
    for position, method, value in zip(positions, METHODS, reached):
        text = f"{value:,}" if value else "never"
        left.annotate(text, (position, value), xytext=(0, 3),
                      textcoords="offset points", ha="center", fontsize=8,
                      color=p.fg)
    left.set_xticks(positions)
    left.set_xticklabels([LABELS[m].split(" (")[0] for m in METHODS],
                         fontsize=7, rotation=12)
    left.set_ylabel(f"episodes to first reach length {TARGET_LENGTH}")
    left.set_title(f"{SEEDS} seeds, mean of those that got there",
                   fontsize=10)

    seconds = [runs[method]["seconds"] for method in METHODS]
    right.bar(positions, seconds, color=colours, width=0.6)
    for position, value in zip(positions, seconds):
        right.annotate(f"{value:.0f}s", (position, value), xytext=(0, 3),
                       textcoords="offset points", ha="center", fontsize=8,
                       color=p.fg)
    right.set_xticks(positions)
    right.set_xticklabels([LABELS[m].split(" (")[0] for m in METHODS],
                          fontsize=7, rotation=12)
    right.set_ylabel(f"seconds for {UPDATES} updates")
    right.set_title("what the extra machinery costs", fontsize=10)


def clipping(fig, axes, p: Palette) -> None:
    rows = _clip_study()["rows"]
    left, right = fig.subplots(1, 2)
    positions = np.arange(len(rows))
    width = 0.36
    clipped = [row["clipped"]["final"] for row in rows]
    unclipped = [row["unclipped"]["final"] for row in rows]
    left.bar(positions - width / 2, clipped, width * 0.92, color=p.green,
             label=f"clip {CLIP}")
    left.bar(positions + width / 2, unclipped, width * 0.92, color=p.red,
             label="no clip")
    for position, value in zip(positions - width / 2, clipped):
        left.annotate(f"{value:.0f}", (position, value), xytext=(0, 3),
                      textcoords="offset points", ha="center", fontsize=7.5,
                      color=p.fg)
    for position, value in zip(positions + width / 2, unclipped):
        left.annotate(f"{value:.0f}", (position, value), xytext=(0, 3),
                      textcoords="offset points", ha="center", fontsize=7.5,
                      color=p.fg)
    left.set_xticks(positions)
    left.set_xticklabels([f"{row['epochs']}" for row in rows])
    left.set_xlabel("gradient steps taken on one batch")
    left.set_ylabel("mean episode length, last 10 updates")
    left.set_title(f"{SEEDS} seeds each, same episode budget", fontsize=10)
    left.legend(fontsize=8, loc="lower left")

    worst_clipped = [row["clipped"]["worst"] for row in rows]
    worst_unclipped = [row["unclipped"]["worst"] for row in rows]
    steps = [row["epochs"] for row in rows]
    right.plot(steps, clipped, "o-", color=p.green, lw=1.8, ms=5,
               label=f"clip {CLIP}, mean")
    right.plot(steps, worst_clipped, "o--", color=p.green, lw=1.2, ms=4,
               alpha=0.65, label=f"clip {CLIP}, worst seed")
    right.plot(steps, unclipped, "o-", color=p.red, lw=1.8, ms=5,
               label="no clip, mean")
    right.plot(steps, worst_unclipped, "o--", color=p.red, lw=1.2, ms=4,
               alpha=0.65, label="no clip, worst seed")
    for step, value in zip(steps, worst_unclipped):
        right.annotate(f"{value:.1f}", (step, value), xytext=(0, -12),
                       textcoords="offset points", ha="center", fontsize=7.5,
                       color=p.red)
    right.axhline(23.09, color=p.fg, lw=1.0, ls=":")
    right.annotate("random policy 23.09", (steps[0], 23.09), xytext=(2, 4),
                   textcoords="offset points", fontsize=7.5, color=p.fg)
    right.set_xscale("log", base=2)
    right.set_xticks(steps)
    right.set_xticklabels([str(step) for step in steps])
    right.set_xlabel("gradient steps taken on one batch")
    right.set_ylabel("mean episode length, last 10 updates")
    right.set_title("the clip bounds the worst case, not the average",
                    fontsize=10)
    right.legend(fontsize=7, loc="lower left")


FIGURES = [
    figure("learning-curves", learning_curves, size=(8.6, 4.4), axes=False),
    figure("sample-efficiency", sample_efficiency, size=(9.0, 4.4),
           axes=False),
    figure("clipping", clipping, size=(9.2, 4.4), axes=False),
]


if __name__ == "__main__":
    runs = _runs()
    print("=== four methods, CartPole ===")
    print(f"{'method':34s} {'final':>8} {'episodes':>10} {'to target':>11} "
          f"{'solved':>8} {'seconds':>9}")
    for method in METHODS:
        info = runs[method]
        target = f"{info['reached']:,}" if info["reached"] else "never"
        print(f"{LABELS[method]:34s} {info['final']:8.1f} "
              f"{info['episodes']:10,} {target:>11} "
              f"{info['solved']}/{SEEDS:<6} {info['seconds']:9.1f}")

    study = _clip_study()["rows"]
    print("\n=== how much reuse can one batch support? ===")
    print(f"{'steps':>6} {'clipped':>9} {'worst':>8} {'unclipped':>11} "
          f"{'worst':>8} {'drift':>8}")
    for row in study:
        print(f"{row['epochs']:6d} {row['clipped']['final']:9.1f} "
              f"{row['clipped']['worst']:8.1f} "
              f"{row['unclipped']['final']:11.1f} "
              f"{row['unclipped']['worst']:8.1f} "
              f"{row['unclipped']['drift']:8.4f}")
    print("\nthe first gradient step is always inside the trust region -- the")
    print("ratio starts at exactly 1. Every later step reuses data collected")
    print("under a policy that no longer exists, and the drift column is how")
    print("far gone that policy is by the end of the batch")
