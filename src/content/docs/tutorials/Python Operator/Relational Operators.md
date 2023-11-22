---
title: Python Relational Operators
description: Learn how to use relational operators in Python. Relational operators are used to compare two values. The result of a relational operator is either `True` or `False`. Relational operators are also known as comparison operators.
sidebar: 
    order: 23
---

## Navigating Relationships: Relational Operators in Python
Relational operators in Python play a pivotal role in evaluating and expressing relationships between values. They allow you to compare variables, check conditions, and make decisions based on the outcomes of these comparisons. In this comprehensive guide, we'll explore the realm of relational operators, their syntax, and their applications in Python programming.

:::tip
Relational operators in Python are the same as in other programming languages (like C, C++, Java, etc.). However, there are a few differences that you should be aware of. For example, the equality operator (`==`) in Python is different from the assignment operator (`=`). We'll discuss these differences in detail later in this tutorial.
:::


The following table lists the relational operators in Python:
| Operator | Description | Example |
| :--- | :--- | :--- |
| `==` | If the values of two operands are equal, then the condition becomes true | `x == y` |
| `!=` | If values of two operands are not equal, then the condition becomes true | `x != y` |
| `>` | If the value of the left operand is greater than the value of the right operand, then the condition becomes true | `x > y` |
| `<` | If the value of the left operand is less than the value of the right operand, then the condition becomes true | `x < y` |
| `>=` | If the value of the left operand is greater than or equal to the value of the right operand, then the condition becomes true | `x >= y` |
| `<=` | If the value of the left operand is less than or equal to the value of the right operand, then the condition becomes true | `x <= y` |


:::note
Relational operators in Python are binary operators, meaning they require two operands. However, the identity operators (`is` and `is not`) are unary operators, meaning they require only one operand. Relational operators are also known as comparison operators. The Result of a relational operator is either `True` or `False`. For example, `x == y` returns `True` if `x` is equal to `y`, otherwise it returns `False`. We'll discuss this in detail later in this tutorial.
:::

## Equality
#### `==` (Equality) Operator
The equality operator (`==`) compares the values of two operands. If the values of both operands are equal, then the condition becomes `True`. Otherwise, the condition becomes `False`. The following example demonstrates how to use the equality operator in Python:

```python title="operators.py" showLineNumbers{1} {4-5}
# Equality operator
x = 10
y = 5
z = x == y
t = x == 10
print(z)
print(t)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\Your Name> python operators.py
False
True
```

In the above example, we have used the equality operator to compare the values of two operands `x` and `y`. Since the value of `x` is not equal to the value of `y`, the condition becomes `False`. The result of the equality operator is then assigned to the variable `z`. The value of `z` is then printed to the console.

## Inequality
#### `!=` (Inequality) Operator
The inequality operator (`!=`) compares the values of two operands. If the values of both operands are not equal, then the condition becomes `True`. Otherwise, the condition becomes `False`. The following example demonstrates how to use the inequality operator in Python:

```python title="operators.py" showLineNumbers{1} {4-5}
# Inequality operator
x = 10
y = 5
z = x != y
t = x != 10
print(z)
print(t)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\Your Name> python operators.py
True
False
```

In the above example, we have used the inequality operator to compare the values of two operands `x` and `y`. Since the value of `x` is not equal to the value of `y`, the condition becomes `True`. The result of the inequality operator is then assigned to the variable `z`. The value of `z` is then printed to the console.

## Greater Than
#### `>` (Greater Than) Operator
The greater than operator (`>`) compares the values of two operands. If the value of the left operand is greater than the value of the right operand, then the condition becomes `True`. Otherwise, the condition becomes `False`. The following example demonstrates how to use the greater than operator in Python:

```python title="operators.py" showLineNumbers{1} {4-5}
# Greater than operator
x = 10
y = 5
z = x > y
t = x > 10
print(z)
print(t)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\Your Name> python operators.py
True
False
```

In the above example, we have used the greater than operator to compare the values of two operands `x` and `y`. Since the value of `x` is greater than the value of `y`, the condition becomes `True`. The result of the greater than operator is then assigned to the variable `z`. The value of `z` is then printed to the console.

## Less Than
#### `<` (Less Than) Operator
The less than operator (`<`) compares the values of two operands. If the value of the left operand is less than the value of the right operand, then the condition becomes `True`. Otherwise, the condition becomes `False`. The following example demonstrates how to use the less than operator in Python:

```python title="operators.py" showLineNumbers{1} {4-5}
# Less than operator
x = 10
y = 5
z = x < y
t = x < 10
print(z)
print(t)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\Your Name> python operators.py
False
False
```

In the above example, we have used the less than operator to compare the values of two operands `x` and `y`. Since the value of `x` is not less than the value of `y`, the condition becomes `False`. The result of the less than operator is then assigned to the variable `z`. The value of `z` is then printed to the console.

## Greater Than or Equal To
#### `>=` (Greater Than or Equal To) Operator
The greater than or equal to operator (`>=`) compares the values of two operands. If the value of the left operand is greater than or equal to the value of the right operand, then the condition becomes `True`. Otherwise, the condition becomes `False`. The following example demonstrates how to use the greater than or equal to operator in Python:

```python title="operators.py" showLineNumbers{1} {4-5}
# Greater than or equal to operator
x = 10
y = 5
z = x >= y
t = x >= 10
print(z)
print(t)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\Your Name> python operators.py
True
True
```

In the above example, we have used the greater than or equal to operator to compare the values of two operands `x` and `y`. Since the value of `x` is greater than the value of `y`, the condition becomes `True`. The result of the greater than or equal to operator is then assigned to the variable `z`. The value of `z` is then printed to the console.

## Less Than or Equal To
#### `<=` (Less Than or Equal To) Operator
The less than or equal to operator (`<=`) compares the values of two operands. If the value of the left operand is less than or equal to the value of the right operand, then the condition becomes `True`. Otherwise, the condition becomes `False`. The following example demonstrates how to use the less than or equal to operator in Python:

```python title="operators.py" showLineNumbers{1} {4-5}
# Less than or equal to operator
x = 10
y = 5
z = x <= y
t = x <= 10
print(z)
print(t)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\Your Name> python operators.py
False
True
```

In the above example, we have used the less than or equal to operator to compare the values of two operands `x` and `y`. Since the value of `x` is not less than the value of `y`, the condition becomes `False`. The result of the less than or equal to operator is then assigned to the variable `z`. The value of `z` is then printed to the console.

## Combining Relational Operators
You can combine relational operators in Python to create complex conditions. For example, you can combine the equality operator (`==`) and the greater than operator (`>`) to create a condition that checks if the value of `x` is greater than `y` and equal to `z`. The following example demonstrates how to combine relational operators in Python:

```python title="operators.py" showLineNumbers{1} {4-5}
# Combining relational operators
x = 10
y = 5
z = 10
t = x > y and x == z
print(t)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python operators.py
True
```

In the above example, we have combined the equality operator (`==`) and the greater than operator (`>`) to create a condition that checks if the value of `x` is greater than `y` and equal to `z`. Since the value of `x` is greater than `y` and equal to `z`, the condition becomes `True`. The result of the condition is then assigned to the variable `t`. The value of `t` is then printed to the console.

## Relational Operators with Strings
You can also use relational operators with strings in Python. For example, you can use the equality operator (`==`) to check if two strings are equal. The following example demonstrates how to use relational operators with strings in Python:

```python title="operators.py" showLineNumbers{1} {4-5}
# Relational operators with strings
x = "Hello"
y = "World"
z = x == y
t = x == "Hello"
print(z)
print(t)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\Your Name> python operators.py
False
True
```

In the above example, we have used the equality operator to check if the value of `x` is equal to the value of `y`. Since the value of `x` is not equal to the value of `y`, the condition becomes `False`. The result of the condition is then assigned to the variable `z`. The value of `z` is then printed to the console.

## Conclusion
Relational operators are fundamental tools for expressing conditions and making decisions in Python. Whether you're comparing numerical values, checking string order, or combining conditions with logical operators, relational operators provide the means to navigate relationships between variables.

As you continue your Python journey, experiment with different relational operators, explore their applications in real-world scenarios, and use them to create dynamic and responsive code. For more insights and practical examples, check out our tutorials on Python Central Hub!