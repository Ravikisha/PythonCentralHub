---
title: Operators in Python
description: Learn how to use Python Operators. In this comprehensive guide, we'll delve into the diverse world of operators in Python and explore their applications in different contexts.
sidebar: 
    order: 21
---


## Unleashing the Power of Operators in Python
Operators in Python play a pivotal role in performing various operations on variables and values. They are the building blocks of expressions, allowing you to manipulate data, make comparisons, and control the flow of your programs. In this comprehensive guide, we'll delve into the diverse world of operators in Python and explore their applications in different contexts.

For example:

```python title="operators.py" showLineNumbers{1} {1} 
x = 10 + 5
print(x)
```

Output:

```cmd title="command" showLineNumbers{1}
C:\Users\Your Name> python operators.py
15
```

Here, `+` is the operator that performs addition. `10` and `5` are the operands and `15` is the output of the operation.

In python, we have the following types of operators:

1. **Arithmetic Operators**
2. **Comparison (Relational) Operators**
3. **Assignment Operators**
4. **Logical Operators**
5. **Bitwise Operators**
6. **Membership Operators**
7. **Identity Operators**
8. **Operator Precedence**
9. **Ternary Operator**
10. **Operator Overloading**
11. **Operator Functions**

Let's take a closer look at each of these operators.

## 1. Arithmetic Operators
Arithmetic operators are used to perform mathematical operations like addition, subtraction, multiplication, etc. They operate on numeric values and return a numeric value as the output. 

The following table lists the arithmetic operators in Python:

| Operator | Description | Example |
| :--- | :--- | :--- |
| `+` | Adds two operands or unary plus | `x + y` |
| `-` | Subtracts right operand from the left or unary minus | `x - y` |
| `*` | Multiplies two operands | `x * y` |
| `/` | Divides left operand by right operand | `x / y` |
| `%` | Modulus operator | `x % y` |
| `**` | Exponentiation operator | `x ** y` |
| `//` | Floor division operator | `x // y` |


## 2. Comparison Operators
Comparison operators are used to compare two values. They either return `True` or `False` according to the condition. The following table lists the comparison operators in Python:

| Operator | Description | Example |
| :--- | :--- | :--- |
| `==` | If the values of two operands are equal, then the condition becomes true | `x == y` |
| `!=` | If values of two operands are not equal, then the condition becomes true | `x != y` |
| `>` | If the value of the left operand is greater than the value of the right operand, then the condition becomes true | `x > y` |
| `<` | If the value of the left operand is less than the value of the right operand, then the condition becomes true | `x < y` |
| `>=` | If the value of the left operand is greater than or equal to the value of the right operand, then the condition becomes true | `x >= y` |
| `<=` | If the value of the left operand is less than or equal to the value of the right operand, then the condition becomes true | `x <= y` |


## 3. Assignment Operators
Assignment operators are used to assign values to variables. The following table lists the assignment operators in Python:

| Operator | Description | Example |
| :--- | :--- | :--- |
| `=` | Assigns values from the right side operands to the left side operand | `x = y + z` |
| `+=` | It adds the right operand to the left operand and assigns the result to the left operand | `x += y` is equivalent to `x = x + y` |
| `-=` | It subtracts the right operand from the left operand and assigns the result to the left operand | `x -= y` is equivalent to `x = x - y` |
| `*=` | It multiplies the right operand with the left operand and assigns the result to the left operand | `x *= y` is equivalent to `x = x * y` |
| `/=` | It divides the left operand with the right operand and assigns the result to the left operand | `x /= y` is equivalent to `x = x / y` |
| `%=` | It takes modulus using two operands and assigns the result to the left operand | `x %= y` is equivalent to `x = x % y` |
| `**=` | Performs exponential (power) calculation on operators and assigns the result to the left operand | `x **= y` is equivalent to `x = x ** y` |
| `//=` | It performs floor division on operators and assigns the result to the left operand | `x //= y` is equivalent to `x = x // y` |
| `&=` | Performs bitwise AND on operators and assigns the result to the left operand | `x &= y` is equivalent to `x = x & y` |
| `\|=` | Performs bitwise OR on operators and assigns the result to the left operand | `x \|= y` is equivalent to `x = x \| y` |
| `^=` | Performs bitwise XOR on operators and assigns the result to the left operand | `x ^= y` is equivalent to `x = x ^ y` |
| `>>=` | Performs bitwise right shift on operators and assigns the result to the left operand | `x >>= y` is equivalent to `x = x >> y` |
| `<<=` | Performs bitwise left shift on operators and assigns the result to the left operand | `x <<= y` is equivalent to `x = x << y` |


## 4. Logical Operators
Logical operators are used to combine conditional statements. They either return `True` or `False` according to the condition. The following table lists the logical operators in Python:

| Operator | Description | Example |
| :--- | :--- | :--- |
| `and` | Returns `True` if both statements are true | `x < 5 and  x < 10` |
| `or` | Returns `True` if one of the statements is true | `x < 5 or x < 4` |
| `not` | Reverse the result, returns `False` if the result is true | `not(x < 5 and x < 10)` |


## 5. Bitwise Operators
Bitwise operators are used to perform bitwise calculations on integers. The following table lists the bitwise operators in Python:

| Operator | Description | Example |
| :--- | :--- | :--- |
| `&` | Performs bitwise AND on operands | `x & y` |
| `\|` | Performs bitwise OR on operands | `x \| y` |
| `^` | Performs bitwise XOR on operands | `x ^ y` |
| `~` | Performs bitwise NOT on operands | `~x` |
| `<<` | Performs bitwise left shift on operands | `x << y` |
| `>>` | Performs bitwise right shift on operands | `x >> y` |


## 6. Membership Operators
Membership operators are used to test if a sequence is presented in an object. The following table lists the membership operators in Python:

| Operator | Description | Example |
| :--- | :--- | :--- |
| `in` | Returns `True` if a sequence with the specified value is present in the object | `x in y` |
| `not in` | Returns `True` if a sequence with the specified value is not present in the object | `x not in y` |

## 7. Identity Operators
Identity operators are used to compare the objects, not if they are equal, but if they are actually the same object, with the same memory location. The following table lists the identity operators in Python:

| Operator | Description | Example |
| :--- | :--- | :--- |
| `is` | Returns `True` if both variables are the same object | `x is y` |
| `is not` | Returns `True` if both variables are not the same object | `x is not y` |

## 8. Operator Precedence
Operator precedence is a set of rules that defines the order in which the operators are evaluated in an expression. The following table lists the operator precedence in Python:

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


## 9. Ternary Operator
Ternary operator is also known as conditional operator. It is used to evaluate an expression based on some condition. The following is the syntax of ternary operator in Python:

```python title="ternary_operator.py" showLineNumbers{1}
[on_true] if [expression] else [on_false]
```

Here, `expression` is evaluated and if it is `True`, then `on_true` is returned otherwise `on_false` is returned.

For example:

```python title="ternary_operator.py" showLineNumbers{1} {3}
x = 10
y = 20
big = x if x > y else y
print(big)
```

Output:

```cmd title="command" showLineNumbers{1}
C:\Users\Your Name> python ternary_operator.py
20
```


## 10. Operator Overloading
Operator overloading is a feature in Python that allows the same operator to have different meanings according to the context. For example, the `+` operator will, perform arithmetic addition on two numbers, merge two lists, or concatenate two strings.

In Python, we can redefine or overload most of the built-in operators available in Python. Thus, we can use operators with user-defined types as well.

For example, suppose we have created a class named `Vector` to represent two-dimensional vectors. Let's overload the `+` operator to perform vector addition.

```python title="operator_overloading.py" showLineNumbers{1} {6-7}
class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

first = Vector(2, 3)
second = Vector(4, 5)
result = first + second
print(result.x)
print(result.y)
```

Output:

```cmd title="command" showLineNumbers{1}
C:\Users\Your Name> python operator_overloading.py
6
8
```

Here, we have overloaded the `+` operator to add two `Vector` objects. The `__add__()` method is called when `+` operator is used on `Vector` objects.

Similarly, we can overload other operators as well. The following table lists the operators that can be overloaded in Python:

| Operator | Method | Description |
| :--- | :--- | :--- |
| `+` | `__add__(self, other)` | Addition |
| `-` | `__sub__(self, other)` | Subtraction |
| `*` | `__mul__(self, other)` | Multiplication |
| `/` | `__truediv__(self, other)` | Division |
| `%` | `__mod__(self, other)` | Modulus |
| `//` | `__floordiv__(self, other)` | Floor Division |
| `**` | `__pow__(self, other)` | Exponentiation |
| `&` | `__and__(self, other)` | Bitwise AND |
| `\|` | `__or__(self, other)` | Bitwise OR |
| `^` | `__xor__(self, other)` | Bitwise XOR |
| `~` | `__invert__(self)` | Bitwise NOT |
| `<<` | `__lshift__(self, other)` | Bitwise left shift |
| `>>` | `__rshift__(self, other)` | Bitwise right shift |
| `==` | `__eq__(self, other)` | Equal to |
| `!=` | `__ne__(self, other)` | Not equal to |
| `<` | `__lt__(self, other)` | Less than |
| `>` | `__gt__(self, other)` | Greater than |
| `<=` | `__le__(self, other)` | Less than or equal to |
| `>=` | `__ge__(self, other)` | Greater than or equal to |
| `+=` | `__iadd__(self, other)` | Addition | 
| `-=` | `__isub__(self, other)` | Subtraction |
| `*=` | `__imul__(self, other)` | Multiplication |
| `/=` | `__idiv__(self, other)` | Division |
| `%=` | `__imod__(self, other)` | Modulus |
| `//=` | `__ifloordiv__(self, other)` | Floor Division |
| `**=` | `__ipow__(self, other)` | Exponentiation |
| `&=` | `__iand__(self, other)` | Bitwise AND |
| `\|=` | `__ior__(self, other)` | Bitwise OR |
| `^=` | `__ixor__(self, other)` | Bitwise XOR |
| `<<=` | `__ilshift__(self, other)` | Bitwise left shift |
| `>>=` | `__irshift__(self, other)` | Bitwise right shift |
| `()` | `__call__(self, other)` | Call operator |
| `[]` | `__getitem__(self, other)` | Index operator |
| `()` | `__setitem__(self, other)` | Index assignment operator |
| `del` | `__delitem__(self, other)` | Index deletion operator |
| `len()` | `__len__(self, other)` | Length operator |
| `str()` | `__str__(self, other)` | String conversion operator |
| `repr()` | `__repr__(self, other)` | Object representation operator |
| `iter()` | `__iter__(self, other)` | Iteration operator |
| `next()` | `__next__(self, other)` | Next iteration operator |
| `reversed()` | `__reversed__(self, other)` | Reverse iteration operator |
| `cmp()` | `__cmp__(self, other)` | Comparison operator |
| `pos()` | `__pos__(self, other)` | Unary plus |
| `neg()` | `__neg__(self, other)` | Unary minus |
| `abs()` | `__abs__(self, other)` | Absolute value |
| `invert()` | `__invert__(self, other)` | Bitwise NOT |
| `complex()` | `__complex__(self, other)` | Complex number conversion |
| `int()` | `__int__(self, other)` | Integer conversion |
| `long()` | `__long__(self, other)` | Long integer conversion |
| `float()` | `__float__(self, other)` | Float conversion |
| `oct()` | `__oct__(self, other)` | Octal conversion |
| `hex()` | `__hex__(self, other)` | Hexadecimal conversion |
| `index()` | `__index__(self, other)` | Conversion to an integer |
| `trunc()` | `__trunc__(self, other)` | Truncation operator |
| `coerce()` | `__coerce__(self, other)` | Coercion |
| `enter()` | `__enter__(self, other)` | Context management protocol |
| `exit()` | `__exit__(self, other)` | Context management protocol |
| `hash()` | `__hash__(self, other)` | Hashing operator |
| `getattr()` | `__getattr__(self, other)` | Attribute access |
| `setattr()` | `__setattr__(self, other)` | Attribute assignment |
| `delattr()` | `__delattr__(self, other)` | Attribute deletion |
| `dir()` | `__dir__(self, other)` | Attribute query |
| `getattribute()` | `__getattribute__(self, other)` | Attribute access |
| `set()` | `__set__(self, other)` | Descriptor access |
| `delete()` | `__delete__(self, other)` | Descriptor deletion |
| `get()` | `__get__(self, other)` | Descriptor access |

## 11. Operator Functions
Python provides built-in functions for performing various operations. These functions are called operator functions. 
For example, `operator.add(x, y)` is equivalent to `x + y`.
```python title="operator_functions.py" showLineNumbers{1} {1-2}
import operator
print(operator.add(10, 20))
```

Output:

```cmd title="command" showLineNumbers{1}
C:\Users\Your Name> python operator_functions.py
30
```

The following table lists the operator functions in Python:

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


## Conclusion
Operators in Python provide a powerful and flexible means of manipulating data, making decisions, and controlling the flow of your programs. Understanding how to use and combine different operators is essential for writing expressive, efficient, and functional code.

As you explore Python programming, experiment with various operators, understand their behaviors, and leverage their capabilities in your projects. Whether you're performing arithmetic calculations, making logical decisions, or managing data, operators are your allies in creating robust and dynamic Python code.

For more in-depth tutorials and practical examples, check out our resources on Python Central Hub!