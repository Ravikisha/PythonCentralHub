---
title: OOPS in Python
description: Learn about OOPS in Python. In this tutorial, we will learn about classes, objects, inheritance, polymorphism, encapsulation, and abstraction in Python. We are going to learn about OOPS in Python with examples.
sidebar: 
    order: 80
---

## Object-Oriented Programming (OOP) in Python: An In-Depth Guide
Object-Oriented Programming (OOP) is a programming paradigm that revolves around the concept of objects, which encapsulate data and behavior. Python is an object-oriented programming language, and it provides robust support for OOP principles. In this in-depth guide, we will explore the key concepts of OOP in Python, including classes, objects, inheritance, encapsulation, and polymorphism.

## Programming Paradigms
A programming paradigm is a way of thinking about and approaching problems. It is a way of structuring and organizing code. There are several programming paradigms, including procedural programming, functional programming, and object-oriented programming. A programming paradigm is a way of thinking about and approaching problems. It is a way of structuring and organizing code. There are several programming paradigms, including procedural programming, functional programming, and object-oriented programming.

**The following are the most common programming paradigms:**
- **Procedural Programming**
- **Functional Programming**
- **Object-Oriented Programming**

<!-- ```python title="os_chdir.py" showLineNumbers{1} {1,3}
import os

os.chdir('C:\\Users\\User\\Desktop')
print(os.getcwd())
```

Output:
```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python os_chdir.py
C:\Users\username\Desktop
```

In the above example, we import the os module and use the os.chdir() method to change the current working directory to the Desktop directory. -->


## Procedural Programming
Procedural programming is a programming paradigm that revolves around the concept of procedures, which are also known as routines, subroutines, or functions. A procedure is a set of instructions that perform a specific task. Procedural programming is a programming paradigm that revolves around the concept of procedures, which are also known as routines, subroutines, or functions. A procedure is a set of instructions that perform a specific task. Procedural programming is a programming paradigm that revolves around the concept of procedures, which are also known as routines, subroutines, or functions. A procedure is a set of instructions that perform a specific task.

### Properties of Procedural Programming
- **Imperative**: Procedural programming is imperative, meaning it specifies explicit steps for the computer to perform.
- **Top-Down Design**: Programs are typically designed using a top-down approach, breaking down tasks into subtasks and sub-subtasks.
- **Global Data**: Data is often global and shared among procedures, which can lead to unintended side effects.
- **Structured Programming**: Procedural programming often follows structured programming principles, emphasizing the use of control structures like loops and conditionals.
- **Readability**: Programs tend to be more readable and understandable for beginners and those familiar with step-by-step procedural logic.

### Advantages of Procedural Programming
- **Simplicity**: Procedural programs are often straightforward and easy to understand.
- **Reusability**: Functions or procedures can be reused across different parts of the program.
- **Efficiency**: Procedural code can be more efficient in terms of memory usage and execution speed for certain tasks.
- **Easier Maintenance**: Code maintenance is often simpler as procedures are typically independent of each other.
- **Predictability**: The flow of the program is predictable and follows a clear sequence of steps.

### Disadvantages of Procedural Programming
- **Global State**: Shared global data can lead to unintended side effects and make it harder to reason about the program.
- **Limited Abstraction**: It may be challenging to represent complex relationships and abstractions in a procedural paradigm.
- **Code Duplication**: Without proper organization, code duplication may occur, leading to maintenance challenges.
- **Less Reusable**: Code can be less reusable when compared to more modular paradigms.
- **Scalability Issues**: Large programs may become harder to manage and scale as they grow in size.

## Functional Programming
Functional programming is a programming paradigm that revolves around the concept of functions. A function is a block of code that performs a specific task. Functional programming is a programming paradigm that revolves around the concept of functions. A function is a block of code that performs a specific task. Functional programming is a programming paradigm that revolves around the concept of functions. A function is a block of code that performs a specific task.

### Properties of Functional Programming
- **Declarative Style**: Functional programming emphasizes a declarative style where the focus is on expressing what the program should accomplish rather than how it should achieve it.
- **Immutability**: Data is treated as immutable, meaning once it is created, it cannot be changed. Functions do not have side effects.
- **First-Class Functions**: Functions are first-class citizens, allowing them to be passed as arguments, returned from other functions, and assigned to variables.
- **Higher-Order Functions**: Functions can take other functions as parameters or return functions as results.
- **Recursion**: Recursion is often used instead of traditional loops for repetitive tasks.

### Advantages of Functional Programming
- **Modularity**: Functional programs are often modular, promoting code reuse and maintainability.
- **Parallelization**: Immutability allows for easier parallelization of code, taking advantage of multicore processors.
- **Predictability**: Functions in functional programming tend to be deterministic, making it easier to reason about program behavior.
- **No Side Effects**: The avoidance of side effects makes programs less error-prone and easier to debug.
- **Expressiveness**: Functional programs can be highly expressive, allowing concise representation of complex operations.

### Disadvantages of Functional Programming
- **Learning Curve**: Functional programming concepts can be challenging for those accustomed to imperative paradigms.
- **Performance Overhead**: Functional programming may introduce a performance overhead due to the creation of new data structures rather than modifying existing ones.
- **Limited Mutability**: The restriction on mutability might be seen as a limitation in scenarios where mutable state is essential.
- **Compatibility**: Some existing libraries and frameworks may not be designed with functional programming in mind.
- **Not Always Intuitive**: Some problems may not be naturally expressed using a functional paradigm, leading to less intuitive solutions.



## What is Object-Oriented Programming (OOP)?
Object-Oriented Programming (OOP) is a programming paradigm that revolves around the concept of objects, which encapsulate data and behavior. An object is an instance of a class. A class is a blueprint for an object. In other words, a class is a template for creating objects. A class defines the properties and behavior of an object. An object is an instance of a class. An object is an entity that has state and behavior. For example, a car is an object. It has a state (color, model, etc.) and behavior (braking, accelerating, etc.). A class is a blueprint for creating objects.
