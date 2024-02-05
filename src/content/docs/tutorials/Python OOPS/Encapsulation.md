---
title: Encapsulation in Python
description: Learn about encapsulation in Python. Encapsulation is the process of wrapping up data and methods into a single unit. It helps in data hiding and prevents direct access to the data. In Python, encapsulation can be achieved using private variables and methods.
sidebar: 
    order: 91
---

<!-- 
```python title="dynamic_binding.py" showLineNumbers{1} {1-3, 5-7, 9-11}
class Animal:
    def speak(self):
        print("Generic animal sound")

class Dog(Animal):
    def speak(self):
        print("Woof!")

class Cat(Animal):
    def speak(self):
        print("Meow!")

objects = [Animal(), Dog(), Cat()]
 for obj in objects:
      obj.speak()
```

Output:
```cmd title="command" showLineNumbers{1} {2-4}
C:\Users\user\Desktop>python dynamic_binding.py
Generic animal sound
Woof!
Meow!
```

In this example, we have a base class `Animal` with a method `speak`. We have two subclasses `Dog` and `Cat` that override the `speak` method inherited from the `Animal` class. The `Dog` and `Cat` classes provide specialized implementations of the `speak` method that are specific to each animal. The `Dog` class overrides the `speak` method to print "Woof!", while the `Cat` class overrides the `speak` method to print "Meow!". We then create a list of objects of type `Animal`, `Dog`, and `Cat` and iterate over the list, calling the `speak` method on each object. Since Python is dynamically-bound, the method call is resolved at runtime, and the overridden methods in the respective subclasses are invoked, printing "Woof!" and "Meow!". -->

# Encapsulation in Python OOP: Safeguarding the Essence of Objects

Encapsulation is a key pillar of object-oriented programming (OOP) that involves bundling data (attributes) and the methods (functions) that operate on that data into a single unit known as a class. This concept emphasizes the idea of encapsulating the implementation details within a class, allowing controlled access to the internal state of an object. In Python, encapsulation plays a crucial role in creating robust and secure code. Let's explore the principles of encapsulation, its implementation in Python, and the benefits it brings to the world of OOP.

## Principles of Encapsulation:

### 1. **Data Hiding:**
   - Encapsulation hides the internal details of an object's implementation from the outside world. It restricts direct access to the attributes of a class, promoting a controlled and secure interaction.

### 2. **Access Control:**
   - Encapsulation provides mechanisms to control the level of access to the attributes and methods of a class. This helps prevent unintended modifications or misuse of the internal state.

### 3. **Modularity:**
   - By bundling data and methods into a class, encapsulation promotes modularity. Changes to the internal implementation details do not affect the external code that interacts with the class.

### 4. **Information Hiding:**
   - Encapsulation enables information hiding, allowing developers to expose only the necessary details of an object's behavior while concealing the rest. This simplifies the usage of the class.

## Access Modifiers in Python:
In Python, access control is not enforced through access modifiers such as `public`, `private`, or `protected` as in some other programming languages. Instead, Python uses naming conventions and language features to achieve encapsulation. The following are the common naming conventions used to indicate the level of access to attributes and methods in Python:

- **Public Attributes and Methods**
- **Private Attributes and Methods**
- **Protected Attributes and Methods**

### Access Modifier Table:

| Access Modifier | Naming Convention | Description | Example |
| --- | --- | --- | --- |
| Public | No leading underscore | Accessible from outside the class | `name` |
| Private | Single leading underscore | Intended for internal use within the class | `_name` |
| Protected | Single leading underscore | Conventional indication of protected attribute | `_name` |

In Python, the use of access modifiers is based on conventions rather than strict enforcement by the language. The single leading underscore (`_`) is used to indicate that an attribute or method is intended for internal use within the class. This convention serves as a signal to other developers that the attribute or method is not part of the public interface of the class. It is important to note that direct access to private attributes and methods is still possible in Python, as the language does not enforce strict access control. However, the use of naming conventions and encapsulation principles helps promote secure and maintainable code.

### Access Modifiers Access Levels:

|Access Modifier| Class | Subclass | Module | Anywhere |
|---|---|---|---|---|
| Public | ✅ | ✅ | ✅ | ✅ |
| Private | ✅ | ❌ | ❌ | ❌ |
| Protected | ✅ | ✅ | ❌ | ❌ |


### Public Attributes and Methods:
Public attributes and methods are accessible from outside the class. They form the public interface of the class, allowing external code to interact with the object. In Python, public attributes and methods do not have a leading underscore in their names. They are intended to be part of the public interface of the class and can be accessed from anywhere.

#### Syntax:
```python title="Syntax" showLineNumbers{1} {1-4, 6-7}
class ClassName:
    def __init__(self, attribute1, attribute2):
        self.attribute1 = attribute1      # Public attribute
        self.attribute2 = attribute2      # Public attribute

    def public_method(self):
        pass
```

In the above syntax:
- The `attribute1` and `attribute2` are public attributes of the class, as they do
- The `public_method` is a public method that forms part of the public interface of the class.
- Public attributes and methods are accessible from outside the class, allowing external code to interact with the object.
- Public attributes and methods do not have a leading underscore in their names.
- Public attributes and methods are intended to be part of the public interface of the class and can be accessed from anywhere.
- Public attributes and methods are used to expose the essential details of an object's behavior to external code.
- Public attributes and methods can be used to modify the internal state of the object in a controlled manner, ensuring data integrity.

#### Example:
```python title="encapsulation.py" showLineNumbers{1} {1-4, 6-7, 9-10}
class Student:
    def __init__(self, name, age):
        self.name = name      # Public attribute
        self.age = age        # Public attribute

    def get_name(self):
        return self.name

    def get_age(self):
        return self.age

student = Student("Alice", 22)
print(student.name)    # Direct access to a public attribute
print(student.get_age())    # Accessing a public attribute through a public method
```

Output:
```cmd title="command" showLineNumbers{1} {2-6}
C:\Users\user\Desktop>python encapsulation.py
Alice
22
```

In this example, the `name` and `age` attributes of the `Student` class are public attributes, as they do not have a leading underscore in their names. The `get_name` and `get_age` methods are public methods that form part of the public interface of the class. These methods provide controlled access to the public attributes, allowing external code to interact with the encapsulated data in a controlled manner. The public attributes and methods are accessible from outside the class, enabling external code to access the essential details of the object's behavior.

### Private Attributes and Methods:
Private attributes and methods are intended for internal use within the class. They are not directly accessible from outside the class, promoting data hiding and information hiding. In Python, private attributes and methods are indicated by a single leading underscore (`_`) in their names. This convention signals that the attributes and methods are intended for internal use within the class and should not be accessed directly from outside the class.

#### Syntax:
```python title="Syntax" showLineNumbers{1} {1-4, 6-7}
class ClassName:
    def __init__(self, attribute1, attribute2):
        self.__attribute1 = attribute1      # Private attribute
        self.__attribute2 = attribute2      # Private attribute

    def __private_method(self):
        pass
```

In the above syntax:
- The `__attribute1` and `__attribute2` are private attributes of the class, as they have a double leading underscore (`__`) in their names.
- The `__private_method` is a private method that is intended for internal use within the class.
- Private attributes and methods are not directly accessible from outside the class, promoting data hiding and information hiding.
- Private attributes and methods are indicated by a double leading underscore (`__`) in their names, signaling that they are intended for internal use within the class.
- Private attributes and methods are used to encapsulate the internal state and behavior of the object, preventing unauthorized access and modifications.
- Private attributes and methods can include additional logic for processing the encapsulated data, ensuring data integrity and security.

#### Example:
```python title="encapsulation.py" showLineNumbers{1} {1-4, 6-7}
class Employee:
    def __init__(self, name, salary):
        self.__name = name      # Private attribute
        self.__salary = salary  # Private attribute

    def __calculate_bonus(self):
        pass

employee = Employee("Bob", 50000)
print(employee.__name)    # Direct access to a private attribute
```

Output:
```cmd title="command" showLineNumbers{1} {2-6}
C:\Users\user\Desktop>python encapsulation.py
Traceback (most recent call last):
  File "encapsulation.py", line 7, in <module>
    print(employee.__name)    # Direct access to a private attribute
AttributeError: 'Employee' object has no attribute '__name'
```

In this example, the `name` and `salary` attributes of the `Employee` class are private attributes, as they have a double leading underscore (`__`) in their names. The `__calculate_bonus` method is a private method that is intended for internal use within the class. The private attributes and methods are not directly accessible from outside the class, preventing unauthorized access and modifications. Attempting to access the private attributes directly from outside the class results in an `AttributeError`, indicating that the attributes are not directly accessible.

### Protected Attributes and Methods:
Protected attributes and methods are indicated by a single leading underscore (`_`) in their names. This convention is a conventional indication of a protected attribute or method, although it does not enforce strict access control. Protected attributes and methods are intended for internal use within the class and its subclasses, promoting a limited level of access to the encapsulated data.

#### Syntax:
```python title="Syntax" showLineNumbers{1} {1-4, 6-7}
class ClassName:
    def __init__(self, attribute1, attribute2):
        self._attribute1 = attribute1      # Protected attribute
        self._attribute2 = attribute2      # Protected attribute

    def _protected_method(self):
        pass
```

In the above syntax:
- The `_attribute1` and `_attribute2` are protected attributes of the class, as they have a single leading underscore (`_`) in their names.
- The `_protected_method` is a protected method that is intended for internal use within the class and its subclasses.
- Protected attributes and methods are not directly accessible from outside the class, promoting a limited level of access to the encapsulated data.
- Protected attributes and methods are indicated by a single leading underscore (`_`) in their names, serving as a conventional indication of a protected attribute or method.
- Protected attributes and methods are intended for internal use within the class and its subclasses, promoting a limited level of access to the encapsulated data.

#### Example:
```python title="encapsulation.py" showLineNumbers{1} {1-4, 6-7}
class Person:
    def __init__(self, name, age):
        self._name = name      # Protected attribute
        self._age = age        # Protected attribute

    def _display_info(self):
        print(f"Name: {self._name}, Age: {self._age}")

person = Person("Alice", 22)
print(person._name)    # Direct access to a protected attribute
print(person._display_info())    # Accessing a protected method through a public method
```

Output:
```cmd title="command" showLineNumbers{1} {2-6}
C:\Users\user\Desktop>python encapsulation.py
Alice
Name: Alice, Age: 22
```

In this example, the `name` and `age` attributes of the `Person` class are protected attributes, as they have a single leading underscore (`_`) in their names. The `_display_info` method is a protected method that is intended for internal use within the class and its subclasses. The protected attributes and methods are not directly accessible from outside the class, promoting a limited level of access to the encapsulated data. Attempting to access the protected attributes directly from outside the class is possible, but it is discouraged, as it bypasses the principles of encapsulation.

## Implementation of Encapsulation in Python:

### 1. **Private Attributes:**
   - In Python, encapsulation is often achieved by marking attributes as private using a single leading underscore (`_`). This convention indicates that the attribute is intended for internal use within the class.

#### Syntax:
```python title="Syntax" showLineNumbers{1} {1-4}
class ClassName:
    def __init__(self, attribute1, attribute2):
        self.__attribute1 = attribute1      # Private attribute
        self.__attribute2 = attribute2      # Private attribute
```

In the above syntax:
- The `__init__` method is used to initialize the private attributes of the class.
- The private attributes are accessed using the `self` keyword within the class.
- The single leading underscore (`_`) indicates that the attributes are intended for internal use within the class.
- The private attributes are not directly accessible from outside the class.

#### Example:

```python title="encapsulation.py" showLineNumbers{1} {1-4}
class Student:
    def __init__(self, name, age):
        self.__name = name      # Private attribute
        self.__age = age        # Private attribute

student = Student("Alice", 22)
print(student.__name)    # Direct access to a private attribute
```

Output:
```cmd title="command" showLineNumbers{1} {2-6}
C:\Users\user\Desktop>python encapsulation.py
Traceback (most recent call last):
  File "encapsulation.py", line 5, in <module>
    print(student.__name)    # Direct access to a private attribute
AttributeError: 'Student' object has no attribute '__name'
```

In this example, the `name` and `age` attributes of the `Student` class are marked as private by prefixing them with a double leading underscore (`__`). Attempting to access the private attributes directly from outside the class results in an `AttributeError`, indicating that the attributes are not directly accessible. This demonstrates the principle of data hiding and information hiding, as the internal state of the object is not directly exposed.

Another Example:
```python title="encapsulation.py" showLineNumbers{1} {1-4, 6-7}
class Employee:
    def __init__(self, name, salary):
        self.__name = name      # Private attribute
        self.__salary = salary  # Private attribute

        def display_info(self):
            print(f"Name: {self.__name}, Salary: {self.__salary}")

employee = Employee("Bob", 50000)
print(employee.display_info())    # Accessing a private method through a public method
```

Output:
```cmd title="command" showLineNumbers{1} {2-6}
C:\Users\user\Desktop>python encapsulation.py
Name: Bob, Salary: 50000
```

In this example, the `name` and `salary` attributes of the `Employee` class are marked as private by prefixing them with a double leading underscore (`__`). The `display_info` method is a private method that is intended for internal use within the class. The private attributes and methods are not directly accessible from outside the class, promoting data hiding and information hiding. The private method is accessed through a public method, demonstrating controlled access to the encapsulated data.

### 2. **Public Methods:**
   - Public methods, also known as accessor or getter methods, provide controlled access to private attributes. These methods allow external code to interact with the encapsulated data in a controlled manner.
  
#### Syntax:
```python title="Syntax" showLineNumbers{1} {1-6}
class ClassName:
    def __init__(self, attribute1, attribute2):
        self.__attribute1 = attribute1      # Private attribute
        self.__attribute2 = attribute2      # Private attribute

    def get_attribute1(self):
        return self._attribute1

    def get_attribute2(self):
        return self._attribute2

object = ClassName(value1, value2)
print(object.get_attribute1())    # Accessing a private attribute through a public method
```

In this syntax:
- The `get_attribute1` and `get_attribute2` methods are public methods that provide controlled access to the private attributes of the class.
- These methods return the values of the private attributes, allowing external code to access the encapsulated data in a controlled manner.
- The private attributes are accessed through the public methods, ensuring that the internal state of the object is not directly exposed.
- The public methods provide a well-defined interface for interacting with the class, promoting modularity and information hiding.
- The public methods can also include additional logic for validating or processing the encapsulated data.
- The public methods can be used to modify the private attributes in a controlled manner, ensuring data integrity.

#### Example:

```python
class Student:
    def __init__(self, name, age):
        self.__name = name      # Private attribute
        self.__age = age        # Private attribute

    def get_name(self):
        return self.__name

    def get_age(self):
        return self.__age

student = Student("Alice", 22)
print(student.get_name())    # Accessing the name attribute through a public method
```

Output:
```cmd title="command" showLineNumbers{1} {2-6}
C:\Users\user\Desktop>python encapsulation.py
Alice
```

In this example, the `name` and `age` attributes of the `Student` class are marked as private by prefixing them with a double leading underscore (`__`). The `get_name` and `get_age` methods are public methods that provide controlled access to the private attributes. These methods return the values of the private attributes, allowing external code to access the encapsulated data in a controlled manner. The private attributes are accessed through the public methods, ensuring that the internal state of the object is not directly exposed. This demonstrates the principle of information hiding, as the essential details of the object's behavior are exposed through well-defined interfaces.

### 3. **Encapsulation Benefits:**
   - The encapsulated attributes are not directly accessible from outside the class, preventing unauthorized modifications and ensuring data integrity.

```python title="encapsulation.py" showLineNumbers{1} {1-2}
student = Student("Alice", 22)
print(student.get_name())   # Accessing the name attribute through a public method
```

### 4. **Setter Methods:**
   - To allow controlled modification of private attributes, setter methods can be implemented. These methods validate and set new values for the encapsulated data.

```python title="encapsulation.py" showLineNumbers{1} {1-4, 6-10, 12-16}
class Student:
    def __init__(self, name, age):
        self._name = name      # Private attribute
        self._age = age        # Private attribute

    def set_name(self, new_name):
        if isinstance(new_name, str):
            self._name = new_name
        else:
            raise ValueError("Name must be a string.")

    def set_age(self, new_age):
        if isinstance(new_age, int) and new_age > 0:
            self._age = new_age
        else:
            raise ValueError("Age must be a positive integer.")

student = Student("Alice", 22)
student.set_name("Bob")    # Using a setter method to modify the name attribute
student.set_age(25)    # Using a setter method to modify the age attribute
```

In this example, the `name` and `age` attributes of the `Student` class are marked as private by prefixing them with a single leading underscore (`_`). The `set_name` and `set_age` methods are setter methods that provide controlled modification of the private attributes. These methods validate the new values and set them for the encapsulated data, ensuring data integrity and security. The setter methods allow controlled modification of the private attributes, promoting data integrity and information hiding.


```python title="encapsulation.py" showLineNumbers{1} {1-2}
student = Student("Bob", 25)
student.set_age(30)    # Using a setter method to modify the age attribute
```

## Advantages of Encapsulation:

### 1. **Security:**
   - Encapsulation provides a layer of security by restricting direct access to the internal state of an object. This helps prevent unintended modifications and ensures data integrity.

### 2. **Modifiability:**
   - Changes to the internal implementation of a class do not affect the external code that interacts with it. This promotes modifiability and maintains backward compatibility.

### 3. **Readability:**
   - Encapsulation enhances code readability by exposing only the essential details of an object's behavior through well-defined interfaces (public methods).

### 4. **Code Maintenance:**
   - The modularity introduced by encapsulation simplifies code maintenance. Developers can modify the internal details of a class without affecting the rest of the codebase.

## Best Practices for Encapsulation in Python:

### 1. **Consistent Naming Conventions:**
   - Follow consistent naming conventions for private attributes and methods. Use a single leading underscore (`_`) to indicate that an attribute or method is intended for internal use.

### 2. **Documentation:**
   - Provide clear documentation for public methods, describing their intended use and expected behavior. This helps users of the class understand how to interact with it.

### 3. **Immutable Objects:**
   - Consider making encapsulated data immutable, especially if it represents properties that should not change. Immutability contributes to the reliability of the encapsulated data.

### 4. **Encapsulation with Properties:**
   - Python supports the `property` decorator, allowing the creation of getter and setter methods in a more concise way. This can be useful for encapsulating attributes with additional logic.

## Conclusion:

Encapsulation in Python OOP encapsulates the essence of objects by bundling data and methods into a cohesive unit, shielding internal details from external code. Through the use of private

 attributes, public methods, and controlled access, encapsulation enhances security, modifiability, and code readability. Embrace the principles of encapsulation to create robust, maintainable, and secure Python code that stands the test of time in the dynamic landscape of software development.