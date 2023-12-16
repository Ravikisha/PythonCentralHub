---
title: Assert Statement in Python
description: Learn how to use assert statement in Python. assert is used for debugging purposes. While programming, sometimes we wish to know the internal state or check if our assumptions are true. assert helps us do this and find bugs more conveniently. assert is followed by a condition. If the condition is true, nothing happens. But if the condition is false, AssertionError is raised. AssertionError exceptions can be caught and handled like any other exception using the try-except statement, but if not handled, this type of exception will terminate the program. 
sidebar: 
    order: 41
---

## Asserting Excellence: A Comprehensive Guide to the `assert` Statement in Python

In Python, the `assert` statement is a powerful tool for debugging and ensuring that certain conditions hold true during the execution of a program. It allows developers to express assumptions about the state of the code and halts program execution if these assumptions are not met. In this comprehensive guide, we'll explore the syntax, use cases, and best practices associated with the `assert` statement in Python.

## Basic Syntax of the `assert` Statement

The `assert` statement has a simple syntax:

```python title="Syntax" showLineNumbers{1} {1}
assert expression [, message]
```

- `expression`: A condition that should evaluate to `True`. If it evaluates to `False`, the `assert` statement raises an `AssertionError`.
- `message` (optional): An additional message that is displayed when the assertion fails.

### Example:

```python title="assert_statement.py" showLineNumbers{1} {2}
x = 5
assert x > 0, "x should be a positive number"
```

Output:

```cmd title="command" showLineNumbers{1} {2-7}
C:\Users\Your Name> python assert_statement.py
Traceback (most recent call last):
  File "assert_statement.py", line 3, in <module>
    assert x > 0, "x should be a positive number"
AssertionError: x should be a positive number
```

In this example, if the value of `x` is not greater than 0, an `AssertionError` is raised with the specified message.

## Use Cases for the `assert` Statement

### 1. **Debugging and Development:**

During the development phase, the `assert` statement is a valuable tool for catching logical errors early in the code. It allows developers to express their assumptions about the code's state and automatically checks if those assumptions hold true.

```python title="assert_statement.py" showLineNumbers{1} {2}
def calculate_discount(price, discount_rate):
    assert 0 <= discount_rate <= 1, "Discount rate should be between 0 and 1"
    # Rest of the function code
```

Output:

```cmd title="command" showLineNumbers{1} {2-7}
C:\Users\Your Name> python assert_statement.py
Traceback (most recent call last):
  File "assert_statement.py", line 2, in <module>
    assert 0 <= discount_rate <= 1, "Discount rate should be between 0 and 1"
AssertionError: Discount rate should be between 0 and 1
```

Here, the `assert` statement ensures that the discount rate is within a valid range, providing an early indication if it's not.

### 2. **Testing and Quality Assurance:**

In unit testing and quality assurance processes, the `assert` statement is used to verify that the code behaves as expected. It helps in creating test cases and asserting that certain conditions are met during the execution of the code.

```python title="assert_statement.py" showLineNumbers{1} {2}
def divide(a, b):
    assert b != 0, "Cannot divide by zero"
    return a / b

print(divide(10, 0))
```

Output:

```cmd title="command" showLineNumbers{1} {2-7}
C:\Users\Your Name> python assert_statement.py
Traceback (most recent call last):
  File "assert_statement.py", line 4, in <module>
    print(divide(10, 0))
  File "assert_statement.py", line 2, in divide
    assert b != 0, "Cannot divide by zero"
AssertionError: Cannot divide by zero
```

This `assert` statement ensures that attempting to divide by zero will result in an `AssertionError` during testing.

### 3. **Documenting Assumptions:**

The `assert` statement serves as a form of documentation by explicitly stating assumptions about the code. When used judiciously, it can make the code more understandable and help other developers grasp the intended behavior.

```python title="assert_statement.py" showLineNumbers{1} {2}
def process_data(data):
    assert len(data) > 0, "Input data should not be empty"
    # Rest of the function code

process_data([])
```

Output:

```cmd title="command" showLineNumbers{1} {2-7}
C:\Users\Your Name> python assert_statement.py
Traceback (most recent call last):
  File "assert_statement.py", line 4, in <module>
    process_data([])
  File "assert_statement.py", line 2, in process_data
    assert len(data) > 0, "Input data should not be empty"
AssertionError: Input data should not be empty
```

This `assert` statement communicates the expectation that the input data should not be empty.

## Best Practices for Using the `assert` Statement

### 1. **Avoid Side Effects:**

It's essential to keep in mind that the `assert` statement should not have side effects. The purpose of `assert` is to check conditions, not to modify the program's state.

```python title="assert_side_effects.py" showLineNumbers{1} {2, 5}
# Avoid
assert x > 0, x = 0

# Prefer
assert x > 0, "x should be a positive number"
```

Output:

```cmd title="command" showLineNumbers{1} {2-7}
C:\Users\Your Name> python assert_side_effects.py
Traceback (most recent call last):
  File "assert_side_effects.py", line 2, in <module>
    assert x > 0, x = 0
AssertionError: 0
```

In this example, the `assert` statement has a side effect of modifying the value of `x` to 0. This is not recommended and can lead to unexpected behavior. Instead, the `assert` statement should be used to check the condition and raise an `AssertionError` if it's not met. The `assert` statement should not modify the value of `x`. 

### 2. **Do Not Use `assert` for Data Validation:**

While `assert` can be useful for catching bugs, it is not intended for data validation in production code. It can be disabled globally, and relying on it for input validation might introduce security vulnerabilities.

### 3. **Provide Clear Messages:**

When using the `assert` statement, provide clear and informative messages. These messages serve as documentation and aid in understanding the cause of the failure when an assertion error occurs.

```python title="assert_message.py" showLineNumbers{1} {1}
assert len(data) > 0, "Input data should not be empty"
```

Output:

```cmd title="command" showLineNumbers{1} {2-7}
C:\Users\Your Name> python assert_message.py
Traceback (most recent call last):
  File "assert_message.py", line 1, in <module>
    assert len(data) > 0, "Input data should not be empty"
AssertionError: Input data should not be empty
```

In this example, the message "Input data should not be empty" provides additional context about the cause of the assertion error.

### 4. **Use Conditional Statements for Production Code:**

For conditions that are critical for the correctness of the program and should be checked even in production, consider using conditional statements (e.g., `if`, `raise`) rather than `assert`.

```python title="assert_condition.py" showLineNumbers{1} {2}
if x <= 0:
    raise ValueError("x should be a positive number")
```

Output:

```cmd title="command" showLineNumbers{1} {2-7}
C:\Users\Your Name> python assert_condition.py
Traceback (most recent call last):
  File "assert_condition.py", line 2, in <module>
    raise ValueError("x should be a positive number")
ValueError: x should be a positive number
```

In this example, the `raise` statement is used to raise a `ValueError` exception if the condition is not met. This is preferred over using `assert` because it ensures that the condition is checked even in production.

## Conclusion

The `assert` statement in Python is a powerful tool for expressing and validating assumptions about the state of the code. While it is invaluable during development, testing, and debugging, it should be used judiciously and with careful consideration of its limitations. By following best practices and providing clear messages, the `assert` statement contributes to the reliability and maintainability of Python code.

As you advance in your Python programming journey, explore the effective use of the `assert` statement to catch potential issues early and create more robust and dependable software. For more insights and practical examples, check out our tutorials on Python Central Hub!