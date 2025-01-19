---
title: Inner Class in Python
description: Learn about Inner Classes in Python. Understand how to create and use Inner Classes in Python. Inner Classes are classes defined inside another class in Python.
sidebar: 
    order: 93
---

## Inner Class in Python : Definition and Usage

In Python, an inner class is a class defined inside another class. Inner classes are used to logically group classes together. They are used to represent a relationship between the outer class and the inner class.

An inner class can access all the members of the outer class, but the reverse is not true. The outer class cannot access the members of the inner class.

Here is an example of an inner class in Python:

```python title="inner_class.py" showLineNumbers{1} {1-13}
class Outer:
    def __init__(self):
        self.outer_var = "Outer class variable"

    def outer_method(self):
        print("Outer class method")

    class Inner:
        def __init__(self):
            self.inner_var = "Inner class variable"

        def inner_method(self):
            print("Inner class method")

outer = Outer()
inner = outer.Inner()
print(inner.inner_var)
```

In the above example, we have defined an inner class `Inner` inside the outer class `Outer`. The inner class `Inner` has its own variables and methods. We can create an instance of the inner class using the outer class instance.

When we run the above code, it will output:

```cmd title="Command" showLineNumbers{1} {2}
C:\Users\username\Desktop> python inner_class.py
Inner class variable
```

Another way to create an instance of the inner class is by using the outer class name. Here is an example:

```python title="inner_class.py" showLineNumbers{1} {1-13}
class Outer:
    def __init__(self):
        self.outer_var = "Outer class variable"

    def outer_method(self):
        print("Outer class method")

    class Inner:
        def __init__(self):
            self.inner_var = "Inner class variable"

        def inner_method(self):
            print("Inner class method")

inner = Outer().Inner().inner_method()
```

### Accessing Inner Class Members
You can access the members of the inner class using the object of the inner class. Here is an example:

```python title="inner_class.py" showLineNumbers{1} {1-13}
class Outer:
    def __init__(self):
        self.outer_var = "Outer class variable"

    def outer_method(self):
        print("Outer class method")

    class Inner:
        def __init__(self):
            self.inner_var = "Inner class variable"

        def inner_method(self):
            print("Inner class method")

inner = Outer().Inner()
print(inner.inner_var)
```

In this example, we have created an object of the inner class `Inner` and accessed the `inner_var` variable using the object.

When we run the above code, it will output:

```cmd title="Command" showLineNumbers{1} {2}
C:\Users\username\Desktop> python inner_class.py
Inner class variable
```

## Types of Inner Classes
There are three types of inner classes in Python:
- **Regular Inner Class**: A regular inner class is a class defined inside another class.
- **Static Inner Class**: A static inner class is a class defined inside another class with the `@staticmethod` decorator.
- **Inner Class with Inheritance**: An inner class can inherit
from another class.

### Regular Inner Class
A regular inner class is a class defined inside another class. Here is an example:

```python title="inner_class.py" showLineNumbers{1} {1-13}
class Outer:
    def __init__(self):
        self.outer_var = "Outer class variable"

    def outer_method(self):
        print("Outer class method")

    class Inner:
        def __init__(self):
            self.inner_var = "Inner class variable"

        def inner_method(self):
            print("Inner class method")

inner = Outer().Inner()
print(inner.inner_var)
```

In the above example, we have defined a regular inner class `Inner` inside the outer class `Outer`.

### Static Inner Class
A static inner class is a class defined inside another class with the `@staticmethod` decorator. Here is an example:

```python title="inner_class.py" showLineNumbers{1} {1-14}
class Outer:
    def __init__(self):
        self.outer_var = "Outer class variable"

    def outer_method(self):
        print("Outer class method")

    @staticmethod
    class Inner:
        def __init__(self):
            self.inner_var = "Inner class variable"

        def inner_method(self):
            print("Inner class method")

inner = Outer.Inner()
print(inner.inner_var)
```

In the above example, we have defined a static inner class `Inner` inside the outer class `Outer` using the `@staticmethod` decorator.

### Inner Class with Inheritance

An inner class can inherit from another class. Here is an example:

```python title="inner_class.py" showLineNumbers{1} {1-13}
class Outer:
    def __init__(self):
        self.outer_var = "Outer class variable"

    def outer_method(self):
        print("Outer class method")

    class Inner(Outer):
        def __init__(self):
            self.inner_var = "Inner class variable"

        def inner_method(self):
            print("Inner class method")

inner = Outer().Inner()
print(inner.inner_var)
```

In the above example, we have defined an inner class `Inner` that inherits from the outer class `Outer`.

## Types of Inner Classes (Categories by the level)
- **Multiple Inner Classes**: A class can have multiple inner classes.
- **Multilevel Inner Classes**: An inner class can have another inner class inside it.
  

### Multiple Inner Classes
A class can have multiple inner classes. Here is an example:

```python title="inner_class.py" showLineNumbers{1} {1-20}
class Outer:
    def __init__(self):
        self.outer_var = "Outer class variable"

    def outer_method(self):
        print("Outer class method")

    class Inner1:
        def __init__(self):
            self.inner_var1 = "Inner class variable 1"

        def inner_method1(self):
            print("Inner class method 1")

    class Inner2:
        def __init__(self):
            self.inner_var2 = "Inner class variable 2"

        def inner_method2(self):
            print("Inner class method 2")

inner1 = Outer().Inner1()
inner2 = Outer().Inner2()
print(inner1.inner_var1)
print(inner2.inner_var2)
```

In the above example, we have defined two inner classes `Inner1` and `Inner2` inside the outer class `Outer`.

### Multilevel Inner Classes
An inner class can have another inner class inside it. Here is an example:

```python title="inner_class.py" showLineNumbers{1} {1-20}
class Outer:
    def __init__(self):
        self.outer_var = "Outer class variable"

    def outer_method(self):
        print("Outer class method")

    class Inner1:
        def __init__(self):
            self.inner_var1 = "Inner class variable 1"

        def inner_method1(self):
            print("Inner class method 1")

        class Inner2:
            def __init__(self):
                self.inner_var2 = "Inner class variable 2"

            def inner_method2(self):
                print("Inner class method 2")

inner1 = Outer().Inner1()
inner2 = inner1.Inner2()
print(inner2.inner_var2)
```

In the above example, we have defined an inner class `Inner2` inside the inner class `Inner1`.

## Conclusion
In this article, you learned about inner classes in Python. You also learned about the different types of inner classes and how to create and use them in Python. Inner classes are a powerful feature of Python that allows you to logically group classes together and represent relationships between classes.
For more information, you can refer to the [official documentation](https://docs.python.org/3/tutorial/classes.html#nested-classes). For more tutorials, you can visit the Python Central Hub.