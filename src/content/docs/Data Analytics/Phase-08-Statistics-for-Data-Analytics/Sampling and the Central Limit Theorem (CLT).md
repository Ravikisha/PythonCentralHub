---
title: Sampling and the Central Limit Theorem (CLT)
description: Learn why sample means look normal and how that powers confidence intervals and tests.
sidebar:
  order: 5
---

## Sampling

A sample is one possible view of the population.

Important ideas:

- Larger samples reduce noise.
- Random sampling reduces bias.

## Central Limit Theorem (CLT)

CLT says (informally):

> For many distributions, the distribution of the **sample mean** becomes approximately normal as sample size grows.

This enables:

- Confidence intervals
- Hypothesis tests

## Demonstration in Python

Even if data is not normal (e.g., exponential), the means become close to normal.

```python title="CLT demo" showLineNumbers{1}
import numpy as np

rng = np.random.default_rng(42)

# Non-normal population
population = rng.exponential(scale=1.0, size=200_000)

means = []
for _ in range(5000):
    sample = rng.choice(population, size=50, replace=False)
    means.append(sample.mean())

means = np.array(means)
print(means.mean(), means.std())
```

## Standard error

The **standard error of the mean** is:

\[ SE(\bar{x}) = \frac{s}{\sqrt{n}} \]

- Bigger n → smaller SE

## Visualize it

The CLT is one of the most surprising facts in statistics: take the **mean** of a handful of
random values, do it thousands of times, and those means pile up into a **bell curve** —
even though each sample came from a flat, non-bell distribution. Watch the histogram of
sample means fill in:

```p5 title="The Central Limit Theorem in action" desc="Each bar counts sample means. Means of uniform values still pile up into a normal bell shape." height="280"
const BINS = 40;
let hist = new Array(BINS).fill(0);
let total = 0;
const n = 8;
function setup() {
  createCanvas(600, 280);
  textFont("monospace");
}
function draw() {
  background(13, 17, 23);
  for (let s = 0; s < 3; s++) {
    let sum = 0;
    for (let i = 0; i < n; i++) sum += random();
    const mean = sum / n;
    let bin = Math.floor(mean * BINS);
    bin = constrain(bin, 0, BINS - 1);
    hist[bin]++;
    total++;
  }
  const maxh = Math.max.apply(null, hist.concat([1]));
  const gx = 30, gy = 20, gw = width - 60, gh = height - 60, bw = gw / BINS;
  noStroke();
  for (let b = 0; b < BINS; b++) {
    const h = hist[b] / maxh * gh;
    fill(75, 139, 190);
    rect(gx + b * bw, gy + gh - h, bw - 1, h);
  }
  stroke(255, 211, 67);
  strokeWeight(2);
  noFill();
  beginShape();
  for (let x = 0; x <= 1; x += 0.02) {
    const y = Math.exp(-((x - 0.5) ** 2) / (2 * 0.011));
    vertex(gx + x * gw, gy + gh - y * gh * 0.95);
  }
  endShape();
  noStroke();
  fill(150);
  textSize(12);
  textAlign(CENTER, TOP);
  text("distribution of sample means (n = " + n + ")", width / 2, gy + gh + 18);
  fill(107, 169, 221);
  textAlign(LEFT, CENTER);
  text(total + " samples", 30, 12);
  if (total > 4000) { hist = new Array(BINS).fill(0); total = 0; }
}
```

## Practical guidance

- Use bootstrap (resampling) if formulas are hard or assumptions unclear.

## The CLT pipeline

```mermaid title="How the CLT builds a bell curve" desc="Repeated sampling and averaging turns any starting shape into a normal-ish distribution of means."
flowchart LR
  A["Any population<br/>(skewed, uniform, etc.)"] --> B["Draw a sample<br/>of size n"]
  B --> C["Compute the<br/>sample mean"]
  C --> D["Repeat<br/>thousands of times"]
  D --> E["Histogram of means<br/>looks normal"]
```

:::tip[From the book]
Chapter 12 of *Python for Data Analysis* points out that tools like statsmodels and
scikit-learn assume you already understand the statistics underneath them — the CLT is
exactly that foundation. It's the reason a t-test or confidence interval can use a normal
or t-distribution formula even when your raw data isn't normal at all: the *sample means*
are what get compared, and those are approximately normal thanks to the CLT.
:::

## 🧪 Try It Yourself

### Exercise 1 – Sample size and standard error

```python
# Task: show that standard error shrinks as sample size grows
import numpy as np

rng = np.random.default_rng(7)
population = rng.exponential(scale=2.0, size=100_000)

for n in [10, 100, 1000]:
    sample = rng.choice(population, size=n, replace=False)
    se = sample.std(ddof=1) / np.sqrt(n)  # replace ___ with sqrt(n) if blanked
    print(f"n={n}: SE={round(se, 3)}")

# Expected output (values will vary slightly, but shrink as n grows):
# n=10: SE=0.6...
# n=100: SE=0.2...
# n=1000: SE=0.06...
```

### Exercise 2 – Means of a skewed population look normal

```python
# Task: collect 2000 sample means from a skewed population and check their shape
import numpy as np

rng = np.random.default_rng(11)
population = rng.exponential(scale=1.0, size=200_000)

means = [rng.choice(population, size=40, replace=False).mean() for _ in range(2000)]
means = np.array(means)

print("population skew ~ exponential, not normal")
print("mean of sample means:", round(means.mean(), 2))
print("std of sample means:", round(means.std(), 2))

# Expected output:
# population skew ~ exponential, not normal
# mean of sample means: ~1.0
# std of sample means: a small number, close to 1/sqrt(40)
```

### Exercise 3 – Bootstrap a confidence range

```python
# Task: use resampling (bootstrap) to estimate uncertainty in a mean
import numpy as np

rng = np.random.default_rng(3)
data = np.array([12, 15, 14, 10, 13, 16, 11, 14, 12, 15])

boot_means = []
for _ in range(2000):
    resample = rng.choice(data, size=len(data), replace=True)
    boot_means.append(resample.mean())

boot_means = np.array(boot_means)
lower = np.percentile(boot_means, 2.5)
upper = np.percentile(boot_means, 97.5)

print("bootstrap 95% range:", round(lower, 2), "to", round(upper, 2))

# Expected output:
# bootstrap 95% range: <roughly 12.0 to 14.6>
```

## Next

Continue to **Confidence Intervals (CI)** to turn the standard error into a range you can
report with confidence.
