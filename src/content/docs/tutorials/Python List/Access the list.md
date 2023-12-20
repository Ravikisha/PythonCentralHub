---
title: Access List Item
description: Learn about List in Python. How to create a list, add elements to a list, remove elements from a list, and more. How to use list comprehension in Python. How to use the built-in functions of list in Python.
sidebar: 
    order: 49
---

## Navigating Lists in Python: A Guide to Accessing List Items
In Python, lists are a versatile and commonly used data structure for storing ordered collections of items. Understanding how to access elements within a list is fundamental to working with this data structure effectively. In this guide, we'll explore the various methods and techniques for accessing list items in Python.


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


## Accessing Multidimensional Lists
Multidimensional lists are lists that contain other lists as elements. In Python, multidimensional lists are accessed using multiple indices, with each index representing a different dimension of the list.

Example:
```python title="multidimensional_list.py" showLineNumbers{1} {1,3-7}
my_list = [['a', 'b', 'c'], ['d', 'e', 'f'], ['g', 'h', 'i']]

print(my_list[0][0])
print(my_list[1][1])
print(my_list[2][2])
```

Output:
```cmd title="command" showLineNumbers{1} {2-4}
C:\Users\username>python multidimensional_list.py
a
e
i
```

In the above example, we create a multidimensional list of three elements, each of which is a list of three elements. We then print the first element of the first list, the second element of the second list, and the third element of the third list.

:::note
Note that multidimensional lists can be nested to any depth, and each dimension is accessed using a separate index.

### Diagram of Multidimensional List Indexing

|Index|0|1|2|
|---|---|---|---|
|0|'a'|'b'|'c'|
|1|'d'|'e'|'f'|
|2|'g'|'h'|'i'|

You can also use negative indices to access multidimensional lists. For example, the last element of the last list can be accessed using an index of -1 for the first dimension and an index of -1 for the second dimension.

|Index|-3|-2|-1|
|---|---|---|---|
|-3|'a'|'b'|'c'|
|-2|'d'|'e'|'f'|
|-1|'g'|'h'|'i'|

```python title="multidimensional_list.py" showLineNumbers{1} {1,3-7}
my_list = [['a', 'b', 'c'], ['d', 'e', 'f'], ['g', 'h', 'i']]

print(my_list[-1][-1])
print(my_list[-2][-2])
print(my_list[-3][-3])
```

Output:
```cmd title="command" showLineNumbers{1} {2-4}
C:\Users\username>python multidimensional_list.py
i
e
a
```

:::

## Accessing List Slices
List slices are a way of accessing a subset of a list. In Python, list slices are created using the syntax `list[start:stop]`, where `start` is the index of the first element to include in the slice and `stop` is the index of the first element to exclude from the slice. If `start` is omitted, it defaults to 0, and if `stop` is omitted, it defaults to the length of the list.

**Syntax**:
```python title="syntax.py" showLineNumbers{1} {1,3-4}
list[start:stop]
```

Example:
```python title="list_slice.py" showLineNumbers{1} {1,3-4}
my_list = ['a', 'b', 'c', 'd', 'e']

print(my_list[1:3])
```

Output:
```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python list_slice.py
['b', 'c']
```

In the above example, we create a list of five elements and print a slice of the list from index 1 to index 3. Note that the element at index 3 is not included in the slice.

### Omitting the Start Index
If the start index is omitted, it defaults to 0. This means that the slice will include all elements from the beginning of the list up to, but not including, the element at the stop index.

Example:
```python title="list_slice.py" showLineNumbers{1} {1,3-4}
my_list = ['a', 'b', 'c', 'd', 'e']

print(my_list[:3])
```

Output:
```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python list_slice.py
['a', 'b', 'c']
```

In the above example, we create a list of five elements and print a slice of the list from index 0 to index 3. Note that the element at index 3 is not included in the slice.

`my_list[:3]` is equivalent to `my_list[0:3]`.

### Omitting the Stop Index
If the stop index is omitted, it defaults to the length of the list. This means that the slice will include all elements from the start index to the end of the list.

Example:
```python title="list_slice.py" showLineNumbers{1} {1,3-4}
my_list = ['a', 'b', 'c', 'd', 'e']

print(my_list[2:])
```

Output:
```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python list_slice.py
['c', 'd', 'e']
```

In the above example, we create a list of five elements and print a slice of the list from index 2 to the end of the list.

`my_list[2:]` is equivalent to `my_list[2:len(my_list)]`.

### Ommiting Both Indices
If both the start and stop indices are omitted, the slice will include all elements in the list.

Example:
```python title="list_slice.py" showLineNumbers{1} {1,3-4}
my_list = ['a', 'b', 'c', 'd', 'e']

print(my_list[:])
```

Output:
```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python list_slice.py
['a', 'b', 'c', 'd', 'e']
```

In the above example, we create a list of five elements and print a slice of the list from index 0 to the end of the list.

### Slicing with a Negative Start Index
If the start index is negative, it will be interpreted as an offset from the end of the list. This means that the slice will include all elements from the element at the start index to the end of the list.

Example:
```python title="list_slice.py" showLineNumbers{1} {1,3-4}
my_list = ['a', 'b', 'c', 'd', 'e']

print(my_list[-3:])
```

Output:
```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python list_slice.py
['c', 'd', 'e']
```

In the above example, we create a list of five elements and print a slice of the list from index -3 to the end of the list.

### Slicing with a Negative Stop Index
If the stop index is negative, it will be interpreted as an offset from the end of the list. This means that the slice will include all elements from the beginning of the list up to, but not including, the element at the stop index.

Example:
```python title="list_slice.py" showLineNumbers{1} {1,3-4}
my_list = ['a', 'b', 'c', 'd', 'e']

print(my_list[:-3])
```

Output:
```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python list_slice.py
['a', 'b']
```

In the above example, we create a list of five elements and print a slice of the list from index 0 to index -3. Note that the element at index -3 is not included in the slice.

### Slicing with a Negative Start and Stop Index
If both the start and stop indices are negative, they will be interpreted as offsets from the end of the list. This means that the slice will include all elements from the element at the start index to the element at the stop index.

Example:
```python title="list_slice.py" showLineNumbers{1} {1,3-4}
my_list = ['a', 'b', 'c', 'd', 'e']

print(my_list[-3:-1])
```

Output:
```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python list_slice.py
['c', 'd']
```

In the above example, we create a list of five elements and print a slice of the list from index -3 to index -1. Note that the element at index -1 is not included in the slice.

### Slice Step
The slice step is an optional third argument that specifies the number of elements to skip between each element in the slice. The default value is 1, meaning that each element in the slice will be included in the result. A value of 2 means that every other element will be included, and so on.

**Syntax**:
```python title="syntax.py" showLineNumbers{1} {1,3-4}
list[start:stop:step]
```

Example:
```python title="list_slice.py" showLineNumbers{1} {1,3-4}
my_list = ['a', 'b', 'c', 'd', 'e']

print(my_list[0:5:2])
```

Output:
```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python list_slice.py
['a', 'c', 'e']
```

In the above example, we create a list of five elements and print a slice of the list from index 0 to index 5 with a step of 2. This means that every other element will be included in the slice.

### Accessing List Items with a Negative Step
If the step is negative, the slice will be created in reverse order. This means that the start index must be greater than the stop index.

Example:
```python title="list_slice.py" showLineNumbers{1} {1,3-4}
my_list = ['a', 'b', 'c', 'd', 'e']

print(my_list[4:0:-1])
```

Output:
```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python list_slice.py
['e', 'd', 'c', 'b']
```

In the above example, we create a list of five elements and print a slice of the list from index 4 to index 0 with a step of -1. This means that the slice will be created in reverse order.

### Accessing List Items with a Negative Start Index and Positive Stop Index
If the start index is negative and the stop index is positive, the slice will be created in reverse order. This means that the start index must be greater than the stop index.

Example:
```python title="list_slice.py" showLineNumbers{1} {1,3-4}
my_list = ['a', 'b', 'c', 'd', 'e']

print(my_list[-1:3:-1])
```

Output:
```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python list_slice.py
['e', 'd', 'c']
```

In the above example, we create a list of five elements and print a slice of the list from index -1 to index 3 with a step of -1. This means that the slice will be created in reverse order.

## Conclusion
In this guide, we explored the various methods and techniques for accessing list items in Python. We also learned about list indexing, negative indexing, multidimensional lists, and list slices. Now that you understand how to access list items in Python, you can start working with lists more effectively in your programs. For more information on lists, check out Python's [official documentation](https://docs.python.org/3/tutorial/datastructures.html#more-on-lists).