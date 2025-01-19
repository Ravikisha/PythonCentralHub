---
title: Reflection in Python
description: Learn about Reflection in Python. Reflection is the ability of a program to examine and modify its structure and behavior at runtime. Reflection in Python is implemented using the `inspect` module.
sidebar: 
    order: 97
---

# Reflection in Python : Reflect on Your Code
Reflection is the ability of a program to examine and modify its structure and behavior at runtime. Reflection is a powerful feature of many programming languages, including Python. Reflection allows you to inspect and modify objects, classes, functions, and modules at runtime. Reflection is implemented in Python using the `inspect` module.

## What is Reflection?
Reflection is the ability of a program to examine and modify its structure and behavior at runtime. Reflection allows you to inspect and modify objects, classes, functions, and modules at runtime. Reflection is a powerful feature of many programming languages, including Python. Reflection is used in many advanced programming techniques, such as metaprogramming, introspection, and dynamic code generation.

## Reflection in Python
Reflection in Python is implemented using the `inspect` module. The `inspect` module provides functions for inspecting live objects, such as modules, classes, and functions. The `inspect` module allows you to get information about objects, such as their attributes, methods, and source code. The `inspect` module also provides functions for examining the call stack, getting the source code of functions, and formatting code objects.

## Using the `inspect` Module
The `inspect` module provides several functions for inspecting objects in Python. Some of the most commonly used functions in the `inspect` module are:

- `inspect.ismodule()`: Returns `True` if the object is a module.
- `inspect.isclass()`: Returns `True` if the object is a class.
- `inspect.isfunction()`: Returns `True` if the object is a function.
- `inspect.ismethod()`: Returns `True` if the object is a method.
- `inspect.isbuiltin()`: Returns `True` if the object is a built-in function or method.
- `inspect.isroutine()`: Returns `True` if the object is a function or method.
- `inspect.getmembers()`: Returns a list of all members of an object.
- `inspect.getsource()`: Returns the source code of an object.
- `inspect.getfile()`: Returns the file name in which an object was defined.
- `inspect.getmodule()`: Returns the module in which an object was defined.
- `inspect.getdoc()`: Returns the docstring of an object.
- `inspect.isabstract()`: Returns `True` if the object is an abstract base class.

Some more functions:
- `isinstance()`: Returns `True` if the object is an instance of a class.
- `issubclass()`: Returns `True` if the object is a subclass of a class.
- `getattr()`: Returns the value of an attribute of an object.
- `setattr()`: Sets the value of an attribute of an object.
- `delattr()`: Deletes an attribute of an object.
- `hasattr()`: Returns `True` if an object has a given attribute.
- `callable()`: Returns `True` if an object is callable.
- `dir()`: Returns a list of all attributes of an object.
- `vars()`: Returns the `__dict__` attribute of an object.
- `type()`: Returns the type of an object.
- `id()`: Returns the unique identifier of an object.

## Example
Here is an example of using the `inspect` module to inspect a module in Python:

```python title="Inspecting a Module" showLineNumbers{1}
import inspect

def hello():
    return "Hello, World!"

print(inspect.ismodule(inspect))
print(inspect.ismodule(hello))
print(insprint.isfunction(hello))
```

In the above code:
- We import the `inspect` module.
- We define a function `hello()` that returns the string `"Hello, World!"`.
- We use the `inspect.ismodule()` function to check if the `inspect` module is a module.
- We use the `inspect.ismodule()` function to check if the `hello` function is a module.
- We use the `inspect.isfunction()` function to check if the `hello` function is a function.

The output of the above code will be:
```cmd title="Output" showLineNumbers{1}
C:/Users/username/desktop>python inspect.py
True
False
True
```

### `isinstance()` and `issubclass()` Functions
The `isinstance()` function is used to check if an object is an instance of a class. The `issubclass()` function is used to check if a class is a subclass of another class. Here is an example of using the `isinstance()` and `issubclass()` functions in Python:

```python title="Using isinstance() and issubclass()" showLineNumbers{1}
class A:
    pass

class B(A):
    pass

objA = A()
objB = B()
print(isinstance(objA, A))
print(isinstance(objB, A))
print(issubclass(B, A))
```

Here, we define two classes `A` and `B`. The class `B` is a subclass of the class `A`. We create instances of the classes `A` and `B` and use the `isinstance()` and `issubclass()` functions to check if the instances are instances of the classes and if the classes are subclasses of each other.

The output of the above code will be:
```cmd title="Output" showLineNumbers{1}
C:/Users/username/desktop>python isinstance.py
True
True
True
```

### `getattr()`, `setattr()`, `delattr()`, and `hasattr()` Functions
The `getattr()`, `setattr()`, `delattr()`, and `hasattr()` functions are used to get, set, delete, and check the existence of attributes of an object, respectively. Here is an example of using the `getattr()`, `setattr()`, `delattr()`, and `hasattr()` functions in Python:

```python title="Using getattr(), setattr(), delattr(), and hasattr()" showLineNumbers{1}
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

person = Person("Alice", 30)
print(getattr(person, "name"))
setattr(person, "age", 35)
print(getattr(person, "age"))
delattr(person, "age")
print(hasattr(person, "age"))
```

Here, we define a class `Person` with two attributes `name` and `age`. We create an instance of the `Person` class and use the `getattr()`, `setattr()`, `delattr()`, and `hasattr()` functions to get, set, delete, and check the existence of the attributes of the object.

The output of the above code will be:
```cmd title="Output" showLineNumbers{1}
C:/Users/username/desktop>python getattr.py
Alice
35
False
```

### `callable()` Function
The `callable()` function is used to check if an object is callable. An object is callable if it can be called like a function. Here is an example of using the `callable()` function in Python:

```python title="Using callable()" showLineNumbers{1}
def hello():
    return "Hello, World!"

print(callable(hello))
print(callable("Hello, World!"))
```

Here, we define a function `hello()` that returns the string `"Hello, World!"`. We use the `callable()` function to check if the function `hello()` is callable and if the string `"Hello, World!"` is callable.

The output of the above code will be:
```cmd title="Output" showLineNumbers{1}
C:/Users/username/desktop>python callable.py
True
False
```

### `dir()` and `vars()` Functions
The `dir()` function is used to get a list of all attributes of an object. The `vars()` function is used to get the `__dict__` attribute of an object. Here is an example of using the `dir()` and `vars()` functions in Python:

```python title="Using dir() and vars()" showLineNumbers{1}
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

person = Person("Alice", 30)
print(dir(person))
print(vars(person))
```

Here, we define a class `Person` with two attributes `name` and `age`. We create an instance of the `Person` class and use the `dir()` and `vars()` functions to get a list of all attributes of the object and the `__dict__` attribute of the object.

The output of the above code will be:
```cmd title="Output" showLineNumbers{1}
C:/Users/username/desktop>python dir.py
['__class__', '__delattr__', '__dict__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', 'age', 'name']
{'name': 'Alice', 'age': 30}
```

### `type()` and `id()` Functions
The `type()` function is used to get the type of an object. The `id()` function is used to get the unique identifier of an object. Here is an example of using the `type()` and `id()` functions in Python:

```python title="Using type() and id()" showLineNumbers{1}
class Person:
    pass

person = Person()
print(type(person))
print(id(person))
```

Here, we define a class `Person` and create an instance of the `Person` class. We use the `type()` function to get the type of the object and the `id()` function to get the unique identifier of the object.

The output of the above code will be:
```cmd title="Output" showLineNumbers{1}
C:/Users/username/desktop>python type.py
<class '__main__.Person'>
140735674221376
```

## Conclusion
Reflection is a powerful feature of Python that allows you to examine and modify objects, classes, functions, and modules at runtime. Reflection is implemented in Python using the `inspect` module. The `inspect` module provides functions for inspecting live objects, such as modules, classes, and functions. By using the `inspect` module, you can get information about objects, such as their attributes, methods, and source code. Reflection is used in many advanced programming techniques, such as metaprogramming, introspection, and dynamic code generation. For more information on the `inspect` module, you can refer to the [official Python documentation](https://docs.python.org/3/library/inspect.html). For more tutorials on Python Central Hub.