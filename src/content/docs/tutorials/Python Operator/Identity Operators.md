---
title: Python Identity Operators
description: Learn about Python Identity Operators. Python Identity Operators are used to compare the memory locations of two objects. Python Identity Operators are is and is not. 
sidebar: 
    order: 28
---

## Unveiling Identity Operators in Python
Identity operators in Python are essential tools for comparing the memory addresses of objects. These operators, is and is not, evaluate whether two variables reference the same object or not. Understanding identity operators is crucial for dealing with object references and managing memory effectively in Python programming. In this comprehensive guide, we'll delve into the world of identity operators, their syntax, and their applications.

:::note
Identity operators are also known as comparison operators. It is because they compare the memory locations of two objects. They don't compare the values of two objects.
:::

The following table lists the identity operators in Python:
| Operator | Description | Example |
| :--- | :--- | :--- |
| `is` | Returns `True` if both variables are the same object | `x is y` |
| `is not` | Returns `True` if both variables are not the same object | `x is not y` |

## is Operator
#### `is` Operator
The `is` operator returns `True` if both variables are the same object. It returns `True` if both variables point to the same memory location otherwise `False`. The following example demonstrates how to use the `is` operator in Python:

```python title="operators.py" showLineNumbers{1} {4}
# is operator
x = 10
y = 10
z = x is y
print(z)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python operators.py
True
```

In the above example, we have used the `is` operator to check if the value of `x` is the same as the value of `y`. Since the value of `x` is the same as the value of `y`, the condition becomes `True`. The result of the `is` operator is then assigned to the variable `z`. The value of `z` is then printed to the console.

:::note
In python, all the variables are references to the objects. When we assign a value to a variable, we are actually binding the variable to the object. The `is` operator compares the memory locations of two objects. If both variables point to the same memory location, the `is` operator returns `True` otherwise `False`.

When we assign a value to a variable, the Python interpreter creates an object and binds the variable to that object. If we create another variable and assign the same value to it, the Python interpreter assigns the same object to the new variable. In this case, both variables point to the same object. The `is` operator returns `True` in this case.

```python title="operators.py" showLineNumbers{1}
a = 10 # Location: 0x0001
b = 10 # Location: 0x0001
print(a is b)
```

However, if we create another variable and assign a different value to it, the Python interpreter creates a new object and binds the new variable to that object. In this case, both variables point to different objects. The `is` operator returns `False` in this case.

```python title="operators.py" showLineNumbers{1}
a = 10 # Location: 0x0001
b = 20 # Location: 0x0002
print(a is b)
```

In the case, if you assign one variable to another variable, both variables point to the same object. The `is` operator returns `True` in this case.
    
```python title="operators.py" showLineNumbers{1}
a = 10 # Location: 0x0001
b = a  # Location: 0x0001
print(a is b)
```

For more details about memory management in Python, please refer to the Python Management.
:::

## is not Operator
#### `is not` Operator
The `is not` operator returns `True` if both variables are not the same object. It returns `True` if both variables point to different memory locations otherwise `False`. The following example demonstrates how to use the `is not` operator in Python:

```python title="operators.py" showLineNumbers{1} {4}
# is not operator
x = 10
y = 5
z = x is not y
print(z)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python operators.py
True
```

In the above example, we have used the `is not` operator to check if the value of `x` is not the same as the value of `y`. Since the value of `x` is not the same as the value of `y`, the condition becomes `True`. The result of the `is not` operator is then assigned to the variable `z`. The value of `z` is then printed to the console.

## Identity Operators with Lists
The identity operators can be used with lists. The following example demonstrates how to use the identity operators with lists in Python:

```python title="operators.py" showLineNumbers{1} {4-5}
# Identity operators with lists
x = [1, 2, 3, 4, 5]
y = 10
z = y is x
t = y is not x
print(z)
print(t)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\Your Name> python operators.py
False
True
```

In the above example, we have used the `is` operator to check if the value of `x` is the same as the value of `y`. Since the value of `x` is not the same as the value of `y`, the condition becomes `False`. The result of the `is` operator is then assigned to the variable `z`. The value of `z` is then printed to the console.

In the above example, we have used the `is not` operator to check if the value of `x` is not the same as the value of `y`. Since the value of `x` is not the same as the value of `y`, the condition becomes `True`. The result of the `is not` operator is then assigned to the variable `t`. The value of `t` is then printed to the console.

Another example of using the identity operators with lists is given below:

```python title="operators.py" showLineNumbers{1}
# Identity operators with lists
x = [1, 2, 3, 4, 5]
y = [1, 2, 3, 4, 5]
z = x is y
t = x is not y
print(z)
print(t)
# After changing the value of y
y = x
y[0] = 10
z = x is y
t = x is not y
print(z)
print(t)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\Your Name> python operators.py
False
True
True
False
```

In the above example, we have used the `is` operator to check if the value of `x` is the same as the value of `y`. Since the value of `x` is not the same as the value of `y`, the condition becomes `False`. The result of the `is` operator is then assigned to the variable `z`. The value of `z` is then printed to the console.

In the above example, we have used the `is not` operator to check if the value of `x` is not the same as the value of `y`. Since the value of `x` is not the same as the value of `y`, the condition becomes `True`. The result of the `is not` operator is then assigned to the variable `t`. The value of `t` is then printed to the console.

In the above example, we have assigned the value of `x` to `y`. Since both variables point to the same object, the `is` operator returns `True` and the `is not` operator returns `False`.

## Identity Operators with Strings
The identity operators can be used with strings. The following example demonstrates how to use the identity operators with strings in Python:

```python title="operators.py" showLineNumbers{1}
# Identity operators with strings
x = "Hello"
y = "Hello"
z = x is y
t = x is not y
print(z)
print(t)
# After changing the value of y
y = "World"
z = x is y
t = x is not y
print(z)
print(t)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\Your Name> python operators.py
True
False
False
True
```

In the above example, we have used the `is` operator to check if the value of `x` is the same as the value of `y`. Since the value of `x` is the same as the value of `y`, the condition becomes `True`. The result of the `is` operator is then assigned to the variable `z`. The value of `z` is then printed to the console.

In the above example, we have used the `is not` operator to check if the value of `x` is not the same as the value of `y`. Since the value of `x` is the same as the value of `y`, the condition becomes `False`. The result of the `is not` operator is then assigned to the variable `t`. The value of `t` is then printed to the console.

In the above example, we have assigned the value of `x` to `y`. Since both variables point to the same object, the `is` operator returns `True` and the `is not` operator returns `False`.

## Comparison Operators vs Identity Operators
The comparison operators and identity operators are different. The comparison operators compare the values of two objects. The identity operators compare the memory locations of two objects. The following example demonstrates the difference between the comparison operators and identity operators in Python:

```python title="operators.py" showLineNumbers{1}
# Comparison operators vs Identity operators
x = [1, 2, 3, 4, 5]
y = [1, 2, 3, 4, 5]
z = x == y
t = x is y
print(z)
print(t)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\Your Name> python operators.py
True
False
```

In the above example, we have used the `==` operator to check if the value of `x` is the same as the value of `y`. Since the value of `x` is the same as the value of `y`, the condition becomes `True`. The result of the `==` operator is then assigned to the variable `z`. The value of `z` is then printed to the console.

In the above example, we have used the `is` operator to check if the value of `x` is the same as the value of `y`. Since the value of `x` is not the same as the value of `y`, the condition becomes `False`. The result of the `is` operator is then assigned to the variable `t`. The value of `t` is then printed to the console.

## Conditional Statements with Identity Operators
The identity operators can be used in conditional statements. The following example demonstrates how to use the identity operators in conditional statements in Python:

```python title="operators.py" showLineNumbers{1}
# Conditional statements with identity operators
x = 10
y = 5
if x is y:
    print("x is y")
else:
    print("x is not y")
```

Output:

```cmd title="command" showLineNumbers{1}
C:\Users\Your Name> python operators.py
x is not y
```

In the above example, we have used the `is` operator in the conditional statement. Since the value of `x` is not the same as the value of `y`, the condition becomes `False`. The `else` block is executed in this case.


## Conclusion
Identity operators in Python provide a powerful mechanism for comparing object identity and avoiding unintended side effects in your code. Whether you're checking for None, ensuring variables reference the same object, or managing mutable objects, is and is not offer a precise and efficient way to handle object identity.

As you progress in your Python programming journey, experiment with identity operators, understand their use cases, and incorporate them into your code where needed. For more insights and practical examples, check out our tutorials on Python Central Hub!