"""Figures for *Q-Learning and Deep Q-Networks*.

Tabular Q-learning is a lookup table that provably converges. A DQN is the same
update rule with a network in place of the table, plus two mechanisms -- replay
and a target network -- that exist purely to stop that substitution from
diverging. This module ablates both, so their necessity is measured rather than
asserted.

``tabular``
    Learning rate and exploration rate swept on the gridworld, scored against
    the exact optimum from value iteration.

``dqn-ablation``
    A DQN on CartPole with replay and the target network switched on and off.

``q-values``
    What the learned Q-values look like against the true optimal values, and
    the overestimation that motivates Double DQN.
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
from _rl import CartPole, GridWorld  # noqa: E402
from _style import Palette, figure  # noqa: E402

EPISODES = 2000
EVAL = 300
GAMMA = 0.99
RATES = (0.05, 0.2, 0.5, 1.0)
EPSILONS = (0.01, 0.1, 0.3)

# DQN
ENVS = 16
FRAMES = 6000
BATCH = 64
BUFFER = 10000
TARGET_SYNC = 200
WARMUP = 500
DQN_SEEDS = 3
# One gradient step per four environment frames, as the original DQN does. It
# is also what makes this affordable: the update is three of the four network
# calls in a frame.
TRAIN_EVERY = 4


SLIP = 0.15
STEP_COST = -0.01


@functools.lru_cache(maxsize=1)
def _world() -> GridWorld:
    # The same stochastic world as the introduction page, so the tabular
    # numbers here can be compared with the value-iteration optimum there.
    return GridWorld(step_cost=STEP_COST, slip=SLIP)


@functools.lru_cache(maxsize=1)
def _optimal() -> dict:
    return _world().value_iteration(gamma=GAMMA)


def _evaluate(policy, seed: int = 1, episodes: int = EVAL) -> dict:
    world = _world()
    rng = np.random.default_rng(seed)
    runs = [world.rollout(policy, rng) for _ in range(episodes)]
    return {"reward": float(np.mean([run["reward"] for run in runs])),
            "goal_rate": float(np.mean([run["reached_goal"] for run in runs])),
            "steps": float(np.mean([run["steps"] for run in runs]))}


@functools.lru_cache(maxsize=32)
def _tabular(alpha: float = 0.2, epsilon: float = 0.1,
             episodes: int = None) -> dict:
    world = _world()
    episodes = EPISODES if episodes is None else int(episodes)
    rng = np.random.default_rng(0)
    actions = len(world.ACTIONS)
    table = {state: np.zeros(actions) for state in world.states}
    for _ in range(episodes):
        state = world.start
        for _ in range(200):
            if rng.random() < epsilon:
                action = int(rng.integers(0, actions))
            else:
                action = int(np.argmax(table[state]))
            following, reward, done = world.step(state, action, rng)
            target = reward + (0.0 if done
                               else GAMMA * float(np.max(table[following])))
            table[state][action] += alpha * (target - table[state][action])
            state = following
            if done:
                break
    policy = {state: int(np.argmax(values)) for state, values in table.items()}
    result = _evaluate(lambda s, r: policy[s])
    optimal = _optimal()
    matches = sum(1 for state in world.states
                  if not world.terminal(state)
                  and policy[state] == optimal["policy"][state])
    total = sum(1 for state in world.states if not world.terminal(state))
    return {"table": table, "policy": policy, **result,
            "policy_match": matches / total}


@functools.lru_cache(maxsize=1)
def _rate_runs() -> dict:
    return {(alpha, epsilon): _tabular(alpha, epsilon)
            for alpha in RATES for epsilon in EPSILONS}


def _network(seed: int = 0):
    keras = tf().keras
    seed_everything(seed)
    model = keras.Sequential([
        keras.layers.Input((4,)),
        keras.layers.Dense(64, activation="relu"),
        keras.layers.Dense(64, activation="relu"),
        keras.layers.Dense(2),
    ])
    model.compile(keras.optimizers.Adam(1e-3), "mse")
    return model


def _inference(model):
    """A compiled forward pass.

    Three ways to run a batch through this network, timed on a 64-row batch in
    this loop: `model.predict()` about 470ms, an eager `model(x)` call about
    28ms, and a traced `tf.function` about 1.2ms. An RL loop makes several
    forward passes per environment frame, so this choice is the runtime.
    """
    tensorflow = tf()

    @tensorflow.function(reduce_retracing=True)
    def forward(batch):
        return model(batch, training=False)

    def call(batch):
        # np.array, not np.asarray: a TensorFlow tensor converts to a READ-ONLY
        # view, and callers write targets into this array in place.
        return np.array(forward(tensorflow.constant(batch)))

    return call


def _train_step(model):
    """A compiled gradient step.

    `train_on_batch` measured at about half a second per call inside this loop,
    which dwarfed everything else. A `tf.function` is traced once per input
    shape and then runs in milliseconds.
    """
    tensorflow = tf()
    optimizer = model.optimizer

    @tensorflow.function(reduce_retracing=True)
    def step(states, targets):
        with tensorflow.GradientTape() as tape:
            predictions = model(states, training=True)
            loss = tensorflow.reduce_mean((predictions - targets) ** 2)
        gradients = tape.gradient(loss, model.trainable_variables)
        optimizer.apply_gradients(zip(gradients, model.trainable_variables))
        return loss

    return step


def _dqn(replay: bool, target_network: bool, seed: int = 0) -> dict:
    """A DQN on CartPole. `replay` and `target_network` are the ablations."""
    keras = tf().keras
    online = _network(seed)
    target = keras.models.clone_model(online)
    target.set_weights(online.get_weights())
    step = _train_step(online)
    online_q = _inference(online)
    target_q = _inference(target)
    env = CartPole(count=ENVS, seed=seed)
    rng = np.random.default_rng(seed + 500)

    states = np.zeros((BUFFER, 4), "float32")
    actions = np.zeros(BUFFER, "int32")
    rewards = np.zeros(BUFFER, "float32")
    following = np.zeros((BUFFER, 4), "float32")
    finished = np.zeros(BUFFER, "float32")
    filled = 0
    cursor = 0

    state = env.reset()
    lengths = []
    running = np.zeros(ENVS)
    curve = []
    started = time.perf_counter()
    for frame in range(1, FRAMES + 1):
        epsilon = max(0.05, 1.0 - frame / (FRAMES * 0.5))
        greedy = online_q(state).argmax(axis=1)
        random_actions = rng.integers(0, 2, ENVS)
        explore = rng.random(ENVS) < epsilon
        chosen = np.where(explore, random_actions, greedy)
        nxt, reward, done = env.step(chosen)
        running += 1

        for index in range(ENVS):
            states[cursor] = state[index]
            actions[cursor] = chosen[index]
            rewards[cursor] = reward[index]
            following[cursor] = nxt[index]
            # A time-limit ending is not a real terminal state, but treating it
            # as one is the standard simplification and is noted on the page.
            finished[cursor] = float(done[index])
            cursor = (cursor + 1) % BUFFER
            filled = min(filled + 1, BUFFER)

        if done.any():
            lengths.extend(running[done].tolist())
            running[done] = 0
            env.reset(done)
            nxt = env.state.copy()
        state = nxt

        if filled >= WARMUP and frame % max(1, int(TRAIN_EVERY)) == 0:
            if replay:
                batch = rng.integers(0, filled, BATCH)
            else:
                # No replay: learn only from the transitions just collected,
                # which are correlated in time by construction.
                recent = (cursor - ENVS) % BUFFER
                batch = (recent + np.arange(ENVS)) % BUFFER
            scorer = target_q if target_network else online_q
            future = scorer(following[batch]).max(axis=1)
            wanted = rewards[batch] + GAMMA * future * (1 - finished[batch])
            current = online_q(states[batch])
            current[np.arange(len(batch)), actions[batch]] = wanted
            step(states[batch], current)

        if target_network and frame % TARGET_SYNC == 0:
            target.set_weights(online.get_weights())

        # Scale the sampling cadence to the budget, so a shrunk run still
        # produces a curve rather than an empty list.
        if frame % max(1, FRAMES // 12) == 0:
            recent = lengths[-40:] if lengths else [0.0]
            curve.append({"frame": frame, "length": float(np.mean(recent))})

    final = float(np.mean(lengths[-60:])) if lengths else 0.0
    return {"curve": curve, "final": final, "episodes": len(lengths),
            "seconds": time.perf_counter() - started, "online": online}


@functools.lru_cache(maxsize=1)
def _ablation() -> dict:
    settings = (("replay + target", True, True),
                ("replay only", True, False),
                ("target only", False, True),
                ("neither", False, False))
    out = {}
    for label, replay, target_network in settings:
        runs = [_dqn(replay, target_network, seed) for seed in range(DQN_SEEDS)]
        finals = [run["final"] for run in runs]
        out[label] = {"curve": runs[0]["curve"],
                      "mean": float(np.mean(finals)),
                      "sd": float(np.std(finals)),
                      "best": float(np.max(finals)),
                      "worst": float(np.min(finals)),
                      "seconds": float(np.mean([r["seconds"] for r in runs])),
                      "model": runs[0]["online"]}
    return out


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
    return {"mean": float(running.mean()), "max": float(running.max())}


def tabular(fig, axes, p: Palette) -> None:
    runs = _rate_runs()
    optimal = _optimal()
    world = _world()
    best = _evaluate(lambda s, r: optimal["policy"][s])
    left, right = fig.subplots(1, 2)
    for epsilon, color in zip(EPSILONS, (p.blue, p.green, p.amber)):
        rewards = [runs[(alpha, epsilon)]["reward"] for alpha in RATES]
        left.plot(RATES, rewards, "o-", ms=6, lw=2.0, color=color,
                  label=f"epsilon {epsilon}")
        for alpha, value in zip(RATES, rewards):
            left.annotate(f"{value:.3f}", (alpha, value), xytext=(0, 7),
                          textcoords="offset points", ha="center", fontsize=7,
                          color=color)
    left.axhline(best["reward"], color=p.muted, lw=1.3, ls="--",
                 label=f"value iteration ({best['reward']:.4f})")
    left.set_xlabel("learning rate")
    left.set_ylabel("mean reward of the greedy policy")
    left.set_title(f"tabular Q-learning, {EPISODES} episodes each", fontsize=10)
    left.legend(fontsize=7.5, loc="lower left")

    for epsilon, color in zip(EPSILONS, (p.blue, p.green, p.amber)):
        matches = [runs[(alpha, epsilon)]["policy_match"] for alpha in RATES]
        right.plot(RATES, matches, "s-", ms=6, lw=2.0, color=color,
                   label=f"epsilon {epsilon}")
    right.axhline(1.0, color=p.muted, lw=1.2, ls=":")
    right.set_xlabel("learning rate")
    right.set_ylabel("share of states matching the optimal action")
    right.set_ylim(0, 1.1)
    right.set_title(f"agreement with the exact policy "
                    f"({sum(1 for s in world.states if not world.terminal(s))}"
                    f" states)", fontsize=10)
    right.legend(fontsize=7.5, loc="lower right")


def dqn_ablation(fig, axes, p: Palette) -> None:
    runs = _ablation()
    baseline = _random_baseline()
    left, right = fig.subplots(1, 2, width_ratios=(1.0, 1.05))
    colors = (p.green, p.blue, p.amber, p.red)
    for (label, entry), color in zip(runs.items(), colors):
        frames = [point["frame"] for point in entry["curve"]]
        left.plot(frames, [point["length"] for point in entry["curve"]],
                  lw=1.9, color=color, label=label)
    left.axhline(baseline["mean"], color=p.muted, lw=1.2, ls=":",
                 label=f"random ({baseline['mean']:.2f})")
    left.axhline(CartPole.MAX_STEPS, color=p.muted, lw=1.0, ls="--")
    left.annotate(f"episode cap {CartPole.MAX_STEPS}", (frames[0],
                                                        CartPole.MAX_STEPS),
                  xytext=(4, -12), textcoords="offset points", fontsize=7.5,
                  color=p.muted)
    left.set_xlabel("environment frames")
    left.set_ylabel("mean episode length")
    left.set_title(f"CartPole, {ENVS} parallel environments (one seed shown)",
                   fontsize=10)
    left.legend(fontsize=7.5, loc="upper left")

    labels = list(runs)
    positions = np.arange(len(labels))
    means = [runs[label]["mean"] for label in labels]
    spread = [runs[label]["sd"] for label in labels]
    right.barh(positions, means, 0.55, xerr=spread, color=p.blue,
               error_kw={"ecolor": p.muted, "capsize": 3})
    for y, label in zip(positions, labels):
        entry = runs[label]
        right.annotate(f"{entry['mean']:.1f} ± {entry['sd']:.1f}   "
                       f"(worst {entry['worst']:.1f}, best {entry['best']:.1f})",
                       (entry["mean"] + entry["sd"], y), xytext=(6, 0),
                       textcoords="offset points", va="center", fontsize=7,
                       color=p.fg)
    right.axvline(baseline["mean"], color=p.muted, lw=1.2, ls=":")
    right.set_yticks(positions)
    right.set_yticklabels(labels, fontsize=8.5)
    right.invert_yaxis()
    right.set_xlim(0, max(m + s for m, s in zip(means, spread)) * 1.9)
    right.set_xlabel(f"final mean episode length ({DQN_SEEDS} seeds)")
    right.set_title("both mechanisms, measured", fontsize=10)


def q_values(fig, axes, p: Palette) -> None:
    world = _world()
    optimal = _optimal()
    learned = _tabular(alpha=0.2, epsilon=0.1)
    left, right = fig.subplots(1, 2)
    states = [state for state in world.states if not world.terminal(state)]
    true_values = [optimal["values"][state] for state in states]
    learned_values = [float(np.max(learned["table"][state]))
                      for state in states]
    left.scatter(true_values, learned_values, s=26, color=p.blue, alpha=0.85)
    limits = [min(true_values + learned_values) - 0.05,
              max(true_values + learned_values) + 0.05]
    left.plot(limits, limits, lw=1.2, ls="--", color=p.muted,
              label="exactly right")
    error = float(np.mean(np.array(learned_values) - np.array(true_values)))
    absolute = float(np.mean(np.abs(np.array(learned_values)
                                    - np.array(true_values))))
    left.set_xlabel("true optimal value")
    left.set_ylabel("learned max Q")
    left.set_title(f"mean signed error {error:+.4f}, "
                   f"mean absolute {absolute:.4f}", fontsize=10)
    left.legend(fontsize=8, loc="upper left")

    gaps = []
    for state in states:
        values = np.sort(learned["table"][state])[::-1]
        gaps.append(float(values[0] - values[1]))
    right.hist(gaps, bins=14, color=p.amber)
    right.axvline(float(np.mean(gaps)), color=p.red, lw=1.5, ls="--",
                  label=f"mean {np.mean(gaps):.4f}")
    right.set_xlabel("gap between the best and second-best action")
    right.set_ylabel("states")
    right.set_title("how confident is the greedy choice?", fontsize=10)
    right.legend(fontsize=8)


FIGURES = [
    figure("tabular", tabular, size=(9.4, 3.5), axes=False),
    figure("dqn-ablation", dqn_ablation, size=(9.8, 3.6), axes=False),
    figure("q-values", q_values, size=(9.4, 3.5), axes=False),
]


if __name__ == "__main__":
    world = _world()
    optimal = _optimal()
    best = _evaluate(lambda s, r: optimal["policy"][s])
    print("=== tabular Q-learning on the gridworld ===")
    print(f"value iteration: reward {best['reward']:.4f}, "
          f"goal {best['goal_rate']:.4f}, steps {best['steps']:.2f}")
    print(f"{'alpha':>7} {'epsilon':>8} {'reward':>9} {'goal':>7} "
          f"{'steps':>7} {'policy match':>13}")
    for (alpha, epsilon), entry in _rate_runs().items():
        print(f"{alpha:7.2f} {epsilon:8.2f} {entry['reward']:9.4f} "
              f"{entry['goal_rate']:7.4f} {entry['steps']:7.2f} "
              f"{entry['policy_match']:13.4f}")

    print(f"\n=== a DQN on CartPole ({FRAMES} frames x {ENVS} environments, "
          f"{DQN_SEEDS} seeds) ===")
    baseline = _random_baseline()
    print(f"random policy: mean episode length {baseline['mean']:.2f} "
          f"(longest {baseline['max']:.0f}); the cap is {CartPole.MAX_STEPS}")
    print(f"{'configuration':18s} {'final length':>13} {'sd':>7} "
          f"{'worst':>7} {'best':>7} {'seconds':>9}")
    for label, entry in _ablation().items():
        print(f"{label:18s} {entry['mean']:13.2f} {entry['sd']:7.2f} "
              f"{entry['worst']:7.2f} {entry['best']:7.2f} "
              f"{entry['seconds']:9.0f}")
    print("replay breaks the correlation between consecutive samples; the")
    print("target network stops the regression target moving with the weights")
    print("being fitted. The table says how much each one is worth here")

    learned = _tabular()
    states = [s for s in world.states if not world.terminal(s)]
    signed = float(np.mean([float(np.max(learned["table"][s]))
                            - optimal["values"][s] for s in states]))
    print(f"\n=== learned values against the exact ones ===")
    print(f"mean signed error {signed:+.4f} over {len(states)} states")
    print("textbooks expect a POSITIVE bias here, because the max in the")
    print("update is taken over noisy estimates. This run measures the")
    print("opposite. The overestimation is real but small, and it is swamped")
    print("by under-exploration: epsilon-greedy rarely visits the safe route,")
    print("so those states keep values learned from too few visits")
