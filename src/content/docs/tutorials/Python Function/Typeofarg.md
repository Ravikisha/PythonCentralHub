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


### Keyword Arguments
Keyword arguments are the arguments that are passed to a function or method with a keyword. In other words, keyword arguments are the arguments that are passed to a function or method with a keyword. 

```python title="Syntax" showLineNumbers{1} {1-3}
function_name(argument1=value1, argument2=value2, argument3=value3, ...)
```

In the above syntax, `argument1`, `argument2`, `argument3`, and so on are the arguments passed to the function or method call. `value1`, `value2`, `value3`, and so on are the values passed to the function or method call.

Let's see an example of a function with keyword arguments.

```python title="keyword-arguments.py" {1-3, 5}
def add(x, y):
    """Adds two numbers"""
    print(x + y)

add(x=5, y=10)
```

Output:
```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\Your Name> python keyword-arguments.py
15
```

In the above example, we define a function named `add` that takes two parameters `x` and `y`. We then call the function with two keyword arguments `x=5` and `y=10`. The function prints `15` to the console.

:::note
**You can pass the keyword arguments in any order.** <br> 
In the positional arguments, you have to pass the arguments in the same order as they are defined in the function definition but in the keyword arguments, you can pass the arguments in any order.
:::

Another example of a function with keyword arguments.

```python title="keyword-arguments.py" {1-4, 6-8}
def interest(p, r, t):
    """Calculates the simple interest"""
    i = (p * r * t) / 100
    print(f"Simple interest is {i}")

interest(p=1000, r=5, t=1)
interest(t=2, p=1000, r=10)
interest(r=10, t=2, p=1000)
```

Output:
```cmd title="command" showLineNumbers{1} {2-4}
C:\Users\Your Name> python keyword-arguments.py
Simple interest is 50.0
Simple interest is 200.0
Simple interest is 200.0
```

In this example, we are calling the function with keyword arguments. We are passing the arguments in different orders. In the positional arguments, you have to pass the arguments in the same order as they are defined in the function definition but in the keyword arguments, you can pass the arguments in any order.

:::note
You can call a function with positional arguments and keyword arguments. <br>
You can call a function with positional arguments and keyword arguments. But you have to pass the positional arguments before the keyword arguments.
    
```python title="keyword-arguments.py" {1-4, 6-8}
def interest(p, r, t):
    """Calculates the simple interest"""
    i = (p * r * t) / 100
    print(f"Simple interest is {i}")

interest(1000, r=5, t=1)
```

Output:
```cmd title="command" showLineNumbers{1} {2-4}
C:\Users\Your Name> python keyword-arguments.py
Simple interest is 50.0
```

In the above example, we are calling the function with positional arguments and keyword arguments. We are passing the positional arguments before the keyword arguments. This will not give us an error.
:::

:::danger
**You cannot pass the positional arguments after the keyword arguments.** <br>
In the positional arguments, you have to pass the arguments in the same order as they are defined in the function definition but in the keyword arguments, you can pass the arguments in any order. But you cannot pass the positional arguments after the keyword arguments. If you do so, you will get an error.

```python title="keyword-arguments.py" {1-4, 6-8}
def interest(p, r, t):
    """Calculates the simple interest"""
    i = (p * r * t) / 100
    print(f"Simple interest is {i}")

interest(p=1000, r=5, 1)
```

Output:
```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\Your Name> python keyword-arguments.py
  File "keyword-arguments.py", line 6
    interest(p=1000, r=5, 1)
                          ^
SyntaxError: positional argument follows keyword argument
```

In the above example, we are passing the positional argument `1` after the keyword argument `r=5`. This will give us an error.
:::

## Keyword Arguments vs Positional Arguments

Let's see the difference between keyword arguments and positional arguments.

| Keyword Arguments | Positional Arguments |
| --- | --- |
| Keyword arguments are the arguments that are passed to a function or method with a keyword. | Positional arguments are the arguments that are passed to a function or method without a keyword. |
| You can pass the keyword arguments in any order. | You have to pass the positional arguments in the same order as they are defined in the function definition. |
| You cannot pass the positional arguments after the keyword arguments. | You can pass the positional arguments after the keyword arguments. |
| You can call a function with positional arguments and keyword arguments. | You can call a function with positional arguments and keyword arguments. But you have to pass the positional arguments before the keyword arguments. |


## Positional Only Arguments

In Python, you can define a function with positional only arguments. Positional only arguments are the arguments that can be passed to a function or method only without a keyword. In other words, positional only arguments are the arguments that can be passed to a function or method only without a keyword. 

```python title="Syntax" showLineNumbers{1} {1-3}
def function_name(argument1, argument2, argument3, /):
    """Docstring"""
    # Function body
```

In the above syntax, `argument1`, `argument2`, `argument3`, and so on are the positional only arguments passed to the function or method call. You have to pass the positional only arguments without a keyword. You cannot pass the positional only arguments with a keyword.

Let's see an example of a function with positional only arguments.

```python title="positional-only-arguments.py" {1-3}
def add(x, y, /):
    """Adds two numbers"""
    print(x + y)

add(5, 10)
```

Output:
```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\Your Name> python positional-only-arguments.py
15
```

In the above example, we define a function named `add` that takes two positional only arguments `x` and `y`. We then call the function with two positional arguments `5` and `10`. The function prints `15` to the console.

Another example of a function with positional only arguments.

```python title="positional-only-arguments.py" {1-4, 6-8}
def interest(p, /, r, t):
    """Calculates the simple interest"""
    i = (p * r * t) / 100
    print(f"Simple interest is {i}")

interest(1000, 5, 1)
interest(1000, r=10, t=2)
interest(1000, 10, t=2)
```

Output:
```cmd title="command" showLineNumbers{1} {2-4}
C:\Users\Your Name> python positional-only-arguments.py
Simple interest is 50.0
Simple interest is 200.0
Simple interest is 200.0
```

In this example, we declare `p` as a positional only argument and `r` and `t` as keyword arguments. We are calling the function with positional arguments. We are passing the arguments in different orders. In the positional arguments, you have to pass the arguments in the same order as they are defined in the function definition but in the keyword arguments, you can pass the arguments in any order.

:::danger
In the interest function, `p` is a positional only argument and `r` and `t` are keyword arguments. You cannot pass the keyword arguments before the positional only arguments. If you do so, you will get an error.

```python title="positional-only-arguments.py" {1-4, 6-9}
def interest(p, /, r,*, t):
    """Calculates the simple interest"""
    i = (p * r * t) / 100
    print(f"Simple interest is {i}")

interest(1000, r=5, t=1)
interest(1000, r=10, t=2)
interest(1000, 10, t=2)
interest(1000, 10, 2)
```

Output:

```cmd title="command" showLineNumbers{1} {2-7}
C:\Users\Your Name> python positional-only-arguments.py
Simple interest is 50.0
Simple interest is 200.0
Simple interest is 200.0
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
TypeError: interest() takes 2 positional arguments but 3 were given
```
:::

## Keyword Only Arguments

In Python, you can define a function with keyword only arguments. Keyword only arguments are the arguments that can be passed to a function or method only with a keyword. In other words, keyword only arguments are the arguments that can be passed to a function or method only with a keyword. 

```python title="Syntax" showLineNumbers{1} {1-3}
def function_name(*, argument1, argument2, argument3, ...):
    """Docstring"""
    # Function body
```

In the above syntax, `argument1`, `argument2`, `argument3`, and so on are the keyword only arguments passed to the function or method call. You have to pass the keyword only arguments with a keyword. You cannot pass the keyword only arguments without a keyword. 

Let's see an example of a function with keyword only arguments.

```python title="keyword-only-arguments.py" {1-3}
def add(*, x, y):
    """Adds two numbers"""
    print(x + y)

add(x=5, y=10)
```

Output:
```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\Your Name> python keyword-only-arguments.py
15
```

In the above example, we define a function named `add` that takes two keyword only arguments `x` and `y`. We then call the function with two keyword arguments `x=5` and `y=10`. The function prints `15` to the console.

Another example of a function with keyword only arguments.

```python title="keyword-only-arguments.py" {1-4, 6-8}
def interest(p, *, r, t):
    """Calculates the simple interest"""
    i = (p * r * t) / 100
    print(f"Simple interest is {i}")

interest(1000, r=5, t=1)
interest(1000, t=2, r=10)
interest(1000, r=10, t=2)
```

Output:
```cmd title="command" showLineNumbers{1} {2-4}
C:\Users\Your Name> python keyword-only-arguments.py
Simple interest is 50.0
Simple interest is 200.0
Simple interest is 200.0
```

In this example, we are calling the function with keyword only arguments. We are passing the arguments in different orders. In the positional arguments, you have to pass the arguments in the same order as they are defined in the function definition but in the keyword arguments, you can pass the arguments in any order.

:::danger
In the interest function, `p` is a positional argument and `r` and `t` are keyword only arguments. You cannot pass the positional arguments after the keyword only arguments. If you do so, you will get an error.

```python title="keyword-only-arguments.py" {1-4, 6-8}
def interest(p, *, r, t):
    """Calculates the simple interest"""
    i = (p * r * t) / 100
    print(f"Simple interest is {i}")

interest(1000, r=5, 1)
```

Output:
```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\Your Name> python keyword-only-arguments.py
  File "keyword-only-arguments.py", line 6
    interest(1000, r=5, 1)
                        ^
TypeError: interest() takes 1 positional argument but 2 positional arguments (and 1 keyword-only argument) were given
```

In the above example, we are passing the positional argument `1` after the keyword only argument `r=5`. This will give us an error.
:::


## Arbitrary Arguments

In Python, you can define a function with arbitrary arguments. Arbitrary arguments are the arguments that can be passed to a function or method with any number of arguments. In other words, arbitrary arguments are the arguments that can be passed to a function or method with any number of arguments. 

There are two types of arbitrary arguments in Python. They are:
- **Arbitrary Positional Arguments**
- **Arbitrary Keyword Arguments**


### Arbitrary Positional Arguments
In Python, you can define a function with arbitrary positional arguments. Arbitrary positional arguments are the positional arguments that can be passed to a function or method with any number of arguments. In other words, arbitrary positional arguments are the positional arguments that can be passed to a function or method with any number of arguments. 

```python title="Syntax" showLineNumbers{1} {1-3}
def function_name(*args):
    """Docstring"""
    # Function body
```

In the above syntax, `args` is the arbitrary positional arguments passed to the function or method call. You can pass any number of arguments to the function or method.

Let's see an example of a function with arbitrary positional arguments.

```python title="arbitrary-positional-arguments.py" {1-6}
def add(*args):
    """Adds two numbers"""
    result = 0
    for num in args:
        result += num
    print(result)

add(5, 10)
add(5, 10, 15)
add(5, 10, 15, 20)
```

Output:
```cmd title="command" showLineNumbers{1} {2-4}
C:\Users\Your Name> python arbitrary-positional-arguments.py
15
30
50
```

In the above example, we define a function named `add` that takes arbitrary positional arguments `args`. We then call the function with two arguments `5` and `10`. The function prints `15` to the console. We then call the function with three arguments `5`, `10`, and `15`. The function prints `30` to the console. We then call the function with four arguments `5`, `10`, `15`, and `20`. The function prints `50` to the console.

Another example of a function with arbitrary positional arguments.

```python title="arbitrary-positional-arguments.py" {1-5, 7-9}
def interest(*args):
    """Calculates the simple interest"""
    p, r, t = args
    i = (p * r * t) / 100
    print(f"Simple interest is {i}")

interest(1000, 5, 1)
interest(1000, 10, 2)
interest(1000, 10, 6)
```

Output:
```cmd title="command" showLineNumbers{1} {2-4}
C:\Users\Your Name> python arbitrary-positional-arguments.py
Simple interest is 50.0
Simple interest is 200.0
Simple interest is 600.0
```

In this example, we are calling the function with arbitrary positional arguments. We are passing the arguments in different orders. In the positional arguments, you have to pass the arguments in the same order as they are defined in the function definition. Here, we are unpacking the arguments into three variables `p`, `r`, and `t`. We are then using these variables to calculate the simple interest. 

### Arbitrary Keyword Arguments
In Python, you can define a function with arbitrary keyword arguments. Arbitrary keyword arguments are the keyword arguments that can be passed to a function or method with any number of arguments. In other words, arbitrary keyword arguments are the keyword arguments that can be passed to a function or method with any number of arguments. 

```python title="Syntax" showLineNumbers{1} {1-3}
def function_name(**kwargs):
    """Docstring"""
    # Function body
```

In the above syntax, `kwargs` is the arbitrary keyword arguments passed to the function or method call. You can pass any number of arguments to the function or method.

Let's see an example of a function with arbitrary keyword arguments.

```python title="arbitrary-keyword-arguments.py" {1-6}
def add(**kwargs):
    """Adds two numbers"""
    result = 0
    for key, value in kwargs.items():
        result += value
    print(result)

add(x=5, y=10)
add(x=5, y=10, z=15)
add(x=5, y=10, z=15, a=20)
```

Output:
```cmd title="command" showLineNumbers{1} {2-4}
C:\Users\Your Name> python arbitrary-keyword-arguments.py
15
30
50
```

In the above example, we define a function named `add` that takes arbitrary keyword arguments `kwargs`. We then call the function with two arguments `x=5` and `y=10`. The function prints `15` to the console. We then call the function with three arguments `x=5`, `y=10`, and `z=15`. The function prints `30` to the console. We then call the function with four arguments `x=5`, `y=10`, `z=15`, and `a=20`. The function prints `50` to the console.

Another example of a function with arbitrary keyword arguments.

```python title="arbitrary-keyword-arguments.py" {1-7, 9-12}
def interest(**kwargs):
    """Calculates the simple interest"""
    p = kwargs["p"]
    r = kwargs["r"]
    t = kwargs["t"]
    i = (p * r * t) / 100
    print(f"Simple interest is {i}")

interest(p=1000, r=5, t=1)
interest(p=1000, r=10, t=2)
interest(p=1000, r=10, t=6)
```

Output:
```cmd title="command" showLineNumbers{1} {2-4}
C:\Users\Your Name> python arbitrary-keyword-arguments.py
Simple interest is 50.0
Simple interest is 200.0
Simple interest is 600.0
```

In this example, we are calling the function with arbitrary keyword arguments. We are passing the arguments in different orders. In the positional arguments, you have to pass the arguments in the same order as they are defined in the function definition. Here, we are accessing the arguments using the keys `p`, `r`, and `t`. We are then using these variables to calculate the simple interest.

Another example of a function with arbitrary keyword arguments.

```python title="arbitrary-keyword-arguments.py" {1-7, 9-14}
def intro(name, age, **kwargs):
    """Prints the name and age"""
    print(f"Name: {name}")
    print(f"Age: {age}")
    print("Other information:")
    for key, value in kwargs.items():
        print(f"{key}: {value}")
    
intro("John", 25, city="New York", country="USA")
print("-------------------------")
intro("John", 25, city="New York", country="USA", phone="1234567890")
print("-------------------------")
intro("John", 25, city="New York", country="USA", phone="1234567890", email="john@gmail.com")
```

Output:
```cmd title="command" showLineNumbers{1} {2-30}
C:\Users\Your Name> python arbitrary-keyword-arguments.py
Name: John
Age: 25
Other information:
city: New York
country: USA
-------------------------
Name: John
Age: 25
Other information:
city: New York
country: USA
phone: 1234567890
-------------------------
Name: John
Age: 25
Other information:
city: New York
country: USA
phone: 1234567890
email: john@gmail.com
```

