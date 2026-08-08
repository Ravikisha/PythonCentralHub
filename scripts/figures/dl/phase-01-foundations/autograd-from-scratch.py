"""Figures for *Autograd from Scratch*.

``gradient-check``
    Every operation the 60-line engine implements, checked against a central
    difference. The bars are the absolute error, and the point of the figure is
    that they are all at the floating-point floor.

``forward-vs-reverse``
    Measured cost of one full gradient by forward mode (one pass per parameter,
    which is what a numeric gradient does) against reverse mode (one backward
    pass regardless), as the parameter count grows.

``xor-training``
    The 2-2-1 tanh network trained by the scratch engine alone: loss per epoch,
    and the decision surface it ends up with.
"""

from __future__ import annotations

import functools
import math
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "..", ".."))

from _dl import seed_everything  # noqa: E402
from _style import Palette, figure  # noqa: E402

EPOCHS = 3000
GRID = 60
SIZES = (2, 10, 50, 200, 800)


class Value:
    """The engine from the page, verbatim in behaviour."""

    def __init__(self, data, children=(), operation=""):
        self.data = float(data)
        self.grad = 0.0
        self._backward = lambda: None
        self._prev = set(children)
        self._operation = operation

    def __add__(self, other):
        other = other if isinstance(other, Value) else Value(other)
        out = Value(self.data + other.data, (self, other), "+")

        def _backward():
            self.grad += out.grad
            other.grad += out.grad

        out._backward = _backward
        return out

    def __mul__(self, other):
        other = other if isinstance(other, Value) else Value(other)
        out = Value(self.data * other.data, (self, other), "*")

        def _backward():
            self.grad += other.data * out.grad
            other.grad += self.data * out.grad

        out._backward = _backward
        return out

    def __pow__(self, power):
        out = Value(self.data ** power, (self,), f"**{power}")

        def _backward():
            self.grad += power * self.data ** (power - 1) * out.grad

        out._backward = _backward
        return out

    def tanh(self):
        value = math.tanh(self.data)
        out = Value(value, (self,), "tanh")

        def _backward():
            self.grad += (1 - value ** 2) * out.grad

        out._backward = _backward
        return out

    def exp(self):
        value = math.exp(self.data)
        out = Value(value, (self,), "exp")

        def _backward():
            self.grad += value * out.grad

        out._backward = _backward
        return out

    def log(self):
        out = Value(math.log(self.data), (self,), "log")

        def _backward():
            self.grad += out.grad / self.data

        out._backward = _backward
        return out

    def __neg__(self):
        return self * -1

    def __sub__(self, other):
        return self + (-other if isinstance(other, Value) else Value(-other))

    def __radd__(self, other):
        return self + other

    def __rmul__(self, other):
        return self * other

    def __truediv__(self, other):
        other = other if isinstance(other, Value) else Value(other)
        return self * other ** -1

    def backward(self):
        order, seen = [], set()

        def visit(node):
            if node in seen:
                return
            seen.add(node)
            for child in node._prev:
                visit(child)
            order.append(node)

        visit(self)
        self.grad = 1.0
        for node in reversed(order):
            node._backward()


# (label, function of a numpy vector, arity) — every rule the engine defines.
CASES = (
    ("a + b", lambda v: v[0] + v[1], 2),
    ("a * b", lambda v: v[0] * v[1], 2),
    ("a ** 3", lambda v: v[0] ** 3, 1),
    ("tanh(a)", lambda v: math.tanh(v[0]), 1),
    ("exp(a)", lambda v: math.exp(v[0]), 1),
    ("log(a)", lambda v: math.log(v[0]), 1),
    ("a / b", lambda v: v[0] / v[1], 2),
    ("(a*b + a).tanh()", lambda v: math.tanh(v[0] * v[1] + v[0]), 2),
    ("a*a (shared node)", lambda v: v[0] * v[0], 1),
)


def _engine(label, values):
    """Run one case through the Value graph and return the gradients."""
    nodes = [Value(x) for x in values]
    a = nodes[0]
    b = nodes[1] if len(nodes) > 1 else None
    if label == "a + b":
        out = a + b
    elif label == "a * b":
        out = a * b
    elif label == "a ** 3":
        out = a ** 3
    elif label == "tanh(a)":
        out = a.tanh()
    elif label == "exp(a)":
        out = a.exp()
    elif label == "log(a)":
        out = a.log()
    elif label == "a / b":
        out = a / b
    elif label == "(a*b + a).tanh()":
        out = (a * b + a).tanh()
    else:
        out = a * a
    out.backward()
    return np.array([node.grad for node in nodes])


def _numeric(function, point, step=1e-6):
    out = np.zeros_like(point)
    for index in range(len(point)):
        forward, backward = point.copy(), point.copy()
        forward[index] += step
        backward[index] -= step
        out[index] = (function(forward) - function(backward)) / (2 * step)
    return out


@functools.lru_cache(maxsize=1)
def _gradient_check() -> dict:
    rng = np.random.default_rng(0)
    labels, errors = [], []
    for label, function, arity in CASES:
        point = rng.uniform(0.6, 1.8, 2)
        analytic = _engine(label, point[:arity])
        numeric = _numeric(function, point)[:arity]
        errors.append(float(np.abs(analytic - numeric).max()))
        labels.append(label)
    return {"labels": labels, "errors": errors,
            "worst": max(errors), "cases": len(labels)}


class Dual:
    """Forward mode, same Python-object style as ``Value`` so the timing
    comparison is like for like. Each pass carries the derivative with respect
    to exactly one input, which is why you need one pass per parameter."""

    __slots__ = ("data", "dot")

    def __init__(self, data, dot=0.0):
        self.data = float(data)
        self.dot = float(dot)

    def __add__(self, other):
        other = other if isinstance(other, Dual) else Dual(other)
        return Dual(self.data + other.data, self.dot + other.dot)

    def __mul__(self, other):
        other = other if isinstance(other, Dual) else Dual(other)
        return Dual(self.data * other.data,
                    self.dot * other.data + self.data * other.dot)

    def __pow__(self, power):
        return Dual(self.data ** power,
                    power * self.data ** (power - 1) * self.dot)

    def tanh(self):
        value = math.tanh(self.data)
        return Dual(value, (1 - value ** 2) * self.dot)


def _objective_reverse(weights, inputs):
    nodes = [Value(w) for w in weights]
    total = Value(0.0)
    for node, x in zip(nodes, inputs):
        total = total + (node * float(x)).tanh() ** 2
    total.backward()
    return np.array([node.grad for node in nodes])


def _objective_forward(weights, inputs):
    """One pass per parameter — the definition of forward mode."""
    out = np.zeros(len(weights))
    for index in range(len(weights)):
        total = Dual(0.0)
        for position, (w, x) in enumerate(zip(weights, inputs)):
            seed = 1.0 if position == index else 0.0
            total = total + (Dual(w, seed) * float(x)).tanh() ** 2
        out[index] = total.dot
    return out


@functools.lru_cache(maxsize=1)
def _forward_vs_reverse() -> dict:
    """The same gradient computed both ways on the same machinery, timed."""
    rng = np.random.default_rng(0)
    rows = []
    for size in SIZES:
        weights = rng.uniform(-1, 1, size)
        inputs = rng.uniform(-1, 1, size)

        start = time.perf_counter()
        forward_gradient = _objective_forward(weights, inputs)
        forward_seconds = time.perf_counter() - start

        start = time.perf_counter()
        reverse_gradient = _objective_reverse(weights, inputs)
        reverse_seconds = time.perf_counter() - start

        rows.append({
            "size": size,
            "forward": forward_seconds,
            "reverse": reverse_seconds,
            "passes": size,
            "error": float(np.abs(forward_gradient - reverse_gradient).max()),
        })
    return {"rows": rows}


@functools.lru_cache(maxsize=1)
def _xor() -> dict:
    seed_everything(0)
    rng = np.random.default_rng(0)
    parameters = [Value(float(x)) for x in rng.uniform(-1, 1, 9)]
    rows = [([0.0, 0.0], 0.0), ([0.0, 1.0], 1.0),
            ([1.0, 0.0], 1.0), ([1.0, 1.0], 0.0)]

    def predict(x0, x1, params):
        w = params
        h0 = (w[0] * x0 + w[1] * x1 + w[2]).tanh()
        h1 = (w[3] * x0 + w[4] * x1 + w[5]).tanh()
        return (w[6] * h0 + w[7] * h1 + w[8]).tanh()

    history = []
    for epoch in range(EPOCHS):
        for parameter in parameters:
            parameter.grad = 0.0
        loss = Value(0.0)
        for (x0, x1), target in rows:
            prediction = predict(Value(x0), Value(x1), parameters)
            loss = loss + (prediction + Value(-target)) ** 2
        loss.backward()
        for parameter in parameters:
            parameter.data -= 0.1 * parameter.grad
        history.append(loss.data)

    axis = np.linspace(-0.4, 1.4, GRID)
    surface = np.zeros((GRID, GRID))
    for row, y in enumerate(axis):
        for column, x in enumerate(axis):
            surface[row, column] = predict(Value(x), Value(y), parameters).data

    predictions = [predict(Value(x0), Value(x1), parameters).data
                   for (x0, x1), _ in rows]
    steps = np.diff(np.array(history))
    return {"history": history, "surface": surface, "axis": axis,
            "rows": rows, "predictions": predictions,
            "final": history[-1],
            "rises": int((steps > 0).sum()),
            "largest_rise": float(steps.max()),
            "best": float(min(history)),
            "best_epoch": int(np.argmin(history)) + 1}


def gradient_check(fig, axes, p: Palette) -> None:
    info = _gradient_check()
    ax = fig.subplots(1, 1)
    positions = np.arange(len(info["labels"]))
    floor = 1e-18
    heights = [max(error, floor) for error in info["errors"]]
    ax.barh(positions, heights, color=p.green, height=0.65)
    ax.set_yticks(positions)
    ax.set_yticklabels(info["labels"], fontsize=8)
    ax.set_xscale("log")
    ax.set_xlim(floor, 1e-6)
    ax.axvline(1e-9, color=p.amber, lw=1.2, ls="--")
    ax.annotate("1e-9: the usual pass threshold", (1e-9, len(positions) - 0.4),
                xytext=(4, 0), textcoords="offset points", fontsize=7.5,
                color=p.amber, va="center")
    for position, error in zip(positions, info["errors"]):
        ax.annotate(f"{error:.2e}", (max(error, floor), position),
                    xytext=(4, 0), textcoords="offset points", fontsize=7,
                    color=p.fg, va="center")
    ax.set_xlabel("absolute difference from a central-difference gradient")
    ax.set_title(f"all {info['cases']} rules, worst error "
                 f"{info['worst']:.2e}", fontsize=10)
    ax.invert_yaxis()


def forward_vs_reverse(fig, axes, p: Palette) -> None:
    rows = _forward_vs_reverse()["rows"]
    left, right = fig.subplots(1, 2)
    sizes = [row["size"] for row in rows]
    forward = [row["forward"] * 1000 for row in rows]
    reverse = [row["reverse"] * 1000 for row in rows]

    left.plot(sizes, forward, "o-", color=p.red, lw=1.8, ms=5,
              label="forward mode (one pass per parameter)")
    left.plot(sizes, reverse, "o-", color=p.green, lw=1.8, ms=5,
              label="reverse (one backward pass)")
    left.set_xscale("log")
    left.set_yscale("log")
    left.set_xlabel("parameters")
    left.set_ylabel("milliseconds for one full gradient")
    left.set_title("both axes log", fontsize=10)
    left.legend(fontsize=7.5, loc="upper left")

    ratios = [row["forward"] / row["reverse"] for row in rows]
    positions = np.arange(len(rows))
    right.bar(positions, ratios, color=p.blue, width=0.6)
    for position, ratio in zip(positions, ratios):
        right.annotate(f"{ratio:.1f}x", (position, ratio), xytext=(0, 3),
                       textcoords="offset points", ha="center", fontsize=8,
                       color=p.fg)
    right.set_xticks(positions)
    right.set_xticklabels([f"{size}" for size in sizes])
    right.set_xlabel("parameters")
    right.set_ylabel("forward cost / reverse cost")
    right.set_title("the gap widens with every parameter", fontsize=10)


def xor_training(fig, axes, p: Palette) -> None:
    info = _xor()
    left, right = fig.subplots(1, 2)
    left.plot(info["history"], color=p.blue, lw=1.4)
    left.set_yscale("log")
    left.set_xlabel("epoch")
    left.set_ylabel("loss, summed over the 4 rows")
    left.set_title(f"nine parameters, plain gradient descent\n"
                   f"final loss {info['final']:.6f}", fontsize=10)

    axis = info["axis"]
    mesh = right.pcolormesh(axis, axis, info["surface"], cmap="coolwarm",
                            vmin=-1, vmax=1, shading="auto")
    fig.colorbar(mesh, ax=right, fraction=0.046, label="network output")
    for (x0, x1), target in info["rows"]:
        right.scatter([x0], [x1], s=90, marker="o" if target else "X",
                      c=p.fg, edgecolors=p.bg, linewidths=1.2, zorder=3)
    right.set_xlabel("input 0")
    right.set_ylabel("input 1")
    right.set_title("the XOR surface a perceptron cannot draw", fontsize=10)


FIGURES = [
    figure("gradient-check", gradient_check, size=(8.0, 4.4), axes=False),
    figure("forward-vs-reverse", forward_vs_reverse, size=(9.0, 4.2),
           axes=False),
    figure("xor-training", xor_training, size=(9.2, 4.2), axes=False),
]


if __name__ == "__main__":
    check = _gradient_check()
    print("=== gradient check ===")
    for label, error in zip(check["labels"], check["errors"]):
        print(f"{label:22s} {error:.3e}")
    print(f"worst: {check['worst']:.3e}")

    print("\n=== forward vs reverse ===")
    print(f"{'params':>8} {'fwd ms':>9} {'rev ms':>9} {'ratio':>8} "
          f"{'passes':>7} {'max err':>10}")
    for row in _forward_vs_reverse()["rows"]:
        print(f"{row['size']:8d} {row['forward'] * 1000:9.3f} "
              f"{row['reverse'] * 1000:9.3f} "
              f"{row['forward'] / row['reverse']:8.1f} "
              f"{row['passes']:7d} {row['error']:10.2e}")

    xor = _xor()
    print("\n=== XOR ===")
    for epoch in (0, 99, 499, 999, 1999, 2999):
        print(f"epoch {epoch + 1:5d}: {xor['history'][epoch]:.6f}")
    print(f"final loss: {xor['final']:.6f}")
    print(f"lowest loss: {xor['best']:.6f} at epoch {xor['best_epoch']}")
    print(f"epochs where the loss went UP: {xor['rises']} of {EPOCHS - 1}, "
          f"largest single rise {xor['largest_rise']:.6f}")
    for ((x0, x1), target), prediction in zip(xor["rows"], xor["predictions"]):
        print(f"  [{x0:.0f}, {x1:.0f}] -> {prediction:+.4f}  target {target:.0f}")
