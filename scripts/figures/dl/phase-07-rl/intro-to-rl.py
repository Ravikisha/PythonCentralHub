"""Figures for *Introduction to Reinforcement Learning*.

A gridworld small enough to solve exactly is the only honest way to introduce
RL: value iteration gives the true optimum, so every learned policy can be
scored against it instead of against a plot that looks like it is improving.

``policy-quality``
    A random policy, a learned policy and the exact optimum on the same axes --
    reward, steps and how often the goal is actually reached.

``discount-and-cost``
    What the discount factor and the per-step cost actually change about the
    optimal policy, which is usually asserted rather than shown.

``value-map``
    The exact state values and the greedy policy they imply, drawn on the grid.
"""

from __future__ import annotations

import functools
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "..", ".."))

from _rl import GridWorld  # noqa: E402
from _style import Palette, figure  # noqa: E402

EPISODES = 3000
EVAL = 400
GAMMAS = (0.5, 0.8, 0.9, 0.95, 0.99)
STEP_COSTS = (0.0, -0.01, -0.04, -0.2)
ALPHA = 0.2
EPSILON = 0.1
# Actions succeed only most of the time. Without this the world has a single
# sensible route and every discount factor produces an identical policy.
SLIP = 0.15
DEFAULT_COST = -0.01


@functools.lru_cache(maxsize=8)
def _world(step_cost: float = DEFAULT_COST) -> GridWorld:
    return GridWorld(step_cost=step_cost, slip=SLIP)


@functools.lru_cache(maxsize=8)
def _optimal(gamma: float = 0.99, step_cost: float = DEFAULT_COST) -> dict:
    return _world(step_cost).value_iteration(gamma=gamma)


def _evaluate(world: GridWorld, policy, seed: int = 0,
              episodes: int = EVAL) -> dict:
    rng = np.random.default_rng(seed)
    runs = [world.rollout(policy, rng) for _ in range(episodes)]
    # Which route did it take? The short one never leaves the top two rows.
    short = [1.0 if all(cell[0] <= 2 for cell in run["path"]) else 0.0
             for run in runs]
    return {"reward": float(np.mean([run["reward"] for run in runs])),
            "steps": float(np.mean([run["steps"] for run in runs])),
            "goal_rate": float(np.mean([run["reached_goal"] for run in runs])),
            "short_route": float(np.mean(short)),
            "reward_sd": float(np.std([run["reward"] for run in runs]))}


@functools.lru_cache(maxsize=4)
def _q_learning(gamma: float = 0.99, step_cost: float = -0.04,
                episodes: int = None) -> dict:
    """Tabular Q-learning, with a learning curve scored against the optimum."""
    world = _world(step_cost)
    episodes = EPISODES if episodes is None else int(episodes)
    rng = np.random.default_rng(0)
    actions = len(world.ACTIONS)
    table = {state: np.zeros(actions) for state in world.states}
    curve = []
    for episode in range(1, episodes + 1):
        state = world.start
        for _ in range(200):
            if rng.random() < EPSILON:
                action = int(rng.integers(0, actions))
            else:
                action = int(np.argmax(table[state]))
            following, reward, done = world.step(state, action, rng)
            target = reward + (0.0 if done
                               else gamma * float(np.max(table[following])))
            table[state][action] += ALPHA * (target - table[state][action])
            state = following
            if done:
                break
        if episode % 100 == 0 or episode == 1:
            greedy = _evaluate(world,
                               lambda s, r: int(np.argmax(table[s])),
                               seed=1, episodes=60)
            curve.append({"episode": episode, **greedy})
    return {"table": table, "curve": curve,
            "policy": {state: int(np.argmax(values))
                       for state, values in table.items()}}


@functools.lru_cache(maxsize=1)
def _policy_comparison() -> dict:
    world = _world()
    optimal = _optimal()
    learned = _q_learning()
    actions = len(world.ACTIONS)
    return {
        "random": _evaluate(world, lambda s, r: int(r.integers(0, actions))),
        "Q-learning": _evaluate(world, lambda s, r: learned["policy"][s]),
        "value iteration": _evaluate(world, lambda s, r: optimal["policy"][s]),
        "curve": learned["curve"],
    }


@functools.lru_cache(maxsize=1)
def _discount_runs() -> dict:
    out = {}
    for gamma in GAMMAS:
        solved = _optimal(gamma=gamma)
        world = _world()
        result = _evaluate(world, lambda s, r: solved["policy"][s])
        out[gamma] = {**result, "sweeps": solved["sweeps"],
                      "start_value": float(solved["values"][world.start])}
    return out


@functools.lru_cache(maxsize=1)
def _cost_runs() -> dict:
    out = {}
    for cost in STEP_COSTS:
        world = _world(step_cost=cost)
        solved = _optimal(step_cost=cost)
        result = _evaluate(world, lambda s, r: solved["policy"][s])
        out[cost] = {**result, "start_value": float(solved["values"][world.start])}
    return out


def policy_quality(fig, axes, p: Palette) -> None:
    info = _policy_comparison()
    left, right = fig.subplots(1, 2, width_ratios=(1.0, 1.15))
    labels = ["random", "Q-learning", "value iteration"]
    metrics = (("reward", "mean total reward"), ("steps", "mean steps"),
               ("goal_rate", "goal reached"))
    positions = np.arange(len(metrics))
    width = 0.26
    scales = [max(abs(info[label][key]) for label in labels) or 1.0
              for key, _ in metrics]
    for index, (label, color) in enumerate(zip(labels,
                                               (p.muted, p.blue, p.green))):
        offset = (index - 1) * width
        values = [info[label][key] for key, _ in metrics]
        left.bar(positions + offset, [v / s for v, s in zip(values, scales)],
                 width * 0.9, color=color, label=label)
        for x, value, scale in zip(positions + offset, values, scales):
            left.annotate(f"{value:.3f}", (x, value / scale), xytext=(0, 3),
                          textcoords="offset points", ha="center",
                          fontsize=7, color=p.fg)
    left.set_xticks(positions)
    left.set_xticklabels([name for _, name in metrics], fontsize=8.5)
    left.axhline(0, color=p.muted, lw=0.8)
    left.set_ylabel("scaled to the largest value in each group")
    left.set_title(f"{EVAL} episodes per policy", fontsize=10)
    left.legend(fontsize=8, loc="lower right")

    curve = info["curve"]
    episodes = [entry["episode"] for entry in curve]
    right.plot(episodes, [entry["reward"] for entry in curve], lw=2.0,
               color=p.blue, label="Q-learning, greedy evaluation")
    right.axhline(info["value iteration"]["reward"], color=p.green, lw=1.4,
                  ls="--",
                  label=f"optimum ({info['value iteration']['reward']:.4f})")
    right.axhline(info["random"]["reward"], color=p.muted, lw=1.2, ls=":",
                  label=f"random ({info['random']['reward']:.4f})")
    right.set_xlabel("training episode")
    right.set_ylabel("mean total reward")
    right.set_title("learning curve against the exact answer", fontsize=10)
    right.legend(fontsize=8, loc="lower right")


def discount_and_cost(fig, axes, p: Palette) -> None:
    discounts = _discount_runs()
    costs = _cost_runs()
    left, right = fig.subplots(1, 2)
    gammas = list(discounts)
    left.plot(gammas, [discounts[g]["short_route"] for g in gammas], "o-",
              ms=6, lw=2.0, color=p.red, label="takes the short risky route")
    left.plot(gammas, [discounts[g]["goal_rate"] for g in gammas], "s-", ms=6,
              lw=2.0, color=p.green, label="reaches the goal")
    for gamma in gammas:
        left.annotate(f"{discounts[gamma]['short_route']:.2f}",
                      (gamma, discounts[gamma]["short_route"]), xytext=(0, 8),
                      textcoords="offset points", ha="center", fontsize=7,
                      color=p.red)
    left.set_xlabel("discount factor")
    left.set_ylabel("share of episodes")
    left.set_ylim(-0.05, 1.15)
    left.set_title("a myopic agent gambles on the shortcut", fontsize=10)
    left.legend(fontsize=7.5, loc="center left")

    labels = [f"{cost:g}" for cost in costs]
    positions = np.arange(len(labels))
    short = [costs[cost]["short_route"] for cost in costs]
    goal_rates = [costs[cost]["goal_rate"] for cost in costs]
    right.bar(positions - 0.2, short, 0.38, color=p.red,
              label="takes the short risky route")
    right.bar(positions + 0.2, goal_rates, 0.38, color=p.green,
              label="reaches the goal")
    for x, value in zip(positions - 0.2, short):
        right.annotate(f"{value:.2f}", (x, value), xytext=(0, 3),
                       textcoords="offset points", ha="center", fontsize=7,
                       color=p.fg)
    for x, value in zip(positions + 0.2, goal_rates):
        right.annotate(f"{value:.3f}", (x, value), xytext=(0, 3),
                       textcoords="offset points", ha="center", fontsize=7,
                       color=p.fg)
    right.set_xticks(positions)
    right.set_xticklabels(labels)
    right.set_xlabel("reward per step")
    right.set_ylim(0, 1.25)
    right.set_title("expensive steps buy a worse route", fontsize=10)
    right.legend(fontsize=8, loc="upper center")


def value_map(fig, axes, p: Palette) -> None:
    world = _world()
    solved = _optimal()
    grid = np.full((world.rows, world.columns), np.nan)
    for state, value in solved["values"].items():
        grid[state] = value
    axes.imshow(grid, cmap="viridis")
    arrows = {0: "^", 1: "v", 2: "<", 3: ">"}
    for row in range(world.rows):
        for column in range(world.columns):
            cell = world.grid[row][column]
            if cell == "#":
                continue          # walls stay NaN, so imshow leaves them blank
            value = solved["values"][(row, column)]
            marker = ""
            if cell == "G":
                marker = "GOAL"
            elif cell == "X":
                marker = "PIT"
            else:
                marker = arrows[solved["policy"][(row, column)]]
            axes.text(column, row - 0.15, marker, ha="center", va="center",
                      fontsize=11, color="white", weight="bold")
            axes.text(column, row + 0.25, f"{value:.2f}", ha="center",
                      va="center", fontsize=7.5, color="white")
    axes.set_xticks([])
    axes.set_yticks([])
    axes.grid(False)
    axes.set_title(f"exact state values and the greedy policy "
                   f"(gamma 0.99, step {world.step_cost})", fontsize=10)


FIGURES = [
    figure("policy-quality", policy_quality, size=(9.6, 3.6), axes=False),
    figure("discount-and-cost", discount_and_cost, size=(9.4, 3.5), axes=False),
    figure("value-map", value_map, size=(7.6, 5.0)),
]


if __name__ == "__main__":
    world = _world()
    solved = _optimal()
    print("=== the gridworld ===")
    for row in world.LAYOUT:
        print("   " + row)
    print(f"{len(world.states)} reachable states, start {world.start}, "
          f"goal {world.goal}, step cost {world.step_cost}, slip {SLIP}")
    print("two routes: the top row is 6 steps but runs directly above the")
    print("pits, and the bottom is 12 steps and safe. Slip is what makes that")
    print("a real choice -- an action does the wrong thing 15% of the time")
    print(f"value iteration converged in {solved['sweeps']} sweeps; the exact")
    print(f"value of the start state is {solved['values'][world.start]:.4f}")

    print(f"\n=== three policies, {EVAL} episodes each ===")
    info = _policy_comparison()
    print(f"{'policy':18s} {'mean reward':>12} {'sd':>8} {'mean steps':>11} "
          f"{'goal reached':>13} {'short route':>12}")
    for label in ("random", "Q-learning", "value iteration"):
        entry = info[label]
        print(f"{label:18s} {entry['reward']:12.4f} {entry['reward_sd']:8.4f} "
              f"{entry['steps']:11.2f} {entry['goal_rate']:13.4f} "
              f"{entry['short_route']:12.4f}")
    print("Q-learning is scored greedily, with exploration switched off, so")
    print("this is the policy it learned rather than the policy it followed")

    print(f"\n=== the discount factor (optimal policy re-solved for each) ===")
    print(f"{'gamma':>6} {'reward':>8} {'steps':>7} {'goal':>7} "
          f"{'short route':>12} {'start value':>12} {'sweeps':>7}")
    for gamma, entry in _discount_runs().items():
        print(f"{gamma:6.2f} {entry['reward']:8.4f} {entry['steps']:7.2f} "
              f"{entry['goal_rate']:7.4f} {entry['short_route']:12.4f} "
              f"{entry['start_value']:12.4f} {entry['sweeps']:7d}")
    print("a low discount makes the pit's cost feel far away, so the agent")
    print("gambles on the shortcut and reaches the goal LESS often")

    print(f"\n=== the step cost ===")
    print(f"{'step':>6} {'reward':>8} {'steps':>7} {'goal':>7} "
          f"{'short route':>12} {'start value':>12}")
    for cost, entry in _cost_runs().items():
        print(f"{cost:+6.2f} {entry['reward']:8.4f} {entry['steps']:7.2f} "
              f"{entry['goal_rate']:7.4f} {entry['short_route']:12.4f} "
              f"{entry['start_value']:12.4f}")
    print("cheap steps buy the safe detour; expensive steps make the risky")
    print("shortcut worth taking, and the goal rate drops accordingly")
