---
title: Interfaces in Python
description: Learn about Interfaces in Python. Understand how to create and use interfaces in Python. Python Does not have a native support for interfaces, but we can use Abstract Base Classes to create interfaces in Python.
sidebar: 
    order: 92
---

## Interfaces in Python
In Python, an interface is a collection of abstract methods. Python does not have a native support for interfaces, but we can use Abstract Base Classes to create interfaces in Python.

An interface is like a contract. It defines the syntax that any class must follow to implement that interface. An interface is like a blueprint for a class. If a class follows the blueprint, it is guaranteed to provide the necessary functionality.

### Abstract Base Classes
Python comes with a module which provides the infrastructure for defining Abstract Base Classes (ABCs). The module is called `abc`. ABCs allow you to define a set of methods that must be implemented by the derived classes.

To create an interface in Python, you can create an abstract class using the `abc` module. The abstract class can have abstract methods that must be implemented by the derived classes.

Here is an example of an interface in Python using the `abc` module:

```python title="interfaces.py" showLineNumbers{1} {1, 3-6, 8-10}
from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def area(self):
        pass

    @abstractmethod
    def perimeter(self):
        pass
```

In the above example, we have created an interface called `Shape`. The `Shape` interface has two abstract methods `area` and `perimeter`. Any class that implements the `Shape` interface must provide the implementation for these two methods.

Here is an example of a class that implements the `Shape` interface:

```python title="rectangle.py" showLineNumbers{1} {1, 3-6}
from interfaces import Shape

class Rectangle(Shape):
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def area(self):
        return self.width * self.height

    def perimeter(self):
        return 2 * (self.width + self.height)
```
