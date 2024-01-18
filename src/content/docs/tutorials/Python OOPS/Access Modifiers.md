---
title: Access Modifiers in Python
description: Learn about access modifiers in Python. How to use them and what are the different types of access modifiers in Python. In this tutorial, we will learn about access modifiers in Python like public, private, and protected. We will also learn how to use them in Python.
sidebar: 
    order: 84
---

## Access Modifiers in Python: Public, Private, and Protected
Access modifiers in Python define the visibility and accessibility of class members (attributes and methods). While Python doesn't have explicit keywords like public, private, or protected as seen in some other languages, it achieves access control through naming conventions and the use of underscores. Let's explore how access modifiers work in Python.

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


## Public Access Modifier
In Python, all class members are public by default. We can access them from anywhere within the program. Let's see an example of a public access modifier in Python.

```python title="public.py" showLineNumbers{1} {2-5}
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
C:\Users\username>python public.py
Name: John
Roll: 1
```

In the above example, we have created two instance variables named `name` and `roll`. We have initialized the `name` and `roll` variables to the `name` and `roll` parameters of the `__init__()` method. We have printed the `name` and `roll` variables using the `student1` object. The output shows that the `name` and `roll` variables are unique to the object.

:::tip
All class members are public by default in Python. We can access them from anywhere within the program. You don't need to specify the public access modifier explicitly.
:::

## Private Access Modifier
In Python, we can use double underscores (`__`) to make a class member private. We can't access private members from outside the class. Let's see an example of a private access modifier in Python.

```python title="private.py" showLineNumbers{1} {2-5}
class Student:
    def __init__(self, name, roll):
        self.__name = name
        self.__roll = roll

student1 = Student('John', 1)
print('Name:', student1.__name)
print('Roll:', student1.__roll)
```

Output:
```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\username>python private.py
Traceback (most recent call last):
  File "private.py", line 6, in <module>
    print('Name:', student1.__name)
AttributeError: 'Student' object has no attribute '__name'
```

In the above example, we have created two private instance variables named `__name` and `__roll`. We have initialized the `__name` and `__roll` variables to the `name` and `roll` parameters of the `__init__()` method. We have tried to print the `__name` and `__roll` variables using the `student1` object. The output shows that we can't access private members from outside the class.

:::tip
We can use double underscores (`__`) to make a class member private. We can't access private members from outside the class.
:::

## Protected Access Modifier
In Python, we can use a single underscore (`_`) to make a class member protected. We can access protected members from outside the class but within the same module. Let's see an example of a protected access modifier in Python.

```python title="protected.py" showLineNumbers{1} {2-5}
class Student:
    def __init__(self, name, roll):
        self._name = name
        self._roll = roll

student1 = Student('John', 1)
print('Name:', student1._name)
print('Roll:', student1._roll)
```

Output:
```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\username>python protected.py
Name: John
Roll: 1
```

In the above example, we have created two protected instance variables named `_name` and `_roll`. We have initialized the `_name` and `_roll` variables to the `name` and `roll` parameters of the `__init__()` method. We have printed the `_name` and `_roll` variables using the `student1` object. The output shows that we can access protected members from outside the class but within the same module.

:::tip
We can use a single underscore (`_`) to make a class member protected. We can access protected members from outside the class but within the same module.
:::

:::caution
Protected members can be accessed from outside the class but within the same module. However, it's not recommended to access protected members from outside the class. It's better to access protected members from inside the class.
:::

## Difference Between Public, Private, and Protected Access Modifiers
The following table summarizes the difference between public, private, and protected access modifiers in Python.

| Access Modifier | Description | Example |
| --- | --- | --- |
| Public | Public members can be accessed from anywhere within the program. | `self.name = name` |
| Private | Private members can't be accessed from outside the class. | `self.__name = name` |
| Protected | Protected members can be accessed from outside the class but within the same module. | `self._name = name` |

## Access Table
The following table summarizes the access of class members from different places.

| Class Member | Inside Class | Outside Class | Same Module | Different Module |
| --- | --- | --- | --- | --- |
| Public | ✅ | ✅ | ✅ | ✅ |
| Private | ✅ | ❌ | ❌ | ❌ |
| Protected | ✅ | ✅ | ✅ | ❌ |

