---
title: Class in Python
description: Learn about Class in Python. How class is used in Python. How to create a class in Python. What are the properties of class and methods.
sidebar: 
    order: 81
---

## Class in Python
In object-oriented programming (OOP), a class is a blueprint or template for creating objects. It defines a set of attributes (data members) and methods (functions) that characterize any object instantiated from that class. A class encapsulates the common properties and behaviors that its objects share. It serves as a blueprint for creating instances or objects, providing a way to model and organize code in a modular and reusable fashion.

## How to create a class in Python
You can create a class in Python using the `class` keyword followed by the name of the class and a colon `:`. The class body is indented and contains class attributes (data members) and methods (functions).

**Syntax:**
```python title="class.py" showLineNumbers{1} {1-5}
class ClassName:
    pass
```

In the above example, we have created a class named `ClassName`. The class body is empty. We have used the `pass` keyword to avoid getting an error. The `pass` keyword is used as a placeholder for future code.

## How to create an object of a class in Python
You can create an object of a class in Python using the class name followed by parentheses `()`.

**Syntax:**
```python title="class.py" showLineNumbers{1} {4}
class ClassName:
    pass

object_name = ClassName()
```

In the above example, we have created an object of the `ClassName` class. We have assigned the object to the `object_name` variable.

## Example: Create a class and object in Python
```python title="class.py" {1-5}
class Person:
    pass
```

In the above example, we have created a class named `Person`. The class body is empty. We have used the `pass` keyword to avoid getting an error. The `pass` keyword is used as a placeholder for future code.

```python title="class.py" {4-5}
class Person:
    pass

person = Person()
print(person)
```

Output:
```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python class.py
<__main__.Person object at 0x0000020E7F7F4F70>
```

In the above example, we have created an object of the `Person` class. We have assigned the object to the `person` variable. We have printed the `person` variable. The output shows the memory address of the object.

:::note
**Instance**: An individual object of a certain class. An object obj that belongs to a class Circle, for example, is an instance of the class Circle.

**Instantiation**: The creation of an instance of a class.

**Object**: A unique instance of a data structure that's defined by its class. An object comprises both data members (class variables and instance variables) and methods.

```mermaid title="Class, Object, and Instance" desc="Person is a class. person1 and person2 are objects. person1 and person2 are instances of the Person class."
classDiagram
    class Person {
        - name: String
        - age: int
        + say_hi(): void
    }
    class person1{
        - name: "John"
        - age: 20
        + say_hi(): void
    }
    class person2{
        - name: "Bob"
        - age: 30
        + say_hi(): void
    }
    Person --|> person1 : instance/object
    Person --|> person2 : instance/object
```

In the above example, we have created a class named `Person`. The `Person` class has two data members `name` and `age` and one method `say_hi()`. We have created two objects `person1` and `person2` of the `Person` class. The `person1` and `person2` objects have the same data members and methods as the `Person` class. The `person1` and `person2` objects are instances of the `Person` class.

:::

## Instance Variables
In Python, an instance variable is a variable that is defined inside a method and belongs only to the current instance of a class. Instance variables are not shared by all instances of a class. Each instance variable is unique to the object. They are defined inside the constructor method `__init__(self)`.

#### Properties of instance variables:
- Instance variables are owned by objects of the class.
- Instance variables are not shared by all objects of the class. Each object has its own copy of the instance variable.
- Instance variables are defined inside the constructor method `__init__(self)`.
- Instance variables are initialized using the `self` keyword.
- Instance variables can be accessed using the dot `.` operator with the object.
- Instance variables can be accessed outside the class using the object name.

## Example: Instance variables in Python
```python title="class.py" showLineNumbers{1} {1-6}
class Person:
    '''This is a Person class'''
    def __init__(self, name):
        self.name = name
    def say_hi(self):
        print('Hello, my name is', self.name)

person1 = Person('John')
person2 = Person('Bob')
print(person1.name)
print(person2.name)
```

Output:
```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python class.py
John
Bob
```

In the above example, we have created an instance variable named `name`. We have initialized the `name` variable to the `name` parameter of the `__init__()` method. We have printed the `name` variable using the `person1` and `person2` objects. The output shows that the `name` variable is unique to the object.

Another example of instance variables:
```python title="class.py" showLineNumbers{1} {1-10}
class Employee:
    '''This is an Employee class'''
    name # Optional
    salary # Optional
    def __init__(self, name, salary):
        self.name = name
        self.salary = salary
    def display(self):
        print('Name:', self.name)
        print('Salary:', self.salary)

employee1 = Employee('John', 10000)
employee2 = Employee('Bob', 20000)
employee1.display()
employee2.display()
```

Output:
```cmd title="command" showLineNumbers{1} {2-7}
C:\Users\username>python class.py
Name: John
Salary: 10000
Name: Bob
Salary: 20000
```

In the above example, we have created two instance variables named `name` and `salary`. We have initialized the `name` and `salary` variables to the `name` and `salary` parameters of the `__init__()` method. We have printed the `name` and `salary` variables using the `employee1` and `employee2` objects. The output shows that the `name` and `salary` variables are unique to the object.

## Class Variables
In Python, a class variable is a variable that is shared by all objects of a class. Class variables are defined within the class construction. Because class variables are owned by the class itself, they are shared by all instances of the class. They therefore will generally have the same value for every instance unless you are using the class variable to initialize a variable.

#### Properties of class variables:
- Class variables are owned by the class itself.
- Class variables are shared by all objects of the class.
- Class variables are defined within the class construction.
- Class variables are initialized using the class name.
- Class variables can be accessed using the dot `.` operator with the class name.
- Class variables can be accessed outside the class using the class name.
- Class variables can be accessed outside the class using the object name.

## Example: Class variables in Python
```python title="class.py" showLineNumbers{1} {3}
class Person:
    '''This is a Person class'''
    count = 0
    def __init__(self, name):
        self.name = name
        Person.count += 1
    def say_hi(self):
        print('Hello, my name is', self.name)

person1 = Person('John')
person2 = Person('Bob')
print(person1.count)
print(person2.count)
print(Person.count)
```

Output:
```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\username>python class.py
2
2
2
```

In the above example, we have created a class variable named `count`. We have initialized the `count` variable to `0`. We have incremented the `count` variable by `1` in the `__init__()` method. We have printed the `count` variable using the `person1`, `person2`, and `Person` objects. The output shows that the `count` variable is shared by all objects of the `Person` class. 

:::tip
You can access the class variable using the class name.

```python title="class.py" showLineNumbers{1} {12}
class Person:
    '''This is a Person class'''
    count = 0
    def __init__(self, name):
        self.name = name
        Person.count += 1
    def say_hi(self):
        print('Hello, my name is', self.name)

person1 = Person('John')
person2 = Person('Bob')
print(Person.count)
```

Output:
```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python class.py
2
```

In the above example, we have printed the `count` variable using the `Person` class name. The output shows that the `count` variable is shared by all objects of the `Person` class.
:::

## Class attributes
Every python class have the following built-in attributes:
- `__name__`: It returns the name of the class.
- `__module__`: It returns the name of the module in which the class is defined.
- `__dict__`: It returns a dictionary containing the class's namespace.
- `__doc__`: It returns the class documentation string or `None` if undefined.
- `__bases__`: It returns a tuple containing the base classes, in the order of their occurrence in the base class list.

## Example: Class attributes in Python
```python title="class.py" showLineNumbers{1} {8-13}
class Person:
    '''This is a Person class'''
    def __init__(self, name):
        self.name = name
    def say_hi(self):
        print('Hello, my name is', self.name)

print(Person.__name__)
print(Person.__module__)
print(Person.__dict__)
print(Person.__doc__)
print(Person.__bases__)
```

Output:
```cmd title="command" showLineNumbers{1} {2-6}
C:\Users\username>python class.py
Person
__main__
{'__module__': '__main__', '__doc__': 'This is a Person class', '__init__': <function Person.__init__ at 0x0000020E7F7F1CA0>, 'say_hi': <function Person.say_hi at 0x0000020E7F7F1D30>}
This is a Person class
(<class 'object'>,)
```

In the above example, we have printed the class attributes. We have used the `__name__`, `__module__`, `__dict__`, `__doc__`, and `__bases__` attributes to print the class attributes.

:::note
Python Documentation Strings (or docstrings) provide a convenient way of associating documentation with Python modules, functions, classes, and methods. It's specified in source code that is used, like a comment, to document a specific segment of code. Unlike conventional source code comments, the docstring should describe what the function does, not how.

The docstring is declared using triple quotes `'''` or `"""` at the top of the class. The docstring is available in the `__doc__` attribute of the class.

```python title="class.py" showLineNumbers{1} {2}
class Person:
    '''This is a Person class'''
    pass

print(Person.__doc__)
```

Output:
```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python class.py
This is a Person class
```

In the above example, we have printed the docstring of the `Person` class. We have used the `__doc__` attribute to print the docstring of the `Person` class.

Another way to read the docstring is to use the `help()` function.

```python title="class.py" showLineNumbers{1} {2}
class Person:
    '''This is a Person class'''
    pass

help(Person)
```

Output:
```cmd title="command" showLineNumbers{1} {3}
C:\Users\username>python class.py
class Person(builtins.object)
 |  This is a Person class
 |
 |  Data descriptors defined here:
 |
 |  __dict__
 |      dictionary for instance variables (if defined)
 |
 |  __weakref__
 |      list of weak references to the object (if defined)
```

In the above example, we have printed the docstring of the `Person` class. We have used the `help()` function to print the docstring of the `Person` class.
:::
