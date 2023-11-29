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

#### Example:
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

## Calling a Function in Python
In Python, you can call a function using its name followed by parentheses. The syntax for calling a function is as follows:

```python title="Syntax" showLineNumbers{1} {1}
[variable] = function_name(arguments)
```

- **`variable`**: An optional variable that stores the return value of the function.
- **`function_name`**: The name of the function.
- **`arguments`**: A comma-separated list of arguments. Each argument consists of a value followed by a colon and a type annotation. The type annotation is optional.
- **`=`**: An optional assignment operator. It is used to assign the return value of the function to a variable.

#### Example:
```python title="function.py" showLineNumbers{1} {5}
def add(x: int, y: int) -> int:
    """Adds two numbers"""
    return x + y

result = add(5, 10)
print(result)
```

Output:
```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python function.py
15
```

In this example, we call the `add()` function with two arguments `5` and `10`. The function returns `15`, which is assigned to the variable `result`. The value of `result` is then printed to the console. 

:::tip
You can also call a function without assigning its return value to a variable. In this case, the return value is discarded.
```python title="function.py" showLineNumbers{1} {5}
def add(x: int, y: int) -> int:
    """Adds two numbers"""
    return x + y

add(5, 10)
```

Output:
```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python function.py
```

In this example, we call the `add()` function without assigning its return value to a variable. The function returns `15`, but the return value is discarded.
:::

:::note
### Docstring
The docstring is used to describe the function. It is a string literal that is the first statement in the function body. It is enclosed in triple quotes. The docstring is used by the `help()` function to display information about the function.

```python title="function.py" showLineNumbers{1} {1-3}
def add(x: int, y: int) -> int:
    """Adds two numbers"""
    return x + y
```

In this example, we define a function named `add` that takes two parameters `x` and `y` and returns their sum. The type annotation for the parameters and return value is optional. The docstring is also optional, but it is good practice to include it. The docstring is used to describe the function. It is a string literal that is the first statement in the function body. It is enclosed in triple quotes. The docstring is used by the `help()` function to display information about the function.
:::

## Parameters of a Function in Python
In Python, you can pass parameters to a function. The syntax for passing parameters to a function is as follows:

```python title="Syntax" showLineNumbers{1} {1-2}
def function_name(parameter1, parameter2, ...):
```

- **`function_name`**: The name of the function.
- **`parameter1, parameter2, ...`**: A comma-separated list of parameters. Each parameter consists of a name followed by a colon and a type annotation. The type annotation is optional.
- **`,`**: A comma that separates the parameters.

#### Example:
```python title="function.py" showLineNumbers{1} {1-3}
def add(x: int, y: int) -> int:
    """Adds two numbers"""
    return x + y

result = add(5, 10)
print(result)
```

Output:
```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python function.py
15
```

In this example, we define a function named `add` that takes two parameters `x` and `y` and returns their sum. We then call the function with two arguments `5` and `10`. The function returns `15`, which is assigned to the variable `result`. The value of `result` is then printed to the console.

:::danger
The number of arguments passed to a function must match the number of parameters defined in the function. If the number of arguments is less than the number of parameters, the remaining parameters are set to `None`. If the number of arguments is greater than the number of parameters, the extra arguments are ignored.

```python title="function.py" showLineNumbers{1} {1-3}
def add(x: int, y: int) -> int:
    """Adds two numbers"""
    return x + y

result = add(5)
print(result)
```

Output:
```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python function.py
Traceback (most recent call last):
  File "function.py", line 4, in <module>
    result = add(5)
TypeError: add() missing 1 required positional argument: 'y'
```

In this example, we define a function named `add` that takes two parameters `x` and `y` and returns their sum. We then call the function with one argument `5`. The function returns `15`, which is assigned to the variable `result`. The value of `result` is then printed to the console. However, this code will throw an error because the number of arguments passed to the function does not match the number of parameters defined in the function.
:::

## Return Value of a Function in Python

In Python, you can return a value from a function using the `return` statement. The syntax for returning a value from a function is as follows:

```python title="Syntax" showLineNumbers{1} {1-2}
return [expression]
```

- **`return`**: The `return` keyword.
- **`expression`**: An optional expression that is evaluated and returned by the function.

#### Example:
```python title="function.py" showLineNumbers{1} {1-3}
def add(x: int, y: int) -> int:
    """Adds two numbers"""
    return x + y

result = add(5, 10)
print(result)
```

Output:
```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python function.py
15
```

In this example, we define a function named `add` that takes two parameters `x` and `y` and returns their sum. We then call the function with two arguments `5` and `10`. The function returns `15`, which is assigned to the variable `result`. The value of `result` is then printed to the console.

Return values are optional in Python. If you don't specify a return value, the function returns `None`. For example:

```python title="function.py" showLineNumbers{1} {1-3}
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

In this example, we define a function named `add` that takes two parameters `x` and `y` and prints their sum. We then call the function with two arguments `5` and `10`. The function prints `15` to the console. The return value of the function is `None`, which is assigned to the variable `result`. The value of `result` is then printed to the console.

## Multiple calls to a Function in Python

In Python, you can call a function multiple times. The syntax for calling a function multiple times is as follows:

```python title="Syntax" showLineNumbers{1} {1-3}
function_name(arguments)
function_name(arguments)
function_name(arguments)
```

#### Example:
```python title="function.py" showLineNumbers{1} {5-7}
def add(x: int, y: int) -> int:
    """Adds two numbers"""
    return x + y

result1 = add(5, 10)
result2 = add(10, 20)
result3 = add(20, 30)
print(result1)
print(result2)
print(result3)
```

Output:
```cmd title="command" showLineNumbers{1} {2-4}
C:\Users\Your Name> python function.py
15
30
50
```

In this example, we define a function named `add` that takes two parameters `x` and `y` and returns their sum. We then call the function three times with different arguments. The function returns the sum of the arguments, which is assigned to the variables `result1`, `result2`, and `result3`. The values of these variables are then printed to the console. This is how you can call a function multiple times in Python. A function can be called as many times as you want. This is the main advantage of using functions in Python.

## Types of Functions in Python

In Python, there are two types of functions:

- **Built-in functions**
- **User-defined functions** 
 
Built-in functions are functions that are provided by Python. They are used to perform common tasks such as printing text to the console, reading input from the user, and converting data types. 

User-defined functions are functions that are defined by the user. They are used to perform specific tasks that are not provided by Python. For example, you might want to define a function that adds two numbers. This function can then be called from anywhere in the program.

:::tip
Python has a large number of built-in functions. You can find a list of all built-in functions in the [Python documentation](https://docs.python.org/3/library/functions.html). We are going to cover some of the most commonly used built-in functions in next section.
:::


## Arguments of a Function in Python

In Python, you can pass arguments to a function. The syntax for passing arguments to a function is as follows:

```python title="Syntax" showLineNumbers{1} {1-2}
function_name(argument1, argument2, ...)
```

- **`function_name`**: The name of the function.
- **`argument1, argument2, ...`**: A comma-separated list of arguments. Each argument consists of a value followed by a colon and a type annotation. The type annotation is optional.
- **`,`**: A comma that separates the arguments.

#### Example:
```python title="function.py" showLineNumbers{1} {1-3}
def add(x: int, y: int) -> int:
    """Adds two numbers"""
    return x + y

result = add(5, 10)
print(result)
```

Output:
```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python function.py
15
```

In this example, we define a function named `add` that takes two parameters `x` and `y` and returns their sum. We then call the function with two arguments `5` and `10`. The function returns `15`, which is assigned to the variable `result`. The value of `result` is then printed to the console. Here, we are passing arguments to the function. The arguments are `5` and `10`. The function takes these arguments and returns their sum.

:::note
### What is difference between parameter and argument?

Parameters are variables that are used in the function definition. Arguments are the values that are passed to the function when it is called. 

For example, in the following function definition, `x` and `y` are parameters:
```python title="function.py" showLineNumbers{1} {1-3}
def add(x: int, y: int) -> int:
    """Adds two numbers"""
    return x + y
```

In the following function call, `5` and `10` are arguments:
```python title="function.py" showLineNumbers{1} {1-3}
result = add(5, 10)
```

In this example, we define a function named `add` that takes two parameters `x` and `y` and returns their sum. We then call the function with two arguments `5` and `10`. The function returns `15`, which is assigned to the variable `result`. The value of `result` is then printed to the console. Here, we are passing arguments to the function. The arguments are `5` and `10`. The function takes these arguments and returns their sum.
:::

## Pass by Reference vs Pass by Value in Python

In Python, the terms "pass by value" and "pass by reference" are often misunderstood because the concept is a bit nuanced. Python uses a mechanism that is more accurately described as "pass by object reference" or "call by object reference." To understand this, let's delve into how values are passed to functions in Python.

### Pass by Value
In Python, values are passed to functions by value. This means that when you pass a value to a function, a copy of the value is created and passed to the function. The function then operates on this copy of the value. The original value is not modified. For example:

```python title="function.py" showLineNumbers{1} {1-3}
def update(x: int):
    """Updates the value of x"""
    x = 10

x = 5
update(x)
print(x)
```

Output:
```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python function.py
5
```

In this example, we define a function named `update` that takes a parameter `x` and updates its value to `10`. We then call the function with the argument `5`. The function updates the value of `x` to `10`. However, the original value of `x` is not modified. The value of `x` is still `5`. This is because the value of `x` is passed to the function by value. A copy of the value is created and passed to the function. The function then operates on this copy of the value. The original value is not modified. This is how values are passed to functions in Python.

### Pass by Reference
In Python, values are passed to functions by reference. This means that when you pass a value to a function, a reference to the value is passed to the function. The function then operates on this reference to the value. The original value is modified. For example:

```python title="function.py" showLineNumbers{1} {1-3}
def update(x: list):
    """Updates the value of x"""
    x[0] = 10

x = [5]
update(x)
print(x)
```

Output:
```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python function.py
[10]
```

In this example, we define a function named `update` that takes a parameter `x` and updates its value to `10`. We then call the function with the argument `[5]`. The function updates the value of `x` to `10`. The original value of `x` is modified. This is because the value of `x` is passed to the function by reference. A reference to the value is passed to the function. The function then operates on this reference to the value. The original value is modified. This is how values are passed to functions in Python. 

In python, the primitive data types like `int`, `float`, `bool`, `str`, etc. are passed by value. The non-primitive data types like `list`, `dict`, `set`, etc. are passed by reference. This is because the primitive data types are immutable, while the non-primitive data types are mutable.
