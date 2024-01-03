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
Arrays are useful when you need to store a large number of elements of the same data type. For example, if you need to store the marks of 100 students, you can use an array instead of a list. This is because arrays are more memory-efficient than lists. We will explore this in detail in the next section.

## Syntax of Arrays in Python
The array module in Python provides a class called array that allows you to create arrays. The syntax for creating an array is as follows:

```python title="syntax.py" showLineNumbers{1} {1-3}
import array as arr
variable_name = arr.array(typecode, [initializers])
```

Here, `typecode` is a string that specifies the data type of the array. The `initializers` are optional and can be used to initialize the array with a list of elements. The `typecode` can be one of the following:

## Typecodes for Arrays in Python
The `typecode` specifies the data type of the array. The following table lists the typecodes and the corresponding data types:

| Typecode | Data Type |
| -------- | --------- |
| b        | Signed integer of size 1 byte |
| B        | Unsigned integer of size 1 byte |
| c        | Character of size 1 byte |
