---
title: Abstract in Python
description: Learn about abstraction in Python. Abstraction is the process of hiding the implementation details and showing only the functionality to the user. It helps in reducing the complexity of the system. In Python, abstraction can be achieved using abstract classes and interfaces.
sidebar: 
    order: 90
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

# Abstraction in OOPs with Python: Unveiling the Essence of Simplicity

Abstraction is a fundamental concept in object-oriented programming (OOP) that allows developers to focus on essential aspects of an object while hiding the unnecessary details. In Python, abstraction provides a powerful mechanism for creating clean, modular, and easily maintainable code. Let's delve into the world of abstraction, exploring its definition, implementation, and the impact it has on the design and structure of Python programs.

## Understanding Abstraction:

### 1. **Abstraction Defined:**
   - Abstraction involves representing essential features of an object while hiding the complex and intricate details. It simplifies the interaction with objects by providing a high-level view.

### 2. **Real-world Analogy:**
   - Think of abstraction as driving a car. As a driver, you focus on essential controls like the steering wheel, pedals, and gears, abstracting away the intricate details of the engine's internal workings.

### 3. **Key Components:**
   - Abstraction in OOPs typically involves two key components:
     - **Abstract Classes:** Classes that cannot be instantiated on their own and may contain abstract methods (methods without a defined implementation).
     - **Abstract Methods:** Methods declared in an abstract class but have no implementation. They are meant to be implemented by the subclasses.

## Implementing Abstraction in Python:

### 1. **Abstract Classes in Python:**
   - Python provides abstraction through abstract base classes (ABCs) using the `abc` module. To create an abstract class, inherit from the `ABC` class, and use the `@abstractmethod` decorator for abstract methods.

```python title="abstraction.py" showLineNumbers{1} {1, 3-6}
from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def area(self):
        pass

shape = Shape()  # Raises TypeError: Can't instantiate abstract class Shape with abstract methods area
```

Output:
```cmd title="command" showLineNumbers{1} {2-6}
C:\Users\user\Desktop>python abstraction.py
Traceback (most recent call last):
  File "abstraction.py", line 6, in <module>
    shape = Shape()  # Raises TypeError: Can't instantiate abstract class Shape with abstract methods area
TypeError: Can't instantiate abstract class Shape with abstract methods area
```

### 2. **Concrete Classes:**
   - Concrete classes are derived from abstract classes and provide concrete implementations for the abstract methods.

```python
class Circle(Shape):
    def __init__(self, radius):
        self.radius = radius

    def area(self):
        return 3.14 * self.radius * self.radius

class Rectangle(Shape):
    def __init__(self, length, width):
        self.length = length
        self.width = width

    def area(self):
       return self.length * self.width

circle = Circle(5)
rectangle = Rectangle(4, 6)


### 3. **Usage:**
   - Users can interact with abstract classes and their methods without needing to know the specific implementations in the concrete classes.

   ```python
   def print_area(shape):
       print(f"Area: {shape.area()}")

   circle = Circle(5)
   rectangle = Rectangle(4, 6)

   print_area(circle)      # Outputs: Area: 78.5
   print_area(rectangle)   # Outputs: Area: 24
    ```

## Advantages of Abstraction:

### 1. **Encapsulation of Complexity:**
   - Abstraction encapsulates the complexity of an object, allowing users to interact with a simplified and high-level representation.

### 2. **Modularity:**
   - Abstract classes serve as modular building blocks that can be extended and reused in various contexts, promoting code reusability.

### 3. **Focus on Essential Details:**
   - Users can focus on essential aspects of an object without being burdened by unnecessary details, leading to more straightforward and readable code.

### 4. **Adaptability:**
   - Abstraction allows for the creation of abstract classes with abstract methods. Concrete classes provide specific implementations, making the code adaptable to different scenarios.

### 5. **Ease of Maintenance:**
   - Changes to the internal details of concrete classes do not affect users interacting with abstract classes, resulting in easier maintenance.

## Best Practices for Abstraction in Python:

### 1. **Meaningful Abstractions:**
   - Create abstract classes that represent meaningful and cohesive abstractions. Avoid creating overly complex abstract classes with too many responsibilities.

### 2. **Clear Interfaces:**
   - Ensure that the interfaces provided by abstract classes are clear and well-documented, guiding users on how to interact with the abstraction.

### 3. **Consistent Naming Conventions:**
   - Follow consistent naming conventions for abstract classes and abstract methods, making the code more readable and understandable.

### 4. **Effective Use of Abstract Methods:**
   - Use abstract methods judiciously. Abstract methods should capture the essence of what all subclasses must implement, avoiding unnecessary abstraction.

### 5. **Polymorphism:**
   - Leverage abstraction to achieve polymorphism, where objects of different classes can be treated uniformly based on a common interface.

## Conclusion:

Abstraction in Python empowers developers to create clean, modular, and adaptable code by hiding unnecessary details and focusing on essential aspects of objects. Through the use of abstract classes and abstract methods, Python promotes a high-level, intuitive approach to designing and interacting with objects. Embrace abstraction to simplify complexity, enhance modularity, and create code that stands the test of time in the ever-evolving landscape of software development.