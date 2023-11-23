---
title: Python Operator Precedence
description: Learn about Python operator precedence and how to use it. How to use parentheses to override the default operator precedence. What is the order of operations in Python? Which operators have the highest precedence? Which operators have the lowest precedence?
sidebar: 
    order: 29
---

## Navigating the Hierarchy: Operator Precedence in Python
Operator precedence in Python is a crucial aspect of the language's syntax, determining the order in which operations are performed in an expression. Understanding operator precedence is essential for writing accurate and predictable code. In this comprehensive guide, we'll delve into the world of operator precedence, exploring how Python interprets and prioritizes various operators.

## What is Operator Precedence?
Operator precedence is a set of rules that determines the order in which operators are evaluated in an expression. In Python, operators are special symbols that perform arithmetic or logical computations. For example, the `+` symbol is an operator that performs addition, while the `>` symbol is an operator that performs a comparison between two values.

Python's operator precedence rules are similar to those of other programming languages. For example, the multiplication operator `*` has a higher precedence than the addition operator `+`. This means that in the expression `2 + 3 * 4`, Python will first evaluate `3 * 4`, then add the result to `2`, returning `14`.

## Operator Precedence Table
Python's operator precedence rules are summarized in the table below. Operators are listed in order of precedence, with operators of equal precedence grouped together. Operators in the same group are evaluated from left to right.

| Operator | Description |
| :--- | :--- |
| `()` | Parentheses |
| `**` | Exponentiation |
| `~` | Bitwise not |
| `*`, `/`, `%`, `//` | Multiplication, Division, Modulus, Floor division |
| `+`, `-` | Addition, Subtraction |
| `<<`, `>>` | Bitwise shift operators |
| `&` | Bitwise AND |
| `^` | Bitwise XOR |
| `\|` | Bitwise OR |
| `==`, `!=`, `>`, `>=`, `<`, `<=`, `is`, `is not`, `in`, `not in` | Comparisons, Identity, Membership operators |
| `not` | Logical NOT |
| `and` | Logical AND |
| `or` | Logical OR |

## Operator Precedence Examples
Let's look at some examples of operator precedence in Python.

### Parentheses
#### `()` (Parentheses) Operator
Parentheses (`()`) are used to group expressions and override the default operator precedence. Expressions within parentheses are evaluated first. The following example demonstrates how to use parentheses in Python:

```python title="operators.py" showLineNumbers{1} {4}
# Parentheses operator
x = 10
y = 5
z = (x + y) * 2
print(z)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python operators.py
30
```

In the above example, we have used parentheses to group the addition operation `x + y`. This ensures that the addition operation is evaluated first, before the multiplication operation `* 2`.

### Exponentiation
#### `**` (Exponentiation) Operator
The exponentiation operator (`**`) raises the left operand to the power of the right operand. The following example demonstrates how to use the exponentiation operator in Python:

```python title="operators.py" showLineNumbers{1} {4}
# Exponentiation operator
x = 10
y = 5
z = 2 + x ** y
print(z)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python operators.py
100002
```

In the above example, we have used the exponentiation operator to raise the operand `x` to the power of the operand `y`. The result is then added to `2` and assigned to the variable `z`.

### Multiplication
#### `*` (Multiplication) Operator
The multiplication operator (`*`) multiplies two operands. The following example demonstrates how to use the multiplication operator in Python:

```python title="operators.py" showLineNumbers{1} {4}
# Multiplication operator
x = 10
y = 5
z = 5 + x * y + 5
print(z)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python operators.py
60
```

In the above example, we have used the multiplication operator to multiply the operands `x` and `y`. The result is then added to `5` and `5` and assigned to the variable `z`.

### Division
#### `/` (Division) Operator
The division operator (`/`) divides the left operand by the right operand. The following example demonstrates how to use the division operator in Python:

```python title="operators.py" showLineNumbers{1} {4}
# Division operator
x = 10
y = 5
z = 2 + x / y + 2
print(z)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python operators.py
6.0
```

In the above example, we have used the division operator to divide the operand `x` by the operand `y`. The result is then added to `2` and `2` and assigned to the variable `z`.

### Modulus
#### `%` (Modulus) Operator
The modulus operator (`%`) returns the remainder of the division of the left operand by the right operand. The following example demonstrates how to use the modulus operator in Python:

```python title="operators.py" showLineNumbers{1} {4}
# Modulus operator
x = 10
y = 5
z = 2 + x % y + 2
print(z)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python operators.py
6
```

In the above example, we have used the modulus operator to return the remainder of the division of the operand `x` by the operand `y`. The result is then added to `2` and `2` and assigned to the variable `z`.

### Floor Division
#### `//` (Floor Division) Operator
The floor division operator (`//`) divides the left operand by the right operand and returns the integer part of the result. The following example demonstrates how to use the floor division operator in Python:

```python title="operators.py" showLineNumbers{1} {4}
# Floor division operator
x = 10
y = 5
z = 2 + x // y + 2
print(z)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python operators.py
6
```

In the above example, we have used the floor division operator to divide the operand `x` by the operand `y` and assign the result to the variable `z`. The value of `z` is then printed to the console.

:::tip
The floor division operator (`//`) is also known as the integer division operator.
:::

### Comparison Operators
#### `==`, `!=`, `>`, `>=`, `<`, `<=` (Comparison) Operators
Comparison operators are used to compare two values. They return a boolean value (`True` or `False`) depending on whether the comparison is true or false. The following example demonstrates how to use comparison operators in Python:

```python title="operators.py" showLineNumbers{1} {4}
# Comparison operators
x = 10
y = 5
z = x-5 > y
print(z)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python operators.py
False
```

In the above example, we have used the greater than operator (`>`) to compare the operands `x-5` and `y`. The result of the comparison is then assigned to the variable `z`.

### Logical Operators
#### `not`, `and`, `or` (Logical) Operators
Logical operators are used to combine two or more boolean expressions. They return a boolean value (`True` or `False`) depending on the result of the logical operation. The following example demonstrates how to use logical operators in Python:

```python title="operators.py" showLineNumbers{1} {4}
# Logical operators
x = 10
y = 5
z = x > y and x+12 > 0
print(z)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python operators.py
True
```

In the above example, we have used the logical AND operator (`and`) to combine the boolean expressions `x > y` and `x+12 > 0`. The result of the logical operation is then assigned to the variable `z`.

## Overriding Operator Precedence
You can override Python's default operator precedence by using parentheses. Expressions within parentheses are evaluated first. The following example demonstrates how to override operator precedence in Python:

```python title="operators.py" showLineNumbers{1} {4-5}
# Overriding operator precedence
x = 10
y = 5
z = (x + y) * 2 + 5
t = x + y * 2 + 5
print(z)
print(t)
```

Output:

```cmd title="command" showLineNumbers{1} {3-4}
C:\Users\Your Name> python operators.py
30
20
```

In the above example, we have used parentheses to group the addition operation `x + y`. This ensures that the addition operation is evaluated first, before the multiplication operation `* 2`.

## Conclusion
Understanding operator precedence in Python is vital for writing code that behaves as expected. By knowing the hierarchy of operators, you can predict how expressions will be evaluated and avoid unintended results. As you continue your Python programming journey, be mindful of operator precedence, use parentheses when needed, and create code that is both readable and reliable.

For more insights and practical examples, check out our tutorials on Python Central Hub!