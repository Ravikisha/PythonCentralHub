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

