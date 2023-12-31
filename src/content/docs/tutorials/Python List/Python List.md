---
title: List in Python
description: Learn about List in Python. How to create a list, add elements to a list, remove elements from a list, and more. How to use list comprehension in Python. How to use the built-in functions of list in Python.
sidebar: 
    order: 48
---

## Mastering Lists in Python: A Comprehensive Exploration
Lists in Python are versatile and powerful data structures that play a crucial role in many programming scenarios. Whether you're a Python beginner or an experienced developer, understanding lists and their various operations is fundamental. In this comprehensive guide, we will explore the ins and outs of Python lists, covering creation, manipulation, iteration, and best practices.

## Introduction to Lists
A list in Python is an ordered collection of elements. These elements can be of any data type, including numbers, strings, or even other lists. Lists are mutable, meaning their elements can be modified after creation. They provide a flexible and dynamic way to organize and manipulate data.

## Creating Lists
Lists are created using square brackets `[]` and commas `,` to separate elements. For example, the following code creates a list of integers:

```python title="list_integers.py" showLineNumbers{1} {1}
list_integers = [1, 2, 3, 4, 5]
print(list_integers)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python list_integers.py
[1, 2, 3, 4, 5]
```

:::tip
A List in Python is similar to an array in other programming languages. However, unlike arrays, lists can contain elements of different data types.
:::

## Properties of Lists
Lists in Python have the following properties:
- **Lists are ordered**: The elements in a list are stored in a particular order. This order is preserved until the list is modified.
- **Lists are mutable**: The elements in a list can be modified after creation.
- **Lists are heterogeneous**: The elements in a list can be of any data type.
- **Lists can contain duplicate elements**: The same element can appear multiple times in a list.
- **Lists can be nested**: A list can contain other lists as elements.
- **Lists are dynamic**: The size of a list is not fixed. It can grow or shrink as needed.
- **Lists are iterable**: The elements in a list can be accessed using a for loop.
- **Lists are zero-indexed**: The first element in a list has an index of 0.

## Declaring Lists
Lists can be declared in several ways. The simplest way is to use square brackets `[]` and commas `,` to separate elements.

### Declaring an Empty List
An empty list can be declared using empty square brackets `[]`:

```python title="empty_list.py" showLineNumbers{1} {1}
empty_list = []
print(empty_list)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python empty_list.py
[]
```

In this example, we declare an empty list and assign it to the variable `empty_list`. We then print the list to the console. The output shows that the list is empty.

### Declaring a List with Elements
A list with elements can be declared using square brackets `[]` and commas `,` to separate elements:

```python title="list_with_elements.py" showLineNumbers{1-3} {1}
list_with_elements = [1, 2, 3, 4, 5]
print(list_with_elements)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python list_with_elements.py
[1, 2, 3, 4, 5]
```

In this example, we declare a list with five elements and assign it to the variable `list_with_elements`. We then print the list to the console. The output shows that the list contains five elements.

### Declaring a List with Duplicate Elements
A list with duplicate elements can be declared using square brackets `[]` and commas `,` to separate elements:

```python title="list_with_duplicate_elements.py" showLineNumbers{1-3} {1}
list_with_duplicate_elements = [1, 2, 3, 4, 5, 1, 2, 3, 4, 5]
print(list_with_duplicate_elements)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python list_with_duplicate_elements.py
[1, 2, 3, 4, 5, 1, 2, 3, 4, 5]
```

In this example, we declare a list with ten elements, including duplicates, and assign it to the variable `list_with_duplicate_elements`. We then print the list to the console. The output shows that the list contains ten elements, including duplicates.

### Declaring a List with Elements of Different Data Types
A list with elements of different data types can be declared using square brackets `[]` and commas `,` to separate elements:

```python title="list_with_elements_of_different_data_types.py" showLineNumbers{1-3} {1}
list_with_elements_of_different_data_types = [1, 2.0, "three", [4, 5]]
print(list_with_elements_of_different_data_types)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python list_with_elements_of_different_data_types.py
[1, 2.0, 'three', [4, 5]]
```

In this example, we declare a list with four elements of different data types and assign it to the variable `list_with_elements_of_different_data_types`. We then print the list to the console. The output shows that the list contains four elements of different data types.

### Declaring a List with Elements of the Same Data Type
A list with elements of the same data type can be declared using square brackets `[]` and commas `,` to separate elements:

```python title="list_with_elements_of_same_data_type.py" showLineNumbers{1-3} {1}
list_with_elements_of_same_data_type = [1, 2, 3, 4, 5]
print(list_with_elements_of_same_data_type)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python list_with_elements_of_same_data_type.py
[1, 2, 3, 4, 5]
```

In this example, we declare a list with five elements of the same data type and assign it to the variable `list_with_elements_of_same_data_type`. We then print the list to the console. The output shows that the list contains five elements of the same data type.

### Declaring a List with a Single Element
A list with a single element can be declared using square brackets `[]` and commas `,` to separate elements:

```python title="list_with_single_element.py" showLineNumbers{1-3} {1}
list_with_single_element = [1]
print(list_with_single_element)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python list_with_single_element.py
[1]
```

In this example, we declare a list with a single element and assign it to the variable `list_with_single_element`. We then print the list to the console. The output shows that the list contains a single element.

### Declaring a List with Multiple Lines
A list with multiple lines can be declared using square brackets `[]` and commas `,` to separate elements:

```python title="list_with_multiple_lines.py" showLineNumbers{1-3} {1-6}
list_with_multiple_lines = [
    1,
    2,
    3,
    4,
    5
]
print(list_with_multiple_lines)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python list_with_multiple_lines.py
[1, 2, 3, 4, 5]
```

In this example, we declare a list with five elements on multiple lines and assign it to the variable `list_with_multiple_lines`. We then print the list to the console. The output shows that the list contains five elements.

### Declaring a List with list()
A list can be declared using the built-in `list()` function:

```python title="list_with_list_function.py" showLineNumbers{1-3} {1}
list_with_list_function = list([1, 2, 3, 4, 5])
print(list_with_list_function)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python list_with_list_function.py
[1, 2, 3, 4, 5]
```

In this example, we declare a list using the built-in `list()` function and assign it to the variable `list_with_list_function`. We then print the list to the console. The output shows that the list contains five elements.

### Declaring a List with no elements using list()
A list with no elements can be declared using the built-in `list()` function:

```python title="empty_list_with_list_function.py" showLineNumbers{1-3} {1}
empty_list_with_list_function = list()
print(empty_list_with_list_function)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python empty_list_with_list_function.py
[]
```

In this example, we declare an empty list using the built-in `list()` function and assign it to the variable `empty_list_with_list_function`. We then print the list to the console. The output shows that the list is empty.

### Declaring a List with a Range of Numbers
A list with a range of numbers can be declared using the built-in `range()` function:

```python title="list_with_range_function.py" showLineNumbers{1-3} {1}
list_with_range_function = list(range(1, 6))
print(list_with_range_function)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python list_with_range_function.py
[1, 2, 3, 4, 5]
```

In this example, we declare a list with a range of numbers using the built-in `range()` function and assign it to the variable `list_with_range_function`. We then print the list to the console. The output shows that the list contains five elements.

### Declaring a List with a Range of Numbers and a Step
A list with a range of numbers and a step can be declared using the built-in `range()` function:

```python title="list_with_range_function_and_step.py" showLineNumbers{1-3} {1}
list_with_range_function_and_step = list(range(1, 6, 2))
print(list_with_range_function_and_step)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python list_with_range_function_and_step.py
[1, 3, 5]
```

In this example, we declare a list with a range of numbers and a step using the built-in `range()` function and assign it to the variable `list_with_range_function_and_step`. We then print the list to the console. The output shows that the list contains three elements.

### Declaring a List with a Range of Numbers in Reverse Order
A list with a range of numbers in reverse order can be declared using the built-in `range()` function:

```python title="list_with_range_function_and_reverse_order.py" showLineNumbers{1-3} {1}
list_with_range_function_and_reverse_order = list(range(5, 0, -1))
print(list_with_range_function_and_reverse_order)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python list_with_range_function_and_reverse_order.py
[5, 4, 3, 2, 1]
```

In this example, we declare a list with a range of numbers in reverse order using the built-in `range()` function and assign it to the variable `list_with_range_function_and_reverse_order`. We then print the list to the console. The output shows that the list contains five elements.

### Declare a List using loop
A list can be declared using a loop:

```python title="list_with_loop.py" showLineNumbers{1-4} {1-3}
list_with_loop = []
for i in range(1, 6):
    list_with_loop.append(i)
print(list_with_loop)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python list_with_loop.py
[1, 2, 3, 4, 5]
```

In this example, we declare a list using a loop and assign it to the variable `list_with_loop`. We then print the list to the console. The output shows that the list contains five elements.

### Declaring a List with a List Comprehension
A list can be declared using a list comprehension:

```python title="list_with_list_comprehension.py" showLineNumbers{1} {1}
list_with_list_comprehension = [i for i in range(1, 6)]
print(list_with_list_comprehension)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python list_with_list_comprehension.py
[1, 2, 3, 4, 5]
```

In this example, we declare a list using a list comprehension and assign it to the variable `list_with_list_comprehension`. We then print the list to the console. The output shows that the list contains five elements.

### Declaring a Multi Dimensional List
A multi dimensional list can be declared using square brackets `[]` and commas `,` to separate elements:

```python title="multi_dimensional_list.py" showLineNumbers{1-3} {1}
multi_dimensional_list = [[1, 2, 3], [4, 5, 6]]
print(multi_dimensional_list)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python multi_dimensional_list.py
[[1, 2, 3], [4, 5, 6]]
```

In this example, we declare a multi dimensional list and assign it to the variable `multi_dimensional_list`. We then print the list to the console. The output shows that the list contains two lists as elements. This is also known as a two-dimensional list.

:::note
If you create multi dimensional list, it is called nested list.
```python title="multi_dimensional_list.py" showLineNumbers{1-3} {1}
multi_dimensional_list = [[[1, 2, 3], [4, 5, 6]], [[7, 8, 9], [10, 11, 12]]]
print(multi_dimensional_list)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python multi_dimensional_list.py
[[[1, 2, 3], [4, 5, 6]], [[7, 8, 9], [10, 11, 12]]]
```

In this example, we declare a multi dimensional list and assign it to the variable `multi_dimensional_list`. We then print the list to the console. The output shows that the list contains two lists as elements. This is also known as a three-dimensional list.
:::

### Declaring a List with a List Comprehension and Nested Lists
A list with a list comprehension and nested lists can be declared using square brackets `[]` and commas `,` to separate elements:

```python title="list_with_list_comprehension_and_nested_lists.py" showLineNumbers{1-3} {1}
list_with_list_comprehension_and_nested_lists = [[i for i in range(1, 4)], [i for i in range(4, 7)]]
print(list_with_list_comprehension_and_nested_lists)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python list_with_list_comprehension_and_nested_lists.py
[[1, 2, 3], [4, 5, 6]]
```

In this example, we declare a list with a list comprehension and nested lists and assign it to the variable `list_with_list_comprehension_and_nested_lists`. We then print the list to the console. The output shows that the list contains two lists as elements. This is also known as a two-dimensional list.

### Declaring a List with a List Comprehension and Nested Lists in Reverse Order
A list with a list comprehension and nested lists in reverse order can be declared using square brackets `[]` and commas `,` to separate elements:

```python title="list_with_list_comprehension_and_nested_lists_in_reverse_order.py" showLineNumbers{1-3} {1}
list_with_list_comprehension_and_nested_lists_in_reverse_order = [[i for i in range(3, 0, -1)], [i for i in range(6, 3, -1)]]
print(list_with_list_comprehension_and_nested_lists_in_reverse_order)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python list_with_list_comprehension_and_nested_lists_in_reverse_order.py
[[3, 2, 1], [6, 5, 4]]
```

In this example, we declare a list with a list comprehension and nested lists in reverse order and assign it to the variable `list_with_list_comprehension_and_nested_lists_in_reverse_order`. We then print the list to the console. The output shows that the list contains two lists as elements. This is also known as a two-dimensional list.

## Types of List
Lists in Python can be categorized into the following types:
- **Mutable Lists**: Lists whose elements can be modified after creation.
- **Immutable Lists**: Lists whose elements cannot be modified after creation.
- **Nested Lists**: Lists that contain other lists as elements.
- **Empty Lists**: Lists that contain no elements.
- **Singleton Lists**: Lists that contain a single element.
- **Homogeneous Lists**: Lists that contain elements of the same data type.
- **Heterogeneous Lists**: Lists that contain elements of different data types.
- **Ordered Lists**: Lists whose elements are stored in a particular order.
- **Unordered Lists**: Lists whose elements are not stored in a particular order.
- **Sorted Lists**: Lists whose elements are stored in ascending or descending order.
- **Unsorted Lists**: Lists whose elements are not stored in ascending or descending order.

### Mutable Lists
Lists in Python are mutable, meaning their elements can be modified after creation. For example, the following code modifies the first element of a list:

```python title="mutable_list.py" showLineNumbers{1-3} {1}
mutable_list = [1, 2, 3, 4, 5]
mutable_list[0] = 6
print(mutable_list)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python mutable_list.py
[6, 2, 3, 4, 5]
```

In this example, we declare a list with five elements and assign it to the variable `mutable_list`. We then modify the first element of the list and print the list to the console. The output shows that the first element of the list has been modified.

### Immutable Lists
Lists in Python are immutable, meaning their elements cannot be modified after creation. For example, the following code attempts to modify the first element of a list:

```python title="immutable_list.py" showLineNumbers{1-3} {1}
immutable_list = (1, 2, 3, 4, 5)
immutable_list[0] = 6
print(immutable_list)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python immutable_list.py
Traceback (most recent call last):
  File "immutable_list.py", line 2, in <module>
    immutable_list[0] = 6
TypeError: 'tuple' object does not support item assignment
```

:::tip
We are going to learn about tuples in the upcoming tutorials.
:::

In this example, we declare a list with five elements and assign it to the variable `immutable_list`. We then attempt to modify the first element of the list and print the list to the console. The output shows that the first element of the list cannot be modified.

### Nested Lists
Lists in Python can contain other lists as elements. For example, the following code declares a nested list:

```python title="nested_list.py" showLineNumbers{1-3} {1}
nested_list = [[1, 2, 3], [4, 5, 6]]
print(nested_list)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python nested_list.py
[[1, 2, 3], [4, 5, 6]]
```

In this example, we declare a nested list and assign it to the variable `nested_list`. We then print the list to the console. The output shows that the list contains two lists as elements. This is also known as a two-dimensional list.

:::note
If you create multi dimensional list, it is called nested list.
```python title="nested_list.py" showLineNumbers{1-3} {1}
nested_list = [[[1, 2, 3], [4, 5, 6]], [[7, 8, 9], [10, 11, 12]]]
print(nested_list)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python nested_list.py
[[[1, 2, 3], [4, 5, 6]], [[7, 8, 9], [10, 11, 12]]]
```

In this example, we declare a nested list and assign it to the variable `nested_list`. We then print the list to the console. The output shows that the list contains two lists as elements. This is also known as a three-dimensional list.
:::

### Empty Lists
Lists in Python can be empty, meaning they contain no elements. For example, the following code declares an empty list:

```python title="empty_list.py" showLineNumbers{1-3} {1}
empty_list = []
print(empty_list)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python empty_list.py
[]
```

In this example, we declare an empty list and assign it to the variable `empty_list`. We then print the list to the console. The output shows that the list is empty.

### Singleton Lists
Lists in Python can contain a single element. For example, the following code declares a list with a single element:

```python title="singleton_list.py" showLineNumbers{1-3} {1}
singleton_list = [1]
print(singleton_list)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python singleton_list.py
[1]
```

In this example, we declare a list with a single element and assign it to the variable `singleton_list`. We then print the list to the console. The output shows that the list contains a single element.

### Homogeneous Lists
Lists in Python can contain elements of the same data type. For example, the following code declares a list with five elements of the same data type:

```python title="homogeneous_list.py" showLineNumbers{1-3} {1}
homogeneous_list = [1, 2, 3, 4, 5]
print(homogeneous_list)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python homogeneous_list.py
[1, 2, 3, 4, 5]
```

In this example, we declare a list with five elements of the same data type and assign it to the variable `homogeneous_list`. We then print the list to the console. The output shows that the list contains five elements of the same data type.

### Heterogeneous Lists
Lists in Python can contain elements of different data types. For example, the following code declares a list with four elements of different data types:

```python title="heterogeneous_list.py" showLineNumbers{1-3} {1}
heterogeneous_list = [1, 2.0, "three", [4, 5]]
print(heterogeneous_list)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python heterogeneous_list.py
[1, 2.0, 'three', [4, 5]]
```

In this example, we declare a list with four elements of different data types and assign it to the variable `heterogeneous_list`. We then print the list to the console. The output shows that the list contains four elements of different data types.

### Ordered Lists
Lists in Python are ordered, meaning their elements are stored in a particular order. It can't be changed. If you add elements to the list, it will be added at the end of the list. For example, the following code declares a list with five elements in a particular order:

```python title="ordered_list.py" showLineNumbers{1-3} {1}
ordered_list = [1, 2, 6, 9, 5]
print(ordered_list)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python ordered_list.py
[1, 2, 6, 9, 5]
```

In this example, we declare a list with five elements in a particular order and assign it to the variable `ordered_list`. We then print the list to the console. The output shows that the list contains five elements in a particular order.


### Unordered Lists
Lists in Python are unordered, meaning their elements are not stored in a particular order. It can be changed automatically. For example, the following code declares a list with five elements in no particular order:

```python title="unordered_list.py" showLineNumbers{1-3} {1}
unordered_list = {1, 2, 6, 9, 5}
print(unordered_list)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python unordered_list.py
{1, 2, 6, 9, 5}
```
:::tip
A Set in Python is similar to a list in other programming languages. However, unlike lists, sets do not preserve the order of their elements. It is important to note that sets are unordered.
:::

In this example, we declare a list with five elements in no particular order and assign it to the variable `unordered_list`. We then print the list to the console. The output shows that the list contains five elements in no particular order.

### Sorted Lists
Lists in Python can be sorted in ascending or descending order. For example, the following code declares a list with five elements in ascending order:

```python title="sorted_list.py" showLineNumbers{1-3} {1-2}
sorted_list = [1, 2, 6, 9, 5]
sorted_list.sort()
print(sorted_list)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python sorted_list.py
[1, 2, 5, 6, 9]
```

In this example, we declare a list with five elements in ascending order and assign it to the variable `sorted_list`. We then print the list to the console. The output shows that the list contains five elements in ascending order.

:::tip
We are going to learn about sorting in the upcoming tutorials.
:::


### Unsorted Lists
Lists in Python can be unsorted in ascending or descending order. For example, the following code declares a list with five elements in unsorted order:

```python title="unsorted_list.py" showLineNumbers{1-3} {1}
unsorted_list = [1, 2, 6, 9, 5]
print(unsorted_list)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python unsorted_list.py
[1, 2, 6, 9, 5]
```

In this example, we declare a list with five elements in unsorted order and assign it to the variable `unsorted_list`. We then print the list to the console. The output shows that the list contains five elements in unsorted order.



## Conclusion
In this guide, we explored the ins and outs of Python lists, covering creation, manipulation, iteration, and best practices. We also covered the properties of lists and how to declare lists in Python. Now that you have a solid understanding of lists, you can start using them in your Python programs.