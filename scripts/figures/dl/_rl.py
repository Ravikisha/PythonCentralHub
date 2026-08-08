"""Environments for the reinforcement-learning pages.

There is no ``gymnasium`` on this machine and nothing may be downloaded, so the
three environments the phase needs are implemented here. They are small enough
to read in full, which is the point: an RL result is only interpretable if you
know exactly what the agent was rewarded for.

``Bandit``      k arms, fixed Gaussian payouts -- the smallest setting where
                exploration and exploitation actually conflict.
``GridWorld``   a tabular navigation task with walls, a goal and a step cost.
``CartPole``    the classic control problem, with the same dynamics constants
                Gym uses, vectorised so many episodes run at once.
"""

from __future__ import annotations

import numpy as np


class Bandit:
    """A k-armed bandit with fixed Gaussian arms.

    The optimal arm is knowable here, which is what makes *regret* -- reward
    lost against always pulling the best arm -- a measurable quantity rather
    than a theoretical one.
    """

    def __init__(self, arms: int = 10, seed: int = 0, spread: float = 1.0,
                 noise: float = 1.0):
        rng = np.random.default_rng(seed)
        self.means = rng.normal(0.0, spread, arms)
        self.noise = noise
        self.arms = arms
        self.best = int(np.argmax(self.means))
        self.best_mean = float(self.means[self.best])
        self._rng = rng

    def pull(self, arm: int) -> float:
        return float(self._rng.normal(self.means[arm], self.noise))

    def regret(self, arm: int) -> float:
        """Expected reward given up by pulling this arm instead of the best."""
        return self.best_mean - float(self.means[arm])


class GridWorld:
    """A small navigation task: reach the goal, avoid the pits, pay per step.

    The layout is a string grid so the reward structure is visible rather than
    described. ``#`` wall, ``.`` floor, ``X`` pit, ``G`` goal, ``S`` start.

    The design matters. There are two routes: a SHORT one along the top row
    (6 steps) that runs directly above a row of pits, and a LONG one along the
    bottom (12 steps) that is nowhere near them. With ``slip`` above zero the
    short route can drop the agent into a pit, so the discount factor and the
    step cost genuinely change which route is optimal. An earlier version of
    this world had only one sensible path, and every discount factor produced
    exactly the same policy -- which made those sweeps meaningless.
    """

    LAYOUT = (
        "#########",
        "#S.....G#",
        "#.XXXXX.#",
        "#.......#",
        "#.......#",
        "#########",
    )
    ACTIONS = ((-1, 0), (1, 0), (0, -1), (0, 1))       # up, down, left, right
    ACTION_NAMES = ("up", "down", "left", "right")

    def __init__(self, step_cost: float = -0.04, pit: float = -1.0,
                 goal: float = 1.0, slip: float = 0.0):
        self.grid = [list(row) for row in self.LAYOUT]
        self.rows = len(self.grid)
        self.columns = len(self.grid[0])
        self.step_cost = step_cost
        self.pit_reward = pit
        self.goal_reward = goal
        self.slip = slip
        self.start = self._find("S")
        self.goal = self._find("G")
        self.states = [(r, c) for r in range(self.rows)
                       for c in range(self.columns)
                       if self.grid[r][c] != "#"]
        self.index = {state: number for number, state in enumerate(self.states)}

    def _find(self, symbol: str) -> tuple:
        for r, row in enumerate(self.grid):
            for c, cell in enumerate(row):
                if cell == symbol:
                    return (r, c)
        raise ValueError(f"{symbol!r} is not in the layout")

    def terminal(self, state: tuple) -> bool:
        return self.grid[state[0]][state[1]] in "GX"

    def step(self, state: tuple, action: int, rng=None) -> tuple:
        """Return (next_state, reward, done)."""
        if self.slip and rng is not None and rng.random() < self.slip:
            action = int(rng.integers(0, len(self.ACTIONS)))
        delta = self.ACTIONS[action]
        row, column = state[0] + delta[0], state[1] + delta[1]
        if self.grid[row][column] == "#":               # walls block movement
            row, column = state
        cell = self.grid[row][column]
        if cell == "G":
            return (row, column), self.goal_reward, True
        if cell == "X":
            return (row, column), self.pit_reward, True
        return (row, column), self.step_cost, False

    def rollout(self, policy, rng, limit: int = 200) -> dict:
        """Follow `policy(state, rng)` from the start until it stops."""
        state = self.start
        total = 0.0
        discounted = 0.0
        path = [state]
        for step in range(limit):
            action = policy(state, rng)
            state, reward, done = self.step(state, action, rng)
            total += reward
            discounted += reward * (0.99 ** step)
            path.append(state)
            if done:
                return {"reward": total, "discounted": discounted,
                        "steps": step + 1, "path": path,
                        "reached_goal": state == self.goal}
        return {"reward": total, "discounted": discounted, "steps": limit,
                "path": path, "reached_goal": False}

    def _backup(self, state: tuple, action: int, values: dict,
                gamma: float) -> float:
        """Expected value of one action, accounting for slip.

        `step` replaces the chosen action with a uniformly random one with
        probability `slip`, so the intended action actually happens with
        probability (1 - slip) + slip/4, and each other action with slip/4.
        Value iteration has to use the same distribution or the "exact" answer
        is exact for a different problem.
        """
        total = 0.0
        actions = len(self.ACTIONS)
        for candidate in range(actions):
            probability = self.slip / actions
            if candidate == action:
                probability += 1.0 - self.slip
            if probability == 0.0:
                continue
            following, reward, done = self.step(state, candidate)
            total += probability * (reward + (0.0 if done
                                              else gamma * values[following]))
        return total

    def value_iteration(self, gamma: float = 0.99, sweeps: int = 800) -> dict:
        """The exact answer, for pages that need a ceiling to compare against."""
        values = {state: 0.0 for state in self.states}
        sweep = 0
        for sweep in range(sweeps):
            change = 0.0
            for state in self.states:
                if self.terminal(state):
                    continue
                best = max(self._backup(state, action, values, gamma)
                           for action in range(len(self.ACTIONS)))
                change = max(change, abs(best - values[state]))
                values[state] = best
            if change < 1e-9:
                break
        policy = {}
        for state in self.states:
            if self.terminal(state):
                continue
            policy[state] = int(np.argmax([
                self._backup(state, action, values, gamma)
                for action in range(len(self.ACTIONS))]))
        return {"values": values, "policy": policy, "sweeps": sweep + 1}


class CartPole:
    """Vectorised CartPole, with the constants the classic implementation uses.

    Stepping many environments at once matters here: a python loop over single
    environments spends its time in the interpreter rather than in the network,
    and every RL page in this phase needs thousands of episodes.
    """

    GRAVITY = 9.8
    CART_MASS = 1.0
    POLE_MASS = 0.1
    TOTAL_MASS = CART_MASS + POLE_MASS
    HALF_POLE = 0.5
    POLEMASS_LENGTH = POLE_MASS * HALF_POLE
    FORCE = 10.0
    TAU = 0.02
    THETA_LIMIT = 12 * 2 * np.pi / 360        # 0.2095 radians
    X_LIMIT = 2.4
    MAX_STEPS = 200

    def __init__(self, count: int = 1, seed: int = 0):
        self.count = count
        self.rng = np.random.default_rng(seed)
        self.state = np.zeros((count, 4), dtype="float32")
        self.steps = np.zeros(count, dtype="int32")
        self.reset()

    def reset(self, mask=None) -> np.ndarray:
        """Reset every environment, or only those flagged in `mask`."""
        if mask is None:
            mask = np.ones(self.count, dtype=bool)
        fresh = self.rng.uniform(-0.05, 0.05, (int(mask.sum()), 4))
        self.state[mask] = fresh.astype("float32")
        self.steps[mask] = 0
        return self.state.copy()

    def step(self, actions) -> tuple:
        """Apply one action per environment. Returns (state, reward, done)."""
        actions = np.asarray(actions).reshape(self.count)
        x, x_dot, theta, theta_dot = self.state.T
        force = np.where(actions == 1, self.FORCE, -self.FORCE)
        cos_theta, sin_theta = np.cos(theta), np.sin(theta)
        temp = ((force + self.POLEMASS_LENGTH * theta_dot ** 2 * sin_theta)
                / self.TOTAL_MASS)
        theta_acceleration = (
            (self.GRAVITY * sin_theta - cos_theta * temp)
            / (self.HALF_POLE * (4.0 / 3.0
                                 - self.POLE_MASS * cos_theta ** 2
                                 / self.TOTAL_MASS)))
        x_acceleration = (temp - self.POLEMASS_LENGTH * theta_acceleration
                          * cos_theta / self.TOTAL_MASS)
        # Euler integration, exactly as the reference implementation does it.
        x = x + self.TAU * x_dot
        x_dot = x_dot + self.TAU * x_acceleration
        theta = theta + self.TAU * theta_dot
        theta_dot = theta_dot + self.TAU * theta_acceleration
        self.state = np.stack([x, x_dot, theta, theta_dot],
                              axis=1).astype("float32")
        self.steps += 1
        done = ((np.abs(x) > self.X_LIMIT)
                | (np.abs(theta) > self.THETA_LIMIT)
                | (self.steps >= self.MAX_STEPS))
        # Every surviving step is worth 1, including the one that ends it.
        reward = np.ones(self.count, dtype="float32")
        return self.state.copy(), reward, done


def discounted_returns(rewards, gamma: float = 0.99) -> np.ndarray:
    """Reward-to-go for one episode, newest step first in the recursion."""
    out = np.zeros(len(rewards), dtype="float32")
    running = 0.0
    for index in reversed(range(len(rewards))):
        running = rewards[index] + gamma * running
        out[index] = running
    return out
