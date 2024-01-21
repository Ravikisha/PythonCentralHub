---
title: Method Overloading in Python
description: Learn about Method Overloading in Python. Method overloading is a feature of a programming language that allows a method to be defined more than once. The method is defined with the same name but with different parameters. The method is called based on the number of parameters passed to it.
sidebar: 
    order: 87
---

<!-- ```python title="constructor.py" showLineNumbers{1} {2-5}
class Student:
    def __init__(self, name, roll):
        self.name = name
        self.roll = roll

student1 = Student('John', 1)
print('Name:', student1.name)
print('Roll:', student1.roll)
```

Output:
```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\username>python constructor.py
Name: John
Roll: 1
```

In the above example, we have created two instance variables named `name` and `roll`. We have initialized the `name` and `roll` variables to the `name` and `roll` parameters of the `__init__()` method. We have printed the `name` and `roll` variables using the `student1` object. The output shows that the `name` and `roll` variables are unique to the object. -->

## Compile-time Polymorphism
Compile-time polymorphism is also known as **static polymorphism**. It occurs when the compiler knows which polymorphic function to call at compile-time. Compile-time polymorphism is achieved through function overloading and operator overloading.

### Function Overloading
Function overloading is a feature of a programming language that allows a function to be defined more than once. The function is defined with the same name but with different parameters. The function is called based on the number of parameters passed to it. Function overloading is a type of compile-time polymorphism. It is achieved by defining multiple functions with the same name but with different parameters. The function is called based on the number of parameters passed to it. Function overloading is not supported in Python. However, it can be achieved by using default arguments and variable-length arguments. Let's see how to achieve function overloading in Python.

```python title="function_overloading.py" showLineNumbers{1} {1-3, 5-7, 9-11}
def add(a, b):
    print("Two arguments\n")
    return a + b

def add(a, b, c):
    print("Three arguments\n")
    return a + b + c

def add(a, b, c, d):
    print("Four arguments\n")
    return a + b + c + d

print(add(1, 2))
print(add(1, 2, 3))
print(add(1, 2, 3, 4))
```

Output:
```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\username>python function_overloading.py
Traceback (most recent call last):
  File "function_overloading.py", line 11, in <module>
    print(add(1, 2))
TypeError: add() missing 2 required positional arguments: 'c' and 'd'
```

In the above example, we have defined three functions with the same name but with different parameters. The first function takes two arguments, the second function takes three arguments, and the third function takes four arguments. We have called the `add()` function with two, three, and four arguments. The output shows that the `add()` function is called based on the number of arguments passed to it. The `add()` function is called with two arguments, three arguments, and four arguments. In Python, function overloading is achieved by using default arguments and variable-length arguments. Let's see how to achieve function overloading in Python using default arguments and variable-length arguments.

:::tip
Python does not support function overloading. However, it can be achieved by using default arguments and variable-length arguments.
:::

#### Function Overloading using Default Arguments
```python title="function_overloading.py" showLineNumbers{1} {1-3}
def add(a, b, c=0, d=0):
    # Default arguments
    return a + b + c + d

print(add(1, 2))
print(add(1, 2, 3))
print(add(1, 2, 3, 4))
```

Output:
```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\username>python function_overloading.py
3
6
10
```

In the above example, we have defined the `add()` function with four parameters. The `c` and `d` parameters have default values of `0`. We have called the `add()` function with two, three, and four arguments. The output shows that the `add()` function is called based on the number of arguments passed to it. The `add()` function is called with two arguments, three arguments, and four arguments.

#### Function Overloading using Variable-length Arguments
```python title="function_overloading.py" showLineNumbers{1} {1-6}
def add(*args):
    # Variable-length arguments
    total = 0
    for arg in args:
        total += arg
    return total

print(add(1, 2))
print(add(1, 2, 3))
print(add(1, 2, 3, 4))
```

Output:
```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\username>python function_overloading.py
3
6
10
```

In the above example, we have defined the `add()` function with a variable-length argument. We have called the `add()` function with two, three, and four arguments. The output shows that the `add()` function is called based on the number of arguments passed to it. The `add()` function is called with two arguments, three arguments, and four arguments.

### Function Overloading in class
Function overloading is a feature of a programming language that allows a function to be defined more than once. The function is defined with the same name but with different parameters. The function is called based on the number of parameters passed to it. Function overloading is a type of compile-time polymorphism. It is achieved by defining multiple functions with the same name but with different parameters. The function is called based on the number of parameters passed to it. Function overloading is not supported in Python. However, it can be achieved by using default arguments and variable-length arguments. Let's see how to achieve function overloading in Python.

```python title="function_overloading.py" showLineNumbers{1} {6-8, 10-13}
class Student:
    def __init__(self, name, roll):
        self.name = name
        self.roll = roll

    def display(self):
        print('Name:', self.name)
        print('Roll:', self.roll)

    def display(self, age):
        print('Name:', self.name)
        print('Roll:', self.roll)
        print('Age:', age)

student1 = Student('John', 1)
student1.display()
student1.display(20)
```

Output:
```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\username>python function_overloading.py
Traceback (most recent call last):
  File "function_overloading.py", line 17, in <module>
    student1.display()
TypeError: display() missing 1 required positional argument: 'age'
```

In the above example, we have defined two `display()` methods in the `Student` class. The first `display()` method takes one argument, and the second `display()` method takes two arguments. We have created an object named `student1` of the `Student` class. We have called the `display()` method of the `student1` object with one argument. The output shows that the `display()` method is called with one argument. We have called the `display()` method of the `student1` object with two arguments. The output shows that the `display()` method is called with two arguments. In Python, function overloading is achieved by using default arguments and variable-length arguments. Let's see how to achieve function overloading in Python using default arguments and variable-length arguments.

### Operator Overloading
Operator overloading is a feature of a programming language that allows an operator to be defined more than once. The operator is defined with the same name but with different parameters. The operator is called based on the number of parameters passed to it. Operator overloading is a type of compile-time polymorphism. It is achieved by defining multiple operators with the same name but with different parameters. The operator is called based on the number of parameters passed to it. Operator overloading is not supported in Python. However, it can be achieved by using magic methods. Let's see how to achieve operator overloading in Python.

```python title="operator_overloading.py" showLineNumbers{1} {1-3, 5-7, 9-11}
class Complex:
    def __init__(self, real, imag):
        self.real = real
        self.imag = imag

    def __add__(self, other):
        return Complex(self.real + other.real, self.imag + other.imag)

    def __sub__(self, other):
        return Complex(self.real - other.real, self.imag - other.imag)

    def __mul__(self, other):
        return Complex(self.real * other.real, self.imag * other.imag)

    def __truediv__(self, other):
        return Complex(self.real / other.real, self.imag / other.imag)

    def __str__(self):
        return f'{self.real} + {self.imag}j'

c1 = Complex(1, 2)
c2 = Complex(3, 4)
print(c1 + c2)
print(c1 - c2)
print(c1 * c2)
print(c1 / c2)
```

Output:
```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\username>python operator_overloading.py
4 + 6j
-2 + -2j
3 + 8j
0.3333333333333333 + 0.5j
```

In the above example, we have defined four magic methods named `__add__()`, `__sub__()`, `__mul__()`, and `__truediv__()`. The `__add__()` method is called when the `+` operator is used with two `Complex` objects. The `__sub__()` method is called when the `-` operator is used with two `Complex` objects. The `__mul__()` method is called when the `*` operator is used with two `Complex` objects. The `__truediv__()` method is called when the `/` operator is used with two `Complex` objects. We have created two `Complex` objects named `c1` and `c2`. We have added, subtracted, multiplied, and divided the `c1` and `c2` objects. The output shows that the `__add__()`, `__sub__()`, `__mul__()`, and `__truediv__()` methods are called when the `+`, `-`, `*`, and `/` operators are used with two `Complex` objects.