---
title: Anonymous Class in Python
description: Learn about Anonymous Class in Python, also known as Lambda Class, and how to create and use them. Anonymous Classes are classes without a name in Python.
sidebar: 
    order: 94
---

## Anonymous Class in Python : Create classes without a name
In Python, an anonymous class is a class without a name. Anonymous classes are also known as Lambda classes. They are used to create classes on the fly without defining a class name.

Anonymous classes are created using the `type` function. The `type` function takes three arguments: the class name, a tuple of base classes, and a dictionary of class attributes.

### Syntax of Anonymous Classes
Syntax:
```python title="Syntax" showLineNumbers{1}
type(class_name, base_classes, class_attributes)
```
Here,
- `class_name`: The name of the class. If you want to create an anonymous class, you can pass an empty string `""`.
- `base_classes`: A tuple of base classes. If the class has no base class, you can pass an empty tuple `()`.
- `class_attributes`: A dictionary of class attributes. You can define the class variables and methods in this dictionary.
- The `type` function returns a class object.
- You can create an instance of the anonymous class by calling the class object.

Here is an example of an anonymous class in Python:

```python title="anonymous_class.py" showLineNumbers{1} {2}
# Create an instance of the anonymous class
obj = type("AnonymousClass", (MyClass,), {"name": "Alice"})()

# Call the display method of the anonymous class
obj.display()
```

In the above example, we have created an anonymous class `AnonymousClass` that inherits from the `MyClass` class. The anonymous class has a class attribute `name` with the value `"Alice"`. We have created an instance of the anonymous class and called the `display` method.

When we run the above code, it will output:
```cmd title="Command" showLineNumbers{1} {2}
C:\Users\username\Desktop> python anonymous_class.py
Hello, Alice!
```

### Advantages of Anonymous Classes
1. **Dynamic Class Creation**: Anonymous classes allow you to create classes dynamically at runtime.
2. **Simplifies Code**: Anonymous classes help in simplifying the code by creating classes without a name.
3. **Encapsulation**: Anonymous classes encapsulate the class definition within a single expression.
4. **Code Reusability**: Anonymous classes can be reused at multiple places in the code.
5. **Flexibility**: Anonymous classes provide flexibility in creating classes with different attributes and methods.
6. **Functional Programming**: Anonymous classes are used in functional programming to create classes on the fly.
7. **Reduced Boilerplate Code**: Anonymous classes reduce the boilerplate code required to define a class.
8. **Cleaner Code**: Anonymous classes help in writing cleaner and concise code.
9. **Less Code**: Anonymous classes require less code to define a class compared to

### Limitations of Anonymous Classes
1. **Readability**: Anonymous classes can make the code less readable if used excessively.
2. **Debugging**: Debugging anonymous classes can be difficult as they do not have a name.
3. **Testing**: Testing anonymous classes can be challenging as they are not named.
4. **Documentation**: Anonymous classes lack proper documentation as they do not have a name.
5. **Complexity**: Anonymous classes can introduce complexity in the code if not used judiciously.

### Variables and Methods in Anonymous Classes
You can define class variables and methods in anonymous classes using the dictionary of class attributes. Here is an example:

```python title="anonymous_class.py" showLineNumbers{1} {2}
# Create an instance of the anonymous class
obj = type("AnonymousClass", (), {"name": "Alice", "display": lambda self: print(f"Hello, {self.name}!")})()

# Call the display method of the anonymous class
obj.display()
```

In the above example, we have defined a class variable `name` and a class method `display` in the dictionary of class attributes. We have created an instance of the anonymous class and called the `display` method.

When we run the above code, it will output:
```cmd title="Command" showLineNumbers{1} {2}
C:\Users\username\Desktop> python anonymous_class.py
Hello, Alice!
```

## Conclusion
In Python, anonymous classes are used to create classes without a name. Anonymous classes are created using the `type` function. They are useful for creating classes dynamically at runtime. Anonymous classes help in simplifying the code and encapsulating the class definition within a single expression. However, excessive use of anonymous classes can make the code less readable and difficult to debug. It is recommended to use anonymous classes judiciously to maintain code readability and simplicity. For more information, you can refer to the [official documentation](https://docs.python.org/3/library/functions.html#type). For more tutorials, you can visit the Python Central Hub.