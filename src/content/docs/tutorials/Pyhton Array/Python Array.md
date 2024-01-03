---
title: Array in Python
description: Learn about Array in Python. How to create an array, how to access elements, how to add elements, how to remove elements, how to update elements, and how to search for elements in an array.
sidebar: 
    order: 70
---

## Understanding Arrays in Python: A Guide to the array Module
Arrays in Python provide a more efficient way to store and manipulate sequences of elements compared to regular lists. The array module in Python offers a dedicated class called array that allows you to create arrays with specified data types. In this guide, we will explore the basics of arrays, how to use the array module, and understand the advantages it offers.

## Introduction to Arrays
An array is a collection of elements of the same data type stored in contiguous memory locations. Unlike lists, arrays in Python are more memory-efficient because they are homogeneous, meaning all elements must be of the same type. This leads to a more compact representation of the data.

<!-- ```python title="clear.py" showLineNumbers{1} {1-3}
data = {'a': 1, 'b': 2, 'c': 3}
data.clear()
print(data)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python clear.py
{}
```

In this example, we declare a dictionary and assign it to the variable `data`. We then use the `clear()` method to remove all the elements from the dictionary. The output shows that the dictionary is empty. -->

## Need for Arrays
Arrays are useful when you need to store a large number of elements of the same data type. For example, if you need to store the marks of 100 students, you can use an array instead of a list. This is because arrays are more memory-efficient than lists. It uses less memory to store the same number of elements compared to lists. It use the Typecode to store the data in the array. We will explore this in detail in the next section.

## Syntax of Arrays in Python
The array module in Python provides a class called array that allows you to create arrays. The syntax for creating an array is as follows:

```python title="syntax.py" showLineNumbers{1} {1-3}
import array as arr
variable_name = arr.array(typecode, [initializers])
```

Here, `typecode` is a string that specifies the data type of the array. The `initializers` are optional and can be used to initialize the array with a list of elements. The `typecode` can be one of the following:

## Typecodes for Arrays in Python
The `typecode` specifies the data type of the array. The following table lists the typecodes and the corresponding data types:

| Typecode | Data Type | Size (bytes) | Description |
| -------- | --------- | ------------ | ----------- |
| b | signed char | 1 | integer |
| B | unsigned char | 1 | integer |
| c | char | 1 | character |
| i | signed int | 2 | integer |
| I | unsigned int | 2 | integer |
| f | float | 4 | float |
| d | double | 8 | float |
| h | signed short | 2 | integer |
| H | unsigned short | 2 | integer |
| l | signed long | 4 | integer |
| L | unsigned long | 4 | integer |
| q | signed long long | 8 | integer |
| Q | unsigned long long | 8 | integer |
| s | char[] | 1 | character |
| u | Py_UNICODE | 2 | Unicode character |
| S | char[] | 1 | character |
| U | Py_UNICODE | 2 | Unicode character |
| w | wchar_t | 2 | Unicode character |

## Creating Arrays in Python
To create an array, you need to import the array module and use the `array()` function. The following example shows how to create an array of integers:

```python title="create.py" showLineNumbers{1} {1-3}
import array as arr
a = arr.array('i', [1, 2, 3, 4, 5])
print(a)
```

Output:

```cmd title="command" showLineNumbers{1} {2-6}
C:\Users\username>python create.py
array('i', [1, 2, 3, 4, 5])
```

Here, we import the array module and assign it to the variable `arr`. We then create an array of integers and assign it to the variable `a`. We then print the array. The output shows that the array is created successfully.

## Accessing Elements of an Array
You can access the elements of an array using the index operator `[]`. The following example shows how to access the elements of an array:

```python title="access.py" showLineNumbers{1} {1-4}
import array as arr
a = arr.array('i', [1, 2, 3, 4, 5])
print(a[0])
print(a[1])
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python access.py
1
2
```

Here, we create an array of integers and assign it to the variable `a`. We then print the first and second elements of the array. The output shows that the elements are accessed successfully.

## Type of an Array
You can use the `typecode` attribute to get the type of an array. The following example shows how to get the type of an array:

```python title="type.py" showLineNumbers{1} {1-3}
import array as arr
a = arr.array('i', [1, 2, 3, 4, 5])
print(a)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python type.py
array('i', [1, 2, 3, 4, 5])
```

Here, we create an array of integers and assign it to the variable `a`. We then print the array. The output shows that the array is created successfully.

## Properties of Array
- **Array are mutable** - The elements of an array can be modified.
- **Array are ordered** - The elements of an array are stored in a sequence and can be accessed using the index.
- **Array are homogeneous** - The elements of an array must be of the same data type.
- **Array are iterable** - The elements of an array can be accessed using the for loop.
- **Array are compact** - The elements of an array are stored in contiguous memory locations.
- **Array are more memory-efficient** - The elements of an array are stored in contiguous memory locations. This leads to a more compact representation of the data.
- **Array are faster than lists** - The elements of an array are stored in contiguous memory locations. This leads to faster access of elements compared to lists.
- **Array are less flexible than lists** - The elements of an array must be of the same data type. This leads to less flexibility compared to lists.
- **Array are less secure than lists** - The elements of an array are stored in contiguous memory locations. This leads to less security compared to lists.
- **Array are less popular than lists** - The elements of an array are stored in contiguous memory locations. This leads to less popularity compared to lists.
- **Array are less versatile than lists** - The elements of an array are stored in contiguous memory locations. This leads to less versatility compared to lists.

## Declaring Arrays in Python
You can declare an array in Python using the `array()` function.

### Declaring an Array of Integers
The following example shows how to declare an array of integers:

```python title="integers.py" showLineNumbers{1} {1-3}
import array as arr
a = arr.array('i', [1, 2, 3, 4, 5])
print(a)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python integers.py
array('i', [1, 2, 3, 4, 5])
```

Here, we import the array module and assign it to the variable `arr`. We then create an array of integers and assign it to the variable `a`. We then print the array. The output shows that the array is created successfully.

### Declaring an Array of Characters
The following example shows how to declare an array of characters:

```python title="characters.py" showLineNumbers{1} {1-3}
import array as arr
a = arr.array('c', ['a', 'b', 'c', 'd', 'e'])
print(a)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python characters.py
array('c', 'abcde')
```

Here, we import the array module and assign it to the variable `arr`. We then create an array of characters and assign it to the variable `a`. We then print the array. The output shows that the array is created successfully.

::: tip
You can try others typecode to create an array.
:::

### Declaring an Empty Array
The following example shows how to declare an empty array:

```python title="empty.py" showLineNumbers{1} {1-3}
import array as arr
a = arr.array('i')
print(a)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python empty.py
array('i')
```

Here, we import the array module and assign it to the variable `arr`. We then create an empty array and assign it to the variable `a`. We then print the array. The output shows that the array is created successfully.

### Declaring an Array with Multiple Data Types
The following example shows how to declare an array with multiple data types:

```python title="multiple.py" showLineNumbers{1} {1-3}
import array as arr
a = arr.array('i', [1, 2, "Hello", 4, 5])
print(a)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python multiple.py
Traceback (most recent call last):
  File "multiple.py", line 2, in <module>
    a = arr.array('i', [1, 2, "Hello", 4, 5])
TypeError: an integer is required (got type str)
```

Here, we import the array module and assign it to the variable `arr`. We then create an array with multiple data types and assign it to the variable `a`. We then print the array. The output shows that the array is created successfully.

:::caution
You can't create an array with multiple data types. You can only create an array with a single data type. It can't be homogeneous.
:::

### Declaring an Array with Multiple Lines
The following example shows how to declare an array with multiple lines:

```python title="multiple_lines.py" showLineNumbers{1} {1-10}
import array as arr
a = arr.array('i', [
    1,
    2,
    3,
    4,
    5
])
print(a)
```

Output:

```cmd title="command" showLineNumbers{1} {2-6}
C:\Users\username>python multiple_lines.py
array('i', [1, 2, 3, 4, 5])
```

Here, we import the array module and assign it to the variable `arr`. We then create an array with multiple lines and assign it to the variable `a`. We then print the array. The output shows that the array is created successfully.

### Declaring an Array with Range
The following example shows how to declare an array with range:

```python title="range.py" showLineNumbers{1} {1-3}
import array as arr
a = arr.array('i', range(1, 6))
print(a)
```

Output:

```cmd title="command" showLineNumbers{1} {2-6}
C:\Users\username>python range.py
array('i', [1, 2, 3, 4, 5])
```

Here, we import the array module and assign it to the variable `arr`. We then create an array with range and assign it to the variable `a`. We then print the array. The output shows that the array is created successfully.

### Declaring Arrays with List
You can declare an array in Python using a list.

```python title="list.py" showLineNumbers{1} {1-3}
import array as arr
list1 = [1, 2, 3, 4, 5]
a = arr.array('i', list1)
print(a)
```

Output:

```cmd title="command" showLineNumbers{1} {2-6}
C:\Users\username>python list.py
array('i', [1, 2, 3, 4, 5])
```

Here, we import the array module and assign it to the variable `arr`. We then create a list and assign it to the variable `list1`. We then create an array using the list and assign it to the variable `a`. We then print the array. The output shows that the array is created successfully.

### Declaring Arrays with Tuple
You can declare an array in Python using a tuple.

```python title="tuple.py" showLineNumbers{1} {1-3}
import array as arr
tuple1 = (1, 2, 3, 4, 5)
a = arr.array('i', tuple1)
print(a)
```

Output:

```cmd title="command" showLineNumbers{1} {2-6}
C:\Users\username>python tuple.py
array('i', [1, 2, 3, 4, 5])
```

Here, we import the array module and assign it to the variable `arr`. We then create a tuple and assign it to the variable `tuple1`. We then create an array using the tuple and assign it to the variable `a`. We then print the array. The output shows that the array is created successfully.

### Declaring Arrays with Set
You can declare an array in Python using a set.

```python title="set.py" showLineNumbers{1} {1-3}
import array as arr
set1 = {1, 2, 3, 4, 5}
a = arr.array('i', set1)
print(a)
```

Output:

```cmd title="command" showLineNumbers{1} {2-6}
C:\Users\username>python set.py
array('i', [1, 2, 3, 4, 5])
```

Here, we import the array module and assign it to the variable `arr`. We then create a set and assign it to the variable `set1`. We then create an array using the set and assign it to the variable `a`. We then print the array. The output shows that the array is created successfully.

### Declaring Arrays with List Comprehension
You can declare an array in Python using list comprehension.

```python title="list_comprehension.py" showLineNumbers{1} {1-3}
import array as arr
a = arr.array('i', [x for x in range(1, 6)])
print(a)
```

Output:

```cmd title="command" showLineNumbers{1} {2-6}
C:\Users\username>python list_comprehension.py
array('i', [1, 2, 3, 4, 5])
```

Here, we import the array module and assign it to the variable `arr`. We then create an array using list comprehension and assign it to the variable `a`. We then print the array. The output shows that the array is created successfully.

### Declaring Multidimensional Arrays
You can declare a multidimensional array in Python using a list of lists.

```python title="multidimensional.py" showLineNumbers{1} {1-3}
import array as arr
a = arr.array('i', [[1, 2, 3], [4, 5, 6], [7, 8, 9]])
print(a)
```

Output:

```cmd title="command" showLineNumbers{1} {2-6}
C:\Users\username>python multidimensional.py
Traceback (most recent call last):
  File "multidimensional.py", line 2, in <module>
    a = arr.array('i', [[1, 2, 3], [4, 5, 6], [7, 8, 9]])
TypeError: an integer is required (got type list)
```

Here, we import the array module and assign it to the variable `arr`. We then create a multidimensional array and assign it to the variable `a`. We then print the array. The output shows that the array is created successfully.

:::caution
You can't create a multidimensional array in Python. You can only create a one-dimensional array.
:::

## Conclusion
In this guide, we explored the basics of arrays, how to use the array module, and understand the advantages it offers. We also explored the typecodes for arrays in Python, how to create arrays, how to access elements, how to add elements, how to remove elements, how to update elements, and how to search for elements in an array. For more information on the array module, refer to the [official documentation](https://docs.python.org/3/library/array.html). For tutorials like this, Python Central Hub.