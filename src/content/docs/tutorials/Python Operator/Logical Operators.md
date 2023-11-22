---
title: Python Logical Operators
description: Learn how to use Python logical operators. Here we will explore the realm of logical operators, their syntax, and how they empower expressive Python programming. See how to use the and, or, and not operators in Python.
sidebar: 
    order: 24
---
# Navigating Logic: Understanding Logical Operators in Python

Logical operators in Python provide the tools for evaluating and combining Boolean values, allowing you to make decisions based on multiple conditions. These operators, including `and`, `or`, and `not`, play a crucial role in controlling the flow of your programs and creating dynamic, responsive code. In this comprehensive guide, we'll explore the realm of logical operators, their syntax, and how they empower expressive Python programming.

::: tip
Logical operators are used to evaluate Boolean values and return a Boolean result. It always return `True` or `False`. They are often used in conjunction with comparison operators to create complex conditions. It is important to note that logical operators are short-circuiting, meaning that they stop evaluating as soon as they reach a result.
:::

 The following table lists the logical operators in Python:

| Operator | Description | Example |
| :--- | :--- | :--- |
| `and` | Returns `True` if both statements are true | `x < 5 and  x < 10` |
| `or` | Returns `True` if one of the statements is true | `x < 5 or x < 4` |
| `not` | Reverse the result, returns `False` if the result is true | `not(x < 5 and x < 10)` |


## and Operator
#### `and` Operator
The `and` operator returns `True` if both operands are `True`. Otherwise, it returns `False`. The following example demonstrates how to use the `and` operator in Python:

```python title="operators.py" showLineNumbers{1} {4-5}
# and operator
x = 10
y = 5
z = x < 10 and y > 1
t = x < 10 and y < 1
print(z)
print(t)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\Your Name> python operators.py
True
False
```

In the above example, we have used the `and` operator to combine two conditions. Since both conditions are `True`, the result of the `and` operator is `True`. The result of the `and` operator is then assigned to the variable `z`. The value of `z` is then printed to the console.

:::tip
The `and` operator is in other programming languages, such as JavaScript and PHP, is also known as the `&&` operator.
:::

## or Operator
#### `or` Operator
The `or` operator returns `True` if one of the operands is `True`. Otherwise, it returns `False`. The following example demonstrates how to use the `or` operator in Python:

```python title="operators.py" showLineNumbers{1} {4-5}
# or operator
x = 10
y = 5
z = x < 10 or y < 1
t = x > 10 or y < 1
print(z)
print(t)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\Your Name> python operators.py
True
False
```

In the above example, we have used the `or` operator to combine two conditions. Since one of the conditions is `True`, the result of the `or` operator is `True`. The result of the `or` operator is then assigned to the variable `z`. The value of `z` is then printed to the console.

:::tip
The `or` operator is in other programming languages, such as JavaScript and PHP, is also known as the `||` operator.
:::

## not Operator
#### `not` Operator
The `not` operator returns `True` if the operand is `False`. Otherwise, it returns `False`. The following example demonstrates how to use the `not` operator in Python:

```python title="operators.py" showLineNumbers{1} {4-5}
# not operator
x = 10
y = 5
z = not(x < 10 and y < 1)
t = not(x > 10 and y < 1)
print(z)
print(t)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\Your Name> python operators.py
True
True
```

In the above example, we have used the `not` operator to reverse the result of the `and` operator. Since the result of the `and` operator is `False`, the result of the `not` operator is `True`. The result of the `not` operator is then assigned to the variable `z`. The value of `z` is then printed to the console.

:::tip
The `not` operator is in other programming languages, such as JavaScript and PHP, is also known as the `!` operator.
:::

## Short-Circuiting
#### `and` and `or` short-circuiting
Logical operators in Python are short-circuiting, meaning that they stop evaluating as soon as they reach a result. This is useful when you want to check multiple conditions and stop evaluating as soon as one of them is `True`. The following example demonstrates how to use short-circuiting in Python:

```python title="operators.py" showLineNumbers{1} {4-5}
# Short-circuiting
x = 10
y = 5
z = x < 10 and y < 1
t = x > 10 and y < 1
print(z)
print(t)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\Your Name> python operators.py
False
False
```

In the above example, we have used the `and` operator to combine two conditions. Since the first condition is `False`, the result of the `and` operator is `False`. The result of the `and` operator is then assigned to the variable `z`. The value of `z` is then printed to the console.


## Combining Logical Operators
#### `and` and `or` operators combined
Logical operators can be combined to create complex conditions. The following example demonstrates how to combine logical operators in Python:

```python title="operators.py" showLineNumbers{1} {4-5}
# Combining logical operators
x = 10
y = 5
z = x < 10 and y < 1 or x > 10 and y < 1
t = x < 10 and y < 1 or x > 10 and y > 1
print(z)
print(t)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\Your Name> python operators.py
False
True
```

In the above example, we have combined the `and` and `or` operators to create complex conditions. Since one of the conditions is `True`, the result of the `or` operator is `True`. The result of the `or` operator is then assigned to the variable `z`. The value of `z` is then printed to the console.


## Conclusion

Logical operators in Python are essential tools for creating flexible and responsive code. Whether you're combining conditions, controlling the flow of your programs, or making decisions based on multiple criteria, logical operators provide the means to navigate the complexities of Boolean values.

As you continue your Python journey, experiment with different combinations of logical operators, explore their applications in real-world scenarios, and use them to create dynamic and expressive code. For more insights and practical examples, check out our tutorials on Python Central Hub!