---
title: Variable Assignment
description: An introduction to variables in Python. Learn about variable assignment, data types, and best practices for naming variables.
sidebar: 
    order: 6
---

## What is a Variable?
Python variables are the reserved memory locations used to store values with in a Python Program. This means that when you create a variable you reserve some space in the memory. Based on the data type of a variable, Python interpreter allocates memory and decides what can be stored in the reserved memory. Therefore, by assigning different data types to Python variables, you can store integers, decimals or characters in these variables.

## Declaring Variables in Python
In Python, variables do not need explicit declaration to reserve memory space. The declaration happens automatically when you assign a value to a variable. The equal sign (=) is used to assign values to variables.

#### Example:
```python title="variable.py" showLineNumbers{1} {2,3,4}
# Declaring variables
a = 10 # an integer
b = 20.5 # a float
c = "Hello, World!" # a string
```

## Getting the Data Type of a Variable
To get the data type of a variable, you can use the `type()` function.

#### Example:
```python title="variable.py" showLineNumbers{1} {7-9}
# Declaring variables
a = 10 # an integer
b = 20.5 # a float
c = "Hello, World!" # a string

# Getting the data type of a variable
print(type(a))
print(type(b))
print(type(c))
```

Output:
```cmd title="command" showLineNumbers{1} {2-4}
C:\Users\Your Name> python variable.py
<class 'int'>
<class 'float'>
<class 'str'>
```

## Single and Multiple Assignments
Python allows you to assign a single value to several variables simultaneously.

#### Example:
```python title="variable.py" showLineNumbers{1} {3,6}
# Single assignment
a = b = c = 10
print(a, b, c)

# Multiple assignments
a, b, c = 10, 20.5, "Hello, World!"
print(a, b, c)
```

Output:
```cmd title="command" showLineNumbers{1} {2-4}
C:\Users\Your Name> python variable.py
10 10 10
10 20.5 Hello, World!
```

## Single Quotes vs Double Quotes
In Python, you can use either single quotes (`'`) or double quotes (`"`) to declare a string. Both are valid, but you must use the same type of quotes to start and end a string.

#### Example:
```python title="variable.py" showLineNumbers{1} {2,6}
# Single quotes
a = 'Hello, World!'
print(a)

# Double quotes
b = "Hello, World!"
print(b)
```

Output:
```cmd title="command" showLineNumbers{1} {2-4}
C:\Users\Your Name> python variable.py
Hello, World!
Hello, World!
```

## Case Sensitivity
Python is case-sensitive, which means that `a` and `A` are different variables. For example:

#### Example:
```python title="variable.py" showLineNumbers{1} {2,3}
# Case-sensitive variables
a = 10
A = 20.5
print(a)
print(A)
```

Output:
```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\Your Name> python variable.py
10
20.5
```