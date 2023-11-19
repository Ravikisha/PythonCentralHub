---
title: Global Variables
description: An introduction to global variables in Python. Learn about global variables, local variables, and the global keyword. This tutorial is part of the Python Variables Course.
sidebar: 
    order: 9
---

We can create a variable outside of a function. This is called a global variable. We can access the global variable inside or outside of a function. Let's see an example.

#### Example:
```python title="variable.py" showLineNumbers{1} {2}
# Global variable
name = "John"
def display():
    print("Hello, " + name)
display() # Hello, John
print("Hello, " + name) # Hello, John
```

In the above example, we created a global variable `name` outside of the function `display()`. We can access the global variable `name` inside or outside of the function `display()`.
:::tip
We can access the global variable inside or outside of a function.
:::

## Global Keyword
We can create a local variable inside a function. This is called a local variable. We can access the local variable inside the function. We can't access the local variable outside the function. Let's see an example.

#### Example:
```python title="variable.py" showLineNumbers{1} {2,3,4,5,6}
# Global variable
name = "John"
def display():
    # Local variable
    name = "Smith"
    print("Hello, " + name)
display() # Hello, Smith
print("Hello, " + name) # Hello, John
```
In this example, we created a local variable `name` inside the function `display()`. We can access the local variable `name` inside the function `display()`. We can't access the local variable `name` outside the function `display()`.
:::tip
We can access the local variable inside the function. We can't access the local variable outside the function.
:::

We can use the `global` keyword to access the global variable inside the function. Let's see an example.
#### Example:
```python title="variable.py" showLineNumbers{1} {2,3,4,5,6}
# Global variable
name = "John"
def display():
    # Local variable
    global name
    name = "Smith"
    print("Hello, " + name)
display() # Hello, Smith
print("Hello, " + name) # Hello, Smith
```
In this example, we used the `global` keyword to access the global variable `name` inside the function `display()`. We can access the global variable `name` inside the function `display()`. We can also access the global variable `name` outside the function `display()`.