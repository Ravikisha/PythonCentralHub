---
title: Strings in Python
description: Learn how to use strings in Python. This tutorial covers the basics of strings, including string indexing, string methods, and string formatting.
sidebar: 
    order: 15
---

## Mastering Python Strings

A string is a sequence of characters enclosed in quotation marks. In Python, strings are ordered sequences of character data, and thus can be indexed in this way. You can access individual characters of a string using indexing and a range of characters using slicing. Strings are immutable data types, which means that once a string is created, you can't modify it.

In this tutorial, we'll learn everything about Python strings, from how to create and format strings to the different methods you can use to manipulate and work with string data.

## Creating Strings

In Python, you can create strings by enclosing a sequence of characters within a pair of single or double quotes. For example:

```python title="strings.py" showLineNumbers{1}
# Single word
print('hello')

# Entire phrase
print('This is also a string')

# We can also use double quote
print("String built with double quotes")
```

Output:

```cmd title="command" showLineNumbers{1} {2-4}
C:\Users\Your Name> python strings.py
hello
This is also a string
String built with double quotes
```

## String Type

In Python, string is an object of type `str` class. You can verify this with the `type()` function:

```python title="strings.py" showLineNumbers{1}
a = "Hello"
print(type(a))
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python strings.py
<class 'str'>
```

## Assign String to a Variable

Assigning a string to a variable is as simple as assigning a value to a variable. For example:

```python title="strings.py" showLineNumbers{1}
# You can use single or double quotes
a = "Hello" 
b = 'Hello'
print(a)
print(b)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\Your Name> python strings.py
Hello
Hello
```

## Multiline Strings

In Python, you can assign a multiline string to a variable by using three quotes:

```python title="strings.py" showLineNumbers{1}
a = """Lorem ipsum dolor sit amet,
consectetur adipiscing elit,
sed do eiusmod tempor incididunt
ut labore et dolore magna aliqua."""

# You can also use three single quotes:
b = '''Lorem ipsum dolor sit amet,
consectetur adipiscing elit,
sed do eiusmod tempor incididunt
ut labore et dolore magna aliqua.'''

print(a)
print("------")
print(b)
```

Output:

```cmd title="command" showLineNumbers{1} {2-9}
C:\Users\Your Name> python strings.py
Lorem ipsum dolor sit amet,
consectetur adipiscing elit,
sed do eiusmod tempor incididunt
ut labore et dolore magna aliqua.
------
Lorem ipsum dolor sit amet,
consectetur adipiscing elit,
sed do eiusmod tempor incididunt
ut labore et dolore magna aliqua.
```

## Strings Arrays

In Python, strings are arrays of bytes representing Unicode characters. A string can be thought of as an array of characters. Like other programming languages, Python strings are indexed starting from 0. For example:

```python title="strings.py" showLineNumbers{1}
a = "Hello, World!"
print(a[1])
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python strings.py
e
```

## Length of a String

To get the length of a string, use the `len()` function:

```python title="strings.py" showLineNumbers{1}
a = "Hello, World!"
print(len(a))
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python strings.py
13
```

## Going through a String with a Loop

Strings are iterable objects, which means you can iterate through each character of the string using a `for` loop. For example:

```python title="strings.py" showLineNumbers{1}
for x in "cricket":
  print(x)
```

Output:

```cmd title="command" showLineNumbers{1} {2-8}
C:\Users\Your Name> python strings.py
c
r
i
c
k
e
t
```
:::note 
You can also use a `while` loop to iterate through a string.
```python title="strings.py" showLineNumbers{1}
i = 0
while i < len(a):
  print(a[i])
  i = i + 1
```
:::
:::tip
We are going to learn more about loops in the next tutorial. [Click here](/docs/tutorials/loops) to learn more about loops.
:::

## Finding a String in a String

To check if a certain phrase or character is present in a string, we can use the keyword `in`.

```python title="strings.py" showLineNumbers{1}
txt = "Nothing is impossible, you need to believe"
print("impossible" in txt)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python strings.py
True
```

## Not Finding a String in a String

To check if a certain phrase or character is not present in a string, we can use the keyword `not in`.

```python title="strings.py" showLineNumbers{1}
txt = "Nothing is impossible, you need to believe"
print("possible" not in txt)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python strings.py
True
```

## Conclusion
In this tutorial, we learned how to create strings, assign strings to variables, and access string characters using indexing and slicing. We also learned how to get the length of a string, iterate through a string using a loop, and check if a string contains a certain phrase or character. In the next tutorial, we'll learn how to format strings in Python. For more information on strings, check out the [official Python documentation](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str). For more tutorials, Visit Python Central Hub.