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

## Dynamic Binding in Python:

### 1. **Dynamic Binding Defined:**
   - Dynamic binding, also known as late binding or runtime binding, allows the association between a method call and the method implementation to be resolved at runtime.

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

In this example, we have a base class `Animal` with a method `speak`. We have two subclasses `Dog` and `Cat` that override the `speak` method inherited from the `Animal` class. The `Dog` and `Cat` classes provide specialized implementations of the `speak` method that are specific to each animal. The `Dog` class overrides the `speak` method to print "Woof!", while the `Cat` class overrides the `speak` method to print "Meow!". We then create a list of objects of type `Animal`, `Dog`, and `Cat` and iterate over the list, calling the `speak` method on each object. Since Python is dynamically-bound, the method call is resolved at runtime, and the overridden methods in the respective subclasses are invoked, printing "Woof!" and "Meow!".


### 2. **Polymorphism in Action:**
   - Dynamic binding plays a crucial role in achieving polymorphism in Python. Objects of different types can be treated uniformly based on a common interface.

```python title="dynamic_binding.py" showLineNumbers{1} {1-2}
def make_animal_speak(animal):
    animal.speak()

dog = Dog()
cat = Cat()
make_animal_speak(dog)  # Resolves to Dog's speak method dynamically
make_animal_speak(cat)  # Resolves to Cat's speak method dynamically
```

Output:
```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\user\Desktop>python dynamic_binding.py
Woof!
Meow!
```

In this example, we define a function `make_animal_speak` that takes an `Animal` object as an argument and calls the `speak` method on the object. We then create objects of type `Dog` and `Cat` and pass them to the `make_animal_speak` function. Since Python is dynamically-bound, the method call is resolved at runtime, and the overridden methods in the respective subclasses are invoked, printing "Woof!" and "Meow!".


### 3. **Late Decision-Making:**
   - The decision about which method to call is made at runtime, allowing for late decision-making and adaptability.

### 4. **Flexibility and Extensibility:**
   - Dynamic binding enhances the flexibility and extensibility of the code, making it easy to add new functionality without modifying existing code.

```python title="dynamic_binding.py" showLineNumbers{1} {1-3}
class Cow(Animal):
    def speak(self):
        print("Moo!")

cow = Cow()
make_animal_speak(dog)  # Resolves to Dog's speak method dynamically
make_animal_speak(cat)  # Resolves to Cat's speak method dynamically
make_animal_speak(cow)  # Resolves to Cow's speak method dynamically
```

Output:
```cmd title="command" showLineNumbers{1} {2-4}
C:\Users\user\Desktop>python dynamic_binding.py
Woof!
Meow!
Moo!
```

In this example, we define a new subclass `Cow` that inherits from the `Animal` class and overrides the `speak` method to print "Moo!". We then create an object of type `Cow` and pass it to the `make_animal_speak` function. Since Python is dynamically-bound, the method call is resolved at runtime, and the overridden method in the `Cow` class is invoked, printing "Moo!".
