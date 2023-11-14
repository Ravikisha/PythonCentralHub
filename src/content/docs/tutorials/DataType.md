---
title: Python Data Types
description: An introduction to data types in Python.
sidebar: 
    order: 10
---

# Understanding Data Types in Python

Data types in Python are a fundamental concept that plays a crucial role in defining the nature of variables and how they behave during operations. Python is a dynamically-typed language, which means that the interpreter can determine the type of a variable at runtime. This flexibility allows for more concise and expressive code. Let's delve into the essential data types in Python.

## Numeric Data Types

### Integers
#### `int`

Integers represent whole numbers without any fractional part. They can be positive or negative.

```python title="datatype.py" showLineNumbers{1} {1-2}
age = 25
population = -1000
```
**or** you can use the `int()` function to convert a string to an integer.
```python title="datatype.py" showLineNumbers{1} {1-2}
age = int(25)
population = int(-1000)
```

### Floating-Point Numbers
#### `float`

Floating-point numbers are used to represent real numbers with a decimal point.

```python title="datatype.py" showLineNumbers{1} {1-2}
pi = 3.14
temperature = -15.5
```
**or** you can use the `float()` function to convert a string to a floating-point number.
```python title="datatype.py" showLineNumbers{1} {1-2}
pi = float(3.14)
temperature = float(-15.5)
```


### Complex Numbers
#### `complex`

Complex numbers have both a real and an imaginary part.

```python title="datatype.py" showLineNumbers{1} {1}
z = 3 + 4j
```
**or** you can use the `complex()` function to create a complex number.
```python title="datatype.py" showLineNumbers{1} {1}
z = complex(3, 4)
```

## Sequence Types

### Strings
#### `str`

Strings are sequences of characters and are enclosed in single or double quotes.

```python title="datatype.py" showLineNumbers{1} {1-2}
name = "John"
message = 'Hello, Python!'
```
**or** you can use the `str()` function to convert a number to a string.
```python title="datatype.py" showLineNumbers{1} {1-2}
name = str("John")
message = str('Hello, Python!')
```

### Lists
#### `list`

Lists are ordered, mutable sequences that can contain elements of different data types.

```python title="datatype.py" showLineNumbers{1} {1-2}
fruits = ['apple', 'banana', 'orange']
mixed_list = [1, 'two', 3.0, [4, 5]]
```
**or** you can use the `list()` function to convert a tuple to a list.
```python title="datatype.py" showLineNumbers{1} {1-2}
fruits = list(('apple', 'banana', 'orange'))
mixed_list = list((1, 'two', 3.0, [4, 5]))
```


### Tuples
#### `tuple`

Tuples are ordered, immutable sequences. Once created, their elements cannot be changed.

```python title="datatype.py" showLineNumbers{1} {1-2}
coordinates = (3, 4)
RGB_color = (255, 0, 0)
```
**or** you can use the `tuple()` function to convert a list to a tuple.
```python title="datatype.py" showLineNumbers{1} {1-2}
coordinates = tuple([3, 4])
RGB_color = tuple([255, 0, 0])
```


## Set Types

### Sets
#### `set`

Sets are unordered collections of unique elements.

```python title="datatype.py" showLineNumbers{1} {1}
unique_numbers = {1, 2, 3, 4, 5}
```
**or** you can use the `set()` function to create a set.
```python title="datatype.py" showLineNumbers{1} {1}
unique_numbers = set([1, 2, 3, 4, 5])
```

## Mapping Type

### Dictionary
#### `dict`

Dictionaries are unordered collections of key-value pairs.

```python title="datatype.py" showLineNumbers{1} {1}
person = {'name': 'Alice', 'age': 30, 'city': 'Wonderland'}
```
**or** you can use the `dict()` function to create a dictionary.
```python title="datatype.py" showLineNumbers{1} {1}
person = dict({'name': 'Alice', 'age': 30, 'city': 'Wonderland'})
```


## Boolean Type

### Boolean
#### `bool`

Boolean values represent truth or falsehood and are used in logical operations.

```python title="datatype.py" showLineNumbers{1} {1-2}
is_raining = True
has_pet = False
```
**or** you can use the `bool()` function to convert a number to a boolean.
```python title="datatype.py" showLineNumbers{1} {1-2}
is_raining = bool(1)
has_pet = bool(0)
```


## Special Types

### None Type 
#### `NoneType`

The `None` type represents the absence of a value or a null value.

```python title="datatype.py" showLineNumbers{1} {1}
result = None
```


## Type Conversion

Python allows you to convert between different data types using built-in functions like `int()`, `float()`, `str()`, etc.

```python title="datatype.py" showLineNumbers{1} {2}
num_str = "42"
num_int = int(num_str)
```

## Checking Data Types

You can check the data type of a variable using the `type()` function.

```python title="datatype.py" showLineNumbers{1} {2}
age = 25
print(type(age))  # <class 'int'>
```

## Operations on Data Types

Different data types support various operations. For example, you can concatenate strings, perform arithmetic operations on numbers, and use logical operators with booleans.

```python title="datatype.py" showLineNumbers{1} {3}
greeting = "Hello, "
name = "Alice"
full_greeting = greeting + name  # Concatenation of strings
```

## Data Type Table
There are many more data types in Python, but the ones listed above are the most commonly used ones. The following table summarizes the data types in Python.

| Data Type &nbsp; &nbsp; &nbsp; &nbsp; | Description | Example |
| --- | --- | --- |
| `int` | Integer | `age = 25` |
| `float` | Floating-point number | `pi = 3.14` |
| `complex` | Complex number | `z = 3 + 4j` |
| `str` | String | `name = "Alice"` |
| `list` | List | `fruits = ['apple', 'banana', 'orange']` |
| `tuple` | Tuple | `coordinates = (3, 4)` |
| `set` | Set | `unique_numbers = {1, 2, 3, 4, 5}` |
| `frozenset` | Frozen set | `unique_numbers = frozenset({1, 2, 3, 4, 5})` |
| `dict` | Dictionary | `person = {'name': 'Alice', 'age': 30, 'city': 'Wonderland'}` |
| `bool` | Boolean | `is_raining = True` |
| `NoneType` | None | `result = None` |
| `range` | Range | `numbers = range(1, 10)` |
| `bytes` | Bytes | `data = b'Hello, Python!'` |
| `bytearray` | Byte array | `data = bytearray(10)` |
| `memoryview` | Memory view | `data = memoryview(bytes(10))` |



## Conclusion

Understanding Python's data types is fundamental to writing effective and efficient code. Python's flexibility in handling various data types makes it suitable for a wide range of applications, from simple scripts to complex data analysis and machine learning tasks. As you continue your journey in Python programming, a solid grasp of data types will empower you to manipulate and process data effectively.

Explore more Python concepts and practical examples in our tutorials on Python Central Hub!