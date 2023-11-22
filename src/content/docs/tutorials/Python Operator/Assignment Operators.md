---
title: Python Assignment Operators
description: Learn about Python Assignment Operators with examples. 
sidebar: 
    order: 24
---

## Assignment Operators in Python: Bridging Values and Variables
Assignment operators in Python are the linchpin between variables and values, facilitating the assignment of data to variables and enabling dynamic and flexible programming. These operators not only assign values but also offer concise ways to update variables based on their current values. In this comprehensive guide, we'll delve into the world of assignment operators, their syntax, and how they empower efficient Python programming.

The following table lists the assignment operators in Python:

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


## Assignment Operators
#### `=` (Assignment) Operator
The assignment operator (`=`) assigns the value of the right side operand to the left side operand. The following example demonstrates how to use the assignment operator in Python:

```python title="operators.py" showLineNumbers{1} {2-4}
# Assignment operator
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

In the above example, we have used the assignment operator to assign the value of the right side operand to the left side operand. The value of `x` is `10` and the value of `y` is `5`. The assignment operator adds the values of `x` and `y` and assigns the result to the variable `z`. The value of `z` is then printed to the console.

## Addition Assignment Operators
#### `+=` (Addition Assignment) Operator
The addition assignment operator (`+=`) adds the value of the right side operand to the left side operand and assigns the result to the left side operand. The following example demonstrates how to use the addition assignment operator in Python:

```python title="operators.py" showLineNumbers{1} {4}
# Addition assignment operator
x = 10
y = 5
x += y
print(x)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python operators.py
15
```

In the above example, we have used the addition assignment operator to add the value of the right side operand to the left side operand and assign the result to the left side operand. The value of `x` is `10` and the value of `y` is `5`. The addition assignment operator adds the values of `x` and `y` and assigns the result to the variable `x`. The value of `x` is then printed to the console.

## Subtraction Assignment Operators
#### `-=` (Subtraction Assignment) Operator
The subtraction assignment operator (`-=`) subtracts the value of the right side operand from the left side operand and assigns the result to the left side operand. The following example demonstrates how to use the subtraction assignment operator in Python:

```python title="operators.py" showLineNumbers{1} {4}
# Subtraction assignment operator
x = 10
y = 5
x -= y
print(x)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python operators.py
5
```

In the above example, we have used the subtraction assignment operator to subtract the value of the right side operand from the left side operand and assign the result to the left side operand. The value of `x` is `10` and the value of `y` is `5`. The subtraction assignment operator subtracts the value of `y` from the value of `x` and assigns the result to the variable `x`. The value of `x` is then printed to the console.

## Multiplication Assignment Operators
#### `*=` (Multiplication Assignment) Operator
The multiplication assignment operator (`*=`) multiplies the value of the right side operand with the left side operand and assigns the result to the left side operand. The following example demonstrates how to use the multiplication assignment operator in Python:

```python title="operators.py" showLineNumbers{1} {4}
# Multiplication assignment operator
x = 10
y = 5
x *= y
print(x)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python operators.py
50
```

In the above example, we have used the multiplication assignment operator to multiply the value of the right side operand with the left side operand and assign the result to the left side operand. The value of `x` is `10` and the value of `y` is `5`. The multiplication assignment operator multiplies the value of `x` with the value of `y` and assigns the result to the variable `x`. The value of `x` is then printed to the console.

## Division Assignment Operators
#### `/=` (Division Assignment) Operator
The division assignment operator (`/=`) divides the left side operand with the right side operand and assigns the result to the left side operand. The following example demonstrates how to use the division assignment operator in Python:

```python title="operators.py" showLineNumbers{1} {4}
# Division assignment operator
x = 10
y = 5
x /= y
print(x)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python operators.py
2.0
``` 

In the above example, we have used the division assignment operator to divide the left side operand with the right side operand and assign the result to the left side operand. The value of `x` is `10` and the value of `y` is `5`. The division assignment operator divides the value of `x` with the value of `y` and assigns the result to the variable `x`. The value of `x` is then printed to the console.

## Modulus Assignment Operators
#### `%=` (Modulus Assignment) Operator
The modulus assignment operator (`%=`) takes modulus using two operands and assigns the result to the left side operand. The following example demonstrates how to use the modulus assignment operator in Python:

```python title="operators.py" showLineNumbers{1} {4}
# Modulus assignment operator
x = 10
y = 5
x %= y
print(x)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python operators.py
0
```

In the above example, we have used the modulus assignment operator to take modulus using two operands and assign the result to the left side operand. The value of `x` is `10` and the value of `y` is `5`. The modulus assignment operator takes modulus using the values of `x` and `y` and assigns the result to the variable `x`. The value of `x` is then printed to the console.

## Exponent Assignment Operators
#### `**=` (Exponent Assignment) Operator
The exponent assignment operator (`**=`) performs exponential (power) calculation on operators and assigns the result to the left side operand. The following example demonstrates how to use the exponent assignment operator in Python:

```python title="operators.py" showLineNumbers{1} {4}
# Exponent assignment operator
x = 10
y = 5
x **= y
print(x)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python operators.py
100000
```

In the above example, we have used the exponent assignment operator to perform exponential (power) calculation on operators and assign the result to the left side operand. The value of `x` is `10` and the value of `y` is `5`. The exponent assignment operator performs exponential (power) calculation on the values of `x` and `y` and assigns the result to the variable `x`. The value of `x` is then printed to the console.

## Floor Division Assignment Operators
#### `//=` (Floor Division Assignment) Operator
The floor division assignment operator (`//=`) performs floor division on operators and assigns the result to the left side operand. The following example demonstrates how to use the floor division assignment operator in Python:

```python title="operators.py" showLineNumbers{1} {4}
# Floor division assignment operator
x = 10
y = 5
x //= y
print(x)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python operators.py
2
```

In the above example, we have used the floor division assignment operator to perform floor division on operators and assign the result to the left side operand. The value of `x` is `10` and the value of `y` is `5`. The floor division assignment operator performs floor division on the values of `x` and `y` and assigns the result to the variable `x`. The value of `x` is then printed to the console.

## Bitwise AND Assignment Operators
#### `&=` (Bitwise AND Assignment) Operator
The bitwise AND assignment operator (`&=`) performs bitwise AND on operators and assigns the result to the left side operand. The following example demonstrates how to use the bitwise AND assignment operator in Python:

```python title="operators.py" showLineNumbers{1} {4}
# Bitwise AND assignment operator
x = 10
y = 5
x &= y
print(x)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python operators.py
0
```

In the above example, we have used the bitwise AND assignment operator to perform bitwise AND on operators and assign the result to the left side operand. The value of `x` is `10` and the value of `y` is `5`. The bitwise AND assignment operator performs bitwise AND on the values of `x` and `y` and assigns the result to the variable `x`. The value of `x` is then printed to the console.

## Bitwise OR Assignment Operators
#### `\|=` (Bitwise OR Assignment) Operator
The bitwise OR assignment operator (`\|=`) performs bitwise OR on operators and assigns the result to the left side operand. The following example demonstrates how to use the bitwise OR assignment operator in Python:

```python title="operators.py" showLineNumbers{1} {4}
# Bitwise OR assignment operator
x = 10
y = 5
x |= y
print(x)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python operators.py
15
```

In the above example, we have used the bitwise OR assignment operator to perform bitwise OR on operators and assign the result to the left side operand. The value of `x` is `10` and the value of `y` is `5`. The bitwise OR assignment operator performs bitwise OR on the values of `x` and `y` and assigns the result to the variable `x`. The value of `x` is then printed to the console.

## Bitwise XOR Assignment Operators
#### `^=` (Bitwise XOR Assignment) Operator
The bitwise XOR assignment operator (`^=`) performs bitwise XOR on operators and assigns the result to the left side operand. The following example demonstrates how to use the bitwise XOR assignment operator in Python:

```python title="operators.py" showLineNumbers{1} {4}
# Bitwise XOR assignment operator
x = 10
y = 5
x ^= y
print(x)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python operators.py
15
```

In the above example, we have used the bitwise XOR assignment operator to perform bitwise XOR on operators and assign the result to the left side operand. The value of `x` is `10` and the value of `y` is `5`. The bitwise XOR assignment operator performs bitwise XOR on the values of `x` and `y` and assigns the result to the variable `x`. The value of `x` is then printed to the console.

## Bitwise Right Shift Assignment Operators
#### `>>=` (Bitwise Right Shift Assignment) Operator
The bitwise right shift assignment operator (`>>=`) performs bitwise right shift on operators and assigns the result to the left side operand. The following example demonstrates how to use the bitwise right shift assignment operator in Python:

```python title="operators.py" showLineNumbers{1} {4}
# Bitwise right shift assignment operator
x = 10
y = 5
x >>= y
print(x)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python operators.py
0
```

In the above example, we have used the bitwise right shift assignment operator to perform bitwise right shift on operators and assign the result to the left side operand. The value of `x` is `10` and the value of `y` is `5`. The bitwise right shift assignment operator performs bitwise right shift on the values of `x` and `y` and assigns the result to the variable `x`. The value of `x` is then printed to the console.

## Bitwise Left Shift Assignment Operators
#### `<<=` (Bitwise Left Shift Assignment) Operator
The bitwise left shift assignment operator (`<<=`) performs bitwise left shift on operators and assigns the result to the left side operand. The following example demonstrates how to use the bitwise left shift assignment operator in Python:

```python title="operators.py" showLineNumbers{1} {4}
# Bitwise left shift assignment operator
x = 10
y = 5
x <<= y
print(x)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python operators.py
320
```

In the above example, we have used the bitwise left shift assignment operator to perform bitwise left shift on operators and assign the result to the left side operand. The value of `x` is `10` and the value of `y` is `5`. The bitwise left shift assignment operator performs bitwise left shift on the values of `x` and `y` and assigns the result to the variable `x`. The value of `x` is then printed to the console.

## Conclusion
Assignment operators are the cornerstone of variable manipulation in Python, providing the means to assign values, update variables, and handle multiple assignments. Whether you're incrementing counters, performing complex calculations, or swapping values, assignment operators streamline these operations and contribute to the readability of your code.

As you delve deeper into Python programming, experiment with different assignment operators, explore their applications in real-world scenarios, and use them to enhance the efficiency and clarity of your code. For more hands-on examples and in-depth tutorials, explore our resources on Python Central Hub!