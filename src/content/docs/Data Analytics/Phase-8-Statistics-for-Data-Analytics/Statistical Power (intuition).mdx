---
title: Statistical Power (intuition)
description: Understand power, effect size, and why many tests fail to detect real changes.
sidebar:
  order: 14
---

## Power in one sentence

**Power** is the probability your test detects a real effect.

\[ \text{Power} = 1 - \beta \]

Where \(\beta\) is the Type II error rate.

## What controls power

1. **Sample size (n)**: larger n → higher power
2. **Effect size**: bigger effect → easier to detect
3. **Noise/variance**: more noise → lower power
4. **Significance level (alpha)**: smaller alpha → lower power

## Why it matters in analytics

You might conclude “no effect” when:

- sample size was too small
- metric variance was high

## Quick simulation idea

You can estimate power by simulation:

- simulate A/B outcomes under a known effect
- run the test repeatedly
- measure how often p < 0.05

```python title="Power simulation sketch" showLineNumbers{1}
# This is a conceptual sketch.
# For real experiments, use statsmodels or a dedicated power calculator.

import numpy as np

rng = np.random.default_rng(0)

def run_once(n=2000, p1=0.03, p2=0.031):
    A = rng.binomial(1, p1, size=n)
    B = rng.binomial(1, p2, size=n)
    # compute a simple z-test here (see A/B page)
    return A.mean(), B.mean()

# Repeat many times and track rejection rate.
```

## Practical guidance

- If you can’t increase n, reduce noise (better logging, stronger metric).
- Pre-register hypotheses and expected effect sizes.
