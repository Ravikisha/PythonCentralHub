---
title: Function in Python
description: Learn how to define and call a function in Python. Also learn about parameters and return values of functions in Python.
sidebar: 
    order: 42
---

## Exploring the Power of Functions in Python: A Comprehensive Guide
In the realm of Python programming, functions stand as essential building blocks, allowing developers to encapsulate reusable blocks of code, enhance modularity, and streamline the overall structure of a program. In this comprehensive guide, we will delve into the fundamentals of functions in Python, exploring their syntax, use cases, and best practices.

## Functions in Python
A function is a block of code that performs a specific task. Functions are used to make code more modular and reusable. For example, you might have a function that adds two numbers. Instead of writing the same code again, you can just call the function. You can also pass parameters to a function, which allows you to reuse the same code with different inputs. In this tutorial, you'll learn how to define and call a function in Python. You'll also learn about parameters and return values of functions in Python.

A top-down approach is used to define functions in Python. This means that you start with the main function and then define other functions as you go. This is different from other programming languages like C, where you define all the functions at the top of the program. In Python, you can define a function anywhere in the program, and you can call a function before it is defined. This is because Python reads the entire program before executing it. 

## Defining a Function in Python
In Python, you can define a function using the `def` keyword. The syntax for defining a function is as follows:

```python title="Syntax" showLineNumbers{1} {1-4}
def function_name(parameters):
    """docstring"""
    statement(s)
    return [expression] # Optional
```

- **`function_name`**: The name of the function. It must follow the same rules as variable names.
- **`parameters`**: A comma-separated list of parameters. Each parameter consists of a name followed by a colon and a type annotation. The type annotation is optional.
- **`docstring`**: An optional docstring that describes the function.
- **`statement(s)`**: The body of the function. It consists of one or more statements.
- **`return`**: An optional return statement. It is used to return a value from the function.
- **`expression`**: An optional expression that is evaluated and returned by the function.
- **`:`**: A colon that marks the end of the function header. It is followed by an indented block of code. The indentation is used to indicate the scope of the function. All statements in the function body must be indented.

### Example:
```python title="function.py" showLineNumbers{1} {1-3}
def add(x: int, y: int) -> int:
    """Adds two numbers"""
    return x + y
```

In this example, we define a function named `add` that takes two parameters `x` and `y` and returns their sum. The type annotation for the parameters and return value is optional. The docstring is also optional, but it is good practice to include it.

:::note
The docstring is used to describe the function. It is a string literal that is the first statement in the function body. It is enclosed in triple quotes. The docstring is used by the `help()` function to display information about the function.
:::

:::tip
The `help()` function is used to display information about a function. It takes the function name as an argument and returns a string containing the docstring of the function.
:::

:::tip
Data types are optional in Python. You can use type annotations to specify the data types of parameters and return values. However, Python does not enforce these types. It is up to the developer to ensure that the correct types are passed to the function.
:::