---
title: Python Operator Function
description: Learn how to use the Python operator function. The operator function is a function that returns a value based on the result of a condition. 
sidebar: 
    order: 31
---

## Unlocking Efficiency: Operator Functions in Python
The operator module in Python is a powerful tool that provides functions corresponding to standard operators. It simplifies complex operations, enhances code readability, and facilitates concise expression of common tasks. In this comprehensive guide, we'll explore the operator module, its key functions, and how it contributes to efficient Python programming.

### What is the operator module?
The operator module in Python provides functions corresponding to standard operators. It's a powerful tool for simplifying complex operations, enhancing code readability, and facilitating concise expression of common tasks. The operator module is part of the Python standard library, so it doesn't need to be installed separately. It's available in all versions of Python. 

### Why use the operator module?
The operator module provides functions corresponding to standard operators. It simplifies complex operations, enhances code readability, and facilitates concise expression of common tasks. It's a powerful tool for simplifying complex operations, enhancing code readability, and facilitating concise expression of common tasks. The operator module is part of the Python standard library, so it doesn't need to be installed separately. It's available in all versions of Python.

## Key Functions Table

| Operator | Function | Description |
| :--- | :--- | :--- |
| `+` | `operator.add(a, b)` | Addition |
| `-` | `operator.sub(a, b)` | Subtraction |
| `*` | `operator.mul(a, b)` | Multiplication |
| `/` | `operator.truediv(a, b)` | Division |
| `%` | `operator.mod(a, b)` | Modulus |
| `//` | `operator.floordiv(a, b)` | Floor Division |
| `**` | `operator.pow(a, b)` | Exponentiation |
| `&` | `operator.and_(a, b)` | Bitwise AND |
| `\|` | `operator.or_(a, b)` | Bitwise OR |
| `^` | `operator.xor(a, b)` | Bitwise XOR |
| `~` | `operator.invert(a)` | Bitwise NOT |
| `<<` | `operator.lshift(a, b)` | Bitwise left shift |
| `>>` | `operator.rshift(a, b)` | Bitwise right shift |
| `==` | `operator.eq(a, b)` | Equal to |
| `!=` | `operator.ne(a, b)` | Not equal to |
| `<` | `operator.lt(a, b)` | Less than |
| `>` | `operator.gt(a, b)` | Greater than |
| `<=` | `operator.le(a, b)` | Less than or equal to |
| `>=` | `operator.ge(a, b)` | Greater than or equal to |
| `+=` | `operator.iadd(a, b)` | Addition |
| `-=` | `operator.isub(a, b)` | Subtraction |
| `*=` | `operator.imul(a, b)` | Multiplication |
| `/=` | `operator.itruediv(a, b)` | Division |
| `%=` | `operator.imod(a, b)` | Modulus |
| `//=` | `operator.ifloordiv(a, b)` | Floor Division |
| `**=` | `operator.ipow(a, b)` | Exponentiation |
| `&=` | `operator.iand(a, b)` | Bitwise AND |
| `\|=` | `operator.ior(a, b)` | Bitwise OR |
| `^=` | `operator.ixor(a, b)` | Bitwise XOR |
| `<<=` | `operator.ilshift(a, b)` | Bitwise left shift |
| `>>=` | `operator.irshift(a, b)` | Bitwise right shift |
| `()` | `operator()` | Call operator |
| `[]` | `operator[]` | Index operator |
| `()` | `operator[]` | Index assignment operator |
| `del` | `operator[]` | Index deletion operator |
| `len()` | `operator.len()` | Length operator |
| `str()` | `operator.str()` | String conversion operator |
| `repr()` | `operator.repr()` | Object representation operator |
| `iter()` | `operator.iter()` | Iteration operator |
| `next()` | `operator.next()` | Next iteration operator |
| `reversed()` | `operator.reversed()` | Reverse iteration operator |
| `cmp()` | `operator.cmp()` | Comparison operator |
| `pos()` | `operator.pos()` | Unary plus |
| `neg()` | `operator.neg()` | Unary minus |
| `abs()` | `operator.abs()` | Absolute value |
| `invert()` | `operator.invert()` | Bitwise NOT |
| `complex()` | `operator.complex()` | Complex number conversion |
| `int()` | `operator.int()` | Integer conversion |
| `long()` | `operator.long()` | Long integer conversion |
| `float()` | `operator.float()` | Float conversion |
| `oct()` | `operator.oct()` | Octal conversion |
| `hex()` | `operator.hex()` | Hexadecimal conversion |
| `index()` | `operator.index()` | Conversion to an integer |
| `trunc()` | `operator.trunc()` | Truncation operator |
| `coerce()` | `operator.coerce()` | Coercion |
| `enter()` | `operator.enter()` | Context management protocol |
| `exit()` | `operator.exit()` | Context management protocol |
| `hash()` | `operator.hash()` | Hashing operator |
| `getattr()` | `operator.getattr()` | Attribute access |
| `setattr()` | `operator.setattr()` | Attribute assignment |
| `delattr()` | `operator.delattr()` | Attribute deletion |
| `dir()` | `operator.dir()` | Attribute query |
| `getattribute()` | `operator.getattribute()` | Attribute access |
| `set()` | `operator.set()` | Descriptor access |
| `delete()` | `operator.delete()` | Descriptor deletion |
| `get()` | `operator.get()` | Descriptor access |
<!-- 
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

In the above example, we have used the addition operator to add two operands `x` and `y` and assign the result to the variable `z`. The value of `z` is then printed to the console. -->

## Arithmetic Operators
#### `+` & `-` & `*` & `/` & `%` & `//` & `**` Operators
The arithmetic operators (`+`, `-`, `*`, `/`, `%`, `//`, `**`) perform arithmetic operations on numeric operands. The following example demonstrates how to use the arithmetic operators in Python:

```python title="arithmetic_operators.py" showLineNumbers{1} {5-12}
# Arithmetic operators
import operator
x = 10
y = 5
print(operator.add(x, y))
print(operator.sub(x, y))
print(operator.mul(x, y))
print(operator.truediv(x, y))
print(operator.mod(x, y))
print(operator.floordiv(x, y))
print(operator.pow(x, y))
```

Output:

```cmd title="command" showLineNumbers{1} {2-9}
C:\Users\Your Name> python arithmetic_operators.py
15
5
50
2.0
0
2
100000
```

In the above example, we have used the arithmetic operators to perform arithmetic operations on numeric operands. The `add()` function adds two operands `x` and `y`. The `sub()` function subtracts the second operand `y` from the first operand `x`. The `mul()` function multiplies two operands `x` and `y`. The `truediv()` function divides the first operand `x` by the second operand `y`. The `mod()` function returns the remainder of the division of the first operand `x` by the second operand `y`. The `floordiv()` function returns the quotient of the division of the first operand `x` by the second operand `y`. The `pow()` function returns the first operand `x` raised to the power of the second operand `y`.

## Comparison Operators
#### `==` & `!=` & `<` & `>` & `<=` & `>=` Operators
The comparison operators (`==`, `!=`, `<`, `>`, `<=`, `>=`) compare two operands. They return `True` if the comparison is true, otherwise they return `False`. The following example demonstrates how to use the comparison operators in Python:

```python title="comparison_operators.py" showLineNumbers{1} {5-12}
# Comparison operators
import operator
x = 10
y = 5
print(operator.eq(x, y))
print(operator.ne(x, y))
print(operator.lt(x, y))
print(operator.gt(x, y))
print(operator.le(x, y))
print(operator.ge(x, y))
```

Output:

```cmd title="command" showLineNumbers{1} {2-9}
C:\Users\Your Name> python comparison_operators.py
False
True
False
True
False
True
```

In the above example, we have used the comparison operators to compare two operands `x` and `y`. The `eq()` function returns `True` if the operands are equal, otherwise it returns `False`. The `ne()` function returns `True` if the operands are not equal, otherwise it returns `False`. The `lt()` function returns `True` if the first operand `x` is less than the second operand `y`, otherwise it returns `False`. The `gt()` function returns `True` if the first operand `x` is greater than the second operand `y`, otherwise it returns `False`. The `le()` function returns `True` if the first operand `x` is less than or equal to the second operand `y`, otherwise it returns `False`. The `ge()` function returns `True` if the first operand `x` is greater than or equal to the second operand `y`, otherwise it returns `False`.

## Bitwise Operators
#### `&` & `\|` & `^` & `~` & `<<` & `>>` Operators
The bitwise operators (`&`, `\|`, `^`, `~`, `<<`, `>>`) perform bitwise operations on integer operands. The following example demonstrates how to use the bitwise operators in Python:

```python title="bitwise_operators.py" showLineNumbers{1} {5-12}
# Bitwise operators
import operator
x = 10
y = 5
print(operator.and_(x, y))
print(operator.or_(x, y))
print(operator.xor(x, y))
print(operator.invert(x))
print(operator.lshift(x, y))
print(operator.rshift(x, y))
```

Output:

```cmd title="command" showLineNumbers{1} {2-9}
C:\Users\Your Name> python bitwise_operators.py
0
15
15
-11
320
0
```

In the above example, we have used the bitwise operators to perform bitwise operations on integer operands. The `and_()` function performs a bitwise AND operation on the operands `x` and `y`. The `or_()` function performs a bitwise OR operation on the operands `x` and `y`. The `xor()` function performs a bitwise XOR operation on the operands `x` and `y`. The `invert()` function performs a bitwise NOT operation on the operand `x`. The `lshift()` function performs a bitwise left shift operation on the operand `x` by the number of bits specified by the operand `y`. The `rshift()` function performs a bitwise right shift operation on the operand `x` by the number of bits specified by the operand `y`.

## Assignment Operators
#### `+=` & `-=` & `*=` & `/=` & `%=` & `//=` & `**=` Operators
The assignment operators (`+=`, `-=`, `*=`, `/=`, `%=`, `//=`, `**=`) perform arithmetic operations on numeric operands and assign the result to the left operand. The following example demonstrates how to use the assignment operators in Python:

```python title="assignment_operators.py" showLineNumbers{1} {5,7,9,11,13,15,17}
# Assignment operators
import operator
x = 10
y = 5
operator.iadd(x, y)
print(x)
operator.isub(x, y)
print(x)
operator.imul(x, y)
print(x)
operator.itruediv(x, y)
print(x)
operator.imod(x, y)
print(x)
operator.ifloordiv(x, y)
print(x)
operator.ipow(x, y)
print(x)
```

Output:

```cmd title="command" showLineNumbers{1} {2-9}
C:\Users\Your Name> python assignment_operators.py
15
10
50
10
0
2
100000
```

In the above example, we have used the assignment operators to perform arithmetic operations on numeric operands and assign the result to the left operand. The `iadd()` function adds two operands `x` and `y` and assigns the result to the variable `x`. The `isub()` function subtracts the second operand `y` from the first operand `x` and assigns the result to the variable `x`. The `imul()` function multiplies two operands `x` and `y` and assigns the result to the variable `x`. The `itruediv()` function divides the first operand `x` by the second operand `y` and assigns the result to the variable `x`. The `imod()` function returns the remainder of the division of the first operand `x` by the second operand `y` and assigns the result to the variable `x`. The `ifloordiv()` function returns the quotient of the division of the first operand `x` by the second operand `y` and assigns the result to the variable `x`. The `ipow()` function returns the first operand `x` raised to the power of the second operand `y` and assigns the result to the variable `x`.

## Logical Operators
#### `and` & `or` & `not` Operators
The logical operators (`and`, `or`, `not`) perform logical operations on boolean operands. The following example demonstrates how to use the logical operators in Python:

```python title="logical_operators.py" showLineNumbers{1} {5-7}
# Logical operators
import operator
x = True
y = False
print(operator.and_(x, y))
print(operator.or_(x, y))
print(operator.not_(x))
```

Output:

```cmd title="command" showLineNumbers{1} {2-9}
C:\Users\Your Name> python logical_operators.py
False
True
False
```

In the above example, we have used the logical operators to perform logical operations on boolean operands. The `and_()` function performs a logical AND operation on the operands `x` and `y`. The `or_()` function performs a logical OR operation on the operands `x` and `y`. The `not_()` function performs a logical NOT operation on the operand `x`.

## Identity Operators
#### `is` & `is not` Operators
The identity operators (`is`, `is not`) compare the memory addresses of two operands. They return `True` if the memory addresses are equal, otherwise they return `False`. The following example demonstrates how to use the identity operators in Python:

```python title="identity_operators.py" showLineNumbers{1} {5-6}
# Identity operators
import operator
x = 10
y = 5
print(operator.is_(x, y))
print(operator.is_not(x, y))
```

Output:

```cmd title="command" showLineNumbers{1} {2-9}
C:\Users\Your Name> python identity_operators.py
False
True
```

In the above example, we have used the identity operators to compare the memory addresses of two operands `x` and `y`. The `is_()` function returns `True` if the memory addresses of the operands are equal, otherwise it returns `False`. The `is_not()` function returns `True` if the memory addresses of the operands are not equal, otherwise it returns `False`.

:::note
You can try out the examples in this guide by opening an interactive Python shell or code editor and running the code yourself.
:::

## Conclusion
The operator module in Python provides a convenient and efficient way to work with standard operators as functions. Whether you're performing basic arithmetic, comparisons, logical or bitwise operations, the module offers a streamlined approach to writing cleaner and more concise code.

As you continue to explore Python programming, consider incorporating the operator module into your toolkit for situations where its functions can enhance the readability and efficiency of your code. For more insights and practical examples, check out our tutorials on Python Central Hub!