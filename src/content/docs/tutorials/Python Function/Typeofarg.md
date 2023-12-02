---
title: Type of Arguments in Python
description: Learn about the different types of arguments in Python. In this tutorial, we will learn about the different types of arguments in Python. We will also learn how to use them in our Python programs. There are three types of arguments in Python. They are positional arguments, keyword arguments, and default arguments.
sidebar: 
    order: 43
---

<!-- ```python title="function.py" showLineNumbers{1} {1-3}
def add(x: int, y: int) -> int:
    """Adds two numbers"""
    print(x + y)

result = add(5, 10)
print(result)
```

Output:
```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\Your Name> python function.py
15
None
```

In this example, we define a function named `add` that takes two parameters `x` and `y` and prints their sum. We then call the function with two arguments `5` and `10`. The function prints `15` to the console. The return value of the function is `None`, which is assigned to the variable `result`. The value of `result` is then printed to the console. -->

## What are Arguments in Python?

In Python, arguments are the values that are passed to a function or method call. In other words, arguments are the data that is sent to a function or method when it is called. The function or method receives the data as input and uses it to perform the required task. 

In Python, arguments are specified inside the parentheses of a function or method call. The arguments are separated by commas. 

```python title="Syntax" showLineNumbers{1}
function_name(argument1, argument2, argument3, ...)
```

In the above syntax, `argument1`, `argument2`, `argument3`, and so on are the arguments passed to the function or method call. 

:::note
You can pass any number of arguments to a function or method.
:::

We are going to call the function and pass the arguments to it. 

```python title="arguments.py" showLineNumbers{1} {1-3}
def add(x, y):
    """Adds two numbers"""
    print(x + y)

add(5, 10)
```

Output:
```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\Your Name> python arguments.py
15
```

In the above example, we define a function named `add` that takes two parameters `x` and `y` and prints their sum. We then call the function with two arguments `5` and `10`. The function prints `15` to the console.

:::tip
We already know about Arguments and Parameters in previous tutorials. If you don't know about them, please read the [Python Function](/tutorials/python-function/function/)
:::

## Types of Arguments in Python

In Python, there are three types of arguments. They are:

1. Default Arguments
2. Positional Arguments
3. Keyword Arguments

### Default Arguments
Default arguments are the arguments that are assigned a default value. If the function is called without passing the value for the default argument, the default value is used. 

```python title="Syntax" showLineNumbers{1} {1-3}
def function_name(argument1, argument2=default_value):
    """Docstring"""
    # Function body
```

In the above syntax, `argument1` is a positional argument and `argument2` is a default argument.

Let's see an example of a function with a default argument.

```python title="default-arguments.py" {1-3}
def add(x, y=10):
    """Adds two numbers"""
    print(x + y)

add(5)
```

Output:
```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\Your Name> python default-arguments.py
15
```

In the above example, we define a function named `add` that takes two parameters `x` and `y`. The default value of `y` is `10`. We then call the function with one argument `5`. The function prints `15` to the console. You don't have to pass the value for the default argument. If you don't pass the value for the default argument, the default value is used. 

Another example of a function with a default argument.

```python title="default-arguments.py" {1-4, 6-8}
def interest(p, r=5, t=1):
    """Calculates the simple interest"""
    i = (p * r * t) / 100
    print(f"Simple interest is {i}")

interest(1000)
interest(1000, 10)
interest(1000, 10, 2)
```

Output:
```cmd title="command" showLineNumbers{1} {2-4}
C:\Users\Your Name> python default-arguments.py
Simple interest is 50.0
Simple interest is 100.0
Simple interest is 200.0
```

In the above example, we define a function named `interest` that takes three parameters `p`, `r`, and `t`. The default value of `r` is `5` and the default value of `t` is `1`. We then call the function with one argument `1000`. The function prints `50.0` to the console. We then call the function with two arguments `1000` and `10`. The function prints `100.0` to the console. We then call the function with three arguments `1000`, `10`, and `2`. The function prints `200.0` to the console. In this function, if you don't pass the value for `r` and `t`, the default values are used.


### Positional Arguments
Positional arguments are the arguments that are passed to a function or method without a keyword. In other words, positional arguments are the arguments that are passed to a function or method without a keyword. 

```python title="Syntax" showLineNumbers{1} {1-3}
function_name(value1, value2, value3, ...)
```

In the above syntax, `value1`, `value2`, `value3`, and so on are the values passed to the function or method call.

Let's see an example of a function with positional arguments.

```python title="positional-arguments.py" {1-3}
def add(x, y):
    """Adds two numbers"""
    print(x + y)

add(5, 10)
```

Output:
```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\Your Name> python positional-arguments.py
15
```

In the above example, we define a function named `add` that takes two parameters `x` and `y`. We then call the function with two positional arguments `5` and `10`. The function prints `15` to the console.

Another example of a function with positional arguments.

```python title="positional-arguments.py" {1-4, 6-8}
def interest(p, r, t):
    """Calculates the simple interest"""
    i = (p * r * t) / 100
    print(f"Simple interest is {i}")

interest(1000, 5, 1)
interest(1000, 10, 2)
interest(1000, 10, 6)
```

Output:
```cmd title="command" showLineNumbers{1} {2-4}
C:\Users\Your Name> python positional-arguments.py
Simple interest is 50.0
Simple interest is 200.0
Simple interest is 600.0
```

In this example, we are calling the function with positional arguments. We are passing the arguments in different orders. In the positional arguments, you have to pass the arguments in the same order as they are defined in the function definition but in the keyword arguments, you can pass the arguments in any order.

:::note
In the postional arguments, you have to pass the arguments in the same order as they are defined in the function definition.
:::


