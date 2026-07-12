---
title: Probability Basics (events, conditional probability)
description: Learn probability foundations used in analytics - conditional probability, independence, Bayes rule.
sidebar:
  order: 3
---

## Events and probability

- An **event** is a set of outcomes.
- Probability is a number between 0 and 1.

Example: probability of drawing a red card from a standard deck is 26/52 = 0.5.

## Conditional probability

Probability of A given B:

\[ P(A|B) = \frac{P(A \cap B)}{P(B)} \]

In analytics language:

- A = “user churns”
- B = “user is on basic plan”

Then \(P(A|B)\) is the churn rate for basic-plan users.

## Independence

A and B are independent if:

\[ P(A|B) = P(A) \]

If churn rate differs by plan, churn and plan are **not** independent.

## Bayes’ rule

\[ P(A|B) = \frac{P(B|A) P(A)}{P(B)} \]

Common use cases:

- Medical tests (false positives)
- Fraud detection (base rate is tiny)

## Mini example: base rate fallacy

If fraud is rare (say 0.1%), even a “95% accurate” detector can generate many false alarms.

Key lesson:

- Always check base rates and precision/recall, not just accuracy.

## How Bayes' rule flips a probability

Bayes' rule lets you go from "probability of evidence given a cause" to "probability of
a cause given evidence" — which is usually the direction you actually care about.

```mermaid title="Bayes' rule in a fraud check" desc="Bayes' rule combines a rare base rate with test accuracy to get the real probability of fraud given a flag."
flowchart LR
  A["Base rate<br/>P(fraud) = 0.1%"] --> C["Bayes' rule"]
  B["Test accuracy<br/>P(flag | fraud) = 95%"] --> C
  C --> D["P(fraud | flag)<br/>often still small!"]
```

:::tip[From the book]
A classic statistics gotcha: with a rare event (a tiny base rate) even a highly accurate
test produces mostly false alarms, because the huge pool of true negatives generates more
false positives than the tiny pool of true positives generates correct hits. Always run the
numbers with Bayes' rule instead of trusting "95% accurate" at face value.
:::

## 🧪 Try It Yourself

Run each snippet and check your output against the comment.

### Exercise 1 – Conditional probability from a table

```python
# Task: compute P(churn | plan == "basic") from raw counts
# replace ___ with the correct values
basic_total = 200
basic_churned = 40

p_churn_given_basic = basic_churned / basic_total  # replace ___ if needed
print("P(churn | basic):", p_churn_given_basic)

# Expected output:
# P(churn | basic): 0.2
```

### Exercise 2 – Checking independence

```python
# Task: two events are independent if P(A|B) == P(A)
p_a = 0.30          # overall churn rate
p_a_given_b = 0.30  # churn rate for "pro" plan users

independent = p_a_given_b == p_a  # replace ___ with the comparison
print("Independent?", independent)

# Expected output:
# Independent? True
```

### Exercise 3 – Bayes' rule for a fraud detector

```python
# Task: apply Bayes' rule to find P(fraud | flagged)
p_fraud = 0.001            # base rate: 0.1% of transactions are fraud
p_flag_given_fraud = 0.95  # detector catches 95% of real fraud
p_flag_given_ok = 0.05     # detector also flags 5% of legit transactions

p_flag = p_flag_given_fraud * p_fraud + p_flag_given_ok * (1 - p_fraud)
p_fraud_given_flag = (p_flag_given_fraud * p_fraud) / p_flag  # Bayes' rule

print("P(fraud | flagged):", round(p_fraud_given_flag, 3))

# Expected output:
# P(fraud | flagged): 0.019
```

## Next

Continue to **Distributions (normal, binomial, Poisson)** to see how probability rules
build up into full probability models.
