---
title: Python Comments
description: An introduction to comments in Python. Learn about single-line and multi-line comments and best practices for using comments in your Python code.
sidebar: 
    order: 5
---

Comments are used in Python to add explanations or notes to the code. They are not executed and do not affect the program's functionality. Comments are crucial for enhancing code readability and for providing context to readers.

## Single-line Comments

In Python, single-line comments start with the `#` symbol. Anything following the `#` on that line is considered a comment.

### Example:

```python title="comment.py" showLineNumbers{1} {1}
# This is a single-line comment

print("Hello, World!")  # This is also a comment after code
```

## Multi-line Comments

While Python does not have a specific syntax for multi-line comments, you can use triple-quotes (`'''` or `"""`) to create multi-line string literals. Even though these are technically strings, they are often used as a workaround for creating multi-line comments.

### Example:

```python title="comment.py" showLineNumbers{1} {1-4, 6-9}
'''
This is a multi-line comment.
It spans multiple lines.
'''

"""
Another way to create a multi-line comment.
Use triple-quotes to start and end the comment block.
"""

print("Hello, World!")
```

## Comments for Code Documentation

In addition to adding comments for clarifying code, Python has a convention for using docstrings to document functions, modules, and classes. Docstrings are enclosed in triple-quotes and are used to provide information about the code element.

### Example:

```python title="comment.py" showLineNumbers{1} {2-11, 14}
def add_numbers(a, b):
    """
    This function adds two numbers and returns the result.
    
    Parameters:
    - a (int): The first number.
    - b (int): The second number.
    
    Returns:
    int: The sum of a and b.
    """
    return a + b

# Usage of the function
result = add_numbers(5, 3)
print("Result:", result)
```

## Best Practices for Comments

1. **Be Clear and Concise:** Write comments that are easy to understand. Avoid unnecessary comments that restate the obvious.

2. **Keep Comments Updated:** If code changes, remember to update the associated comments to ensure accuracy.

3. **Use Docstrings for Documentation:** For functions, modules, and classes, utilize docstrings to provide comprehensive documentation.

4. **Avoid Excessive Comments:** Code should be self-explanatory whenever possible. Avoid cluttering your code with excessive comments.

Comments play a crucial role in effective communication within your codebase. Use them wisely to make your Python code more understandable and maintainable.

Explore more Python coding practices with our tutorials on Python Central Hub!