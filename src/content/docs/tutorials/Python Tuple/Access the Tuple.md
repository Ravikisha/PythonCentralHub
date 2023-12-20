---
title: Access the Tuple
description: Learn how to access the tuple in Python. How to access the tuple elements using the index number. How to access the tuple elements using the negative index number. How to access the tuple elements using the range of index numbers. How to access the tuple elements using the range of negative index numbers.
sidebar: 
    order: 53
---

<!-- 
```python title="empty_list.py" showLineNumbers{1} {1}
empty_list = []
print(empty_list)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python empty_list.py
[]
```

In this example, we declare an empty list and assign it to the variable `empty_list`. We then print the list to the console. The output shows that the list is empty. -->

## Navigate Tuple Items: A Guide to Access the Tuple List
In Python, Tuple is an immutable sequence of elements. It means that once a tuple is created, we cannot change its values. We can access the tuple elements using the index number. We can also access the tuple elements using the negative index number. We can also access the tuple elements using the range of index numbers. We can also access the tuple elements using the range of negative index numbers.

## Basic of Tuple Indexing
In Python, we can access the tuple elements using the index number. The index number starts from 0. We can also access the tuple elements using the negative index number. The negative index number starts from -1. We can also access the tuple elements using the range of index numbers. We can also access the tuple elements using the range of negative index numbers.

## Access the Tuple Elements Using the Index Number
In Python, we can access the tuple elements using the index number. The index number starts from 0. We can access the tuple elements using the index number by using the following syntax.

```python title="list_index.py" showLineNumbers{1} {1-5}
data = ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j')
print(data[0])
print(data[1])
print(data[2])
print(data[3])
```

Output:

```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\username>python list_index.py
a
b
c
d
```

In this example, we declare a tuple and assign it to the variable `data`. We then print the tuple elements using the index number. The output shows that the tuple elements are accessed using the index number.

## Access the Tuple Elements Using the Negative Index Number
In Python, we can access the tuple elements using the negative index number. The negative index number starts from -1. We can access the tuple elements using the negative index number by using the following syntax.

```python title="list_index.py" showLineNumbers{1} {1-5}
data = ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j')
print(data[-1])
print(data[-2])
print(data[-3])
print(data[-4])
```

Output:

```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\username>python list_index.py
j
i
h
g
```

In this example, we declare a tuple and assign it to the variable `data`. We then print the tuple elements using the negative index number. The output shows that the tuple elements are accessed using the negative index number.

## Diagram of Tuple Indexing
The following diagram illustrates the indexing of a tuple with five elements:

```python title="list_indexing.py" showLineNumbers{1} {1,3-7}
my_list = ('a', 'b', 'c', 'd', 'e')
```

| Element | 'a' | 'b' | 'c' | 'd' | 'e' |
| --- | --- | --- | --- | --- | --- |
| Index | 0 | 1 | 2 | 3 | 4 |
| Index (Negative) | -5 | -4 | -3 | -2 | -1 |

## Accessing Multidimensional Tuples
In Python, Multidimensional Tuples are tuples that contain other tuples. We can access the tuple elements using the index number. We can also access the tuple elements using the negative index number. We can also access the tuple elements using the range of index numbers. We can also access the tuple elements using the range of negative index numbers.

Example:
```python title="multidimensional_tuple.py" showLineNumbers{1} {1-5}
data = (('a', 'b', 'c'), ('d', 'e', 'f'), ('g', 'h', 'i'))
print(data[0])
print(data[1])
print(data[2])
```

Output:

```cmd title="command" showLineNumbers{1} {2-4}
C:\Users\username>python multidimensional_tuple.py
('a', 'b', 'c')
('d', 'e', 'f')
('g', 'h', 'i')
```

In this example, we declare a multidimensional tuple and assign it to the variable `data`. We then print the tuple elements using the index number. The output shows that the tuple elements are accessed using the index number.

### Accessing Elements of Multidimensional Tuples
You can access the elements of a multidimensional tuple by using the index number. The index number starts from 0. We can also access the tuple elements using the negative index number. The negative index number starts from -1. We can also access the tuple elements using the range of index numbers. We can also access the tuple elements using the range of negative index numbers.

Example:
```python title="multidimensional_tuple.py" showLineNumbers{1} {1-5}
data = (('a', 'b', 'c'), ('d', 'e', 'f'), ('g', 'h', 'i'))
print(data[0][0])
print(data[1][1])
print(data[2][2])
```

Output:

```cmd title="command" showLineNumbers{1} {2-4}
C:\Users\username>python multidimensional_tuple.py
a
e
i
```

In this example, we declare a multidimensional tuple and assign it to the variable `data`. We then print the tuple elements using the index number. The output shows that the tuple elements are accessed using the index number.

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

## Access the Tuple Elements Using the Range of Index Numbers
In Python, we can access the tuple elements using the range of index numbers. We can access the tuple elements using the range of index numbers by using the following syntax.

```python title="list_index.py" showLineNumbers{1} {1-5}
data = ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j')
print(data[0:4])
print(data[1:5])
print(data[2:6])
print(data[3:7])
```

Output:

```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\username>python list_index.py
('a', 'b', 'c', 'd')
('b', 'c', 'd', 'e')
('c', 'd', 'e', 'f')
('d', 'e', 'f', 'g')
```

In this example, we declare a tuple and assign it to the variable `data`. We then print the tuple elements using the range of index numbers. The output shows that the tuple elements are accessed using the range of index numbers.

## Access the Tuple Elements Using the Range of Negative Index Numbers
In Python, we can access the tuple elements using the range of negative index numbers. We can access the tuple elements using the range of negative index numbers by using the following syntax.

```python title="list_index.py" showLineNumbers{1} {1-5}
data = ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j')
print(data[-4:-1])
print(data[-5:-2])
print(data[-6:-3])
print(data[-7:-4])
```

Output:

```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\username>python list_index.py
('g', 'h', 'i')
('f', 'g', 'h')
('e', 'f', 'g')
('d', 'e', 'f')
```

In this example, we declare a tuple and assign it to the variable `data`. We then print the tuple elements using the range of negative index numbers. The output shows that the tuple elements are accessed using the range of negative index numbers.

