---
title: Decorator in Python
description: Learn about Decorators in Python, how to create and use them, and the different types of decorators in Python. Decorators are used to modify or extend the behavior of functions or methods in Python.
sidebar: 
    order: 95
---

## Decorator in Python : Modify or Extend Functionality
Decorators are a powerful feature in Python that allows you to modify or extend the behavior of functions or methods. Decorators are functions that take another function as an argument and return a new function. They are used to add functionality to an existing function without modifying its code. Decorators are commonly used in Python to implement cross-cutting concerns such as logging, authentication, caching, and more.

### Working of Decorators
Decorators work by wrapping the original function with another function that adds additional functionality before and after calling the original function. When you apply a decorator to a function, the decorator function is called with the original function as an argument. The decorator function returns a new function that calls the original function and adds additional functionality.


```mermaid title="Working of Decorators" desc="Decorators decorate the original function by adding additional functionality."
graph LR
    A[Original Function] --> B[Decorator Function]
    B --> C[Wrapper Function]
    C --> A
    C --> D[Additional Functionality]
    D --> A
```

### Syntax of Decorators
The syntax of a decorator in Python is as follows:

```python title="Syntax" showLineNumbers{1}
def decorator_function(func):
    def wrapper_function(*args, **kwargs):
        # Add functionality before calling the original function
        result = func(*args, **kwargs)
        # Add functionality after calling the original function
        return result
    return wrapper_function
```

Here,
- `decorator_function`: The decorator function that takes another function as an argument.
- `wrapper_function`: The wrapper function that adds functionality before and after calling the original function.
- `*args` and `**kwargs`: Arguments and keyword arguments passed to the original function.
- The decorator function returns the wrapper function.
- The wrapper function calls the original function and adds additional functionality.

### Applying a Decorator
To apply a decorator to a function, you can use the `@decorator_function` syntax before the function definition. Here is an example of applying a decorator to a function:

```python title="decorator_example.py" showLineNumbers{1} {8}
def my_decorator(func):
    def wrapper():
        print("Before calling the function")
        func()
        print("After calling the function")
    return wrapper

@my_decorator
def say_hello():
    print("Hello, World!")

say_hello()
```

In the above example, we have defined a decorator function `my_decorator` that adds functionality before and after calling the original function. We have applied the decorator to the `say_hello` function using the `@my_decorator` syntax.

When we run the above code, it will output:

```cmd title="Command" showLineNumbers{1} {2-5}
C:\Users\username\Desktop> python decorator_example.py
Before calling the function
Hello, World!
After calling the function
```

### Types of Decorators
There are different types of decorators in Python based on their usage and implementation:
1. **Function Decorators**: Function decorators are the most common type of decorators in Python. They are used to modify the behavior of functions.
2. **Class Decorators**: Class decorators are used to modify the behavior of classes. They take a class as an argument and return a new class.
3. **Method Decorators**: Method decorators are used to modify the behavior of methods. They take a method as an argument and return a new method.
4. **Property Decorators**: Property decorators are used to modify the behavior of properties. They take a property as an argument and return a new property.
5. **Static Method Decorators**: Static method decorators are used to modify the behavior of static methods. They take a static method as an argument and return a new static method.
6. **Class Method Decorators**: Class method decorators are used to modify the behavior of class methods. They take a class method as an argument and return a new class method.
7. **Decorator with Arguments**: Decorators can also take arguments to customize their behavior. You can create decorators that accept arguments by defining a decorator function that returns another function.
8. **Chained Decorators**: You can chain multiple decorators on a single function by applying multiple decorators using the `@` syntax.

### Function Decorator Example
Here is an example of a function decorator that logs the function name before calling it:

```python title="function_decorator.py" showLineNumbers{1}
def log_function(func):
    def wrapper(*args, **kwargs):
        print(f"Calling function: {func.__name__}")
        result = func(*args, **kwargs)
        return result
    return wrapper

@log_function
def add(a, b):
    return a + b

result = add(10, 20)
print("Result:", result)
```

In this example, we have defined a function decorator `log_function` that logs the function name before calling it. We have applied the decorator to the `add` function, which adds two numbers.

When we run the above code, it will output:

```cmd title="Command" showLineNumbers{1} {2-4}
C:\Users\username\Desktop> python function_decorator.py
Calling function: add
Result: 30
```

Decorators are a powerful feature in Python that allows you to modify or extend the behavior of functions or methods. They are widely used in Python libraries and frameworks to implement common functionality such as logging, caching, authentication, and more.

### Class Decorator Example
Here is an example of a class decorator that adds a `display` method to a class:

```python title="class_decorator.py" showLineNumbers{1}
def add_method(cls):
    def display(self):
        print("Displaying the object")
    cls.display = display
    return cls

@add_method
class MyClass:
    pass

obj = MyClass()
obj.display()
```

In this example, we have defined a class decorator `add_method` that adds a `display` method to the class. We have applied the decorator to the `MyClass` class, which adds the `display` method to the class.

When we run the above code, it will output:

```cmd title="Command" showLineNumbers{1} {2}
C:\Users\username\Desktop> python class_decorator.py
Displaying the object
```

### Method Decorator Example
Here is an example of a method decorator that logs the method name before calling it:

```python title="method_decorator.py" showLineNumbers{1}
def log_method(func):
    def wrapper(self, *args, **kwargs):
        print(f"Calling method: {func.__name__}")
        result = func(self, *args, **kwargs)
        return result
    return wrapper

class MyClass:
    def __init__(self):
        self.value = 100
    
    @log_method
    def display(self):
        print(f"Value: {self.value}")

obj = MyClass()
obj.display()
```

In this example, we have defined a method decorator `log_method` that logs the method name before calling it. We have applied the decorator to the `display` method of the `MyClass` class.

When we run the above code, it will output:

```cmd title="Command" showLineNumbers{1} {2-4}
C:\Users\username\Desktop> python method_decorator.py
Calling method: display
Value: 100
```

### Property Decorator Example
Here is an example of a property decorator that logs the property name before accessing it:

```python title="property_decorator.py" showLineNumbers{1}
def log_property(prop):
    def getter(self):
        print(f"Accessing property: {prop.__name__}")
        return prop.fget(self)
    return property(getter)

class MyClass:
    def __init__(self):
        self._value = 100
    
    @log_property
    def value(self):
        return self._value

obj = MyClass()
print(obj.value)
```

In this example, we have defined a property decorator `log_property` that logs the property name before accessing it. We have applied the decorator to the `value` property of the `MyClass` class.

When we run the above code, it will output:

```cmd title="Command" showLineNumbers{1} {2}
C:\Users\username\Desktop> python property_decorator.py
Accessing property: value
100
```

### Static Method Decorator Example
Here is an example of a static method decorator that logs the method name before calling it:

```python title="staticmethod_decorator.py" showLineNumbers{1}
def log_static_method(func):
    def wrapper(*args, **kwargs):
        print(f"Calling static method: {func.__name__}")
        result = func(*args, **kwargs)
        return result
    return staticmethod(wrapper)

class MyClass:
    @log_static_method
    def static_method():
        print("Static method called")

MyClass.static_method()
```

In this example, we have defined a static method decorator `log_static_method` that logs the method name before calling it. We have applied the decorator to the `static_method` static method of the `MyClass` class.

When we run the above code, it will output:

```cmd title="Command" showLineNumbers{1} {2}
C:\Users\username\Desktop> python staticmethod_decorator.py
Calling static method: static_method
Static method called
```

### Class Method Decorator Example
Here is an example of a class method decorator that logs the method name before calling it:

```python title="classmethod_decorator.py" showLineNumbers{1}
def log_class_method(func):
    def wrapper(cls, *args, **kwargs):
        print(f"Calling class method: {func.__name__}")
        result = func(cls, *args, **kwargs)
        return result
    return classmethod(wrapper)

class MyClass:
    @log_class_method
    def class_method(cls):
        print("Class method called")

MyClass.class_method()
```

In this example, we have defined a class method decorator `log_class_method` that logs the method name before calling it. We have applied the decorator to the `class_method` class method of the `MyClass` class.

When we run the above code, it will output:

```cmd title="Command" showLineNumbers{1} {2}
C:\Users\username\Desktop> python classmethod_decorator.py
Calling class method: class_method
Class method called
```

### Decorator with Arguments Example
You can create decorators that accept arguments to customize their behavior. Here is an example of a decorator that logs the function name with a custom message:

```python title="decorator_with_arguments.py" showLineNumbers{1}
def log_message(message):
    def decorator(func):
        def wrapper(*args, **kwargs):
            print(f"{message}: {func.__name__}")
            result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator

@log_message("Calling function")
def add(a, b):
    return a + b

result = add(10, 20)
print("Result:", result)
```

In this example, we have defined a decorator `log_message` that accepts a message as an argument. The decorator returns a decorator function that logs the function name with the custom message. We have applied the decorator to the `add` function with the message `"Calling function"`.

When we run the above code, it will output:

```cmd title="Command" showLineNumbers{1} {2-4}
C:\Users\username\Desktop> python decorator_with_arguments.py
Calling function: add
Result: 30
```

### Chained Decorators Example
You can chain multiple decorators on a single function by applying multiple decorators using the `@` syntax. Here is an example of chaining two decorators on a function:

```python title="chained_decorators.py" showLineNumbers{1}
def log_function(func):
    def wrapper(*args, **kwargs):
        print(f"Calling function: {func.__name__}")
        result = func(*args, **kwargs)
        return result
    return wrapper

def add_message(func):
    def wrapper(*args, **kwargs):
        print("Adding two numbers")
        result = func(*args, **kwargs)
        return result
    return wrapper

@log_function
@add_message
def add(a, b):
    return a + b

result = add(10, 20)
print("Result:", result)
```

In this example, we have defined two decorators `log_function` and `add_message`. We have applied both decorators to the `add` function using the `@` syntax. The decorators are applied in the order they are listed, so the `log_function` decorator is applied first, followed by the `add_message` decorator.

When we run the above code, it will output:

```cmd title="Command" showLineNumbers{1} {2-4}
C:\Users\username\Desktop> python chained_decorators.py
Calling function: wrapper
Adding two numbers
Result: 30
```

Decorators are a powerful feature in Python that allows you to modify or extend the behavior of functions or methods. They are widely used in Python libraries and frameworks to implement common functionality such as logging, caching, authentication, and more.

## Conclusion
In this tutorial, you learned about decorators in Python, how to create and use them, and the different types of decorators in Python. Decorators are a powerful feature that allows you to modify or extend the behavior of functions or methods without modifying their code. Decorators are commonly used in Python to implement cross-cutting concerns such as logging, authentication, caching, and more. You can create function decorators, class decorators, method decorators, property decorators, static method decorators, class method decorators, decorators with arguments, and chained decorators to add functionality to your code. For more information, you can refer to the [Python Decorators](https://docs.python.org/3/glossary.html#term-decorator) documentation. For more tutorials, you can visit the Python Central Hub.