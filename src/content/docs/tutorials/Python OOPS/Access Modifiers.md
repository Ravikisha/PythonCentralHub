---
title: Access Modifiers in Python
description: Learn about access modifiers in Python. How to use them and what are the different types of access modifiers in Python. In this tutorial, we will learn about access modifiers in Python like public, private, and protected. We will also learn how to use them in Python. We will also learn about the difference between public, private, and protected access modifiers in Python. We will also learn about the access table in Python. Finally, we will learn about the Python property object. Now you can use access modifiers in Python to control the visibility and accessibility of class members. You can also use the Python property object to set and get the value of a property.
sidebar: 
    order: 84
---

## Access Modifiers in Python: Public, Private, and Protected
Access modifiers in Python define the visibility and accessibility of class members (attributes and methods). While Python doesn't have explicit keywords like public, private, or protected as seen in some other languages, it achieves access control through naming conventions and the use of underscores. Let's explore how access modifiers work in Python.

## Public Access Modifier
In Python, all class members are public by default. We can access them from anywhere within the program. Let's see an example of a public access modifier in Python.

```python title="public.py" showLineNumbers{1} {2-4}
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

```python title="private.py" showLineNumbers{1} {2-4}
class Student:
    def __init__(self, name, roll):
        self.__name = name
        self.__roll = roll

student1 = Student('John', 1)
print('Name:', student1.__name)
print('Roll:', student1.__roll)
```

Output:
```cmd title="command" showLineNumbers{1} {2-10}
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

```python title="protected.py" showLineNumbers{1} {2-4}
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

## Example: Access Modifiers in Python
Let's see an example of access modifiers in Python.

```python title="access_modifiers.py" showLineNumbers{1} {2-5}
class Student:
    def __init__(self, name, roll):
        self.name = name
        self._roll = roll
        self.__age = 20

    def display(self):
        print('Name:', self.name)
        print('Roll:', self._roll)
        print('Age:', self.__age)

student1 = Student('John', 1)
student1.display()
print('Name:', student1.name)
print('Roll:', student1._roll)
print('Age:', student1.__age)
```

Output:
```cmd title="command" showLineNumbers{1} {2-10}
C:\Users\username>python access_modifiers.py
Name: John
Roll: 1
Age: 20
Name: John
Roll: 1
Traceback (most recent call last):
  File "access_modifiers.py", line 16, in <module>
    print('Age:', student1.__age)
AttributeError: 'Student' object has no attribute '__age'
```

In the above example, we have created three instance variables named `name`, `_roll`, and `__age`. We have initialized the `name`, `_roll`, and `__age` variables to the `name`, `roll`, and `20` parameters of the `__init__()` method. We have printed the `name`, `_roll`, and `__age` variables using the `student1` object. The output shows that we can access public and protected members from outside the class but within the same module. However, we can't access private members from outside the class.

:::tip
We can access public and protected members from outside the class but within the same module. However, we can't access private members from outside the class.
:::

## Name Mangling
In Python, private members are not accessible from outside the class. However, we can access private members from outside the class using the name mangling technique. Let's see an example of name mangling in Python.

```python title="syntax.py" showLineNumbers{1} {2-4}
object._className__variableName
```

In the above syntax, we have used the name mangling technique to access the private variable named `variableName` of the class named `className` using the object named `object`. Let's see an example of name mangling in Python.

```python title="name_mangling.py" showLineNumbers{1} {2-5, 10}
class Student:
    def __init__(self, name, roll):
        self.name = name
        self._roll = roll
        self.__age = 20

student1 = Student('John', 1)
print('Name:', student1.name)
print('Roll:', student1._roll)
print('Age:', student1._Student__age)
```

Output:
```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\username>python name_mangling.py
Name: John
Roll: 1
Age: 20
```

In the above example, we have created three instance variables named `name`, `_roll`, and `__age`. We have initialized the `name`, `_roll`, and `__age` variables to the `name`, `roll`, and `20` parameters of the `__init__()` method. We have printed the `name`, `_roll`, and `__age` variables using the `student1` object. The output shows that we can access public and protected members from outside the class but within the same module. However, we can't access private members from outside the class. We have used the name mangling technique to access the private variable named `__age` of the class named `Student` using the object named `student1`.

:::tip
We can access private members from outside the class using the name mangling technique.
:::

## Python Property Object
In Python, we can use the `property()` function to create a property object. We can use the property object to set and get the value of a property. Let's see an example of a property object in Python.

```python title="property_syntax.py" showLineNumbers{1} {2-4}
property(fget=None, fset=None, fdel=None, doc=None)
```

In the above syntax, we have used the `property()` function to create a property object. We can pass the getter, setter, deleter, and docstring functions as arguments to the `property()` function. Let's see an example of a property object in Python.

```python title="property_object.py" showLineNumbers{1} {2-13}
class Student:
    def __init__(self, name, roll):
        self.name = name
        self._roll = roll
        self.__age = 20

    def get_age(self):
        return self.__age

    def set_age(self, age):
        self.__age = age

    age = property(get_age, set_age)

student1 = Student('John', 1)
print('Name:', student1.name)
print('Roll:', student1._roll)
print('Age:', student1.age)
student1.age = 21
print('Age:', student1.age)
```

Output:
```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\username>python property_object.py
Name: John
Roll: 1
Age: 20
Age: 21
```

In the above example, we have created three instance variables named `name`, `_roll`, and `__age`. We have initialized the `name`, `_roll`, and `__age` variables to the `name`, `roll`, and `20` parameters of the `__init__()` method. We have created two methods named `get_age()` and `set_age()` to get and set the value of the `__age` variable. We have created a property object named `age` using the `property()` function. We have passed the `get_age()` and `set_age()` methods as arguments to the `property()` function. We have printed the `name`, `_roll`, and `age` variables using the `student1` object. We have set the value of the `age` variable using the `student1` object. The output shows that we can use the property object to set and get the value of a property.

:::tip
We can use the `property()` function to create a property object. We can use the property object to set and get the value of a property. We can pass the getter, setter, deleter, and docstring functions as arguments to the `property()` function. We can also use the `@property` decorator to create a property object.

```python title="property_decorator.py" showLineNumbers{1} {2-5}
@property
def age(self):
    return self.__age
```

Example:
```python title="property_object.py" showLineNumbers{1} {2-13}
class Student:
    def __init__(self, name, roll):
        self.name = name
        self._roll = roll
        self.__age = 20

    @property
    def age(self):
        return self.__age

    @age.setter
    def age(self, age):
        self.__age = age

student1 = Student('John', 1)
print('Name:', student1.name)
print('Roll:', student1._roll)
print('Age:', student1.age)
student1.age = 21
print('Age:', student1.age)
```

Output:
```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\username>python property_object.py
Name: John
Roll: 1
Age: 20
Age: 21
```

In the above example, we have created three instance variables named `name`, `_roll`, and `__age`. We have initialized the `name`, `_roll`, and `__age` variables to the `name`, `roll`, and `20` parameters of the `__init__()` method. We have created two methods named `get_age()` and `set_age()` to get and set the value of the `__age` variable. We have created a property object named `age` using the `property()` function. We have passed the `get_age()` and `set_age()` methods as arguments to the `property()` function. We have printed the `name`, `_roll`, and `age` variables using the `student1` object. We have set the value of the `age` variable using the `student1` object. The output shows that we can use the property object to set and get the value of a property.

:::

## Conclusion
In this tutorial, we have learned about access modifiers in Python like public, private, and protected. We have also learned how to use them in Python. We have also learned about the difference between public, private, and protected access modifiers in Python. We have also learned about the access table in Python. Finally, we have learned about the Python property object. Now you can use access modifiers in Python to control the visibility and accessibility of class members. You can also use the Python property object to set and get the value of a property. In the next tutorial, we will learn about inheritance in Python. We will also learn about different types of inheritance in Python. For more information on access modifiers in Python, you can refer to the [official documentation](https://docs.python.org/3/tutorial/classes.html#private-variables). FOr more tutorials on Python, visit Python Central Hub.