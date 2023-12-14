---
title: Access List Item
description: Learn about List in Python. How to create a list, add elements to a list, remove elements from a list, and more. How to use list comprehension in Python. How to use the built-in functions of list in Python.
sidebar: 
    order: 49
---

## Navigating Lists in Python: A Guide to Accessing List Items
In Python, lists are a versatile and commonly used data structure for storing ordered collections of items. Understanding how to access elements within a list is fundamental to working with this data structure effectively. In this guide, we'll explore the various methods and techniques for accessing list items in Python.


<!-- ```python title="math.py" showLineNumbers{1} {1,3}
import math

print(math.pi)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python math.py
3.141592653589793
``` -->

## Basics of List Indexing
List indexing refers to the process of retrieving elements from a list based on their position. In Python, list indexing starts at 0, meaning the first element is at index 0, the second at index 1, and so on. Additionally, negative indices count from the end of the list, with -1 representing the last element.

Example:
```python title="list_indexing.py" showLineNumbers{1} {1,3-7}
my_list = ['a', 'b', 'c', 'd', 'e']

print(my_list[0])
print(my_list[1])
print(my_list[2])
print(my_list[3])
```

Output:
```cmd title="command" showLineNumbers{1} {2-6}
C:\Users\username>python list_indexing.py
a
b
c
d
```

In the above example, we create a list of five elements and print the first four elements using their indices. Note that the last element is not printed because it has an index of 4, which is out of range for the list.

## Negative Indexing
As mentioned above, negative indices count from the end of the list. For example, the last element of a list can be accessed using an index of -1, the second to last with an index of -2, and so on.

Example:
```python title="list_indexing.py" showLineNumbers{1} {1,3-7}
my_list = ['a', 'b', 'c', 'd', 'e']

print(my_list[-1])
print(my_list[-2])
print(my_list[-3])
print(my_list[-4])
```

Output:
```cmd title="command" showLineNumbers{1} {2-6}
C:\Users\username>python list_indexing.py
e
d
c
b
```

In the above example, we create a list of five elements and print the last four elements using their negative indices. Note that the first element is not printed because it has an index of -5, which is out of range for the list.

## Diagram of List Indexing
The following diagram illustrates the indexing of a list with five elements:

```python title="list_indexing.py" showLineNumbers{1} {1,3-7}
my_list = ['a', 'b', 'c', 'd', 'e']
```

| Element | 'a' | 'b' | 'c' | 'd' | 'e' |
| --- | --- | --- | --- | --- | --- |
| Index | 0 | 1 | 2 | 3 | 4 |
| Index (Negative) | -5 | -4 | -3 | -2 | -1 |

