---
title: Set in Python
description: Learn about Set in Python. How to create a set, add and remove elements from a set, and other operations on a set. Set is a collection of unique elements. 
sidebar: 
    order: 58
---

## Exploring Sets in Python: A Comprehensive Guide
Sets in Python are an unordered collection of unique elements. They are a fundamental data type that provides a versatile and efficient way to work with distinct items. In this comprehensive guide, we will delve into the characteristics of sets, how to create and manipulate them, operations that can be performed on sets, and various use cases where sets shine as a data structure in Python.

## What is a Set in Python?
A set is a collection of unique elements. It is an unordered data structure that is mutable and iterable. Sets are defined by enclosing a comma-separated list of elements within curly braces `{}`. The elements in a set are immutable, but the set itself is mutable. This means that the elements of a set cannot be changed, but the set can be modified by adding or removing elements.

## Unordered Collection of Unique Elements
Sets are unordered, which means that the elements in a set do not have a defined order. This also means that sets do not support indexing or slicing operations. Sets are iterable, which means that we can iterate over the elements of a set using a `for` loop.

## Mutable and Iterable
Sets are mutable, which means that we can add or remove elements from a set. Sets are also dynamic, which means that we can add or remove elements from a set after it has been created. Sets are also heterogeneous, which means that we can have elements of different data types in a set.

<!-- ```python title="tuple.py" showLineNumbers{1} {1}
tuple = (1, 2, 3)
print(tuple)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python tuple.py
(1, 2, 3)
```

In this example, we declare a tuple of three elements and assign it to the variable `tuple`. We then print the tuple to the console. The output shows that the tuple contains three elements. -->

## Creating a Set in Python
We can create a set in Python by enclosing a comma-separated list of elements within curly braces `{}`. The elements in a set can be of different data types. The elements in a set are unique, which means that there cannot be duplicate elements in a set. If we try to create a set with duplicate elements, the duplicate elements will be removed from the set.

```python title="set.py" showLineNumbers{1} {1}
set1 = {1, 2, 3}
print(set1)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python set.py
{1, 2, 3}
```

In this example, we declare a set of three elements and assign it to the variable `set1`. We then print the set to the console. The output shows that the set contains three elements.

## Properties of Sets in Python
Sets in Python have the following properties:
- **Unordered**: The elements in a set do not have a defined order.
- **Unique**: The elements in a set are unique, which means that there cannot be duplicate elements in a set.
- **Mutable**: We can add or remove elements from a set.
- **Iterable**: We can iterate over the elements of a set using a `for` loop.
- **Dynamic**: We can add or remove elements from a set after it has been created.
- **Heterogeneous**: We can have elements of different data types in a set.
- **Unhashable**: The elements in a set must be immutable. This means that we cannot have mutable elements in a set.
- **Unindexed**: Sets do not support indexing or slicing operations.

## Declaring a Set
We can declare a set in Python by enclosing a comma-separated list of elements within curly braces `{}`. We can also declare an empty set by using the `set()` function.

```python title="set.py" showLineNumbers{1} {1}
set1 = {1, 2, 3}
print(set1)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python set.py
{1, 2, 3}
```

In this example, we declare a set of three elements and assign it to the variable `set1`. We then print the set to the console. The output shows that the set contains three elements.

### Declaring a Set with Using the `set()` Function
We can also declare a set in Python by using the `set()` function. The `set()` function takes a single argument, which is an iterable object. The elements of the iterable object are added to the set. If the iterable object contains duplicate elements, the duplicate elements are removed from the set.

```python title="set.py" showLineNumbers{1} {1}
set1 = set([1, 2, 3])
print(set1)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python set.py
{1, 2, 3}
```

In this example, we declare a set of three elements and assign it to the variable `set1`. We then print the set to the console. The output shows that the set contains three elements.

### Declaring an Empty Set
We can declare an empty set in Python by using the `set()` function without any arguments. The `set()` function returns an empty set.

```python title="set.py" showLineNumbers{1} {1}
set1 = set()
print(set1)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python set.py
set()
```

In this example, we declare an empty set and assign it to the variable `set1`. We then print the set to the console. The output shows that the set is empty.

You can also declare an empty set by using curly braces `{}`. However, this will create an empty dictionary instead of an empty set. To create an empty set, you must use the `set()` function.

```python title="set.py" showLineNumbers{1} {1}
set1 = {}
print(set1)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python set.py
{}
```

In this example, we declare an empty dictionary and assign it to the variable `set1`. We then print the dictionary to the console. The output shows that the dictionary is empty.

### Declaring a Set with Elements
We can declare a set in Python by enclosing a comma-separated list of elements within curly braces `{}`. The elements in a set can be of different data types. The elements in a set are unique, which means that there cannot be duplicate elements in a set. If we try to create a set with duplicate elements, the duplicate elements will be removed from the set.

```python title="set.py" showLineNumbers{1} {1}
set1 = {1, 2, 3}
print(set1)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python set.py
{1, 2, 3}
```

In this example, we declare a set of three elements and assign it to the variable `set1`. We then print the set to the console. The output shows that the set contains three elements.

### Declaring a Set with Duplicate Elements
We can declare a set with duplicate elements in Python by enclosing a comma-separated list of elements within curly braces `{}`. 

```python title="set.py" showLineNumbers{1} {1}
set1 = {1, 2, 3, 3, 2, 1}
print(set1)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python set.py
{1, 2, 3}
```

In this example, we declare a set of six elements and assign it to the variable `set1`. We then print the set to the console. The output shows that the set contains three elements. The duplicate elements have been removed from the set.

### Declaring a Set with Elements of Different Data Types
We can declare a set in Python with elements of different data types. The elements in a set can be of any data type, including integers, floats, strings, tuples, lists, dictionaries, and other sets.

```python title="set.py" showLineNumbers{1} {1}
set1 = {1, 2.0, "three", (4, 5), [6, 7], {8, 9}}
print(set1)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python set.py
{1, 2.0, 'three', (4, 5), [6, 7], {8, 9}}
```

In this example, we declare a set of six elements and assign it to the variable `set1`. We then print the set to the console. The output shows that the set contains elements of different data types.

### Declaring a Set with Mutable Elements
We can declare a set in Python with mutable elements. The elements in a set must be immutable, which means that we cannot have mutable elements in a set. If we try to create a set with mutable elements, we will get an error.

```python title="set.py" showLineNumbers{1} {1}
set1 = {[1, 2], (3, 4), {5, 6}}
print(set1)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python set.py
Traceback (most recent call last):
  File "set.py", line 1, in <module>
    set1 = {[1, 2], (3, 4), {5, 6}}
TypeError: unhashable type: 'list'
```

In this example, we try to declare a set with three elements. The first element is a list, the second element is a tuple, and the third element is a set. Since the first element is a list, which is mutable, we get an error.

### Declaring a Set with Multiple Lines
We can declare a set in Python with multiple lines by enclosing a comma-separated list of elements within curly braces `{}`. We can also declare a set with multiple lines by using the `set()` function.

```python title="set.py" showLineNumbers{1} {1-5}
set1 = {
    1,
    2,
    3
}
print(set1)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python set.py
{1, 2, 3}
```

In this example, we declare a set of three elements and assign it to the variable `set1`. We then print the set to the console. The output shows that the set contains three elements.

### Declaring a Set with Multiple Lines Using the `set()` Function
We can also declare a set in Python with multiple lines by using the `set()` function. The `set()` function takes a single argument, which is an iterable object. The elements of the iterable object are added to the set. If the iterable object contains duplicate elements, the duplicate elements are removed from the set.

```python title="set.py" showLineNumbers{1} {1-5}
set1 = set([
    1,
    2,
    3
])
print(set1)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python set.py
{1, 2, 3}
```

In this example, we declare a set of three elements and assign it to the variable `set1`. We then print the set to the console. The output shows that the set contains three elements.

### Declaring an Set with Range of Numbers
We can declare a set in Python with a range of numbers by using the `range()` function. The `range()` function takes three arguments: `start`, `stop`, and `step`. The `start` argument is the first number in the range. The `stop` argument is the last number in the range. The `step` argument is the number of steps between each number in the range. The `step` argument is optional, and if it is not specified, it defaults to `1`.

```python title="set.py" showLineNumbers{1} {1}
set1 = set(range(1, 10, 2))
print(set1)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python set.py
{1, 3, 5, 7, 9}
```

In this example, we declare a set of five elements and assign it to the variable `set1`. We then print the set to the console. The output shows that the set contains five elements.

### Declaring a Set using list comprehension
We can declare a set in Python using list comprehension.

:::note
List comprehension is a way to create a list from another list or iterable object. It is a concise way to create a list. List comprehension is a powerful tool that can be used to create lists in a single line of code. It is a great way to create lists in Python.
:::

```python title="set.py" showLineNumbers{1} {1}
set1 = {x for x in range(1, 10, 2)}
print(set1)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python set.py
{1, 3, 5, 7, 9}
```

In this example, we declare a set of five elements and assign it to the variable `set1`. We then print the set to the console. The output shows that the set contains five elements.

### Declaring a Set using List
We can declare a set in Python using a list.

```python title="set.py" showLineNumbers{1} {1-2}
list1 = [1, 2, 3]
set1 = set(list1)
print(set1)
```

Output:

```cmd title="command" showLineNumbers{1} {3}
C:\Users\username>python set.py
{1, 2, 3}
```

In this example, we declare a list of three elements and assign it to the variable `list1`. We then declare a set using the list and assign it to the variable `set1`. We then print the set to the console. The output shows that the set contains three elements.

### Declaring a Set using Tuple
We can declare a set in Python using a tuple.

```python title="set.py" showLineNumbers{1} {1-2}
tuple1 = (1, 2, 3)
set1 = set(tuple1)
print(set1)
```

Output:

```cmd title="command" showLineNumbers{1} {3}
C:\Users\username>python set.py
{1, 2, 3}
```

In this example, we declare a tuple of three elements and assign it to the variable `tuple1`. We then declare a set using the tuple and assign it to the variable `set1`. We then print the set to the console. The output shows that the set contains three elements.

### Declaring a Nested Set
We can declare a nested set in Python by enclosing a comma-separated list of elements within curly braces `{}`. The elements in a nested set can be of different data types. The elements in a nested set are unique, which means that there cannot be duplicate elements in a nested set. If we try to create a nested set with duplicate elements, the duplicate elements will be removed from the nested set.

```python title="set.py" showLineNumbers{1} {1}
set1 = {1, 2, 3, {4, 5, 6}}
print(set1)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python set.py
Traceback (most recent call last):
  File "set.py", line 1, in <module>
    set1 = {1, 2, 3, {4, 5, 6}}
TypeError: unhashable type: 'set'
```

In this example, we try to declare a nested set with four elements. The first element is an integer, the second element is a float, the third element is a string, and the fourth element is a nested set. Since the fourth element is a nested set, which is mutable, we get an error.

