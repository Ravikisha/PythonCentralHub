---
title: Multiple Assignment
description: How to assign multiple values to multiple variables in Python. Learn about multiple assignment, one value to multiple variables, multiple values to one variable, and unpacking a tuple or list.
sidebar: 
    order: 8
---

## Many Values to Multiple Variables
We can assign multiple values to multiple variables in one line. This is called multiple assignment.

#### Example:
```python title="variable.py" showLineNumbers{1} {2,3,4}
# Multiple assignment
a, b, c = 10, 20.5, "Hello, World!"
print(a, b, c)
```

Output

```cmd title="command" showLineNumbers{1} {2-4}
C:\Users\Your Name> python variable.py
10 20.5 Hello, World!
```

:::caution
The number of variables on the left and the number of values on the right must be the same.
:::

## One Value to Multiple Variables
We can assign one value to multiple variables in one line. This is called one value to multiple variables.

#### Example:
```python title="variable.py" showLineNumbers{1} {2}
# One value to multiple variables
a = b = c = 10
print(a, b, c)
```

Output

```cmd title="command" showLineNumbers{1} {2-4}
C:\Users\Your Name> python variable.py
10 10 10
```

## Multiple Values to One Variable
We can assign multiple values to one variable in one line. This is called multiple values to one variable.

#### Example:
```python title="variable.py" showLineNumbers{1} {2}
# Multiple values to one variable
a = 10, 20, 30
print(a)
```

Output

```cmd title="command" showLineNumbers{1} {2-4}
C:\Users\Your Name> python variable.py
(10, 20, 30)
```

In this case, the variable `a` is a tuple.

## Unpacking a Tuple
We can unpack a tuple in multiple variables. This is called unpacking a tuple.

#### Example:
```python title="variable.py" showLineNumbers{1} {3}
# Unpacking a tuple
a = 10, 20, 30
x, y, z = a
print(x, y, z)
```

Output

```cmd title="command" showLineNumbers{1} {2-4}
C:\Users\Your Name> python variable.py
10 20 30
```

## Unpacking a List
We can unpack a list in multiple variables. This is called unpacking a list.

#### Example:
```python title="variable.py" showLineNumbers{1} {3}
# Unpacking a list
a = [10, 20, 30]
x, y, z = a
print(x, y, z)
```

Output

```cmd title="command" showLineNumbers{1} {2-4}
C:\Users\Your Name> python variable.py
10 20 30
```