---
title: Access the Array
description: Learn how to access the array in Python. How to create a Array, add elements to a Array, remove elements from a Array, and more. How to use Array comprehension in Python. How to use the built-in functions of Array in Python. 
sidebar: 
    order: 71
---

## Navigating Array in Python: A Guide to Accessing Array Items
In Python, Array are a versatile and commonly used data structure for storing ordered collections of items. Understanding how to access elements within a Array is fundamental to working with this data structure effectively. In this guide, we'll explore the various methods and techniques for accessing Array items in Python.

## Basic Array Access
The most basic way to access items in a Array is to use the index operator `[]`. The index operator requires one argument: the index of the item to access. The index of the first item in the Array is `0`, the index of the second item is `1`, and so on. The following example demonstrates how to access items in a Array using the index operator:

```python title="array_indexing.py" showLineNumbers{1} {1,3-7}
import array as arr

my_array = arr.array('i', [1, 2, 3, 4, 5])
print(my_array[0])
print(my_array[1])
print(my_array[2])
print(my_array[3])
```

Output:
```cmd title="command" showLineNumbers{1} {2-6}
C:\Users\username>python array_indexing.py
1
2
3
4
```

In the above example, we create a Array of five elements and print the first four elements using their indices. Note that the last element is not printed because it has an index of 4, which is out of range for the Array.

## Negative Array Access
In Python, you can also access Array items using negative indices. Negative indices count backward from the end of the Array. The index of the last item in the Array is `-1`, the index of the second-to-last item is `-2`, and so on. The following example demonstrates how to access items in a Array using negative indices:

```python title="array_indexing_negative.py" showLineNumbers{1} {1,3-7}
import array as arr

my_array = arr.array('i', [1, 2, 3, 4, 5])
print(my_array[-1])
print(my_array[-2])
print(my_array[-3])
print(my_array[-4])
```

Output:
```cmd title="command" showLineNumbers{1} {2-6}
C:\Users\username>python array_indexing_negative.py
5
4
3
2
```

In the above example, we create a Array of five elements and print the last four elements using their negative indices. Note that the first element is not printed because it has an index of -5, which is out of range for the Array.

## Diagram of Array Access
The following diagram illustrates how to access items in a Array using positive and negative indices:

```python title="array_indexing_diagram.py" showLineNumbers{1} {1-2}
import array as arr
my_array = arr.array('i', [1, 2, 3, 4, 5])
```

| Element | 'a' | 'b' | 'c' | 'd' | 'e' |
| --- | --- | --- | --- | --- | --- |
| Index | 0 | 1 | 2 | 3 | 4 |
| Index (Negative) | -5 | -4 | -3 | -2 | -1 |

## Accessing Array Slices
In Python, you can access a slice of a Array using the slice operator `[:]`. The slice operator requires two arguments: the start index and the end index. The slice operator returns a new Array containing the items in the specified range. The following example demonstrates how to access a slice of a Array:

**Syntax:**
```python title="Syntax" showLineNumbers{1} {1}
my_array[start:end:step]
```

**Example:**
```python title="array_slice.py" showLineNumbers{1} {1,3-5}
import array as arr

my_array = arr.array('i', [1, 2, 3, 4, 5])
print(my_array[1:4])
print(my_array[1:4:2])
```

Output:
```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python array_slice.py
array('i', [2, 3, 4])
array('i', [2, 4])
```

In the above example, we create a Array of five elements and print a slice of the Array containing the second, third, and fourth elements. We also print a slice of the Array containing the second and fourth elements.

### Omitting the Start Index
In Python, you can omit the start index when accessing a slice of a Array. If you omit the start index, the slice will start at the beginning of the Array. The following example demonstrates how to omit the start index when accessing a slice of a Array:

```python title="array_slice_omit_start.py" showLineNumbers{1} {1,3-5}
import array as arr

my_array = arr.array('i', [1, 2, 3, 4, 5])
print(my_array[:4])
print(my_array[:4:2])
```

Output:
```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python array_slice_omit_start.py
array('i', [1, 2, 3, 4])
array('i', [1, 3])
```

In the above example, we create a Array of five elements and print a slice of the Array containing the first, second, third, and fourth elements. We also print a slice of the Array containing the first and third elements.

### Omitting the End Index
In Python, you can omit the end index when accessing a slice of a Array. If you omit the end index, the slice will end at the end of the Array. The following example demonstrates how to omit the end index when accessing a slice of a Array:

```python title="array_slice_omit_end.py" showLineNumbers{1} {1,3-5}
import array as arr

my_array = arr.array('i', [1, 2, 3, 4, 5])
print(my_array[1:])
print(my_array[1::2])
```

Output:
```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python array_slice_omit_end.py
array('i', [2, 3, 4, 5])
array('i', [2, 4])
```

In the above example, we create a Array of five elements and print a slice of the Array containing the second, third, fourth, and fifth elements. We also print a slice of the Array containing the second and fourth elements.

### Omitting the Start and End Indices
In Python, you can omit both the start index and the end index when accessing a slice of a Array. If you omit both indices, the slice will contain all of the items in the Array. The following example demonstrates how to omit both the start index and the end index when accessing a slice of a Array:

```python title="array_slice_omit_start_end.py" showLineNumbers{1} {1,3-5}
import array as arr

my_array = arr.array('i', [1, 2, 3, 4, 5])
print(my_array[:])
print(my_array[::2])
```

Output:
```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python array_slice_omit_start_end.py
array('i', [1, 2, 3, 4, 5])
array('i', [1, 3, 5])
```

In the above example, we create a Array of five elements and print a slice of the Array containing all of the elements. We also print a slice of the Array containing the first, third, and fifth elements.

### Negative Array Slices
In Python, you can access a slice of a Array using negative indices. Negative indices count backward from the end of the Array. The index of the last item in the Array is `-1`, the index of the second-to-last item is `-2`, and so on. The following example demonstrates how to access a slice of a Array using negative indices:

```python title="array_slice_negative.py" showLineNumbers{1} {1,3-5}
import array as arr

my_array = arr.array('i', [1, 2, 3, 4, 5])
print(my_array[-4:-1])
print(my_array[-4:-1:2])
```

Output:
```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python array_slice_negative.py
array('i', [2, 3, 4])
array('i', [2, 4])
```

In the above example, we create a Array of five elements and print a slice of the Array containing the second, third, and fourth elements. We also print a slice of the Array containing the second and fourth elements.

### Negative Array Slices with Omitted Indices
In Python, you can omit the start index and the end index when accessing a slice of a Array using negative indices. If you omit the start index, the slice will start at the beginning of the Array. If you omit the end index, the slice will end at the end of the Array. The following example demonstrates how to omit the start index and the end index when accessing a slice of a Array using negative indices:

```python title="array_slice_negative_omit_start_end.py" showLineNumbers{1} {1,3-5}
import array as arr

my_array = arr.array('i', [1, 2, 3, 4, 5])
print(my_array[:-1])
print(my_array[:-1:2])
```

Output:
```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python array_slice_negative_omit_start_end.py
array('i', [1, 2, 3, 4])
array('i', [1, 3])
```

In the above example, we create a Array of five elements and print a slice of the Array containing the first, second, third, and fourth elements. We also print a slice of the Array containing the first and third elements.

### Array Slice with Negative Step
In Python, you can access a slice of a Array using a negative step. The step is the number of items to skip between successive items in the slice. The following example demonstrates how to access a slice of a Array using a negative step:

```python title="array_slice_negative_step.py" showLineNumbers{1} {1,3-5}
import array as arr

my_array = arr.array('i', [1, 2, 3, 4, 5])
print(my_array[4:1:-1])
print(my_array[4:1:-2])
```

Output:
```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python array_slice_negative_step.py
array('i', [5, 4, 3])
array('i', [5, 3])
```

In the above example, we create a Array of five elements and print a slice of the Array containing the fifth, fourth, and third elements. We also print a slice of the Array containing the fifth and third elements.

## in Operator
In Python, you can use the `in` operator to check if a Array contains a specified item. The `in` operator returns `True` if the Array contains the specified item and `False` if it does not. The following example demonstrates how to use the `in` operator to check if a Array contains a specified item:

```python title="array_in.py" showLineNumbers{1} {1,3-5}
import array as arr

my_array = arr.array('i', [1, 2, 3, 4, 5])
print(1 in my_array)
print(6 in my_array)
```

Output:
```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python array_in.py
True
False
```

In the above example, we create a Array of five elements and check if the Array contains the items `1` and `6`. The Array contains `1` but not `6`, so the first check returns `True` and the second check returns `False`.

## not in Operator
In Python, you can use the `not in` operator to check if a Array does not contain a specified item. The `not in` operator returns `True` if the Array does not contain the specified item and `False` if it does. The following example demonstrates how to use the `not in` operator to check if a Array does not contain a specified item:

```python title="array_not_in.py" showLineNumbers{1} {1,3-5}
import array as arr

my_array = arr.array('i', [1, 2, 3, 4, 5])
print(1 not in my_array)
print(6 not in my_array)
```

Output:
```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python array_not_in.py
False
True
```

In the above example, we create a Array of five elements and check if the Array does not contain the items `1` and `6`. The Array contains `1` but not `6`, so the first check returns `False` and the second check returns `True`.

## Conclusion
In this guide, we explored the various methods and techniques for accessing Array items in Python. We also explored how to access Array slices in Python. Now that you are familiar with the basics of accessing Array items in Python, you can learn more about Array in Python from the [official documentation](https://docs.python.org/3/library/array.html). For more Python Array tutorials, Check out the Python Central Hub.