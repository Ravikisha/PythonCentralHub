---
title: Python Input Statement
description: How to get input from the user in Python.
sidebar: 
    order: 12
---

## Mastering User Input in Python

User input is a crucial component of many Python programs, enabling interaction and customization. In this comprehensive guide, we'll explore the various aspects of handling user input in Python, covering the basics, type conversion, input validation, and practical examples.

## Input Function Definition

The `input()` function is used to receive input from the user. It displays a prompt and waits for the user to enter data. The entered data is then returned as a string.

The syntax of the `input()` function is as follows:

```python title="input.py" showLineNumbers{1}
input([prompt])
```
> There is one optional parameter, `prompt`, which is the string displayed to the user. If no prompt is provided, the function simply waits for the user to enter data.

::: tip
`input()` function returns a string. If you expect a different data type, such as an integer or a float, you need to perform type conversion.

for example:

```python title="input.py" showLineNumbers{1}
name = input("Enter your name: ")
age = int(input("Enter your age: "))
height = float(input("Enter your height in meters: "))

print(type(name))
print(type(age))
print(type(height))
```
Output:

```cmd title="command" showLineNumbers{1} {4-6}
Enter your name: John
Enter your age: 25
Enter your height in meters: 1.75
<class 'str'>
<class 'int'>
<class 'float'>
```


## Basics of User Input

In Python, the `input()` function is the gateway to capturing user input. It prompts the user to enter data, and whatever is entered is treated as a string. Here's a simple example:

```python title="input.py" showLineNumbers{1}
user_name = input("Enter your name: ")
print("Hello, " + user_name + "!")
```

Output:

```cmd title="command" showLineNumbers{1} {2}
Enter your name: John
Hello, John!
```

In this snippet, the `input()` function displays the prompt ("Enter your name: ") and waits for the user to input their name. The entered value is then stored in the variable `user_name` and used in the subsequent `print()` statement.

:::note
`raw_input()` function is used in Python 2.x to receive user input. In Python 3.x, `raw_input()` was renamed to `input()`.

```python title="input.py" showLineNumbers{1}
user_name = raw_input("Enter your name: ")
print("Hello, " + user_name + "!")
```

Output:

```cmd title="command" showLineNumbers{1} {2}
Enter your name: John
Hello, John!
```
:::

## Type Conversion of User Input

By default, the input from the user is treated as a string. If you expect a different data type, such as an integer or a float, you need to perform type conversion. Here's an example:

```python title="input.py" showLineNumbers{1}
age = int(input("Enter your age: "))
height = float(input("Enter your height in meters: "))

print(type(age))
print(type(height))
```

Output:

```cmd title="command" showLineNumbers{1} {2}
Enter your age: 25
Enter your height in meters: 1.75
<class 'int'>
<class 'float'>
```

In this example, `int()` and `float()` functions are used to convert the user input to integer and float data types, respectively.

## Handling User Input Validation

Ensuring that the user provides valid input is crucial for the robustness of your program. Using conditional statements and exception handling, you can validate and handle potential errors gracefully:

```python title="input.py" showLineNumbers{1}
while True:
    try:
        age = int(input("Enter your age: "))
        if age < 0:
            print("Please enter a non-negative age.")
        else:
            break  # Exit the loop if the input is valid
    except ValueError:
        print("Invalid input. Please enter a valid integer.")
```

Output:

```cmd title="command" showLineNumbers{1} {2}
Enter your age: -5
Please enter a non-negative age.
Enter your age: 25
```

In this example, a `while` loop is used to continually prompt the user for input until a valid integer is entered. The `try` and `except` blocks handle potential errors, such as non-integer inputs.

## Input in Script Execution

Python scripts can also receive input through command-line arguments using `sys.argv`. This allows users to provide input when executing a script:

```python title="input.py" showLineNumbers{1}
import sys

if len(sys.argv) > 1:
    user_name = sys.argv[1]
    print("Hello, " + user_name + "!")
else:
    print("Please provide your name as a command-line argument.")
```

Output:

```bash title="command" showLineNumbers{1} {2}
$ python input.py John
Hello, John!
```

Or in Windows:
    
```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python input.py John
Hello, John!
```

In this script, if additional arguments are provided during execution, the first argument is used as the user's name. Otherwise, a prompt is displayed.

## Security Considerations

When dealing with user input, it's crucial to handle it securely to prevent issues like code injection or unintended consequences. If user input is used in database queries or other sensitive operations, consider using parameterized queries or input validation techniques to enhance security.

## Conclusion

Handling user input in Python opens up a world of possibilities for creating dynamic and interactive programs. By utilizing the `input()` function, performing type conversion, validating input, and considering security measures, you can create robust and user-friendly applications. Whether you're building command-line tools or interactive scripts, understanding how to effectively interact with users enhances the overall user experience.

As you continue your Python journey, explore more advanced user input techniques, integrate them into your projects, and ensure a smooth and error-resistant user interaction. For additional guidance and hands-on examples, check out our tutorials on Python Central Hub!