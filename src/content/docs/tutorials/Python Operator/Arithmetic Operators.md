---
title: Python Arithmetic Operators
description: Learn how to use arithmetic operators in Python. In this tutorial, you will learn how to use arithmetic operators in Python. Arithmetic operators are used to perform mathematical operations like addition, subtraction, multiplication, etc.
sidebar: 
    order: 22
---

Arithmetic operators in Python are the workhorses of mathematical calculations, allowing you to perform a wide range of operations on numerical values. Whether you're adding, subtracting, multiplying, dividing, or working with more advanced calculations, understanding and mastering these operators is fundamental to effective Python programming. In this comprehensive guide, we'll explore the intricacies of arithmetic operators and how they can be applied in various scenarios.

:::tip
Most of the arithmetic operators in Python are the same as in other programming languages (like C, C++, Java, etc.). However, there are a few differences that you should be aware of. For example, the division operator (`/`) in Python returns a floating-point value, whereas in other languages, it returns an integer value. We'll discuss these differences in detail later in this tutorial.
:::

:::note
Most of the arithmetic operators in Python are binary operators, meaning they require two operands. However, the unary minus operator (`-`) is a unary operator, meaning it requires only one operand.
:::

The following table lists the arithmetic operators in Python:

| Operator | Description | Example |
| :--- | :--- | :--- |
| `+` | Adds two operands or unary plus | `x + y` |
| `-` | Subtracts right operand from the left or unary minus | `x - y` |
| `*` | Multiplies two operands | `x * y` |
| `/` | Divides left operand by right operand | `x / y` |
| `//` | Floor division operator | `x // y` |
| `%` | Modulus operator | `x % y` |
| `**` | Exponentiation operator | `x ** y` |


## Addition
#### `+` (Addition) Operator
The addition operator (`+`) adds two operands. It can also be used as a unary operator to represent a positive value. The following example demonstrates how to use the addition operator in Python:

```python title="operators.py" showLineNumbers{1} {4} 
# Addition operator
x = 10
y = 5
z = x + y
print(z)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python operators.py
15
```

In the above example, we have used the addition operator to add two operands `x` and `y` and assign the result to the variable `z`. The value of `z` is then printed to the console.

## Subtraction
#### `-` (Subtraction) Operator
The subtraction operator (`-`) subtracts the right operand from the left operand. It can also be used as a unary operator to represent a negative value. The following example demonstrates how to use the subtraction operator in Python:

```python title="operators.py" showLineNumbers{1} {4}
# Subtraction operator
x = 10
y = 5
z = x - y
print(z)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python operators.py
5
```

In the above example, we have used the subtraction operator to subtract the operand `y` from the operand `x` and assign the result to the variable `z`. The value of `z` is then printed to the console.

## Multiplication
#### `*` (Multiplication) Operator
The multiplication operator (`*`) multiplies two operands. The following example demonstrates how to use the multiplication operator in Python:

```python title="operators.py" showLineNumbers{1} {4}
# Multiplication operator
x = 10
y = 5
z = x * y
print(z)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python operators.py
50
```

In the above example, we have used the multiplication operator to multiply the operands `x` and `y` and assign the result to the variable `z`. The value of `z` is then printed to the console.


## Division
#### `/` (Division) Operator
The division operator (`/`) divides the left operand by the right operand. The following example demonstrates how to use the division operator in Python:

```python title="operators.py" showLineNumbers{1} {4}
# Division operator
x = 10
y = 5
z = x / y
print(z)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python operators.py
2.0
```

In the above example, we have used the division operator to divide the operand `x` by the operand `y` and assign the result to the variable `z`. The value of `z` is then printed to the console.

:::tip
In Python, the division operator (`/`) always returns a floating-point value. If you want to perform integer division, you can use the floor division operator (`//`), which returns an integer value.
:::

#### `//` (Floor Division) Operator
The floor division operator (`//`) divides the left operand by the right operand and returns the integer part of the result. The following example demonstrates how to use the floor division operator in Python:

```python title="operators.py" showLineNumbers{1} {4}
# Floor division operator
x = 10
y = 5
z = x // y
print(z)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python operators.py
2
```

In the above example, we have used the floor division operator to divide the operand `x` by the operand `y` and assign the result to the variable `z`. The value of `z` is then printed to the console.

:::tip
The floor division operator (`//`) is also known as the integer division operator.
:::

## Modulus
#### `%` (Modulus) Operator
The modulus operator (`%`) returns the remainder when the left operand is divided by the right operand. The following example demonstrates how to use the modulus operator in Python:

```python title="operators.py" showLineNumbers{1} {4}
# Modulus operator
x = 10
y = 3
z = x % y
print(z)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python operators.py
1
```

In the above example, we have used the modulus operator to divide the operand `x` by the operand `y` and assign the remainder to the variable `z`. The value of `z` is then printed to the console.

## Exponentiation
#### `**` (Exponentiation) Operator
The exponentiation operator (`**`) raises the left operand to the power of the right operand. The following example demonstrates how to use the exponentiation operator in Python:

```python title="operators.py" showLineNumbers{1} {4}
# Exponentiation operator
x = 10
y = 3
z = x ** y
print(z)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python operators.py
1000
```

In the above example, we have used the exponentiation operator to raise the operand `x` to the power of the operand `y` and assign the result to the variable `z`. The value of `z` is then printed to the console.

## Combining Arithmetic Operators
You can combine multiple arithmetic operators in a single expression. The following example demonstrates how to combine multiple arithmetic operators in Python:

```python title="operators.py" showLineNumbers{1} {4}
# Combining arithmetic operators
x = 10
y = 5
z = x + y * 2
print(z)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python operators.py
20
```

In the above example, we have combined the addition operator (`+`) and the multiplication operator (`*`) in a single expression. The multiplication operator is evaluated first, and then the addition operator is evaluated. The result of the expression is then assigned to the variable `z`, which is then printed to the console.

:::tip
You can use parentheses to change the order of evaluation of arithmetic operators. For example, if you want to add `x` and `y` first and then multiply the result by `2`, you can use parentheses as follows:

```python title="operators.py" showLineNumbers{1} {4}
# Combining arithmetic operators
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

We are taking about this in detail in the next section. Go to [Operator Precedence](/tutorial/python-operator-precedence) to learn more.
:::

## Conclusion
Arithmetic operators in Python are versatile tools for handling numerical calculations. Whether you're working with basic arithmetic, order of operations, integer division, exponentiation, or compound assignments, understanding how to leverage these operators is crucial for effective programming.

As you dive deeper into Python programming, experiment with arithmetic operators, explore their applications in real-world scenarios, and use them to solve mathematical problems in your projects. For more hands-on examples and in-depth tutorials, explore our resources on Python Central Hub!