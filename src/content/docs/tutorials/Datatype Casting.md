---
title: Python Datatype Casting
description: Learn how to cast data types in Python. How to convert a string to an integer, float, or boolean. How to convert an integer, float, or boolean to a string. How to convert a string to a list or tuple. How to convert a list or tuple to a string. How to convert a list to a tuple and vice versa. How to convert a list to a dictionary and vice versa. How to convert a dictionary to a tuple and vice versa. How to convert a dictionary to a list and vice versa.
sidebar: 
    order: 32
---

## Navigating Data Types: A Guide to Data Type Casting in Python
Data type casting, also known as type conversion, is a fundamental concept in Python that allows you to change the data type of a variable or value. This process is crucial when working with different data types and ensures the compatibility of variables in various operations. In this comprehensive guide, we'll explore the basics of data type casting in Python, including the built-in functions used for conversion and best practices.

## Understanding Data Types in Python
Before we dive into the details of data type casting, let's take a moment to understand the different data types in Python. Python is a dynamically typed language, which means that the interpreter automatically assigns a data type to a variable based on the value it holds. For example, if you assign the value `5` to a variable, the interpreter will assign the integer data type to that variable. Similarly, if you assign the value `5.0` to a variable, the interpreter will assign the float data type to that variable.

Python supports the following data types:
| Data Type | Description |
| --- | --- |
| `int` | Integer |
| `float` | Floating-point number |
| `str` | String |
| `bool` | Boolean |
| `list` | List |
| `tuple` | Tuple |
| `dict` | Dictionary |
| `set` | Set |
| `frozenset` | Frozen set |
| `bytes` | Bytes |
| `bytearray` | Byte array |
| `complex` | Complex number |
| `range` | Range |
| `NoneType` | None |


## Python Data Type Casting (Implicit Type Conversion)
Python automatically converts one data type to another when it encounters an operation that requires the two data types to be compatible. For example, if you add an integer and a float, Python will convert the integer to a float before performing the addition operation. This process is known as implicit type conversion or implicit data type casting.

The following example demonstrates how Python implicitly converts an integer to a float when performing an addition operation:

```python title="casting.py" showLineNumbers{1}
# implicit type conversion
x = 5
y = 5.0
z = x + y
print(z)
```

Output:

```cmd title="command" showLineNumbers{1}
C:\Users\Your Name> python casting.py
10.0
```

In the above example, we have added an integer and a float. Since the two data types are not compatible, Python implicitly converts the integer to a float before performing the addition operation. The result of the addition operation is then assigned to the variable `z`. The value of `z` is then printed to the console.


## Python Data Type Casting (Explicit Type Conversion)
Python also allows you to explicitly convert one data type to another using built-in functions. This process is known as explicit type conversion or explicit data type casting. The following table lists the built-in functions used for explicit type conversion:

| Function | Description |
| --- | --- |
| `int()` | Converts a value to an integer |
| `float()` | Converts a value to a float |
| `str()` | Converts a value to a string |
| `bool()` | Converts a value to a boolean |
| `list()` | Converts a value to a list |
| `tuple()` | Converts a value to a tuple |
| `dict()` | Converts a value to a dictionary |
| `set()` | Converts a value to a set |
| `frozenset()` | Converts a value to a frozen set |
| `bytes()` | Converts a value to bytes |
| `bytearray()` | Converts a value to a byte array |
| `complex()` | Converts a value to a complex number |
| `range()` | Converts a value to a range |
| `None` | Converts a value to None |


## Integer Conversion
#### `int()` Function
The `int()` function converts a value to an integer. The following example demonstrates how to use the `int()` function in Python:

```python title="casting.py" showLineNumbers{1} {3}
# int() function
x = 5.0
y = int(x)
print(y)
print(type(y))
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\Your Name> python casting.py
5
<class 'int'>
```

In the above example, we have used the `int()` function to convert a float to an integer. The `int()` function takes a single argument and returns an integer. The result of the `int()` function is then assigned to the variable `y`. The value of `y` is then printed to the console.

## Float Conversion
#### `float()` Function
The `float()` function converts a value to a float. The following example demonstrates how to use the `float()` function in Python:

```python title="casting.py" showLineNumbers{1} {3}
# float() function
x = 5
y = float(x)
print(y)
print(type(y))
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\Your Name> python casting.py
5.0
<class 'float'>
```

In the above example, we have used the `float()` function to convert an integer to a float. The `float()` function takes a single argument and returns a float. The result of the `float()` function is then assigned to the variable `y`. The value of `y` is then printed to the console.

## String Conversion
#### `str()` Function
The `str()` function converts a value to a string. The following example demonstrates how to use the `str()` function in Python:

```python title="casting.py" showLineNumbers{1} {3}
# str() function
x = 5
y = str(x)
print(y)
print(type(y))
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\Your Name> python casting.py
5
<class 'str'>
```

In the above example, we have used the `str()` function to convert an integer to a string. The `str()` function takes a single argument and returns a string. The result of the `str()` function is then assigned to the variable `y`. The value of `y` is then printed to the console.

## Boolean Conversion
#### `bool()` Function
The `bool()` function converts a value to a boolean. The following example demonstrates how to use the `bool()` function in Python:

```python title="casting.py" showLineNumbers{1} {3}
# bool() function
x = 5
y = bool(x)
print(y)
print(type(y))
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\Your Name> python casting.py
True
<class 'bool'>
```

In the above example, we have used the `bool()` function to convert an integer to a boolean. The `bool()` function takes a single argument and returns a boolean. The result of the `bool()` function is then assigned to the variable `y`. The value of `y` is then printed to the console.

:::note
The `bool()` function returns `False` if the value is `0`, `0.0`, `None`, `False`, `[]`, `()`, `{}`, or `""`. Otherwise, it returns `True`.
:::

## List Conversion
#### `list()` Function
The `list()` function converts a value to a list. The following example demonstrates how to use the `list()` function in Python:

```python title="casting.py" showLineNumbers{1} {3}
# list() function
x = "Hello"
y = list(x)
print(y)
print(type(y))
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\Your Name> python casting.py
['H', 'e', 'l', 'l', 'o']
<class 'list'>
```

In the above example, we have used the `list()` function to convert a string to a list. The `list()` function takes a single argument and returns a list. The result of the `list()` function is then assigned to the variable `y`. The value of `y` is then printed to the console.

## Tuple Conversion
#### `tuple()` Function
The `tuple()` function converts a value to a tuple. The following example demonstrates how to use the `tuple()` function in Python:

```python title="casting.py" showLineNumbers{1} {3}
# tuple() function
x = "Hello"
y = tuple(x)
print(y)
print(type(y))
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\Your Name> python casting.py
('H', 'e', 'l', 'l', 'o')
<class 'tuple'>
```

In the above example, we have used the `tuple()` function to convert a string to a tuple. The `tuple()` function takes a single argument and returns a tuple. The result of the `tuple()` function is then assigned to the variable `y`. The value of `y` is then printed to the console.

## Dictionary Conversion
#### `dict()` Function
The `dict()` function converts a value to a dictionary. The following example demonstrates how to use the `dict()` function in Python:

```python title="casting.py" showLineNumbers{1} {3}
# dict() function
x = (("name", "John"), ("age", 36)) 
y = dict(x)
print(y)
print(type(y))
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\Your Name> python casting.py
{'name': 'John', 'age': 36}
<class 'dict'>
```

In the above example, we have used the `dict()` function to convert a tuple to a dictionary. The `dict()` function takes a single argument and returns a dictionary. The result of the `dict()` function is then assigned to the variable `y`. The value of `y` is then printed to the console.

## Set Conversion
#### `set()` Function
The `set()` function converts a value to a set. The following example demonstrates how to use the `set()` function in Python:

```python title="casting.py" showLineNumbers{1} {3}
# set() function
x = "Hello"
y = set(x)
print(y)
print(type(y))
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\Your Name> python casting.py
{'e', 'H', 'l', 'o'}
<class 'set'>
```

In the above example, we have used the `set()` function to convert a string to a set. The `set()` function takes a single argument and returns a set. The result of the `set()` function is then assigned to the variable `y`. The value of `y` is then printed to the console.

:::note
The `set()` function removes duplicate values from the set.
:::


## List to Tuple Conversion
#### `tuple()` Function
The `tuple()` function converts a list to a tuple. The following example demonstrates how to use the `tuple()` function in Python:

```python title="casting.py" showLineNumbers{1} {3}
# tuple() function
x = ["apple", "banana", "cherry"]
y = tuple(x)
print(y)
print(type(y))
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\Your Name> python casting.py
('apple', 'banana', 'cherry')
<class 'tuple'>
```

In the above example, we have used the `tuple()` function to convert a list to a tuple. The `tuple()` function takes a single argument and returns a tuple. The result of the `tuple()` function is then assigned to the variable `y`. The value of `y` is then printed to the console.

:::tip
You can try other built-in functions to convert a value to a frozen set, bytes, byte array, complex number, range, or None.
:::

## Conclusion
Data type casting is a crucial skill in Python programming, enabling you to handle diverse data types and ensure the compatibility of variables in different operations. Whether it's processing user input, performing mathematical operations, or working with lists, understanding when and how to use type casting is essential for writing robust and efficient code.

As you continue to explore Python, practice using explicit type casting in various scenarios, and be mindful of potential errors and data loss. For more insights and practical examples, check out our tutorials on Python Central Hub!