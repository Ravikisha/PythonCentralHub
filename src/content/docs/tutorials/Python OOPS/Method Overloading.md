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

## Magic Methods
Magic methods are special methods that are used to perform some special operations. They are also known as **dunder methods**. They are always surrounded by double underscores. They are called automatically when certain operations are performed on objects. For example, the `__init__()` method is called automatically when an object is created. Magic methods are also known as dunder methods because they are surrounded by double underscores. Let's see how to use magic methods in Python.

#### List of Magic Methods
|S.No.|Magic Method|Description|Example|
|:---:|:---|:---|:---|
|1|`__init__()`|Called when an object is created.|`__init__(self, name, roll)`|
|2|`__str__()`|Called when the `str()` function is called on an object.|`__str__(self)`|
|3|`__repr__()`|Called when the `repr()` function is called on an object.|`__repr__(self)`|
|4|`__len__()`|Called when the `len()` function is called on an object.|`__len__(self)`|
|5|`__add__()`|Called when the `+` operator is used with two objects.|`__add__(self, other)`|
|6|`__sub__()`|Called when the `-` operator is used with two objects.|`__sub__(self, other)`|
|7|`__mul__()`|Called when the `*` operator is used with two objects.|`__mul__(self, other)`|
|8|`__truediv__()`|Called when the `/` operator is used with two objects.|`__truediv__(self, other)`|
|9|`__floordiv__()`|Called when the `//` operator is used with two objects.|`__floordiv__(self, other)`|
|10|`__mod__()`|Called when the `%` operator is used with two objects.|`__mod__(self, other)`|
|11|`__pow__()`|Called when the `**` operator is used with two objects.|`__pow__(self, other)`|
|12|`__and__()`|Called when the `&` operator is used with two objects.|`__and__(self, other)`|
|13|`__or__()`|Called when the `|` operator is used with two objects.|`__or__(self, other)`|
|14|`__xor__()`|Called when the `^` operator is used with two objects.|`__xor__(self, other)`|
|15|`__lt__()`|Called when the `<` operator is used with two objects.|`__lt__(self, other)`|
|16|`__le__()`|Called when the `<=` operator is used with two objects.|`__le__(self, other)`|
|17|`__eq__()`|Called when the `==` operator is used with two objects.|`__eq__(self, other)`|
|18|`__ne__()`|Called when the `!=` operator is used with two objects.|`__ne__(self, other)`|
|19|`__gt__()`|Called when the `>` operator is used with two objects.|`__gt__(self, other)`|
|20|`__ge__()`|Called when the `>=` operator is used with two objects.|`__ge__(self, other)`|
|21|`__getitem__()`|Called when an item is accessed using the `[]` operator.|`__getitem__(self, key)`|
|22|`__setitem__()`|Called when an item is assigned using the `[]` operator.|`__setitem__(self, key, value)`|
|23|`__delitem__()`|Called when an item is deleted using the `[]` operator.|`__delitem__(self, key)`|
|24|`__contains__()`|Called when the `in` operator is used with an object.|`__contains__(self, item)`|
|25|`__call__()`|Called when an object is called as a function.|`__call__(self, *args, **kwargs)`|
|26|`__enter__()`|Called when the `with` statement is used with an object.|`__enter__(self)`|
|27|`__exit__()`|Called when the `with` statement is used with an object.|`__exit__(self, exc_type, exc_value, traceback)`|
|28|`__iter__()`|Called when an object is iterated.|`__iter__(self)`|
|29|`__next__()`|Called when the `next()` function is called on an object.|`__next__(self)`|
|30|`__reversed__()`|Called when the `reversed()` function is called on an object.|`__reversed__(self)`|
|31|`__hash__()`|Called when the `hash()` function is called on an object.|`__hash__(self)`|
|32|`__bool__()`|Called when the `bool()` function is called on an object.|`__bool__(self)`|
|33|`__format__()`|Called when the `format()` function is called on an object.|`__format__(self, format_spec)`|
|34|`__index__()`|Called when an object is used as an index.|`__index__(self)`|
|35|`__int__()`|Called when the `int()` function is called on an object.|`__int__(self)`|
|36|`__float__()`|Called when the `float()` function is called on an object.|`__float__(self)`|
|37|`__complex__()`|Called when the `complex()` function is called on an object.|`__complex__(self)`|
|38|`__round__()`|Called when the `round()` function is called on an object.|`__round__(self, n)`|
|39|`__floor__()`|Called when the `math.floor()` function is called on an object.|`__floor__(self)`|
|40|`__ceil__()`|Called when the `math.ceil()` function is called on an object.|`__ceil__(self)`|
|41|`__trunc__()`|Called when the `math.trunc()` function is called on an object.|`__trunc__(self)`|
|42|`__pos__()`|Called when the `+` operator is used with an object.|`__pos__(self)`|
|43|`__neg__()`|Called when the `-` operator is used with an object.|`__neg__(self)`|
|44|`__abs__()`|Called when the `abs()` function is called on an object.|`__abs__(self)`|
|45|`__invert__()`|Called when the `~` operator is used with an object.|`__invert__(self)`|


### __init__() Method
The `__init__()` method is called automatically when an object is created. It is used to initialize the instance variables of an object. It is also known as the **constructor** method. Let's see how to use the `__init__()` method in Python.

```python title="init.py" showLineNumbers{1} {2-4}
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
C:\Users\username>python init.py
Name: John
Roll: 1
```

In the above example, we have created two instance variables named `name` and `roll`. We have initialized the `name` and `roll` variables to the `name` and `roll` parameters of the `__init__()` method. We have printed the `name` and `roll` variables using the `student1` object. The output shows that the `name` and `roll` variables are unique to the object.

### __str__() Method
The `__str__()` method is called when the `str()` function is called on an object. It is used to return a string representation of an object. Let's see how to use the `__str__()` method in Python. It also called when the `print()` function is called on an object.

```python title="str.py" showLineNumbers{1} {6-7}
class Student:
    def __init__(self, name, roll):
        self.name = name
        self.roll = roll

    def __str__(self):
        return f'Name: {self.name}\nRoll: {self.roll}'

student1 = Student('John', 1)
print(str(student1))
print(student1)
```

Output:
```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\username>python str.py
Name: John
Roll: 1
Name: John
Roll: 1
```

In the above example, we have defined the `__str__()` method in the `Student` class. The `__str__()` method returns a string representation of the `Student` object. We have created an object named `student1` of the `Student` class. We have printed the `student1` object using the `str()` function. The output shows that the `__str__()` method is called when the `str()` function is called on the `student1` object.

### __repr__() Method
The `__repr__()` method is called when the `repr()` function is called on an object. It is used to return a string representation of an object. Let's see how to use the `__repr__()` method in Python. It also called when the `print()` function is called on an object.

```python title="repr.py" showLineNumbers{1} {6-7}
class Student:
    def __init__(self, name, roll):
        self.name = name
        self.roll = roll

    def __repr__(self):
        return f'Name: {self.name}\nRoll: {self.roll}'

student1 = Student('John', 1)
print(student1)
```

Output:
```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\username>python repr.py
Name: John
Roll: 1
```

In the above example, we have defined the `__repr__()` method in the `Student` class. The `__repr__()` method returns a string representation of the `Student` object. We have created an object named `student1` of the `Student` class. We have printed the `student1` object using the `print()` function. The output shows that the `__repr__()` method is called when the `print()` function is called on the `student1` object.

### __len__() Method
The `__len__()` method is called when the `len()` function is called on an object. It is used to return the length of an object. Let's see how to use the `__len__()` method in Python.

```python title="len.py" showLineNumbers{1} {6-7}
class Store:
    def __init__(self, items):
        self.items = items

    def __len__(self):
        return len(self.items)

store1 = Store(['Apple', 'Banana', 'Orange'])
print(len(store1))
```

Output:
```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\username>python len.py
3
```

In the above example, we have defined the `__len__()` method in the `Store` class. The `__len__()` method returns the length of the `items` list. We have created an object named `store1` of the `Store` class. We have printed the `store1` object using the `len()` function. The output shows that the `__len__()` method is called when the `len()` function is called on the `store1` object.

### __add__() Method
The `__add__()` method is called when the `+` operator is used with two objects. It is used to add two objects. Let's see how to use the `__add__()` method in Python.

```python title="add.py" showLineNumbers{1} {6-8}
class Complex:
    def __init__(self, real, imag):
        self.real = real
        self.imag = imag

    def __add__(self, other):
        return Complex(self.real + other.real, self.imag + other.imag)

c1 = Complex(1, 2)
c2 = Complex(3, 4)
c3 = c1 + c2
print(f'{c1.real} + {c1.imag}j + {c2.real} + {c2.imag}j = {c3.real} + {c3.imag}j')
```

Output:
```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\username>python add.py
1 + 2j + 3 + 4j = 4 + 6j
```

In the above example, we have defined the `__add__()` method in the `Complex` class. The `__add__()` method returns a `Complex` object. We have created two `Complex` objects named `c1` and `c2`. We have added the `c1` and `c2` objects using the `+` operator. The output shows that the `__add__()` method is called when the `+` operator is used with two `Complex` objects.

### __sub__() Method
The `__sub__()` method is called when the `-` operator is used with two objects. It is used to subtract two objects. Let's see how to use the `__sub__()` method in Python.

```python title="sub.py" showLineNumbers{1} {6-8}
class Complex:
    def __init__(self, real, imag):
        self.real = real
        self.imag = imag

    def __sub__(self, other):
        return Complex(self.real - other.real, self.imag - other.imag)

c1 = Complex(1, 2)
c2 = Complex(3, 4)
c3 = c1 - c2
print(f'{c1.real} + {c1.imag}j - {c2.real} + {c2.imag}j = {c3.real} + {c3.imag}j')
```

Output:
```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\username>python sub.py
1 + 2j - 3 + 4j = -2 + -2j
```

In the above example, we have defined the `__sub__()` method in the `Complex` class. The `__sub__()` method returns a `Complex` object. We have created two `Complex` objects named `c1` and `c2`. We have subtracted the `c1` and `c2` objects using the `-` operator. The output shows that the `__sub__()` method is called when the `-` operator is used with two `Complex` objects.

### __mul__() Method
The `__mul__()` method is called when the `*` operator is used with two objects. It is used to multiply two objects. Let's see how to use the `__mul__()` method in Python.

```python title="mul.py" showLineNumbers{1} {6-8}
class Complex:
    def __init__(self, real, imag):
        self.real = real
        self.imag = imag

    def __mul__(self, other):
        return Complex(self.real * other.real, self.imag * other.imag)

c1 = Complex(1, 2)
c2 = Complex(3, 4)
c3 = c1 * c2
print(f'{c1.real} + {c1.imag}j * {c2.real} + {c2.imag}j = {c3.real} + {c3.imag}j')
```

Output:
```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\username>python mul.py
1 + 2j * 3 + 4j = 3 + 8j
```

In the above example, we have defined the `__mul__()` method in the `Complex` class. The `__mul__()` method returns a `Complex` object. We have created two `Complex` objects named `c1` and `c2`. We have multiplied the `c1` and `c2` objects using the `*` operator. The output shows that the `__mul__()` method is called when the `*` operator is used with two `Complex` objects.

### __truediv__() Method
The `__truediv__()` method is called when the `/` operator is used with two objects. It is used to divide two objects. Let's see how to use the `__truediv__()` method in Python.

```python title="truediv.py" showLineNumbers{1} {6-8}
class Complex:
    def __init__(self, real, imag):
        self.real = real
        self.imag = imag

    def __truediv__(self, other):
        return Complex(self.real / other.real, self.imag / other.imag)

c1 = Complex(1, 2)
c2 = Complex(3, 4)
c3 = c1 / c2
print(f'{c1.real} + {c1.imag}j / {c2.real} + {c2.imag}j = {c3.real} + {c3.imag}j')
```

Output:
```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\username>python truediv.py
1 + 2j / 3 + 4j = 0.3333333333333333 + 0.5j
```

In the above example, we have defined the `__truediv__()` method in the `Complex` class. The `__truediv__()` method returns a `Complex` object. We have created two `Complex` objects named `c1` and `c2`. We have divided the `c1` and `c2` objects using the `/` operator. The output shows that the `__truediv__()` method is called when the `/` operator is used with two `Complex` objects.

### __floordiv__() Method
The `__floordiv__()` method is called when the `//` operator is used with two objects. It is used to divide two objects. Let's see how to use the `__floordiv__()` method in Python.

```python title="floordiv.py" showLineNumbers{1} {6-8}
class Complex:
    def __init__(self, real, imag):
        self.real = real
        self.imag = imag

    def __floordiv__(self, other):
        return Complex(self.real // other.real, self.imag // other.imag)

c1 = Complex(1, 2)
c2 = Complex(3, 4)
c3 = c1 // c2
print(f'{c1.real} + {c1.imag}j // {c2.real} + {c2.imag}j = {c3.real} + {c3.imag}j')
```

Output:
```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\username>python floordiv.py
1 + 2j // 3 + 4j = 0 + 0j
```

In the above example, we have defined the `__floordiv__()` method in the `Complex` class. The `__floordiv__()` method returns a `Complex` object. We have created two `Complex` objects named `c1` and `c2`. We have divided the `c1` and `c2` objects using the `//` operator. The output shows that the `__floordiv__()` method is called when the `//` operator is used with two `Complex` objects.

### __mod__() Method
The `__mod__()` method is called when the `%` operator is used with two objects. It is used to find the remainder of two objects. Let's see how to use the `__mod__()` method in Python.

```python title="mod.py" showLineNumbers{1} {6-8}
class Complex:
    def __init__(self, real, imag):
        self.real = real
        self.imag = imag

    def __mod__(self, other):
        return Complex(self.real % other.real, self.imag % other.imag)

c1 = Complex(1, 2)
c2 = Complex(3, 4)
c3 = c1 % c2
print(f'{c1.real} + {c1.imag}j % {c2.real} + {c2.imag}j = {c3.real} + {c3.imag}j')
```

Output:
```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\username>python mod.py
1 + 2j % 3 + 4j = 1 + 2j
```

In the above example, we have defined the `__mod__()` method in the `Complex` class. The `__mod__()` method returns a `Complex` object. We have created two `Complex` objects named `c1` and `c2`. We have found the remainder of the `c1` and `c2` objects using the `%` operator. The output shows that the `__mod__()` method is called when the `%` operator is used with two `Complex` objects.

### __pow__() Method
The `__pow__()` method is called when the `**` operator is used with two objects. It is used to find the power of two objects. Let's see how to use the `__pow__()` method in Python.

```python title="pow.py" showLineNumbers{1} {5-6}
class Number:
    def __init__(self, num):
        self.num = num

    def __pow__(self, other):
        return Number(self.num ** other.num)

n1 = Number(2)
n2 = Number(3)
n3 = n1 ** n2
print(f'{n1.num} ** {n2.num} = {n3.num}')
```

Output:
```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\username>python pow.py
2 ** 3 = 8
```

In the above example, we have defined the `__pow__()` method in the `Number` class. The `__pow__()` method returns a `Number` object. We have created two `Number` objects named `n1` and `n2`. We have found the power of the `n1` and `n2` objects using the `**` operator. The output shows that the `__pow__()` method is called when the `**` operator is used with two `Number` objects.

### __and__() Method
The `__and__()` method is called when the `&` operator is used with two objects. It is used to perform the bitwise AND operation on two objects. Let's see how to use the `__and__()` method in Python.

```python title="and.py" showLineNumbers{1} {5-6}
class Number:
    def __init__(self, num):
        self.num = num

    def __and__(self, other):
        return Number(self.num & other.num)

n1 = Number(2)
n2 = Number(3)
n3 = n1 & n2
print(f'{n1.num} & {n2.num} = {n3.num}')
```

Output:
```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\username>python and.py
2 & 3 = 2
```

In the above example, we have defined the `__and__()` method in the `Number` class. The `__and__()` method returns a `Number` object. We have created two `Number` objects named `n1` and `n2`. We have performed the bitwise AND operation on the `n1` and `n2` objects using the `&` operator. The output shows that the `__and__()` method is called when the `&` operator is used with two `Number` objects.

### __or__() Method
The `__or__()` method is called when the `|` operator is used with two objects. It is used to perform the bitwise OR operation on two objects. Let's see how to use the `__or__()` method in Python.

```python title="or.py" showLineNumbers{1} {5-6}
class Number:
    def __init__(self, num):
        self.num = num

    def __or__(self, other):
        return Number(self.num | other.num)

n1 = Number(2)
n2 = Number(3)
n3 = n1 | n2
print(f'{n1.num} | {n2.num} = {n3.num}')
```

Output:
```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\username>python or.py
2 | 3 = 3
```

In the above example, we have defined the `__or__()` method in the `Number` class. The `__or__()` method returns a `Number` object. We have created two `Number` objects named `n1` and `n2`. We have performed the bitwise OR operation on the `n1` and `n2` objects using the `|` operator. The output shows that the `__or__()` method is called when the `|` operator is used with two `Number` objects.

### __xor__() Method
The `__xor__()` method is called when the `^` operator is used with two objects. It is used to perform the bitwise XOR operation on two objects. Let's see how to use the `__xor__()` method in Python.

```python title="xor.py" showLineNumbers{1} {5-6}
class Number:
    def __init__(self, num):
        self.num = num

    def __xor__(self, other):
        return Number(self.num ^ other.num)

n1 = Number(2)
n2 = Number(3)
n3 = n1 ^ n2
print(f'{n1.num} ^ {n2.num} = {n3.num}')
```

Output:
```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\username>python xor.py
2 ^ 3 = 1
```

In the above example, we have defined the `__xor__()` method in the `Number` class. The `__xor__()` method returns a `Number` object. We have created two `Number` objects named `n1` and `n2`. We have performed the bitwise XOR operation on the `n1` and `n2` objects using the `^` operator. The output shows that the `__xor__()` method is called when the `^` operator is used with two `Number` objects.

### __lt__() Method
The `__lt__()` method is called when the `<` operator is used with two objects. It is used to compare two objects. It returns `True` if the first object is less than the second object. Otherwise, it returns `False`. Let's see how to use the `__lt__()` method in Python.

```python title="lt.py" showLineNumbers{1} {5-6}
class Number:
    def __init__(self, num):
        self.num = num

    def __lt__(self, other):
        return self.num < other.num

n1 = Number(2)
n2 = Number(3)
print(f'{n1.num} < {n2.num} = {n1 < n2}')
print(f'{n2.num} < {n1.num} = {n2 < n1}')
```

Output:
```cmd title="command" showLineNumbers{1} {2-7}
C:\Users\username>python lt.py
2 < 3 = True
3 < 2 = False
```

In the above example, we have defined the `__lt__()` method in the `Number` class. The `__lt__()` method returns `True` if the first object is less than the second object. Otherwise, it returns `False`. We have created two `Number` objects named `n1` and `n2`. We have compared the `n1` and `n2` objects using the `<` operator. The output shows that the `__lt__()` method is called when the `<` operator is used with two `Number` objects.

### __le__() Method
The `__le__()` method is called when the `<=` operator is used with two objects. It is used to compare two objects. It returns `True` if the first object is less than or equal to the second object. Otherwise, it returns `False`. Let's see how to use the `__le__()` method in Python.

```python title="le.py" showLineNumbers{1} {5-6}
class Number:
    def __init__(self, num):
        self.num = num

    def __le__(self, other):
        return self.num <= other.num

n1 = Number(2)
n2 = Number(3)
print(f'{n1.num} <= {n2.num} = {n1 <= n2}')
print(f'{n2.num} <= {n1.num} = {n2 <= n1}')
print(f'{n1.num} <= {n1.num} = {n1 <= n1}')
```

Output:
```cmd title="command" showLineNumbers{1} {2-9}
C:\Users\username>python le.py
2 <= 3 = True
3 <= 2 = False
2 <= 2 = True
```

In the above example, we have defined the `__le__()` method in the `Number` class. The `__le__()` method returns `True` if the first object is less than or equal to the second object. Otherwise, it returns `False`. We have created two `Number` objects named `n1` and `n2`. We have compared the `n1` and `n2` objects using the `<=` operator. The output shows that the `__le__()` method is called when the `<=` operator is used with two `Number` objects.

### __eq__() Method
The `__eq__()` method is called when the `==` operator is used with two objects. It is used to compare two objects. It returns `True` if the first object is equal to the second object. Otherwise, it returns `False`. Let's see how to use the `__eq__()` method in Python.

```python title="eq.py" showLineNumbers{1} {5-6}
class Number:
    def __init__(self, num):
        self.num = num

    def __eq__(self, other):
        return self.num == other.num

n1 = Number(2)
n2 = Number(3)
print(f'{n1.num} == {n2.num} = {n1 == n2}')
print(f'{n2.num} == {n1.num} = {n2 == n1}')
print(f'{n1.num} == {n1.num} = {n1 == n1}')
```

Output:
```cmd title="command" showLineNumbers{1} {2-9}
C:\Users\username>python eq.py
2 == 3 = False
3 == 2 = False
2 == 2 = True
```

In the above example, we have defined the `__eq__()` method in the `Number` class. The `__eq__()` method returns `True` if the first object is equal to the second object. Otherwise, it returns `False`. We have created two `Number` objects named `n1` and `n2`. We have compared the `n1` and `n2` objects using the `==` operator. The output shows that the `__eq__()` method is called when the `==` operator is used with two `Number` objects.

### __ne__() Method
The `__ne__()` method is called when the `!=` operator is used with two objects. It is used to compare two objects. It returns `True` if the first object is not equal to the second object. Otherwise, it returns `False`. Let's see how to use the `__ne__()` method in Python.

```python title="ne.py" showLineNumbers{1} {5-6}
class Number:
    def __init__(self, num):
        self.num = num

    def __ne__(self, other):
        return self.num != other.num

n1 = Number(2)
n2 = Number(3)
print(f'{n1.num} != {n2.num} = {n1 != n2}')
print(f'{n2.num} != {n1.num} = {n2 != n1}')
print(f'{n1.num} != {n1.num} = {n1 != n1}')
```

Output:
```cmd title="command" showLineNumbers{1} {2-9}
C:\Users\username>python ne.py
2 != 3 = True
3 != 2 = True
2 != 2 = False
```

In the above example, we have defined the `__ne__()` method in the `Number` class. The `__ne__()` method returns `True` if the first object is not equal to the second object. Otherwise, it returns `False`. We have created two `Number` objects named `n1` and `n2`. We have compared the `n1` and `n2` objects using the `!=` operator. The output shows that the `__ne__()` method is called when the `!=` operator is used with two `Number` objects.

### __gt__() Method
The `__gt__()` method is called when the `>` operator is used with two objects. It is used to compare two objects. It returns `True` if the first object is greater than the second object. Otherwise, it returns `False`. Let's see how to use the `__gt__()` method in Python.

```python title="gt.py" showLineNumbers{1} {5-6}
class Number:
    def __init__(self, num):
        self.num = num

    def __gt__(self, other):
        return self.num > other.num

n1 = Number(2)
n2 = Number(3)
print(f'{n1.num} > {n2.num} = {n1 > n2}')
print(f'{n2.num} > {n1.num} = {n2 > n1}')
print(f'{n1.num} > {n1.num} = {n1 > n1}')
```

Output:
```cmd title="command" showLineNumbers{1} {2-9}
C:\Users\username>python gt.py
2 > 3 = False
3 > 2 = True
2 > 2 = False
```

In the above example, we have defined the `__gt__()` method in the `Number` class. The `__gt__()` method returns `True` if the first object is greater than the second object. Otherwise, it returns `False`. We have created two `Number` objects named `n1` and `n2`. We have compared the `n1` and `n2` objects using the `>` operator. The output shows that the `__gt__()` method is called when the `>` operator is used with two `Number` objects.

### __ge__() Method
The `__ge__()` method is called when the `>=` operator is used with two objects. It is used to compare two objects. It returns `True` if the first object is greater than or equal to the second object. Otherwise, it returns `False`. Let's see how to use the `__ge__()` method in Python.

```python title="ge.py" showLineNumbers{1} {5-6}
class Number:
    def __init__(self, num):
        self.num = num

    def __ge__(self, other):
        return self.num >= other.num

n1 = Number(2)
n2 = Number(3)
print(f'{n1.num} >= {n2.num} = {n1 >= n2}')
print(f'{n2.num} >= {n1.num} = {n2 >= n1}')
print(f'{n1.num} >= {n1.num} = {n1 >= n1}')
```

Output:
```cmd title="command" showLineNumbers{1} {2-9}
C:\Users\username>python ge.py
2 >= 3 = False
3 >= 2 = True
2 >= 2 = True
```

In the above example, we have defined the `__ge__()` method in the `Number` class. The `__ge__()` method returns `True` if the first object is greater than or equal to the second object. Otherwise, it returns `False`. We have created two `Number` objects named `n1` and `n2`. We have compared the `n1` and `n2` objects using the `>=` operator. The output shows that the `__ge__()` method is called when the `>=` operator is used with two `Number` objects.

### __getitem__() Method
The `__getitem__()` method is called when an item is accessed using the `[]` operator. It is used to access an item of an object. Let's see how to use the `__getitem__()` method in Python.

```python title="getitem.py" showLineNumbers{1} {5-6}
class Store:
    def __init__(self, items):
        self.items = items

    def __getitem__(self, index):
        return self.items[index]

store1 = Store(['Apple', 'Banana', 'Orange'])
print(store1[0])
print(store1[1])
print(store1[2])
```

Output:
```cmd title="command" showLineNumbers{1} {2-7}
C:\Users\username>python getitem.py
Apple
Banana
Orange
```

In the above example, we have defined the `__getitem__()` method in the `Store` class. The `__getitem__()` method returns an item of the `items` list. We have created an object named `store1` of the `Store` class. We have accessed the items of the `store1` object using the `[]` operator. The output shows that the `__getitem__()` method is called when an item is accessed using the `[]` operator.

### __setitem__() Method
The `__setitem__()` method is called when an item is assigned using the `[]` operator. It is used to assign an item of an object. Let's see how to use the `__setitem__()` method in Python.

```python title="setitem.py" showLineNumbers{1} {5-6}
class Store:
    def __init__(self, items):
        self.items = items

    def __setitem__(self, index, value):
        self.items[index] = value

store1 = Store(['Apple', 'Banana', 'Orange'])
store1[0] = 'Mango'
store1[1] = 'Grapes'
store1[2] = 'Watermelon'
print(store1[0])
print(store1[1])
print(store1[2])
```

Output:
```cmd title="command" showLineNumbers{1} {2-9}
C:\Users\username>python setitem.py
Mango
Grapes
Watermelon
```

In the above example, we have defined the `__setitem__()` method in the `Store` class. The `__setitem__()` method assigns an item of the `items` list. We have created an object named `store1` of the `Store` class. We have assigned the items of the `store1` object using the `[]` operator. The output shows that the `__setitem__()` method is called when an item is assigned using the `[]` operator.

### __delitem__() Method
The `__delitem__()` method is called when an item is deleted using the `del` operator. It is used to delete an item of an object. Let's see how to use the `__delitem__()` method in Python.

```python title="delitem.py" showLineNumbers{1} {5-6}
class Store:
    def __init__(self, items):
        self.items = items

    def __delitem__(self, index):
        del self.items[index]

store1 = Store(['Apple', 'Banana', 'Orange'])
del store1[0]
print(store1.items)
del store1[1]
print(store1.items)
```

Output:
```cmd title="command" showLineNumbers{1} {2-7}
C:\Users\username>python delitem.py
['Banana', 'Orange']
['Banana']
```

In the above example, we have defined the `__delitem__()` method in the `Store` class. The `__delitem__()` method deletes an item of the `items` list. We have created an object named `store1` of the `Store` class. We have deleted the items of the `store1` object using the `del` operator. The output shows that the `__delitem__()` method is called when an item is deleted using the `del` operator.

### __contains__() Method
The `__contains__()` method is called when the `in` operator is used with two objects. It is used to check if an item is present in an object. It returns `True` if the item is present in the object. Otherwise, it returns `False`. Let's see how to use the `__contains__()` method in Python.

```python title="contains.py" showLineNumbers{1} {5-6}
class Store:
    def __init__(self, items):
        self.items = items

    def __contains__(self, item):
        return item in self.items

store1 = Store(['Apple', 'Banana', 'Orange'])
print('Apple' in store1)
print('Mango' in store1)
```

Output:
```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\username>python contains.py
True
False
```

In the above example, we have defined the `__contains__()` method in the `Store` class. The `__contains__()` method returns `True` if the item is present in the object. Otherwise, it returns `False`. We have created an object named `store1` of the `Store` class. We have checked if the items are present in the `store1` object using the `in` operator. The output shows that the `__contains__()` method is called when the `in` operator is used with two objects.

### __call__() Method
The `__call__()` method is called when an object is called as a function. It is used to call an object as a function. Let's see how to use the `__call__()` method in Python.

```python title="call.py" showLineNumbers{1} {5-6}
class Store:
    def __init__(self, items):
        self.items = items

    def __call__(self, item):
        return item in self.items

store1 = Store(['Apple', 'Banana', 'Orange'])
print(store1('Apple'))
print(store1('Mango'))
```

Output:
```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\username>python call.py
True
False
```

In the above example, we have defined the `__call__()` method in the `Store` class. The `__call__()` method returns `True` if the item is present in the object. Otherwise, it returns `False`. We have created an object named `store1` of the `Store` class. We have called the `store1` object as a function. The output shows that the `__call__()` method is called when an object is called as a function.

### __enter__() & __exit__() Methods
The `__enter__()` and `__exit__()` methods are called when an object is used with the `with` statement. It is used to create a context manager. Let's see how to use the `__enter__()` and `__exit__()` methods in Python.

```python title="enter_exit.py" showLineNumbers{1} {5-7, 9-10, 12-13}
class Store:
    def __init__(self, items):
        self.items = items

    def __enter__(self):
        print('Entering the Store')
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        print('Exiting the Store')

    def __contains__(self, item):
        return item in self.items

store1 = Store(['Apple', 'Banana', 'Orange'])
with store1 as store:
    print('Apple' in store)
    print('Mango' in store)
```

Output:
```cmd title="command" showLineNumbers{1} {2-15}
C:\Users\username>python enter_exit.py
Entering the Store
True
False
Exiting the Store
```

In the above example, we have defined the `__enter__()` and `__exit__()` methods in the `Store` class. The `__enter__()` method is called when the `with` statement is used with an object. The `__exit__()` method is called when the `with` statement is exited. We have created an object named `store1` of the `Store` class. We have used the `store1` object with the `with` statement. The output shows that the `__enter__()` and `__exit__()` methods are called when an object is used with the `with` statement.

### __iter__() Method
The `__iter__()` method is called when an object is iterated using the `for` loop. It is used to iterate over an object. Let's see how to use the `__iter__()` method in Python.

```python title="iter.py" showLineNumbers{1} {5-6}
class Store:
    def __init__(self, items):
        self.items = items

    def __iter__(self):
        return iter(self.items)

store1 = Store(['Apple', 'Banana', 'Orange'])
for item in store1:
    print(item)
```

Output:
```cmd title="command" showLineNumbers{1} {2-6}
C:\Users\username>python iter.py
Apple
Banana
Orange
```

In the above example, we have defined the `__iter__()` method in the `Store` class. The `__iter__()` method returns an iterator object. We have created an object named `store1` of the `Store` class. We have iterated over the `store1` object using the `for` loop. The output shows that the `__iter__()` method is called when an object is iterated using the `for` loop.

### __next__() Method
The `__next__()` method is called when the `next()` function is called on an iterator object. It is used to return the next item of an iterator object. Let's see how to use the `__next__()` method in Python.

```python title="next.py" showLineNumbers{1} {6-14}
class Store:
    def __init__(self, items):
        self.items = items
        self.index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.index >= len(self.items):
            raise StopIteration
        item = self.items[self.index]
        self.index += 1
        return item

store1 = Store(['Apple', 'Banana', 'Orange'])
print(next(store1))
print(next(store1))
print(next(store1))
print(next(store1))
```

Output:
```cmd title="command" showLineNumbers{1} {2-9}
C:\Users\username>python next.py
Apple
Banana
Orange
Traceback (most recent call last):
  File "next.py", line 21, in <module>
    print(next(store1))
  File "next.py", line 12, in __next__
    raise StopIteration
StopIteration
```

In the above example, we have defined the `__next__()` method in the `Store` class. The `__next__()` method returns the next item of the `items` list. We have created an object named `store1` of the `Store` class. We have called the `next()` function on the `store1` object. The output shows that the `__next__()` method is called when the `next()` function is called on an iterator object.

### __reversed__() Method
The `__reversed__()` method is called when the `reversed()` function is called on an object. It is used to return a reversed iterator object. Let's see how to use the `__reversed__()` method in Python.

```python title="reversed.py" showLineNumbers{1} {5-6}
class Store:
    def __init__(self, items):
        self.items = items

    def __reversed__(self):
        return reversed(self.items)

store1 = Store(['Apple', 'Banana', 'Orange'])
for item in reversed(store1):
    print(item)
```

Output:
```cmd title="command" showLineNumbers{1} {2-6}
C:\Users\username>python reversed.py
Orange
Banana
Apple
```

In the above example, we have defined the `__reversed__()` method in the `Store` class. The `__reversed__()` method returns a reversed iterator object. We have created an object named `store1` of the `Store` class. We have iterated over the `store1` object using the `for` loop. The output shows that the `__reversed__()` method is called when the `reversed()` function is called on an object.

### __hash__() Method
The `__hash__()` method is called when the `hash()` function is called on an object. It is used to return the hash value of an object. Let's see how to use the `__hash__()` method in Python.

```python title="hash.py" showLineNumbers{1} {5-6}
class Store:
    def __init__(self, items):
        self.items = items

    def __hash__(self):
        return hash(self.items)

store1 = Store(['Apple', 'Banana', 'Orange'])
print(hash(store1))
```

Output:
```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\username>python hash.py
-9223372036574775808
```

In the above example, we have defined the `__hash__()` method in the `Store` class. The `__hash__()` method returns the hash value of the `items` list. We have created an object named `store1` of the `Store` class. We have called the `hash()` function on the `store1` object. The output shows that the `__hash__()` method is called when the `hash()` function is called on an object.

### __bool__() Method
The `__bool__()` method is called when the `bool()` function is called on an object. It is used to return the boolean value of an object. Let's see how to use the `__bool__()` method in Python.

```python title="bool.py" showLineNumbers{1} {5-6}
class Number:
    def __init__(self, num):
        self.num = num

    def __bool__(self):
        return bool(self.num)

n1 = Number(0)
n2 = Number(1)
print(bool(n1))
print(bool(n2))
```

Output:
```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\username>python bool.py
False
True
```

In the above example, we have defined the `__bool__()` method in the `Number` class. The `__bool__()` method returns the boolean value of the `num` attribute. We have created two `Number` objects named `n1` and `n2`. We have called the `bool()` function on the `n1` and `n2` objects. The output shows that the `__bool__()` method is called when the `bool()` function is called on an object.

### __format__() Method
The `__format__()` method is called when the `format()` function is called on an object. It is used to return the formatted string of an object. Let's see how to use the `__format__()` method in Python.

```python title="format.py" showLineNumbers{1} {5-6}
class Number:
    def __init__(self, num):
        self.num = num

    def __format__(self, format_spec):
        return format(self.num, format_spec)

n1 = Number(2)
n2 = Number(3)
print(format(n1, 'b'))
print(format(n2, 'b'))
```

Output:
```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\username>python format.py
10
11
```

In the above example, we have defined the `__format__()` method in the `Number` class. The `__format__()` method returns the formatted string of the `num` attribute. We have created two `Number` objects named `n1` and `n2`. We have called the `format()` function on the `n1` and `n2` objects. The output shows that the `__format__()` method is called when the `format()` function is called on an object.

### __index__() Method
The `__index__()` method is called when the `index()` function is called on an object. It is used to return the index of an object. Let's see how to use the `__index__()` method in Python.

```python title="index.py" showLineNumbers{1} {5-6}
class Number:
    def __init__(self, num):
        self.num = num

    def __index__(self):
        return self.num

n1 = Number(2)
n2 = Number(3)
print(index(n1))
print(index(n2))
```

Output:
```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\username>python index.py
2
3
```

In the above example, we have defined the `__index__()` method in the `Number` class. The `__index__()` method returns the index of the `num` attribute. We have created two `Number` objects named `n1` and `n2`. We have called the `index()` function on the `n1` and `n2` objects. The output shows that the `__index__()` method is called when the `index()` function is called on an object.

### __int__() Method
The `__int__()` method is called when the `int()` function is called on an object. It is used to return the integer value of an object. Let's see how to use the `__int__()` method in Python.

```python title="int.py" showLineNumbers{1} {6-7}
class Complex:
    def __init__(self, real, imag):
        self.real = real
        self.imag = imag

    def __int__(self):
        return int(self.real)

c1 = Complex(2.5, 3.5)
c2 = Complex(3.5, 4.5)
print(int(c1))
print(int(c2))
```

Output:
```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\username>python int.py
2
3
```

In the above example, we have defined the `__int__()` method in the `Complex` class. The `__int__()` method returns the integer value of the `real` attribute. We have created two `Complex` objects named `c1` and `c2`. We have called the `int()` function on the `c1` and `c2` objects. The output shows that the `__int__()` method is called when the `int()` function is called on an object.

### __float__() Method
The `__float__()` method is called when the `float()` function is called on an object. It is used to return the float value of an object. Let's see how to use the `__float__()` method in Python.

```python title="float.py" showLineNumbers{1} {5-6}
class Complex:
    def __init__(self, real, imag):
        self.real = real
        self.imag = imag

    def __float__(self):
        return float(self.real)

c1 = Complex(2.5, 3.5)
c2 = Complex(3.5, 4.5)
print(float(c1))
print(float(c2))
```

Output:
```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\username>python float.py
2.5
3.5
```

In the above example, we have defined the `__float__()` method in the `Complex` class. The `__float__()` method returns the float value of the `real` attribute. We have created two `Complex` objects named `c1` and `c2`. We have called the `float()` function on the `c1` and `c2` objects. The output shows that the `__float__()` method is called when the `float()` function is called on an object.

### __complex__() Method
The `__complex__()` method is called when the `complex()` function is called on an object. It is used to return the complex value of an object. Let's see how to use the `__complex__()` method in Python.

```python title="complex.py" showLineNumbers{1} {5-6}
class Number:
    def __init__(self, num):
        self.num = num

    def __complex__(self):
        return complex(self.num)

n1 = Number(2)
n2 = Number(3)
print(complex(n1))
print(complex(n2))
```

Output:
```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\username>python complex.py
(2+0j)
(3+0j)
```

In the above example, we have defined the `__complex__()` method in the `Number` class. The `__complex__()` method returns the complex value of the `num` attribute. We have created two `Number` objects named `n1` and `n2`. We have called the `complex()` function on the `n1` and `n2` objects. The output shows that the `__complex__()` method is called when the `complex()` function is called on an object.

### __round__() Method
The `__round__()` method is called when the `round()` function is called on an object. It is used to return the rounded value of an object. Let's see how to use the `__round__()` method in Python.

```python title="round.py" showLineNumbers{1} {5-6}
class Number:
    def __init__(self, num):
        self.num = num

    def __round__(self):
        return round(self.num)

n1 = Number(2.5)
n2 = Number(3.5)
print(round(n1))
print(round(n2))
```

Output:
```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\username>python round.py
2
4
```

In the above example, we have defined the `__round__()` method in the `Number` class. The `__round__()` method returns the rounded value of the `num` attribute. We have created two `Number` objects named `n1` and `n2`. We have called the `round()` function on the `n1` and `n2` objects. The output shows that the `__round__()` method is called when the `round()` function is called on an object.

### __floor__() Method
The `__floor__()` method is called when the `math.floor()` function is called on an object. It is used to return the floor value of an object. Let's see how to use the `__floor__()` method in Python.

```python title="floor.py" showLineNumbers{1} {7-8}
import math

class Number:
    def __init__(self, num):
        self.num = num

    def __floor__(self):
        return math.floor(self.num)

n1 = Number(2.5)
n2 = Number(3.5)
print(math.floor(n1))
print(math.floor(n2))
```

Output:
```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\username>python floor.py
2
3
```

In the above example, we have defined the `__floor__()` method in the `Number` class. The `__floor__()` method returns the floor value of the `num` attribute. We have created two `Number` objects named `n1` and `n2`. We have called the `math.floor()` function on the `n1` and `n2` objects. The output shows that the `__floor__()` method is called when the `math.floor()` function is called on an object.

### __ceil__() Method
The `__ceil__()` method is called when the `math.ceil()` function is called on an object. It is used to return the ceil value of an object. Let's see how to use the `__ceil__()` method in Python.

```python title="ceil.py" showLineNumbers{1} {7-8}
import math

class Number:
    def __init__(self, num):
        self.num = num

    def __ceil__(self):
        return math.ceil(self.num)

n1 = Number(2.5)
n2 = Number(3.5)
print(math.ceil(n1))
print(math.ceil(n2))
```

Output:
```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\username>python ceil.py
3
4
```

In the above example, we have defined the `__ceil__()` method in the `Number` class. The `__ceil__()` method returns the ceil value of the `num` attribute. We have created two `Number` objects named `n1` and `n2`. We have called the `math.ceil()` function on the `n1` and `n2` objects. The output shows that the `__ceil__()` method is called when the `math.ceil()` function is called on an object.

### __trunc__() Method
The `__trunc__()` method is called when the `math.trunc()` function is called on an object. It is used to return the truncated value of an object. Let's see how to use the `__trunc__()` method in Python.

```python title="trunc.py" showLineNumbers{1} {7-8}
import math

class Number:
    def __init__(self, num):
        self.num = num

    def __trunc__(self):
        return math.trunc(self.num)

n1 = Number(2.5)
n2 = Number(3.5)
print(math.trunc(n1))
print(math.trunc(n2))
```

Output:
```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\username>python trunc.py
2
3
```

In the above example, we have defined the `__trunc__()` method in the `Number` class. The `__trunc__()` method returns the truncated value of the `num` attribute. We have created two `Number` objects named `n1` and `n2`. We have called the `math.trunc()` function on the `n1` and `n2` objects. The output shows that the `__trunc__()` method is called when the `math.trunc()` function is called on an object.

### __pos__() Method
The `__pos__()` method is called when the `+` operator is used with an object. It is used to return the positive value of an object. Let's see how to use the `__pos__()` method in Python.

```python title="pos.py" showLineNumbers{1} {5-6}
class Number:
    def __init__(self, num):
        self.num = num

    def __pos__(self):
        return abs(self.num)

n1 = Number(-2)
n2 = Number(3)
print(+n1)
print(+n2)
```

Output:
```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\username>python pos.py
2
3
```

In the above example, we have defined the `__pos__()` method in the `Number` class. The `__pos__()` method returns the positive value of the `num` attribute. We have created two `Number` objects named `n1` and `n2`. We have used the `+` operator with the `n1` and `n2` objects. The output shows that the `__pos__()` method is called when the `+` operator is used with an object.

### __neg__() Method
The `__neg__()` method is called when the `-` operator is used with an object. It is used to return the negative value of an object. Let's see how to use the `__neg__()` method in Python.

```python title="neg.py" showLineNumbers{1} {5-6}
class Number:
    def __init__(self, num):
        self.num = num

    def __neg__(self):
        return -self.num

n1 = Number(2)
n2 = Number(3)
print(-n1)
print(-n2)
```

Output:
```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\username>python neg.py
-2
-3
```

In the above example, we have defined the `__neg__()` method in the `Number` class. The `__neg__()` method returns the negative value of the `num` attribute. We have created two `Number` objects named `n1` and `n2`. We have used the `-` operator with the `n1` and `n2` objects. The output shows that the `__neg__()` method is called when the `-` operator is used with an object.

### __abs__() Method
The `__abs__()` method is called when the `abs()` function is called on an object. It is used to return the absolute value of an object. Let's see how to use the `__abs__()` method in Python.

```python title="abs.py" showLineNumbers{1} {5-6}
class Number:
    def __init__(self, num):
        self.num = num

    def __abs__(self):
        return abs(self.num)

n1 = Number(-2)
n2 = Number(3)
print(abs(n1))
print(abs(n2))
```

Output:
```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\username>python abs.py
2
3
```

In the above example, we have defined the `__abs__()` method in the `Number` class. The `__abs__()` method returns the absolute value of the `num` attribute. We have created two `Number` objects named `n1` and `n2`. We have called the `abs()` function on the `n1` and `n2` objects. The output shows that the `__abs__()` method is called when the `abs()` function is called on an object.

### __invert__() Method
The `__invert__()` method is called when the `~` operator is used with an object. It is used to return the inverted value of an object. Let's see how to use the `__invert__()` method in Python.

```python title="invert.py" showLineNumbers{1} {5-6}
class Number:
    def __init__(self, num):
        self.num = num

    def __invert__(self):
        return ~self.num

n1 = Number(2)
n2 = Number(3)
print(~n1)
print(~n2)
```

Output:
```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\username>python invert.py
-3
-4
```

In the above example, we have defined the `__invert__()` method in the `Number` class. The `__invert__()` method returns the inverted value of the `num` attribute. We have created two `Number` objects named `n1` and `n2`. We have used the `~` operator with the `n1` and `n2` objects. The output shows that the `__invert__()` method is called when the `~` operator is used with an object.

## Multiple Dispatch
Multiple dispatch is a feature of some programming languages in which a function or method can be dynamically dispatched based on the run time (dynamic) type or, in the more general case, some other attribute of more than one of its arguments. This is a generalization of single dispatch polymorphism and subclass polymorphism, where a method call is dynamically dispatched based on the class of one object.

In python, we can use the `multipledispatch` library to implement multiple dispatch. Let's see how to use the `multipledispatch` library in Python.

```cmd title="command" showLineNumbers{1} {1}
C:\Users\username>pip install multipledispatch
```

In the above example, we have installed the `multipledispatch` library using the `pip` command.

```python title="main.py" showLineNumbers{1} {1, 4-7, 9-12, 14-17, 19-22} 
from multipledispatch import dispatch

class Calculator:
    @dispatch(int, int)
    def add(self, a, b):
        print("Two Numbers Argument")
        return a + b

    @dispatch(int, int, int)
    def add(self, a, b, c):
        print("Three Numbers Argument")
        return a + b + c

    @dispatch(float, float)
    def add(self, a, b):
        print("Two Floats Argument")
        return a + b

    @dispatch(str, str)
    def add(self, a, b):
        print("Two Strings Argument")
        return a + b

calculator = Calculator()
print(calculator.add(2, 3))
print(calculator.add(2, 3, 4))
print(calculator.add(2.5, 3.5))
print(calculator.add('Hello', 'World'))
```

Output:
```cmd title="command" showLineNumbers{1} {2-17}
C:\Users\username>python main.py
Two Numbers Argument
5
Three Numbers Argument
9
Two Floats Argument
6.0
Two Strings Argument
HelloWorld
```

In the above example, we have defined the `Calculator` class. We have defined the `add()` method in the `Calculator` class. We have used the `@dispatch` decorator to define the `add()` method with different arguments. We have created an object named `calculator` of the `Calculator` class. We have called the `add()` method of the `calculator` object with different arguments. The output shows that the `add()` method is called based on the arguments. If the arguments are `int` and `int`, then the `add()` method with two `int` arguments is called. If the arguments are `int`, `int`, and `int`, then the `add()` method with three `int` arguments is called. If the arguments are `float` and `float`, then the `add()` method with two `float` arguments is called. If the arguments are `str` and `str`, then the `add()` method with two `str` arguments is called.

