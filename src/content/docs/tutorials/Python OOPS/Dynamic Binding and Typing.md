---
title: Dyanamic Binding and Typing in Python
description: Learn about dynamic binding and typing in Python. In python, the type of the variable is decided at runtime. You can change the type of the variable at runtime. This is called dynamic typing. The binding of the variable is also decided at runtime. This is called dynamic binding.
sidebar: 
    order: 89
---

<!-- ```python title="method_overriding.py" {2-3, 6-7, 10-11}
class Animal:
    def make_sound(self):
        print("Generic animal sound")

class Dog(Animal):
    def make_sound(self):
        print("Bark!")

class Cat(Animal):
    def make_sound(self):
        print("Meow!")

dog = Dog()
cat = Cat()
dog.make_sound()
cat.make_sound()
```

Output:
```cmd title="command" showLineNumbers{1} {2-5}
Bark!
Meow!
```

In this example, we have a base class `Animal` with a method `make_sound`. We have two subclasses `Dog` and `Cat` that override the `make_sound` method inherited from the `Animal` class. The `Dog` and `Cat` classes provide specialized implementations of the `make_sound` method that are specific to each animal. The `Dog` class overrides the `make_sound` method to print "Bark!", while the `Cat` class overrides the `make_sound` method to print "Meow!". When we call the `make_sound` method on the `dog` and `cat` objects, the overridden methods in the respective subclasses are invoked, printing "Bark!" and "Meow!". -->

## Dynamic Binding and Typing in Python: Embracing Flexibility

Python is a dynamically-typed and dynamically-bound language, and these characteristics contribute significantly to its flexibility and ease of use. Understanding dynamic binding and typing in Python is crucial for writing expressive and adaptable code. Let's explore these concepts and their impact on the Python programming language.

## Dynamic Typing in Python:

### 1. **Dynamic Typing Defined:**
   - In a dynamically-typed language like Python, variable types are determined at runtime, not during compilation. This means you can change the type of a variable during the execution of a program.

   ```python title="dynamic_typing.py" showLineNumbers{1} {1-2}
   x = 5        # Integer type
   x = "Hello"  # String type (dynamic typing)
   ```

### 2. **No Explicit Type Declarations:**
   - Python does not require explicit type declarations when defining variables. The interpreter infers the type based on the assigned value.

   ```python title="dynamic_typing.py" showLineNumbers{1} {1-2}
   message = "Hello, Python!"  # String type
   count = 42                  # Integer type
   ```

### 3. **Ease of Use:**
   - Dynamic typing simplifies the coding process, as developers don't need to specify types explicitly. This makes Python code more concise and readable.

   ```python title="dynamic_typing.py" showLineNumbers{1} {1-3}
   a = 5
   b = "Hello"
   c = 3.14
   ```

### 4. **Flexibility and Expressiveness:**
   - The dynamic nature of Python allows for more flexibility and expressiveness, making it easy to write code that can adapt to changing requirements.

   ```python title="dynamic_typing.py" showLineNumbers{1} {1-4}
   x = 5
   y = "World"
   result = x + y  # Python dynamically handles the concatenation of int and str
   print(result)
   ```

   Output:
```cmd title="command" showLineNumbers{1} {2}
C:\Users\user\Desktop>python dynamic_typing.py
5World
```

In this example, we define two variables `x` and `y` with values of type `int` and `str`, respectively. We then concatenate the two variables and assign the result to a new variable `result`. Since Python is dynamically-typed, it can handle the concatenation of an `int` and `str` without any issues. When we print the value of `result`, we see that the `int` and `str` values are concatenated to produce the output `5World`.

