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

## Types of Sets in Python
There are three types of sets in Python: 
- **Mutable Set**: A mutable set is a set that can be modified after it has been created. We can add or remove elements from a mutable set. We can also change the elements of a mutable set.
- **Immutable Set**: An immutable set is a set that cannot be modified after it has been created. We cannot add or remove elements from an immutable set. We also cannot change the elements of an immutable set.
- **Frozen Set**: A frozen set is a set that cannot be modified after it has been created. We cannot add or remove elements from a frozen set. We also cannot change the elements of a frozen set.
- **Dynamic Set**: A dynamic set is a set that can be modified after it has been created. We can add or remove elements from a dynamic set. We can also change the elements of a dynamic set.
- **Static Set**: A static set is a set that cannot be modified after it has been created. We cannot add or remove elements from a static set. We also cannot change the elements of a static set.
- **Heterogeneous Set**: A heterogeneous set is a set that can contain elements of different data types. The elements in a heterogeneous set can be of any data type, including integers, floats, strings, tuples, lists, dictionaries, and other sets.
- **Homogeneous Set**: A homogeneous set is a set that can contain elements of the same data type. The elements in a homogeneous set must be of the same data type, including integers, floats, strings, tuples, lists, dictionaries, and other sets.
- **Unordered Set**: An unordered set is a set that does not have a defined order. The elements in an unordered set do not have a defined order. We cannot access the elements of an unordered set by index.
- **Ordered Set**: An ordered set is a set that has a defined order. The elements in an ordered set have a defined order. We can access the elements of an ordered set by index.

## Length of a Set
We can get the length of a set in Python by using the `len()` function. The `len()` function takes a single argument, which is a set. The `len()` function returns the number of elements in the set.

```python title="set.py" showLineNumbers{1} {1-2}
set1 = {1, 2, 3}
print(len(set1))
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python set.py
3
```

In this example, we declare a set of three elements and assign it to the variable `set1`. We then print the length of the set to the console. The output shows that the set contains three elements.

## Accessing Elements of a Set
We can access the elements of a set in Python by using the `for` loop. The `for` loop takes a single argument, which is a set. The `for` loop iterates over the elements of the set and executes the code block for each element.

```python title="set.py" showLineNumbers{1} {1-3}
set1 = {1, 2, 3}
for x in set1:
    print(x)
```

Output:

```cmd title="command" showLineNumbers{1} {2-4}
C:\Users\username>python set.py
1
2
3
```

In this example, we declare a set of three elements and assign it to the variable `set1`. We then iterate over the elements of the set and print each element to the console. The output shows that the set contains three elements.

:::caution
Sets are unordered, which means that the elements in a set do not have a defined order. This also means that sets do not support indexing or slicing operations.
:::

:::danger
Accessing elements of a set by index is not supported. If you try to access an element of a set by index, you will get an error.

```python title="set.py" showLineNumbers{1} {1}
set1 = {1, 2, 3}
print(set1[0])
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python set.py
Traceback (most recent call last):
  File "set.py", line 2, in <module>
    print(set1[0])
TypeError: 'set' object is not subscriptable
```

In this example, we try to access the first element of a set by index. Since sets do not support indexing or slicing operations, we get an error.

:::

## Conclusion
In this comprehensive guide, we have explored the characteristics of sets, how to create and manipulate them, operations that can be performed on sets, and various use cases where sets shine as a data structure in Python. We have also explored the different types of sets in Python, including mutable sets, immutable sets, frozen sets, dynamic sets, static sets, heterogeneous sets, homogeneous sets, unordered sets, and ordered sets. We have also explored how to get the length of a set and how to access the elements of a set. We hope that you now have a better understanding of sets in Python and how to use them in your programs. For more information on sets in Python, check out the [official documentation](https://docs.python.org/3/library/stdtypes.html#set-types-set-frozenset). For more tutorials like this check Python Central Hub.