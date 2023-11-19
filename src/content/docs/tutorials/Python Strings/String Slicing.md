---
title: Python String Slicing
description: Learn to slice strings in Python using a step-by-step tutorial.
sidebar: 
    order: 16
---

String slicing is a way to extract a part of a string. In Python, you can slice strings using a range of indices. While slicing strings, you can also specify the step size, which makes it possible to slice only every other character, or every third character in a string.

In this tutorial, we'll learn how to use string slicing in Python. We'll also learn how to reverse a string using slicing, and how to use negative indices to slice a string.

## Array Indexing in Python

In Python, strings are ordered sequences of character data, and thus can be indexed in this way. You can access individual characters of a string using indexing and a range of characters using slicing. Strings are immutable data types, which means that once a string is created, you can't modify it.

|Words| H | e | l | l | o |   | W | o | r | l | d |
|---|---|---|---|---|---|---|---|---|---|---|---|
|Indices| 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |10 |

Let's look at some examples of indexing strings in Python.

#### Example 1: Indexing a String

```python title="strings.py" showLineNumbers{1}
# define a string
string = "Hello World"
print(string[0])
print(string[1])
```

Output:

```cmd title="command" showLineNumbers{1}
C:\Users\Your Name> python strings.py
H
e
```

In the above example, we have indexed the string at index 0. This means that we have accessed the first character of the string.


## Slicing Strings in Python

In Python, you can slice strings using a range of indices. The general syntax for slicing a string is as follows:

#### `string[start:stop:step]`

Here, `start` and `stop` are the indices of the slice, and `step` is the step size. The `start` index is inclusive, and the `stop` index is exclusive. The `step` size defaults to 1 if not provided.

Let's look at some examples of slicing strings in Python.

#### Example 1: Slicing a String

```python title="strings.py" showLineNumbers{1}
# define a string
string = "Hello World"
print(string[0:5])
```

Output:

```cmd title="command" showLineNumbers{1}
C:\Users\Your Name> python strings.py
Hello
```

In the above example, we have sliced the string from index 0 to index 5. Since the `start` index is inclusive, the character at index 0 is included in the slice. Since the `stop` index is exclusive, the character at index 5 is not included in the slice.

## Slicing a String with a Step Size

```python title="strings.py" showLineNumbers{1}
# define a string
string = "Hello World"
print(string[0:5:2])
```

Output:

```cmd title="command" showLineNumbers{1}
C:\Users\Your Name> python strings.py
Hlo
```

In the above example, we have sliced the string from index 0 to index 5 with a step size of 2. This means that we have sliced the string from index 0 to index 5, but only every other character.

## Accessing Characters using Negative Indices

In Python, you can also access characters of a string using negative indices. Negative indices start from the end of the string, and the index of the last character is -1.

|Words| H | e | l | l | o |   | W | o | r | l | d |
|---|---|---|---|---|---|---|---|---|---|---|---|
|Indices| -11 | -10 | -9 | -8 | -7 | -6 | -5 | -4 | -3 | -2 | -1 |

Let's look at some examples of accessing characters of a string using negative indices.

#### Example 1: Accessing a Character using a Negative Index

```python title="strings.py" showLineNumbers{1}
# define a string
string = "Hello World"
print(string[-1])
print(string[-2])
```

Output:

```cmd title="command" showLineNumbers{1}
C:\Users\Your Name> python strings.py
d
l
```


## Slicing a String with Negative Indices

```python title="strings.py" showLineNumbers{1}
# define a string
string = "Hello World"
print(string[-5:-2])
```

Output:

```cmd title="command" showLineNumbers{1}
C:\Users\Your Name> python strings.py
Wor
```

In the above example, we have sliced the string from index -5 to index -2. Since the `start` index is inclusive, the character at index -5 is included in the slice. Since the `stop` index is exclusive, the character at index -2 is not included in the slice.

## Slice from the Start

```python title="strings.py" showLineNumbers{1}
# define a string
string = "Hello World"
print(string[:5])
```

Output:

```cmd title="command" showLineNumbers{1}
C:\Users\Your Name> python strings.py
Hello
```

In the above example, we have sliced the string from the start to index 5. Since the `start` index is inclusive, the character at index 0 is included in the slice. Since the `stop` index is exclusive, the character at index 5 is not included in the slice.

## Slice to the End

```python title="strings.py" showLineNumbers{1}
# define a string
string = "Hello World"
print(string[6:])
```

Output:

```cmd title="command" showLineNumbers{1}
C:\Users\Your Name> python strings.py
World
```

In the above example, we have sliced the string from index 6 to the end. Since the `start` index is inclusive, the character at index 6 is included in the slice. Since the `stop` index is exclusive, the character at the end is also included in the slice.

## Reverse a String using Slicing

```python title="strings.py" showLineNumbers{1}
# define a string
string = "Hello World"
print(string[::-1])
```

Output:

```cmd title="command" showLineNumbers{1}
C:\Users\Your Name> python strings.py
dlroW olleH
```

In the above example, we have sliced the string from the start to the end with a step size of -1. This means that we have sliced the string from the start to the end, but in reverse order.