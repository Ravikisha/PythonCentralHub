---
title: Tuple in Python
description: Learn about Tuple in Python. How to create a tuple, tuple methods, tuple operations, and tuple comprehension. How to use tuple in Python. How to convert a tuple to a list and vice versa.
sidebar: 
    order: 52
---

## Understanding Tuples in Python: A Comprehensive Guide
Tuples are a versatile and fundamental data type in Python. Similar to lists, tuples allow you to store multiple items in a single variable. However, there are crucial differences between the two. In this comprehensive guide, we will explore what tuples are, how to create and manipulate them, their characteristics, use cases, and why they are an essential component of Python programming.

## What is a Tuple?
A tuple is an ordered, immutable collection of elements in Python. Immutable means that once a tuple is created, its contents cannot be changed, added, or removed. This distinguishes tuples from lists, which are mutable.

## Creating a Tuple
Tuples are created by enclosing a sequence of elements in parentheses `()` and separating each element with a comma `,`. For example, the following code creates a tuple of three elements:


```python title="tuple.py" showLineNumbers{1} {1}
tuple = (1, 2, 3)
print(tuple)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python tuple.py
(1, 2, 3)
```

In this example, we declare a tuple of three elements and assign it to the variable `tuple`. We then print the tuple to the console. The output shows that the tuple contains three elements.

## Properties of Tuples
Tuples have the following properties:
- **Tuples are ordered**: The order of elements in a tuple is preserved. This means that the elements in a tuple are stored in a specific order, and that order will not change unless the tuple is modified.
- **Tuples are immutable**: Once a tuple is created, its contents cannot be changed, added, or removed. This means that you cannot modify, add, or remove elements from a tuple.
- **Tuples can contain duplicate elements**: Tuples can contain duplicate elements. This means that a tuple can contain the same element more than once.
- **Tuples can contain elements of different data types**: Tuples can contain elements of different data types. This means that a tuple can contain elements of type `int`, `float`, `str`, `bool`, etc.
- **Tuples can be nested**: Tuples can contain other tuples. This means that a tuple can contain a tuple as an element.
- **Tuples can be empty**: Tuples can be empty. This means that a tuple can contain zero elements.
- **Tuples are iterable**: Tuples can be iterated over using a `for` loop. This means that you can use a `for` loop to iterate over the elements in a tuple.
- **Tuples are hashable**: Tuples are hashable. This means that you can use a tuple as a key in a dictionary or as an element in a set.
- **Tuples are comparable**: Tuples can be compared using the comparison operators `==`, `!=`, `>`, `>=`, `<`, and `<=`. This means that you can use these operators to compare tuples.
- **Tuples are not sortable**: Tuples cannot be sorted. This means that you cannot use the `sorted()` function to sort a tuple.
- **Tuples are dynamic**: Tuples can be modified after they are created. This means that you can modify, add, or remove elements from a tuple after it is created.
- **Tuples are zero-indexed**: The first element in a tuple has an index of `0`. This means that the first element in a tuple is at index `0`, the second element is at index `1`, and so on.

## Declaring a Tuple
Tuples are declared using the `tuple()` function. The `tuple()` function takes a single argument, which is a sequence of elements. The elements in the sequence are converted to a tuple and returned.

### Declaring an Empty Tuple
An empty tuple can be declared using the `tuple()` function with no arguments. The following code declares an empty tuple:

```python title="empty_tuple.py" showLineNumbers{1} {1}
empty_tuple = tuple()
print(empty_tuple)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python empty_tuple.py
()
```

In this example, we declare an empty tuple using the `tuple()` function with no arguments. We then print the tuple to the console. The output shows that the tuple is empty.

You can also declare an empty tuple using the `()` syntax. The following code declares an empty tuple using the `()` syntax:

```python title="empty_tuple.py" showLineNumbers{1} {1}
empty_tuple = ()
print(empty_tuple)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python empty_tuple.py
()
```

In this example, we declare an empty tuple using the `()` syntax. We then print the tuple to the console. The output shows that the tuple is empty.

### Declaring a Tuple with Elements
A tuple with elements can be declared using the `tuple()` function with a sequence of elements as an argument. The following code declares a tuple with three elements:

```python title="tuple.py" showLineNumbers{1} {1}
data = tuple([1, 2, 3])
print(data)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python tuple.py
(1, 2, 3)
```

In this example, we declare a tuple with three elements using the `tuple()` function with a sequence of elements as an argument. We then print the tuple to the console. The output shows that the tuple contains three elements.

You can also declare a tuple with elements using the `()` syntax. The following code declares a tuple with three elements using the `()` syntax:

```python title="tuple.py" showLineNumbers{1} {1}
data = (1, 2, 3)
print(data)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python tuple.py
(1, 2, 3)
```

In this example, we declare a tuple with three elements using the `()` syntax. We then print the tuple to the console. The output shows that the tuple contains three elements.

### Declaring a Tuple with Elements of Different Data Types
A tuple with elements of different data types can be declared using the `tuple()` function with a sequence of elements as an argument. The following code declares a tuple with three elements of different data types:

```python title="tuple.py" showLineNumbers{1} {1}
data = tuple([1, 2.0, "three"])
print(data)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python tuple.py
(1, 2.0, 'three')
```

In this example, we declare a tuple with three elements of different data types using the `tuple()` function with a sequence of elements as an argument. We then print the tuple to the console. The output shows that the tuple contains three elements of different data types.

You can also declare a tuple with elements of different data types using the `()` syntax. The following code declares a tuple with three elements of different data types using the `()` syntax:

```python title="tuple.py" showLineNumbers{1} {1}
data = (1, 2.0, "three")
print(data)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python tuple.py
(1, 2.0, 'three')
```

In this example, we declare a tuple with three elements of different data types using the `()` syntax. We then print the tuple to the console. The output shows that the tuple contains three elements of different data types.


### Declaring a Tuple with Duplicate Elements
A tuple with duplicate elements can be declared using the `tuple()` function with a sequence of elements as an argument. The following code declares a tuple with three elements, two of which are duplicates:

```python title="tuple.py" showLineNumbers{1} {1}
data = tuple([1, 2, 2])
print(data)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python tuple.py
(1, 2, 2)
```

In this example, we declare a tuple with three elements, two of which are duplicates, using the `tuple()` function with a sequence of elements as an argument. We then print the tuple to the console. The output shows that the tuple contains three elements, two of which are duplicates.

### Declaring a Tuple with Multiple Lines
A tuple with multiple lines can be declared using the `tuple()` function with a sequence of elements as an argument. The following code declares a tuple with three elements on multiple lines:

```python title="tuple.py" showLineNumbers{1} {1}
data = tuple([
    1,
    2,
    3
])
print(data)
```

Output:

```cmd title="command" showLineNumbers{1} {4}
C:\Users\username>python tuple.py
(1, 2, 3)
```

In this example, we declare a tuple with three elements on multiple lines using the `tuple()` function with a sequence of elements as an argument. We then print the tuple to the console. The output shows that the tuple contains three elements.

### Declaring a Tuple with a Single Element
A tuple with a single element can be declared using the `tuple()` function with a sequence of elements as an argument. The following code declares a tuple with a single element:

```python title="tuple.py" showLineNumbers{1} {1}
data = tuple([1])
print(data)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python tuple.py
(1,)
```

In this example, we declare a tuple with a single element using the `tuple()` function with a sequence of elements as an argument. We then print the tuple to the console. The output shows that the tuple contains a single element.

### Declaring a Tuple with a Range of Numbers
A tuple with a range of numbers can be declared using the `tuple()` function with a sequence of elements as an argument. The following code declares a tuple with a range of numbers:

```python title="tuple.py" showLineNumbers{1} {1}
data = tuple(range(1, 4))
print(data)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python tuple.py
(1, 2, 3)
```

In this example, we declare a tuple with a range of numbers using the `tuple()` function with a sequence of elements as an argument. We then print the tuple to the console. The output shows that the tuple contains a range of numbers.

### Declaring a Tuple with a Range of Numbers and a Step
A tuple with a range of numbers and a step can be declared using the `tuple()` function with a sequence of elements as an argument. The following code declares a tuple with a range of numbers and a step:

```python title="tuple.py" showLineNumbers{1} {1}
data = tuple(range(1, 4, 2))
print(data)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python tuple.py
(1, 3)
```

In this example, we declare a tuple with a range of numbers and a step using the `tuple()` function with a sequence of elements as an argument. We then print the tuple to the console. The output shows that the tuple contains a range of numbers and a step.

### Declaring a Tuple with a Range of Numbers in Reverse Order
A tuple with a range of numbers in reverse order can be declared using the `tuple()` function with a sequence of elements as an argument. The following code declares a tuple with a range of numbers in reverse order:

```python title="tuple.py" showLineNumbers{1} {1}
data = tuple(range(3, 0, -1))
print(data)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python tuple.py
(3, 2, 1)
```

In this example, we declare a tuple with a range of numbers in reverse order using the `tuple()` function with a sequence of elements as an argument. We then print the tuple to the console. The output shows that the tuple contains a range of numbers in reverse order.

### Declaring a Tuple using list comprehension
A tuple can be declared using a `for` loop. The following code declares a tuple using a `for` loop:

```python title="tuple.py" showLineNumbers{1} {1}
data = tuple(i for i in range(1, 4))
print(data)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python tuple.py
(1, 2, 3)
```

In this example, we declare a tuple using a `for` loop. We then print the tuple to the console. The output shows that the tuple contains a range of numbers.

### Declaring a Tuple using a list
A tuple can be declared using a list. The following code declares a tuple using a list:

```python title="tuple.py" showLineNumbers{1} {2}
list1 = [1, 2, 3]
data = tuple(list1)
print(data)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python tuple.py
(1, 2, 3)
```

In this example, we declare a tuple using a list. We then print the tuple to the console. The output shows that the tuple contains a range of numbers.

### Declaring a Tuple using a set
A tuple can be declared using a set. The following code declares a tuple using a set:

```python title="tuple.py" showLineNumbers{1} {2}
set1 = {1, 2, 3}
data = tuple(set1)
print(data)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python tuple.py
(1, 2, 3)
```

In this example, we declare a tuple using a set. We then print the tuple to the console. The output shows that the tuple contains a range of numbers.

:::tip
We are going to talk about sets in a future article.
:::

### Declaring a Nested Tuple
A tuple can be declared using a nested tuple. The following code declares a tuple using a nested tuple:

```python title="tuple.py" showLineNumbers{1} {3}
tuple1 = (1, 2, 3)
tuple2 = (4, 5, 6)
data = tuple((tuple1, tuple2))
print(data)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python tuple.py
((1, 2, 3), (4, 5, 6))
```

In this example, we declare a tuple using a nested tuple. We then print the tuple to the console. The output shows that the tuple contains a nested tuple.

### Declaring a Tuple using * 
A tuple can be declared using `*`. The following code declares a tuple using `*`:

```python title="tuple.py" showLineNumbers{1} {1}
data = tuple(1,2, *[3,4])
print(data)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python tuple.py
(1, 2, 3, 4)
```

In this example, we declare a tuple using `*`. We then print the tuple to the console. The output shows that the tuple contains a range of numbers.

## Type of a Tuple
The type of a tuple is `tuple`. The following code prints the type of a tuple:

```python title="tuple.py" showLineNumbers{1} {1-2}
data = tuple([1, 2, 3])
print(type(data))
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python tuple.py
<class 'tuple'>
```

In this example, we declare a tuple using the `tuple()` function with a sequence of elements as an argument. We then print the type of the tuple to the console. The output shows that the type of the tuple is `tuple`.

## Length of a Tuple
The length of a tuple is the number of elements in the tuple. The following code prints the length of a tuple:

```python title="tuple.py" showLineNumbers{1} {1-2}
data = tuple([1, 2, 3])
print(len(data))
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python tuple.py
3
```

In this example, we declare a tuple using the `tuple()` function with a sequence of elements as an argument. We then print the length of the tuple to the console. The output shows that the length of the tuple is `3`.

## Accessing Elements in a Tuple
Elements in a tuple can be accessed using the index of the element. The index of an element is its position in the tuple. The first element in a tuple has an index of `0`. The following code accesses the first element in a tuple:

```python title="tuple.py" showLineNumbers{1} {1-2}
data = tuple([1, 2, 3])
print(data[0])
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python tuple.py
1
```

In this example, we declare a tuple using the `tuple()` function with a sequence of elements as an argument. We then print the first element in the tuple to the console. The output shows that the first element in the tuple is `1`.

The following code accesses the second element in a tuple:

```python title="tuple.py" showLineNumbers{1} {1-2}
data = tuple([1, 2, 3])
print(data[1])
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python tuple.py
2
```

In this example, we declare a tuple using the `tuple()` function with a sequence of elements as an argument. We then print the second element in the tuple to the console. The output shows that the second element in the tuple is `2`.

:::tip
We are going to talk about accessing the elements of a tuple in a future article.
:::

## Conclusion
In this article, we explored what tuples are, how to create and manipulate them, their characteristics, use cases, and why they are an essential component of Python programming. We also learned about the properties of tuples, how to declare a tuple, the type of a tuple, the length of a tuple, and how to access elements in a tuple.