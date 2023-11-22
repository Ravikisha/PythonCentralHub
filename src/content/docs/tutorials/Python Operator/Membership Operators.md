---
title: Python Membership Operators
description: Learn about Python Membership Operators with examples. Membership operators are used to test if a sequence is presented in an object. Membership operators are also known as inclusion operators. Membership operators (in and not in) are used to test whether a value or variable is found in a sequence (string, list, tuple, set, and dictionary). In this tutorial, we will learn about Python Membership Operators with examples.
sidebar: 
    order: 27
---

## Exploring Membership Operators in Python
Membership operators in Python are fundamental tools for checking whether a value is a member of a sequence, such as a string, list, or tuple. These operators, in and not in, provide a concise and expressive way to validate the presence or absence of an element within a collection. In this comprehensive guide, we'll delve into the world of membership operators, their syntax, and their applications in Python programming.

:::note
Membership operators are also known as inclusion operators.
:::

The following table lists the membership operators in Python:

| Operator | Description | Example |
| :--- | :--- | :--- |
| `in` | Returns `True` if a sequence with the specified value is present in the object | `x in y` |
| `not in` | Returns `True` if a sequence with the specified value is not present in the object | `x not in y` |


## in Operator
#### `in` Operator
The `in` operator returns `True` if a sequence with the specified value is present in the object. The following example demonstrates how to use the `in` operator in Python:

```python title="operators.py" showLineNumbers{1} {4-5}
# in operator
x = 10
y = 5
z = x in y
t = x in 10
print(z)
print(t)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\Your Name> python operators.py
False
True
```

In the above example, we have used the `in` operator to check if the value of `x` is present in the object `y`. Since the value of `x` is not present in the object `y`, the condition becomes `False`. The result of the `in` operator is then assigned to the variable `z`. The value of `z` is then printed to the console.

## not in Operator
#### `not in` Operator
The `not in` operator returns `True` if a sequence with the specified value is not present in the object. The following example demonstrates how to use the `not in` operator in Python:

```python title="operators.py" showLineNumbers{1} {4-5}
# not in operator
x = 10
y = 5
z = x not in y
t = x not in 10
print(z)
print(t)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\Your Name> python operators.py
True
False
```

In the above example, we have used the `not in` operator to check if the value of `x` is not present in the object `y`. Since the value of `x` is not present in the object `y`, the condition becomes `True`. The result of the `not in` operator is then assigned to the variable `z`. The value of `z` is then printed to the console.

## Membership Operators with Lists
The membership operators can be used with lists. The following example demonstrates how to use the membership operators with lists in Python:

```python title="operators.py" showLineNumbers{1} {4-5}
# Membership operators with lists
x = [1, 2, 3, 4, 5]
y = 10
z = y in x
t = y not in x
print(z)
print(t)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\Your Name> python operators.py
False
True
```

In the above example, we have used the membership operators with lists. The `in` operator returns `True` if the value of `y` is present in the list `x`. Since the value of `y` is not present in the list `x`, the condition becomes `False`. The `not in` operator returns `True` if the value of `y` is not present in the list `x`. Since the value of `y` is not present in the list `x`, the condition becomes `True`.

:::tip
The membership operators can be used with other data types such as tuples, sets, and dictionaries. We are going to explore these data types in the next section. We will explore lists in detail in the [Python Lists](/docs/tutorials/Python%20Lists/) tutorial.

## Membership Operators with Strings
The membership operators can be used with strings. The following example demonstrates how to use the membership operators with strings in Python:

```python title="operators.py" showLineNumbers{1} {4-5}
# Membership operators with strings
x = "Hello World"
y = "World"
z = y in x
t = y not in x
print(z)
print(t)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\Your Name> python operators.py
True
False
```

In the above example, we have used the membership operators with strings. The `in` operator returns `True` if the value of `y` is present in the string `x`. Since the value of `y` is present in the string `x`, the condition becomes `True`. The `not in` operator returns `True` if the value of `y` is not present in the string `x`. Since the value of `y` is present in the string `x`, the condition becomes `False`.


## Membership Operators with Tuples
The membership operators can be used with tuples. The following example demonstrates how to use the membership operators with tuples in Python:

```python title="operators.py" showLineNumbers{1} {4-5}
# Membership operators with tuples
x = (1, 2, 3, 4, 5)
y = 10
z = y in x
t = y not in x
print(z)
print(t)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\Your Name> python operators.py
False
True
```

:::tip
We will explore tuples in detail in the [Python Tuples](/docs/tutorials/Python%20Tuples/) tutorial.
:::


## Conclusion
Membership operators in Python are powerful tools for validating the presence or absence of values within sequences. Whether you're working with lists, tuples, strings, or sets, in and not in provide a concise and readable syntax for membership testing.

As you advance in your Python programming journey, experiment with membership operators, incorporate them into your conditional statements, and explore their applications in real-world scenarios. For more insights and practical examples, check out our tutorials on Python Central Hub!