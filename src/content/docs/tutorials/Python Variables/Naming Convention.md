---
title: Naming Convention
description: An introduction to naming conventions in Python. Learn about variable, constant, function, and class naming conventions and best practices for naming identifiers in Python.
sidebar: 
    order: 7
---

## Variable Naming Conventions
A variable can have a short name (like `x` and `y`) or a more descriptive name (like `age`, `carname`, `total_volume`). Rules for Python variables:
- A variable name must start with a letter or the underscore character
- A variable name cannot start with a number
- A variable name can only contain alpha-numeric characters and underscores (A-z, 0-9, and _ )
- Variable names are case-sensitive (age, Age and AGE are three different variables)
- The reserved words (keywords) cannot be used naming the variable
- Variable names should be short but descriptive
- Use of underscores (`_`) is recommended to improve readability
- Avoid using special characters like `!`, `@`, `#`, `$`, `%`, etc. in variable names
- Avoid using built-in function names as variable names
- Avoid using single characters like `l`, `O`, `I`, etc. as variable names
- Avoid using words with double meaning like `list`, `str`, `dict`, etc. as variable names
- Avoid using words with different spellings like `colour` and `color`, `centre` and `center` , etc. as variable names

#### Example:
```python title="variable.py" showLineNumbers{1} {2,3,4,5,6,7,8,9}
# Valid variable names
name = "John"
my_name = "John"
_my_name = "John"
myName = "John"
MYNAME = "John"
myname = "John"
myName2 = "John"
my2name = "John"
```

:::caution
Python is a case-sensitive language. This means that `my_name` and `myName` are two different variables.
:::

:::caution
Don't use long variable names. Use short names instead. This improves readability and reduces the amount of typing.
```python title="variable.py" showLineNumbers{1} {2,3,4,5,6,7,8,9}
# Don't recommend
my_name_is_john_and_i_am_20_years_old = "John"
```
:::

:::danger
You cannot use Python keywords as variable names. Keywords are the reserved words in Python. They are used to define the syntax and structure of the Python language. You can't use them as variable names.
```python title="variable.py" showLineNumbers{1} {2,3,5,6,7,8}
# Invalid variable names
class = "John"
for = "John"
# Some other Invalid variable names
2myname = "John"
my-name = "John"
my name = "John"
```
:::
B

## Constant Naming Conventions
Constants are usually declared and assigned in a module. Python does not have built-in constant types, but Python programmers use all capital letters to indicate a variable should be treated as a constant and never be changed after it is initialized.

#### Example:
```python title="constant.py" showLineNumbers{1} {2,3,4}
# Valid constant names
PI = 3.14
GRAVITY = 9.8
PLANET = "Earth"
```

## Function Naming Conventions
Function names should be lowercase, with words separated by underscores as necessary to improve readability. Mixed case is allowed only in contexts where that's already the prevailing style (e.g. `threading.py`), to retain backwards compatibility.

#### Example:
```python title="function.py" showLineNumbers{1} {2,3,5,6}
# Valid function names
def my_function():
    pass

def myFunction():
    pass
```

## Class Naming Conventions
Class names should normally use the CapWords convention.

#### Example:
```python title="class.py" showLineNumbers{1} {2,3,4}
# Valid class names
class MyClass:
    pass
```

## Naming Convention Standards
Python has a set of naming conventions for different types of identifiers. These conventions are defined in PEP 8 -- Style Guide for Python Code, which is the style guide that most Python projects follow.

There are different naming styles for different types of identifiers. The following table summarizes the naming conventions for different types of identifiers:
### Camel Case
Starts each word with a capital letter except the first word. For example: `firstName`, `lastName`, `getFirstName()`, `setFirstName()`, etc.
```python title="variable.py" showLineNumbers{1} {2,3,4,5,6,7} 
    # Camel Case
    firstName = "John"
    lastName = "Doe"
    def getFirstName():
        pass
    def setFirstName():
        pass
```
### Pascal Case
Starts each word with a capital letter. For example: `FirstName`, `LastName`, `GetFirstName()`, `SetFirstName()`, etc.
```python title="variable.py" showLineNumbers{1} {2,3,4,5,6,7} 
    # Pascal Case
    FirstName = "John"
    LastName = "Doe"
    def GetFirstName():
        pass
    def SetFirstName():
        pass
```

### Snake Case
Uses underscores (`_`) between words. For example: `first_name`, `last_name`, `get_first_name()`, `set_first_name()`, etc.
```python title="variable.py" showLineNumbers{1} {2,3,4,5,6,7} 
    # Snake Case
    first_name = "John"
    last_name = "Doe"
    def get_first_name():
        pass
    def set_first_name():
        pass
```
