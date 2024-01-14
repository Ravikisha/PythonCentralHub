---
title: Constructor in Python
description: Learn about Constructor in Python. How to create a constructor in Python. What is the use of a constructor in Python. How to use a constructor in Python. How to create a constructor with parameters in Python. How to create a constructor without parameters in Python. How to create a default constructor in Python. How to create a parameterized constructor in Python. How to create a constructor with default parameters in Python.
sidebar: 
    order: 83
---

## Constructors in Python: Initializing Objects with Purpose
In object-oriented programming, a constructor is a special method used for initializing instances of a class. In Python, the constructor method is named __init__, and it is automatically called when an object is created from a class. Constructors play a crucial role in setting up the initial state of objects, allowing for proper initialization and configuration. Let's explore the key aspects of constructors in Python.

<!-- ```python title="instance_method.py" showLineNumbers{1} {5-7, 11-12}
class Student:
    def register(self, name, roll):
        self.name = name
        self.roll = roll

    def display(self):
        print('Name:', self.name)
        print('Roll:', self.roll)

student1 = Student()
student1.register('John', 1)
student1.display()
```

Output:
```cmd title="command" showLineNumbers{1} {2-7}
C:\Users\username>python instance_method.py
Name: John
Roll: 1
```

In the above example, we have created two instance variables named `name` and `roll`. We have initialized the `name` and `roll` variables to the `name` and `roll` parameters of the `register()` method. We have printed the `name` and `roll` variables using the `student1` object. The output shows that the `name` and `roll` variables are unique to the object. -->

## What is a Constructor in Python?
A constructor is a special method of a class or structure in object-oriented programming that initializes a newly created object of that type. Whenever an object is created, the constructor is automatically called. It is used to initialize the object's state. Constructors can also be used to perform any required initialization of the object before it is used. Constructors are not mandatory in Python, but they are used to initialize the state of an object.

## How to Create a Constructor in Python?
In Python, the constructor method is named `__init__`. It is automatically called when an object is created from a class. The `__init__` method is used to initialize the state of an object. The `__init__` method is called the constructor method because it is called when an object is created. 

```python title="constructor.py" showLineNumbers{1} {2-5}
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

In the above example, we have created two instance variables named `name` and `roll`. We have initialized the `name` and `roll` variables to the `name` and `roll` parameters of the `__init__()` method. We have printed the `name` and `roll` variables using the `student1` object. The output shows that the `name` and `roll` variables are unique to the object.

:::note
The `__init__()` method is called the constructor method because it is called when an object is created. It takes a reference to the newly created object as the first argument. The `self` parameter is a reference to the current instance of the class, and is used to access variables that belong to the class. It is not a keyword in Python, but it is a naming convention that is used by most Python programmers. `self` is the first parameter of any method in a class. You can use any name for the first parameter of a method, but `self` is the most common name.

```python title="constructor.py" showLineNumbers{1} {2-5}
class Student:
    def __init__(student, name, roll):
        student.name = name
        student.roll = roll

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

In the above example, we have used `student` instead of `self` as the first parameter of the `__init__()` method. We have initialized the `name` and `roll` variables to the `name` and `roll` parameters of the `__init__()` method. We have printed the `name` and `roll` variables using the `student1` object. The output shows that the `name` and `roll` variables are unique to the object.

:::

## What is the Use of a Constructor in Python?
Constructors are used to initialize the state of an object. They are used to set the initial values of the instance variables of an object. They are used to initialize the state in a better way. You can directly assign values to the instance variables of an object, but it is not a good practice. It is better to use a constructor to initialize the state of an object.

### Initializing Instance Variables Directly
```python title="instance_variables.py" showLineNumbers{1} {2-3}
class Student:
    name
    age

student1 = Student()
student1.name = 'John'
student1.age = 20
print('Name:', student1.name)
print('Age:', student1.age)
```

Output:
```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python instance_variables.py
Name: John
Age: 20
```

In the above example, we have created two instance variables named `name` and `age`. We have initialized the `name` and `age` variables to the `name` and `age` values of the `student1` object. We have printed the `name` and `age` variables using the `student1` object. The output shows that the `name` and `age` variables are unique to the object.

### Initializing Instance Variables Using a Constructor
```python title="constructor.py" showLineNumbers{1} {2-5}
class Student:
    def __init__(self, name, age):
        self.name = name
        self.age = age

student1 = Student('John', 20)
print('Name:', student1.name)
print('Age:', student1.age)
```

Output:
```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\username>python constructor.py
Name: John
Age: 20
```

In the above example, we have created two instance variables named `name` and `age`. We have initialized the `name` and `age` variables to the `name` and `age` parameters of the `__init__()` method. We have printed the `name` and `age` variables using the `student1` object. The output shows that the `name` and `age` variables are unique to the object.

## How to Use a Constructor in Python?
In Python, the constructor method is named `__init__`. It is automatically called when an object is created from a class. The `__init__` method is used to initialize the state of an object. The `__init__` method is called the constructor method because it is called when an object is created. You need to pass the required parameters to the `__init__` method when creating an object except the `self` parameter.

```python title="constructor.py" showLineNumbers{1} {2-5}
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

In the above example, we have created two instance variables named `name` and `roll`. We have initialized the `name` and `roll` variables to the `name` and `roll` parameters of the `__init__()` method. We have printed the `name` and `roll` variables using the `student1` object. The output shows that the `name` and `roll` variables are unique to the object.

## Types of Constructors in Python
There are two types of constructors in Python:
- **Default Constructor**: A default constructor is a constructor that does not take any parameters. It is used to initialize the instance variables of an object to their default values. It is automatically called when an object is created from a class. It is used to initialize the state of an object. It is called the default constructor because it is called when an object is created without any parameters.
- **Parameterized Constructor**: A parameterized constructor is a constructor that takes one or more parameters. It is used to initialize the instance variables of an object to the values passed to the constructor. It is automatically called when an object is created from a class. It is used to initialize the state of an object. It is called the parameterized constructor because it is called when an object is created with parameters.

### Default Constructor in Python
A default constructor is a constructor that does not take any parameters. It is used to initialize the instance variables of an object to their default values. It is automatically called when an object is created from a class. It is used to initialize the state of an object. It is called the default constructor because it is called when an object is created without any parameters.

```python title="default_constructor.py" showLineNumbers{1} {2-4}
class Student:
    def __init__(self):
        pass

student1 = Student()
```

In the above example, we have created a default constructor. It does not take any parameters. It is used to initialize the instance variables of an object to their default values. It is automatically called when an object is created from a class. It is used to initialize the state of an object. It is called the default constructor because it is called when an object is created without any parameters.

Another example of a default constructor:
```python title="default_constructor.py" showLineNumbers{1} {2-4}
class Student:
    def __init__(self):
        self.name = 'John'
        self.roll = 1

student1 = Student()
print('Name:', student1.name)
print('Roll:', student1.roll)
```

Output:
```cmd title="command" showLineNumbers{1} {2-4}
C:\Users\username>python default_constructor.py
Name: John
Roll: 1
```

In the above example, we have created two instance variables named `name` and `roll`. We have initialized the `name` and `roll` variables to the `name` and `roll` values of the `student1` object. We have printed the `name` and `roll` variables using the `student1` object. The output shows that the `name` and `roll` variables are unique to the object.

