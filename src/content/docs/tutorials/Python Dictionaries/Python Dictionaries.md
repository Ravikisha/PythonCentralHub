---
title: Dictionaries in Python
description: Learn how to use dictionaries in Python. How to create, add, remove, and iterate over key-value pairs. Dictionaries are a powerful data structure in Python.
sidebar: 
    order: 63
---

## Mastering Dictionaries in Python: A Comprehensive Guide
Dictionaries in Python are powerful and flexible data structures that allow you to store and retrieve data in key-value pairs. They are an essential part of the Python language, providing an efficient way to organize and manipulate data. In this comprehensive guide, we will explore the fundamentals of dictionaries, how to create and manipulate them, common operations, and practical use cases where dictionaries shine.

## Understanding Dictionaries
A dictionary in Python is an unordered collection of items, where each item consists of a key-value pair. Keys are unique and used to access values associated with them. Dictionaries are dynamic, meaning you can add, modify, or remove key-value pairs as needed.

<!-- ```python title="set.py" showLineNumbers{1} {1}
set1 = {1, 2, 3}
print(set1)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python set.py
{1, 2, 3}
```

In this example, we declare a set of three elements and assign it to the variable `set1`. We then print the set to the console. The output shows that the set contains three elements. -->


## Creating Dictionaries
There are several ways to create dictionaries in Python. The most common way is to use curly braces `{}` and separate key-value pairs with commas. Each key-value pair consists of a key and a value separated by a colon `:`. The following example creates a dictionary with three key-value pairs:

```python title="dict.py" showLineNumbers{1} {1}
dict1 = {"name": "John", "age": 30, "city": "New York"}
print(dict1)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python dict.py
{'name': 'John', 'age': 30, 'city': 'New York'}
```

In this example, we create a dictionary with three key-value pairs and assign it to the variable `dict1`. We then print the dictionary to the console. The output shows that the dictionary contains three key-value pairs.

You can also create dictionaries using the `dict()` constructor. The following example creates a dictionary with three key-value pairs:

```python title="dict.py" showLineNumbers{1} {1}
dict1 = dict(name="John", age=30, city="New York")
print(dict1)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python dict.py
{'name': 'John', 'age': 30, 'city': 'New York'}
```

In this example, we create a dictionary with three key-value pairs and assign it to the variable `dict1`. We then print the dictionary to the console. The output shows that the dictionary contains three key-value pairs.

:::note
Dictionary keys must be unique. If you try to create a dictionary with duplicate keys, the last key-value pair will overwrite the previous one. It creates a dictionary with two key-value pairs, where the second key-value pair overwrites the first one. It create a table like structure.

```python title="dict.py" showLineNumbers{1} {1}
dict1 = {"name": "John", "age": 30, "city": "New York", "name": "Jane"}
print(dict1)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python dict.py
{'name': 'Jane', 'age': 30, 'city': 'New York'}
```

This look like a table with two rows and three columns. The first row is the header row and the second row is the data row. The header row contains the keys and the data row contains the values. The keys are unique and the values are not unique. The keys are used to access the values. The keys are case sensitive. The keys are strings and the values can be any data type.

|key|value|
|---|---|
|name|John|
|age|30|
|city|New York|

After overwriting the first key-value pair, the dictionary contains two key-value pairs. The first key-value pair is `name: Jane` and the second key-value pair is `age: 30`. The output shows that the dictionary contains two key-value pairs.

|key|value|
|---|---|
|name|Jane|
|age|30|
|city|New York|

:::

## Properties of Dictionaries
Dictionaries in Python have the following properties:

- **Unordered**: Dictionaries are unordered, meaning that the order of key-value pairs is not preserved. When you print a dictionary, the order of key-value pairs may change. This is because dictionaries are implemented using hash tables, which are unordered data structures.
- **Mutable**: Dictionaries are mutable, meaning that you can add, modify, or remove key-value pairs as needed.
- **Dynamic**: Dictionaries are dynamic, meaning that you can add, modify, or remove key-value pairs as needed.
- **Unique Keys**: Dictionary keys must be unique. If you try to create a dictionary with duplicate keys, the last key-value pair will overwrite the previous one.
- **Key-Value Pairs**: Dictionaries are key-value pairs, meaning that each item consists of a key and a value separated by a colon `:`.
- **Keys**: Dictionary keys can be any immutable data type, such as strings, numbers, or tuples. Dictionary keys must be unique.
- **Values**: Dictionary values can be any data type, such as strings, numbers, lists, or tuples. Dictionary values can be duplicates.
- **Length**: The length of a dictionary is the number of key-value pairs it contains. You can use the `len()` function to get the length of a dictionary.
- **Access**: You can access dictionary items by their keys. If you try to access a key that does not exist, you will get a `KeyError` exception.
- **Membership**: You can check if a key exists in a dictionary using the `in` operator. If you try to check if a key that does not exist, you will get a `KeyError` exception.
- **Iteration**: You can iterate over a dictionary using a `for` loop. When you iterate over a dictionary, you get the keys of the dictionary.
- **Copying**: You can copy a dictionary using the `copy()` method. The copy is a shallow copy, meaning that the keys and values are not copied.
