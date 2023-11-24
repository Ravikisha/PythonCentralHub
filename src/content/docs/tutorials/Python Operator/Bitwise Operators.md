---
title: Python Bitwise Operators
description: Learn how to use Python bitwise operators. Bitwise operators in Python offer a low-level, efficient means of manipulating individual bits within integers. We use & (Bitwise AND), | (Bitwise OR), ^ (Bitwise XOR), ~ (Bitwise NOT), << (Bitwise Left Shift), >> (Bitwise Right Shift) operators in Python.
sidebar: 
    order: 25
---

## Unleashing the Power of Bitwise Operators in Python
Bitwise operators in Python offer a low-level, efficient means of manipulating individual bits within integers. These operators enable you to perform bit-level operations, making them invaluable in scenarios involving hardware interfaces, cryptography, and other applications where binary representation matters. In this comprehensive guide, we'll explore the world of bitwise operators, their syntax, and their applications in Python programming.

:::tip
Bitwise operators are used to manipulate individual bits within integers. They are often used in conjunction with the `bin()` function to view the binary representation of integers. 
:::

The following table lists the bitwise operators in Python:

| Operator | Description | Example |
| :--- | :--- | :--- |
| `&` | Performs bitwise AND on operands | `x & y` |
| `\|` | Performs bitwise OR on operands | `x \| y` |
| `^` | Performs bitwise XOR on operands | `x ^ y` |
| `~` | Performs bitwise NOT on operands | `~x` |
| `<<` | Performs bitwise left shift on operands | `x << y` |
| `>>` | Performs bitwise right shift on operands | `x >> y` |


## Bitwise AND
#### `&` (Bitwise AND) Operator
The bitwise AND operator (`&`) performs a bitwise AND operation on the binary representations of two integers. The result of this operation is a new integer whose binary representation is the result of the bitwise AND operation. The following example demonstrates how to use the bitwise AND operator in Python:

```python title="operators.py" showLineNumbers{1} {4}
# Bitwise AND operator
x = 10
y = 5
z = x & y
print(z)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python operators.py
0
```

:::note

Table for bitwise AND operation:
|x|y|x & y|
|---|---|---|
|0|0|0|
|0|1|0|
|1|0|0|
|1|1|1|


In this example, we have two integers `x` and `y`. The binary representation of `x` is `1010` and the binary representation of `y` is `0101`. The bitwise AND operation is performed on the binary representations of `x` and `y`. The result of this operation is a new integer whose binary representation is `0000`. The decimal representation of `0000` is `0`.

|x|1|0|1|0|
|---|---|---|---|---|
|y|0|1|0|1|
|z|0|0|0|0|
:::

In the above example, we have used the bitwise AND operator to perform a bitwise AND operation on the binary representations of two integers `x` and `y`. The result of this operation is a new integer whose binary representation is the result of the bitwise AND operation. The result of the bitwise AND operation is then assigned to the variable `z`. The value of `z` is then printed to the console.

## Bitwise OR
#### `|` (Bitwise OR) Operator
The bitwise OR operator (`|`) performs a bitwise OR operation on the binary representations of two integers. The result of this operation is a new integer whose binary representation is the result of the bitwise OR operation. The following example demonstrates how to use the bitwise OR operator in Python:

```python title="operators.py" showLineNumbers{1} {4}
# Bitwise OR operator
x = 10
y = 5
z = x | y
print(z)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python operators.py
15
```

:::note
Table for bitwise OR operation:
|x|y|x \| y|
|---|---|---|
|0|0|0|
|0|1|1|
|1|0|1|
|1|1|1|

In this example, we have two integers `x` and `y`. The binary representation of `x` is `1010` and the binary representation of `y` is `0101`. The bitwise OR operation is performed on the binary representations of `x` and `y`. The result of this operation is a new integer whose binary representation is `1111`. The decimal representation of `1111` is `15`.

|x|1|0|1|0|
|---|---|---|---|---|
|y|0|1|0|1|
|z|1|1|1|1|

:::

In the above example, we have used the bitwise OR operator to perform a bitwise OR operation on the binary representations of two integers `x` and `y`. The result of this operation is a new integer whose binary representation is the result of the bitwise OR operation. The result of the bitwise OR operation is then assigned to the variable `z`. The value of `z` is then printed to the console.

## Bitwise XOR
#### `^` (Bitwise XOR) Operator
The bitwise XOR operator (`^`) performs a bitwise XOR operation on the binary representations of two integers. The result of this operation is a new integer whose binary representation is the result of the bitwise XOR operation. The following example demonstrates how to use the bitwise XOR operator in Python:

```python title="operators.py" showLineNumbers{1} {4}
# Bitwise XOR operator
x = 10
y = 5
z = x ^ y
print(z)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python operators.py
15
```

:::note
Table for bitwise XOR operation:
|x|y|x ^ y|
|---|---|---|
|0|0|0|
|0|1|1|
|1|0|1|
|1|1|0|

In this example, we have two integers `x` and `y`. The binary representation of `x` is `1010` and the binary representation of `y` is `0101`. The bitwise XOR operation is performed on the binary representations of `x` and `y`. The result of this operation is a new integer whose binary representation is `1111`. The decimal representation of `1111` is `15`.

|x|1|0|1|0|
|---|---|---|---|---|
|y|0|1|0|1|
|z|1|1|1|1|

:::

In the above example, we have used the bitwise XOR operator to perform a bitwise XOR operation on the binary representations of two integers `x` and `y`. The result of this operation is a new integer whose binary representation is the result of the bitwise XOR operation. The result of the bitwise XOR operation is then assigned to the variable `z`. The value of `z` is then printed to the console.

## Bitwise NOT
#### `~` (Bitwise NOT) Operator
The bitwise NOT operator (`~`) performs a bitwise NOT operation on the binary representation of an integer. The result of this operation is a new integer whose binary representation is the result of the bitwise NOT operation. The following example demonstrates how to use the bitwise NOT operator in Python:

```python title="operators.py" showLineNumbers{1} {3}
# Bitwise NOT operator
x = 10
z = ~x
print(z)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python operators.py
-11
```

:::note
Table for bitwise NOT operation:
|x|~x|
|---|---|
|0|1|
|1|0|

In this example, we have an integer `x`. The binary representation of `x` is `1010`. The bitwise NOT operation is performed on the binary representation of `x`. The result of this operation is a new integer whose binary representation is `0101`. The decimal representation of `0101` is `-11`.

|x|1|0|1|0|
|---|---|---|---|---|
|z|0|1|0|1|

:::

In the above example, we have used the bitwise NOT operator to perform a bitwise NOT operation on the binary representation of an integer `x`. The result of this operation is a new integer whose binary representation is the result of the bitwise NOT operation. The result of the bitwise NOT operation is then assigned to the variable `z`. The value of `z` is then printed to the console.

## Bitwise Left Shift
#### `<<` (Bitwise Left Shift) Operator
The bitwise left shift operator (`<<`) performs a bitwise left shift operation on the binary representation of an integer. The result of this operation is a new integer whose binary representation is the result of the bitwise left shift operation. Basically, the bitwise left shift operator shifts the bits of an integer to the left by a specified number of bits and fills the empty bits with zeros.

The following example demonstrates how to use the bitwise left shift operator in Python:

```python title="operators.py" showLineNumbers{1} {4}
# Bitwise left shift operator
x = 10
y = 2
z = x << y
print(z)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python operators.py
40
```

:::note
In this example, we have two integers `x` and `y`. The binary representation of `x` is `1010` and the  `y` is `2`. The bitwise left shift operation is performed on the binary representation of `x`. The result of this operation is a new integer whose binary representation is `101000`. The decimal representation of `101000` is `40`.

|x|1|0|1|0|||
|---|---|---|---|---| ---| ---|
|y||||2|||
|z|1|0|1|0|0|0|

:::

In the above example, we have used the bitwise left shift operator to perform a bitwise left shift operation on the binary representation of an integer `x`. The result of this operation is a new integer whose binary representation is the result of the bitwise left shift operation. The result of the bitwise left shift operation is then assigned to the variable `z`. The value of `z` is then printed to the console.

## Bitwise Right Shift
#### `>>` (Bitwise Right Shift) Operator
The bitwise right shift operator (`>>`) performs a bitwise right shift operation on the binary representation of an integer. The result of this operation is a new integer whose binary representation is the result of the bitwise right shift operation. Basically, the bitwise right shift operator shifts the bits of an integer to the right by a specified number of bits and fills the empty bits with zeros.

The following example demonstrates how to use the bitwise right shift operator in Python:

```python title="operators.py" showLineNumbers{1} {4}
# Bitwise right shift operator
x = 10
y = 2
z = x >> y
print(z)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python operators.py
2
```

:::note
In this example, we have two integers `x` and `y`. The binary representation of `x` is `1010` and the binary representation of `y` is `0010`. The bitwise right shift operation is performed on the binary representation of `x`. The result of this operation is a new integer whose binary representation is `10`. The decimal representation of `10` is `2`.

|x|1|0|1|0|||
|---|---|---|---|---| ---| ---|
|y||||2|||
|z|0|0|0|0|1|0|

:::

In the above example, we have used the bitwise right shift operator to perform a bitwise right shift operation on the binary representation of an integer `x`. The result of this operation is a new integer whose binary representation is the result of the bitwise right shift operation. The result of the bitwise right shift operation is then assigned to the variable `z`. The value of `z` is then printed to the console.


## Conclusion
itwise operators in Python offer a powerful set of tools for working with individual bits in integers. While these operators may not be as commonly used in everyday programming, they become crucial in scenarios where low-level bit manipulation is required.

As you advance in your Python programming journey, experiment with bitwise operators, explore their applications in real-world scenarios, and leverage their efficiency for tasks involving binary representation. For more insights and practical examples, check out our tutorials on Python Central Hub!