---
title: Enums in Python
description: Learn about Enums in Python. Enum is a class in Python for creating enumerations, which are a set of symbolic names (members) bound to unique, constant values.
sidebar: 
    order: 96
---

# Enums in Python : Enumerate Your Values
Enums are a way to create a set of symbolic names (members) bound to unique, constant values. They are a way to define a set of named constants. Enums are defined using the `enum` module. Enumerations are created using classes. Enums have names and values associated with them. Enums are defined by creating a new class that inherits from `Enum`. Enums can be iterated over. Enums can be compared using `==` and `is`.

## Syntax
The syntax for creating an Enum in Python is as follows:

```python title="Enum Syntax" showLineNumbers{1} {1, 3-7}
from enum import Enum

class EnumName(Enum):
    MEMBER1 = value1
    MEMBER2 = value2
    MEMBER3 = value3
    ...
```

In the above syntax:
- `EnumName` is the name of the Enum.
- `MEMBER1`, `MEMBER2`, `MEMBER3`, etc. are the members of the Enum.
- `value1`, `value2`, `value3`, etc. are the values associated with the members.

## Creating Enums
To create an Enum, you need to import the `Enum` class from the `enum` module. Then, you can create a new class that inherits from `Enum`. Each member of the Enum is defined as a class attribute. The value of the member is passed as an argument to the `Enum` constructor. The value of the member can be any type, such as an integer, string, or float.

```python title="Enums in Python" showLineNumbers{1}
from enum import Enum

class Color(Enum):
    RED = 1
    GREEN = 2
    BLUE = 3
```

In the above code:
- `Color` is the name of the Enum.
- `RED`, `GREEN`, and `BLUE` are the members of the Enum.
- `1`, `2`, and `3` are the values associated with the members.
- The members of the Enum are accessed using the dot notation, e.g., `Color.RED`, `Color.GREEN`, `Color.BLUE`.
- The members of the Enum can be compared using `==` and `is`.

## Iterating Over Enums
Enums can be iterated over using a `for` loop. When you iterate over an Enum, you get the members of the Enum.

```python title="Iterating Over Enums" showLineNumbers{1}
from enum import Enum

class Color(Enum):
    RED = 1
    GREEN = 2
    BLUE = 3

for color in Color:
    print(color)
```

In the above code, the output will be:

```cmd title="Output" showLineNumbers{1}
C:/Users/username/desktop>python enum.py
Color.RED
Color.GREEN
Color.BLUE
```

## Comparing Enums
Enums can be compared using the `==` and `is` operators. When you compare two Enums using the `==` operator, it compares the values of the Enums. When you compare two Enums using the `is` operator, it compares the memory addresses of the Enums.

```python title="Comparing Enums" showLineNumbers{1}
from enum import Enum

class Color(Enum):
    RED = 1
    GREEN = 2
    BLUE = 3

color1 = Color.RED
color2 = Color.RED

print(color1 == color2) # Output: True
print(color1 is color2) # Output: True
```

In the above code, the output will be:

```cmd title="Output" showLineNumbers{1}
C:/Users/username/desktop>python enum.py
True
True
```

## Enum Members
You can access the members of an Enum using the dot notation. The members of an Enum are instances of the Enum class.

```python title="Accessing Enum Members" showLineNumbers{1}
from enum import Enum

class Color(Enum):
    RED = 1
    GREEN = 2
    BLUE = 3

print(Color.RED) 
print(Color.GREEN)
print(Color.BLUE)
```

In the above code, the output will be:

```cmd title="Output" showLineNumbers{1}
C:/Users/username/desktop>python enum.py
Color.RED
Color.GREEN
Color.BLUE
```

:::danger
Enums are not hashable, so they cannot be used as keys in dictionaries. you can't assign same value to different members of Enum.

```python title="Enums are not hashable" showLineNumbers{1}
from enum import Enum

class Color(Enum):
    RED = 1
    GREEN = 1
    BLUE = 3
```

The above code will raise a `ValueError` as `GREEN` and `RED` have the same value.

```cmd title="Output" showLineNumbers{1}
C:/Users/username/desktop>python enum.py
Traceback (most recent call last):
  File "enum.py", line 5, in <module>
    class Color(Enum):
  File "C:\Users\username\AppData\Local\Programs\Python\Python39\lib\enum.py", line 225, in __new__
    raise ValueError("%r is a duplicate of %r" % (alias, name))
ValueError: duplicate values found in <enum 'Color'>: GREEN -> RED
```
:::

:::tip
Alternatively, you can use different syntax to create Enum members with the same value.

```python title="Enums with same value" showLineNumbers{1}
from enum import Enum

colors = Enum('colors', 'RED GREEN BLUE')

print(colors.RED)
print(colors.GREEN)
print(colors.BLUE)
```

The above code will output:

```cmd title="Output" showLineNumbers{1}
C:/Users/username/desktop>python enum.py
colors.RED
colors.GREEN
colors.BLUE
```
:::

### Accessing Enum Members
You can access the members of an Enum using the dot notation. The members of an Enum are instances of the Enum class.

```python title="Accessing Enum Members" showLineNumbers{1}
from enum import Enum

class Color(Enum):
    RED = 1
    GREEN = 2
    BLUE = 3

currentColor = Color.RED
print(type(currentColor))
print(currentColor.name)
print(currentColor.value)
```

In the above code, the output will be:

```cmd title="Output" showLineNumbers{1}
C:/Users/username/desktop>python enum.py
<enum 'Color'>
RED
1
```

In the above code:
- `currentColor` is an instance of the `Color` Enum.
- `currentColor.name` returns the name of the Enum member.
- `currentColor.value` returns the value of the Enum member.

### Accessing Enum Members using Iteration
You can access the members of an Enum using iteration. When you iterate over an Enum, you get the members of the Enum.

```python title="Accessing Enum Members using Iteration" showLineNumbers{1}
from enum import Enum

class Color(Enum):
    RED = 1
    GREEN = 2
    BLUE = 3

for color in Color:
    print(color.name, color.value)
```

In the above code, the output will be:

```cmd title="Output" showLineNumbers{1}
C:/Users/username/desktop>python enum.py
RED 1
GREEN 2
BLUE 3
```

### A Real-World Example
Here is a real-world example of using Enums in Python. In this example, we define an Enum called `Weekday` that represents the days of the week. We then create a function that takes a `Weekday` Enum as an argument and prints the name of the day.

```python title="Real-World Example" showLineNumbers{1}
from enum import Enum

class Weekday(Enum):
    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    SATURDAY = 6
    SUNDAY = 7

def print_day(day):
    print(day.name)

print_day(Weekday.MONDAY)
print_day(Weekday.FRIDAY)
```

In the above code, the output will be:

```cmd title="Output" showLineNumbers{1}
C:/Users/username/desktop>python enum.py
MONDAY
FRIDAY
```

## Conclusion
In this tutorial, you learned about Enums in Python. Enums are a way to create a set of symbolic names (members) bound to unique, constant values. Enums are defined using the `enum` module. Enums are created using classes. Enums have names and values associated with them. Enums can be iterated over. Enums can be compared using `==` and `is`. For more information on Enums, you can refer to the [official documentation](https://docs.python.org/3/library/enum.html). For more tutorials on Python Central Hub.