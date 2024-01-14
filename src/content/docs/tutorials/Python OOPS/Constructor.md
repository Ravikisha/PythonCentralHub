---
title: Constructor & Destructor in Python
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

### Parameterized Constructor in Python
A parameterized constructor is a constructor that takes one or more parameters. It is used to initialize the instance variables of an object to the values passed to the constructor. It is automatically called when an object is created from a class. It is used to initialize the state of an object. It is called the parameterized constructor because it is called when an object is created with parameters.

```python title="parameterized_constructor.py" showLineNumbers{1} {2-5}
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
C:\Users\username>python parameterized_constructor.py
Name: John
Roll: 1
```

In the above example, we have created two instance variables named `name` and `roll`. We have initialized the `name` and `roll` variables to the `name` and `roll` parameters of the `__init__()` method. We have printed the `name` and `roll` variables using the `student1` object. The output shows that the `name` and `roll` variables are unique to the object.

Another example of a parameterized constructor:
```python title="parameterized_constructor.py" showLineNumbers{1} {2-6}
class Employee:
    def __init__(self, name, salary, department):
        self.name = name
        self.salary = salary
        self.department = department

employee1 = Employee('John', 10000, 'IT')
print('Name:', employee1.name)
print('Salary:', employee1.salary)
print('Department:', employee1.department)
```

Output:
```cmd title="command" showLineNumbers{1} {2-6}
C:\Users\username>python parameterized_constructor.py
Name: John
Salary: 10000
Department: IT
```

In the above example, we have created three instance variables named `name`, `salary`, and `department`. We have initialized the `name`, `salary`, and `department` variables to the `name`, `salary`, and `department` parameters of the `__init__()` method. We have printed the `name`, `salary`, and `department` variables using the `employee1` object. The output shows that the `name`, `salary`, and `department` variables are unique to the object.

### Constructor with Default Parameters in Python
A constructor with default parameters is a constructor that takes one or more parameters with default values. It is used to initialize the instance variables of an object to the values passed to the constructor. It is automatically called when an object is created from a class. It is used to initialize the state of an object. It is called the constructor with default parameters because it is called when an object is created with default parameters.

```python title="constructor_with_default_parameters.py" showLineNumbers{1} {2-5}
class Student:
    def __init__(self, name='John', roll=1):
        self.name = name
        self.roll = roll

student1 = Student()
print('Name:', student1.name)
print('Roll:', student1.roll)
```

Output:
```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\username>python constructor_with_default_parameters.py
Name: John
Roll: 1
```

In the above example, we have created two instance variables named `name` and `roll`. We have initialized the `name` and `roll` variables to the `name` and `roll` parameters of the `__init__()` method. We have printed the `name` and `roll` variables using the `student1` object. The output shows that the `name` and `roll` variables are unique to the object.

Another example of a constructor with default parameters:
```python title="constructor_with_default_parameters.py" showLineNumbers{1} {2-5}
class Employee:
    def __init__(self, name='John', salary=10000, department='IT'):
        self.name = name
        self.salary = salary
        self.department = department

employee1 = Employee()
print('Name:', employee1.name)
print('Salary:', employee1.salary)
print('Department:', employee1.department)
```

Output:
```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\username>python constructor_with_default_parameters.py
Name: John
Salary: 10000
Department: IT
```

In the above example, we have created three instance variables named `name`, `salary`, and `department`. We have initialized the `name`, `salary`, and `department` variables to the `name`, `salary`, and `department` parameters of the `__init__()` method. We have printed the `name`, `salary`, and `department` variables using the `employee1` object. The output shows that the `name`, `salary`, and `department` variables are unique to the object.

### Constructor with Default Parameters and Parameters in Python
A constructor with default parameters and parameters is a constructor that takes one or more parameters with default values and one or more parameters without default values. It is used to initialize the instance variables of an object to the values passed to the constructor. It is automatically called when an object is created from a class. It is used to initialize the state of an object. It is called the constructor with default parameters and parameters because it is called when an object is created with default parameters and parameters.

```python title="constructor_with_default_parameters_and_parameters.py" showLineNumbers{1} {2-6}
class Student:
    def __init__(self, name, roll, age=20):
        self.name = name
        self.roll = roll
        self.age = age

student1 = Student('John', 1)
print('Name:', student1.name)
print('Roll:', student1.roll)
print('Age:', student1.age)
```


Output:
```cmd title="command" showLineNumbers{1} {2-6}
C:\Users\username>python constructor_with_default_parameters_and_parameters.py
Name: John
Roll: 1
Age: 20
```

In the above example, we have created three instance variables named `name`, `roll`, and `age`. We have initialized the `name`, `roll`, and `age` variables to the `name`, `roll`, and `age` parameters of the `__init__()` method. We have printed the `name`, `roll`, and `age` variables using the `student1` object. The output shows that the `name`, `roll`, and `age` variables are unique to the object.

:::danger
If you are using a constructor with default parameters and parameters, then you need to pass the required parameters to the constructor except the parameters with default values.

```python title="constructor.py" showLineNumbers{1} {2-6}
class Student:
    def __init__(self, name, roll, age=20):
        self.name = name
        self.roll = roll
        self.age = age

student1 = Student('John')
print('Name:', student1.name)
print('Roll:', student1.roll)
print('Age:', student1.age)
```

Output:
```cmd title="command" showLineNumbers{1} {2-6}
C:\Users\username>python constructor.py
Traceback (most recent call last):
  File "constructor.py", line 7, in <module>
    student1 = Student('John')
TypeError: __init__() missing 1 required positional argument: 'roll'
```

In the above example, we have created three instance variables named `name`, `roll`, and `age`. We have initialized the `name`, `roll`, and `age` variables to the `name`, `roll`, and `age` parameters of the `__init__()` method. We have printed the `name`, `roll`, and `age` variables using the `student1` object. The output shows that the `name`, `roll`, and `age` variables are unique to the object.
:::

:::caution
If you are passing the required parameters to the constructor, then you need to pass the required parameters to the constructor except the parameters with default values in the same order. If you not pass the required parameters to the constructor in the same order, then you will get a bug about assigning the wrong values to the instance variables.

```python title="constructor.py" showLineNumbers{1} {2-6}
class Student:
    def __init__(self, name, roll, age=20):
        self.name = name
        self.roll = roll
        self.age = age

student1 = Student(1, 'John')
print('Name:', student1.name)
print('Roll:', student1.roll)
print('Age:', student1.age)
```

Output:
```cmd title="command" showLineNumbers{1} {2-6}
C:\Users\username>python constructor.py
Name: 1
Roll: John
Age: 20
```

In the above example, we have created three instance variables named `name`, `roll`, and `age`. We have initialized the `name`, `roll`, and `age` variables to the `name`, `roll`, and `age` parameters of the `__init__()` method. We have printed the `name`, `roll`, and `age` variables using the `student1` object. The output shows that the `name`, `roll`, and `age` variables are unique to the object.
:::

## Constructor with keyword arguments in Python
A constructor with keyword arguments is a constructor that takes one or more parameters with default values and one or more parameters without default values. It is used to initialize the instance variables of an object to the values passed to the constructor. It is automatically called when an object is created from a class. It is used to initialize the state of an object. It is called the constructor with keyword arguments because it is called when an object is created with keyword arguments.

```python title="constructor_keyword_arguments.py" showLineNumbers{1} {2-6}
class Student:
    def __init__(self, name, roll, age=20):
        self.name = name
        self.roll = roll
        self.age = age

student1 = Student(name='John', roll=1)
print('Name:', student1.name)
print('Roll:', student1.roll)
print('Age:', student1.age)
```

Output:
```cmd title="command" showLineNumbers{1} {2-6}
C:\Users\username>python constructor_keyword_arguments.py
Name: John
Roll: 1
Age: 20
```

In the above example, we have created three instance variables named `name`, `roll`, and `age`. We have initialized the `name`, `roll`, and `age` variables to the `name`, `roll`, and `age` parameters of the `__init__()` method. We have printed the `name`, `roll`, and `age` variables using the `student1` object. The output shows that the `name`, `roll`, and `age` variables are unique to the object.

## Constructor Overloading in Python
Constructor overloading is a technique in which a class can have more than one constructor. It is used to initialize the instance variables of an object to the values passed to the constructor. It is automatically called when an object is created from a class. It is used to initialize the state of an object. It is called the constructor overloading because it is called when an object is created with different parameters. You can create more than one constructor in a class. You can create a constructor with default parameters and parameters but constructor signature must be different.

```python title="constructor_overloading.py" showLineNumbers{1} {2-6}
class Student:
    def __init__(self):
        self.name = 'John'
        self.roll = 1
        print('Default Constructor')
    def __init__(self, name, roll):
        self.name = name
        self.roll = roll
        print('Constructor 1')
    def __init__(self, name, roll, age):
        self.name = name
        self.roll = roll
        self.age = age
        print('Constructor 2')
    def __init__(self, name, roll, age, department):
        self.name = name
        self.roll = roll
        self.age = age
        self.department = department
        print('Constructor 3')

student1 = Student()
student2 = Student('John', 1)
student3 = Student('John', 1, 20)
student4 = Student('John', 1, 20, 'IT')
```

Output:
```cmd title="command" showLineNumbers{1} {2-6}
C:\Users\username>python constructor_overloading.py
Default Constructor
Constructor 1
Constructor 2
Constructor 3
```

In the above example, we have created four constructors. We have initialized the `name`, `roll`, `age`, and `department` variables to the `name`, `roll`, `age`, and `department` parameters of the `__init__()` method. We have printed the `name`, `roll`, `age`, and `department` variables using the `student1`, `student2`, `student3`, and `student4` objects. The output shows that the `name`, `roll`, `age`, and `department` variables are unique to the object. In this example, we have created four constructors with different parameters. You can create more than one constructor in a class. You can create a constructor with default parameters and parameters but constructor signature must be different. 

## Constructor Chaining in Python
Constructor chaining is a technique in which a constructor calls another constructor of the same class. It is used to initialize the instance variables of an object to the values passed to the constructor.

```python title="constructor_chaining.py" showLineNumbers{1} {2-6}
class Student:
    def __init__(self, name, roll, age):
        self.name = name
        self.roll = roll
        self.age = age
    def __init__(self, name, roll, age, department):
        self(name, roll, age)
        self.department = department

student1 = Student('John', 1, 20, 'IT')
print('Name:', student1.name)
print('Roll:', student1.roll)
print('Age:', student1.age)
print('Department:', student1.department)
```

Output:
```cmd title="command" showLineNumbers{1} {2-6}
C:\Users\username>python constructor_chaining.py
Name: John
Roll: 1
Age: 20
Department: IT
```

In the above example, we have created two instance variables named `name`, `roll`, `age`, and `department`. We have initialized the `name`, `roll`, `age`, and `department` variables to the `name`, `roll`, `age`, and `department` parameters of the `__init__()` method. We have printed the `name`, `roll`, `age`, and `department` variables using the `student1` object. The output shows that the `name`, `roll`, `age`, and `department` variables are unique to the object. In this example, we have created two constructors. We have initialized the `name`, `roll`, and `age` variables to the `name`, `roll`, and `age` parameters of the `__init__()` method. We have initialized the `department` variable to the `department` parameter of the `__init__()` method. We have called the first constructor from the second constructor using the `self()` method. We have passed the required parameters to the first constructor. We have passed the required parameters to the second constructor. We have printed the `name`, `roll`, `age`, and `department` variables using the `student1` object. The output shows that the `name`, `roll`, `age`, and `department` variables are unique to the object.

## Built-In Instance Methods in Python
There are many built-in instance methods in Python. The following table lists some of the most commonly used built-in instance methods in Python.

|S.No.|Method|Description|
|-----|------|-----------|
|1|`getattr()`|Returns the value of the specified attribute of an object.|
|2|`setattr()`|Sets the value of the specified attribute of an object.|
|3|`delattr()`|Deletes the specified attribute of an object.|
|4|`hasattr()`|Returns `True` if the specified attribute of an object exists, otherwise returns `False`.|

### `getattr()` Method in Python
The `getattr()` method returns the value of the specified attribute of an object. It takes two parameters:
- `object`: The object whose attribute value you want to get.
- `name`: The name of the attribute whose value you want to get.

```python title="getattr.py" showLineNumbers{1} {7-8}
class Student:
    def __init__(self, name, roll):
        self.name = name
        self.roll = roll

student1 = Student('John', 1)
print('Name:', getattr(student1, 'name'))
print('Roll:', getattr(student1, 'roll'))
```

Output:
```cmd title="command" showLineNumbers{1} {2-8}
C:\Users\username>python getattr.py
Name: John
Roll: 1
```

In the above example, we have created two instance variables named `name` and `roll`. We have initialized the `name` and `roll` variables to the `name` and `roll` parameters of the `__init__()` method. We have printed the `name` and `roll` variables using the `getattr()` method. The output shows that the `name` and `roll` variables are unique to the object.

### `setattr()` Method in Python
The `setattr()` method sets the value of the specified attribute of an object. It takes three parameters:
- `object`: The object whose attribute value you want to set.
- `name`: The name of the attribute whose value you want to set.
- `value`: The value of the attribute you want to set.

```python title="setattr.py" showLineNumbers{1} {7-8}
class Student:
    def __init__(self, name, roll):
        self.name = name
        self.roll = roll

student1 = Student('John', 1)
setattr(student1, 'name', 'John Doe')
setattr(student1, 'roll', 2)
print('Name:', student1.name)
print('Roll:', student1.roll)
```

Output:
```cmd title="command" showLineNumbers{1} {2-8}
C:\Users\username>python setattr.py
Name: John Doe
Roll: 2
```

In the above example, we have created two instance variables named `name` and `roll`. We have initialized the `name` and `roll` variables to the `name` and `roll` parameters of the `__init__()` method. We have set the `name` and `roll` variables using the `setattr()` method. We have printed the `name` and `roll` variables using the `student1` object. The output shows that the `name` and `roll` variables are unique to the object.

### `delattr()` Method in Python
The `delattr()` method deletes the specified attribute of an object. It takes two parameters:
- `object`: The object whose attribute you want to delete.
- `name`: The name of the attribute you want to delete.

```python title="delattr.py" showLineNumbers{1} {7-8}
class Student:
    def __init__(self, name, roll):
        self.name = name
        self.roll = roll

student1 = Student('John', 1)
delattr(student1, 'name')
delattr(student1, 'roll')
print('Name:', getattr(student1, 'name'))
print('Roll:', getattr(student1, 'roll'))
```

Output:
```cmd title="command" showLineNumbers{1} {2-8}
C:\Users\username>python delattr.py
Traceback (most recent call last):
  File "delattr.py", line 9, in <module>
    print('Name:', getattr(student1, 'name'))
AttributeError: 'Student' object has no attribute 'name'
```

In the above example, we have created two instance variables named `name` and `roll`. We have initialized the `name` and `roll` variables to the `name` and `roll` parameters of the `__init__()` method. We have deleted the `name` and `roll` variables using the `delattr()` method. We have printed the `name` and `roll` variables using the `student1` object. The output shows that the `name` and `roll` variables are unique to the object.

### `hasattr()` Method in Python
The `hasattr()` method returns `True` if the specified attribute of an object exists, otherwise returns `False`. It takes two parameters:
- `object`: The object whose attribute you want to check.
- `name`: The name of the attribute you want to check.

```python title="hasattr.py" showLineNumbers{1} {7-10}
class Student:
    def __init__(self, name, roll):
        self.name = name
        self.roll = roll

student1 = Student('John', 1)
print('Name:', hasattr(student1, 'name'))
print('Roll:', hasattr(student1, 'roll'))
print('Age:', hasattr(student1, 'age'))
print('Department:', hasattr(student1, 'department'))
```

Output:
```cmd title="command" showLineNumbers{1} {2-8}
C:\Users\username>python hasattr.py
Name: True
Roll: True
Age: False
Department: False
```

In the above example, we have created two instance variables named `name` and `roll`. We have initialized the `name` and `roll` variables to the `name` and `roll` parameters of the `__init__()` method. We have checked the `name` and `roll` variables using the `hasattr()` method. We have printed the `name` and `roll` variables using the `student1` object. The output shows that the `name` and `roll` variables are unique to the object.

## Destructor in Python
In object-oriented programming, a destructor is a special method used for destroying instances of a class. In Python, the destructor method is named `__del__`, and it is automatically called when an object is destroyed. Destructors play a crucial role in cleaning up the resources used by an object, allowing for proper cleanup and disposal. Let's explore the key aspects of destructors in Python.

```python title="destructor.py" showLineNumbers{1} {6-7}
class Student:
    def __init__(self, name, roll):
        self.name = name
        self.roll = roll
    def __del__(self):
        print('Destructor called')

student1 = Student('John', 1)
print('Name:', student1.name)
print('Roll:', student1.roll)
```

Output:
```cmd title="command" showLineNumbers{1} {2-7}
C:\Users\username>python destructor.py
Name: John
Roll: 1
Destructor called
```

In the above example, we have created two instance variables named `name` and `roll`. We have initialized the `name` and `roll` variables to the `name` and `roll` parameters of the `__init__()` method. We have printed the `name` and `roll` variables using the `student1` object. We have created a destructor named `__del__`. We have printed the `Destructor called` message using the `__del__` method. The output shows that the `name` and `roll` variables are unique to the object. The output also shows that the `Destructor called` message is printed when the object is destroyed.

### Usage of Destructors in Python
- Destructors are used to destroy instances of a class.
- Destructors are used to clean up the resources used by an object.
- Destructors are used to perform any required cleanup before an object is destroyed.


## Conclusion
In this tutorial, we have learned about constructors in Python. We have learned how to create a constructor in Python. We have learned what is the use of a constructor in Python. We have learned how to use a constructor in Python. We have learned how to create a constructor with parameters in Python. We have learned how to create a constructor without parameters in Python. We have learned how to create a default constructor in Python. We have learned how to create a parameterized constructor in Python. We have learned how to create a constructor with default parameters in Python. We have learned how to create a constructor with default parameters and parameters in Python. We have learned how to create a constructor with keyword arguments in Python. We have learned how to create constructor overloading in Python. We have learned how to create constructor chaining in Python. We have learned about built-in instance methods in Python. For more information on constructors in Python, see the [official documentation](https://docs.python.org/3/tutorial/classes.html#class-initialization). For more tutorials like this, check out Python Central Hub.