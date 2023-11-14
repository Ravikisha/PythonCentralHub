---
title: Python Numbers
description: Learn about Python numbers - integers, floating-point numbers, and complex numbers.
sidebar: 
    order: 11
---
## Understanding Python Numbers

Numbers are a fundamental and versatile data type in Python, enabling a wide range of mathematical operations and computations. In Python, numbers can be categorized into integers, floating-point numbers, and complex numbers. Let's explore these numeric data types and how they can be utilized in Python.

## Integers
#### `int`

Integers in Python are whole numbers, both positive and negative, without any decimal component. You can perform various arithmetic operations on integers, such as addition, subtraction, multiplication, and division.

```python title="numbers.py" showLineNumbers{1}
a = 5
b = -10
result = a + b  # Result is -5
```

Python allows unlimited precision for integers, meaning they can be as large as your system's memory allows.

## Floating-Point Numbers
#### `float`

Floating-point numbers represent real numbers with a decimal point or in exponential form. They are used to handle both integer and fractional values.

```python title="numbers.py" showLineNumbers{1}
pi = 3.14159
radius = 2.5
area = pi * (radius ** 2)  # Calculating the area of a circle
```

While floating-point numbers are powerful for scientific and mathematical computations, they may introduce precision issues due to the binary representation of real numbers.

## Complex Numbers
#### `complex`

Complex numbers have both a real and an imaginary part, represented as `a + bj`, where `a` and `b` are real numbers, and `j` is the imaginary unit.

```python title="numbers.py" showLineNumbers{1}
z = 3 + 4j
```

You can perform operations like addition, subtraction, multiplication, and division on complex numbers.

```python title="numbers.py" showLineNumbers{1}
w = 1 - 2j
result = z * w  # Result is (11-2j)
```

## Numeric Operations

Python supports a wide range of operations on numeric data types. Here are some common examples:

- **Arithmetic Operations:**
  ```python title="numbers.py" showLineNumbers{1}
  a = 10
  b = 3
  addition = a + b
  subtraction = a - b
  multiplication = a * b
  division = a / b
  ```

- **Exponential Operation:**
  ```python title="numbers.py" showLineNumbers{1}
  square = 4 ** 2  # Result is 16
  ```

- **Modulo Operation:**
  ```python title="numbers.py" showLineNumbers{1}
  remainder = 10 % 3  # Result is 1
  ```

## Numeric Comparisons
In Python, you can compare numeric values using the following comparison operators:
```python title="numbers.py" showLineNumbers{1}
a = 10
b = 5
print(a > b)  # True
```

## Python Number Casting
You can convert numeric values from one data type to another using the following built-in functions:

- `int()` - converts to an integer
- `float()` - converts to a floating-point number
- `complex()` - converts to a complex number

```python title="numbers.py" showLineNumbers{1}
num_int = 10
num_float = float(num_int)  # Convert integer to float
num_complex = complex(num_int)  # Convert integer to complex
```

```python title="numbers.py" showLineNumbers{1}
num_float = 10.5
num_int = int(num_float)  # Convert float to integer
num_complex = complex(num_float)  # Convert float to complex
```

```python title="numbers.py" showLineNumbers{1}
num_complex = 3 + 4j
num_int = int(num_complex)  # Raises TypeError
num_float = float(num_complex)  # Raises TypeError
```
```python title="numbers.py" showLineNumbers{1}
num_str = "42"
num_int = int(num_str)  # Convert string to integer
num_float = float(num_str)  # Convert string to float
num_complex = complex(num_str)  # Convert string to complex
```

## Mathematical Functions

Python's `math` module provides a plethora of mathematical functions, including square root, logarithms, trigonometric functions, and more.

```python title="numbers.py" showLineNumbers{1}
import math
sqrt_result = math.sqrt(25)  # Result is 5.0
```
:::caution
The `math` module only works with floating-point numbers. If you want to perform mathematical operations on integers, use the `cmath` module instead.
:::
:::note
For more information on the `math` module, check out our [Python Math Module Tutorial](https://docs.python.org/3/library/math.html).
:::

## Random Numbers
Python's `random` module provides functions for generating random numbers. For example, you can use the `random()` function to generate a random floating-point number between 0 and 1.

```python title="numbers.py" showLineNumbers{1}
import random
print(random.random())  # Prints a random number between 0 and 1
print(random.randrange(1, 10))  # Prints a random integer between 1 and 10
```
:::note
For more information on the `random` module, check out our [Python Random Module Tutorial](https://docs.python.org/3/library/random.html).
:::



## Conclusion

Numbers in Python are a versatile and integral part of the language's functionality. Whether you're dealing with simple integer calculations or complex mathematical operations involving floating-point or complex numbers, Python provides a straightforward and expressive syntax. Understanding how to work with numbers is crucial for various applications, including scientific computing, data analysis, and algorithmic problem-solving.

As you continue your Python journey, explore the rich set of numeric operations and mathematical functions Python offers. Gain proficiency in leveraging numeric data types to solve diverse problems and unlock the full potential of numerical computing in Python.

For more in-depth tutorials and practical examples, check out our resources on Python Central Hub!