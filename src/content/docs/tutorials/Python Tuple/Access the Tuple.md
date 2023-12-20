---
title: Access the Tuple
description: Learn how to access the tuple in Python. How to access the tuple elements using the index number. How to access the tuple elements using the negative index number. How to access the tuple elements using the range of index numbers. How to access the tuple elements using the range of negative index numbers.
sidebar: 
    order: 53
---

## Navigate Tuple Items: A Guide to Access the Tuple List
In Python, Tuple is an immutable sequence of elements. It means that once a tuple is created, we cannot change its values. We can access the tuple elements using the index number. We can also access the tuple elements using the negative index number. We can also access the tuple elements using the range of index numbers. We can also access the tuple elements using the range of negative index numbers.

## Basic of Tuple Indexing
In Python, we can access the tuple elements using the index number. The index number starts from 0. We can also access the tuple elements using the negative index number. The negative index number starts from -1. We can also access the tuple elements using the range of index numbers. We can also access the tuple elements using the range of negative index numbers.

## Access the Tuple Elements Using the Index Number
In Python, we can access the tuple elements using the index number. The index number starts from 0. We can access the tuple elements using the index number by using the following syntax.

```python title="tuple_index.py" showLineNumbers{1} {1-5}
data = ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j')
print(data[0])
print(data[1])
print(data[2])
print(data[3])
```

Output:

```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\username>python tuple_index.py
a
b
c
d
```

In this example, we declare a tuple and assign it to the variable `data`. We then print the tuple elements using the index number. The output shows that the tuple elements are accessed using the index number.

## Access the Tuple Elements Using the Negative Index Number
In Python, we can access the tuple elements using the negative index number. The negative index number starts from -1. We can access the tuple elements using the negative index number by using the following syntax.

```python title="tuple_index.py" showLineNumbers{1} {1-5}
data = ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j')
print(data[-1])
print(data[-2])
print(data[-3])
print(data[-4])
```

Output:

```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\username>python tuple_index.py
j
i
h
g
```

In this example, we declare a tuple and assign it to the variable `data`. We then print the tuple elements using the negative index number. The output shows that the tuple elements are accessed using the negative index number.

## Diagram of Tuple Indexing
The following diagram illustrates the indexing of a tuple with five elements:

```python title="tuple_indexing.py" showLineNumbers{1} {1,3-7}
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

```python title="tuple_index.py" showLineNumbers{1} {1-5}
data = ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j')
print(data[0:4])
print(data[1:5])
print(data[2:6])
print(data[3:7])
```

Output:

```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\username>python tuple_index.py
('a', 'b', 'c', 'd')
('b', 'c', 'd', 'e')
('c', 'd', 'e', 'f')
('d', 'e', 'f', 'g')
```

In this example, we declare a tuple and assign it to the variable `data`. We then print the tuple elements using the range of index numbers. The output shows that the tuple elements are accessed using the range of index numbers.

## Accessing tuple Slices
tuple slices are a way of accessing a subset of a tuple. In Python, tuple slices are created using the syntax `tuple[start:stop]`, where `start` is the index of the first element to include in the slice and `stop` is the index of the first element to exclude from the slice. If `start` is omitted, it defaults to 0, and if `stop` is omitted, it defaults to the length of the tuple.

**Syntax**:
```python title="syntax.py" showLineNumbers{1} {1,3-4}
tuple[start:stop]
```

### Access the Tuple Elements Using the Range of Negative Index Numbers
In Python, we can access the tuple elements using the range of negative index numbers. We can access the tuple elements using the range of negative index numbers by using the following syntax.

```python title="tuple_index.py" showLineNumbers{1} {1-5}
data = ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j')
print(data[-4:-1])
print(data[-5:-2])
print(data[-6:-3])
print(data[-7:-4])
```

Output:

```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\username>python tuple_index.py
('g', 'h', 'i')
('f', 'g', 'h')
('e', 'f', 'g')
('d', 'e', 'f')
```

In this example, we declare a tuple and assign it to the variable `data`. We then print the tuple elements using the range of negative index numbers. The output shows that the tuple elements are accessed using the range of negative index numbers.

### Access the Tuple Elements Using the Range of Index Numbers and Negative Index Numbers
In Python, we can access the tuple elements using the range of index numbers and negative index numbers. We can access the tuple elements using the range of index numbers and negative index numbers by using the following syntax.

```python title="tuple_index.py" showLineNumbers{1} {1-5}
data = ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j')
print(data[0:-1])
print(data[1:-2])
print(data[2:-3])
print(data[3:-4])
```

Output:

```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\username>python tuple_index.py
('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i')
('b', 'c', 'd', 'e', 'f', 'g', 'h')
('c', 'd', 'e', 'f', 'g')
('d', 'e', 'f')
```

In this example, we declare a tuple and assign it to the variable `data`. We then print the tuple elements using the range of index numbers and negative index numbers. The output shows that the tuple elements are accessed using the range of index numbers and negative index numbers.

### Access the Tuple Elements Using Step
In Python, we can access the tuple elements using the range of negative index numbers and index numbers and step. We can access the tuple elements using the range of negative index numbers and index numbers and step by using the following syntax.

```python title="syntax.py" showLineNumbers{1} {1,3-4}
tuple[start:stop:step]
```

Example:
```python title="tuple_index.py" showLineNumbers{1} {1-5}
data = ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j')
print(data[0:-1:2])
print(data[1:-2:2])
print(data[2:-3:2])
print(data[3:-4:2])
```

Output:

```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\username>python tuple_index.py
('a', 'c', 'e', 'g', 'i')
('b', 'd', 'f', 'h')
('c', 'e', 'g')
('d', 'f')
```

In this example, we declare a tuple and assign it to the variable `data`. We then print the tuple elements using the range of negative index numbers and index numbers and step. The output shows that the tuple elements are accessed using the range of negative index numbers and index numbers and step.

### Omitting the Start and Stop Indices
In Python, we can omit the start and stop indices. We can omit the start and stop indices by using the following syntax.

```python title="syntax.py" showLineNumbers{1} {1-2}
tuple[start:]
tuple[:stop]
```

Example:
```python title="tuple_index.py" showLineNumbers{1} {1-5}
data = ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j')
print(data[0:])
print(data[:5])
print(data[2:])
print(data[:7])
```

Output:

```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\username>python tuple_index.py
('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j')
('a', 'b', 'c', 'd', 'e')
('c', 'd', 'e', 'f', 'g', 'h', 'i', 'j')
('a', 'b', 'c', 'd', 'e', 'f', 'g')
```

In this example, we declare a tuple and assign it to the variable `data`. We then print the tuple elements using the range of negative index numbers and index numbers and step. The output shows that the tuple elements are accessed using the range of negative index numbers and index numbers and step.

In Slicing, when you omit the start index, it defaults to 0. When you omit the stop index, it defaults to the length of the tuple. 

`data[0:]` -> `data[0:len(data)]`
`data[:5]` -> `data[0:5]`
`data[2:]` -> `data[2:len(data)]`
`data[:7]` -> `data[0:7]`

### Omitting the Start and Stop Indices with Step
In Python, we can omit the start and stop indices with step. We can omit the start and stop indices with step by using the following syntax.

```python title="syntax.py" showLineNumbers{1} {1-2}
tuple[start::step]
tuple[:stop:step]
```

Example:
```python title="tuple_index.py" showLineNumbers{1} {1-5}
data = ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j')
print(data[0::2])
print(data[:5:2])
print(data[2::2])
print(data[:7:2])
```

Output:

```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\username>python tuple_index.py
('a', 'c', 'e', 'g', 'i')
('a', 'c', 'e')
('c', 'e', 'g', 'i')
('a', 'c', 'e', 'g')
```

In this example, we declare a tuple and assign it to the variable `data`. We then print the tuple elements using the range of negative index numbers and index numbers and step. The output shows that the tuple elements are accessed using the range of negative index numbers and index numbers and step.

In Slicing, when you omit the start index, it defaults to 0. When you omit the stop index, it defaults to the length of the tuple.

`data[0::2]` -> `data[0:len(data):2]`
`data[:5:2]` -> `data[0:5:2]`
`data[2::2]` -> `data[2:len(data):2]`
`data[:7:2]` -> `data[0:7:2]`

### Omitting the Start and Stop Indices with Negative Step
In Python, we can omit the start and stop indices with negative step. We can omit the start and stop indices with negative step by using the following syntax.

```python title="syntax.py" showLineNumbers{1} {1-2}
tuple[start::-step]
tuple[:stop:-step]
```

Example:
```python title="tuple_index.py" showLineNumbers{1} {1-5}
data = ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j')
print(data[0::-2])
print(data[:5:-2])
print(data[2::-2])
print(data[:7:-2])
```

Output:

```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\username>python tuple_index.py
('a',)
('j', 'h', 'f')
('c', 'a')
('j', 'h', 'f', 'd')
```

In this example, we declare a tuple and assign it to the variable `data`. We then print the tuple elements using the range of negative index numbers and index numbers and step. The output shows that the tuple elements are accessed using the range of negative index numbers and index numbers and step.

`data[0::-2]` -> `data[0: len(data): -2]`
`data[:5:-2]` -> `data[0:5: -2]`
`data[2::-2]` -> `data[2: len(data): -2]`
`data[:7:-2]` -> `data[0:7: -2]`

### Omitting the Both Indices
In Python, we can omit the both indices. We can omit the both indices by using the following syntax.

```python title="syntax.py" showLineNumbers{1} {1}
tuple[::step]
```

Example:
```python title="tuple_index.py" showLineNumbers{1} {1-5}
data = ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j')
print(data[::2])
print(data[::3])
print(data[::4])
print(data[::5])
```

Output:

```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\username>python tuple_index.py
('a', 'c', 'e', 'g', 'i')
('a', 'd', 'g', 'j')
('a', 'e', 'i')
('a', 'f')
```

In this example, we declare a tuple and assign it to the variable `data`. We then print the tuple elements using the range of negative index numbers and index numbers and step. The output shows that the tuple elements are accessed using the range of negative index numbers and index numbers and step.

`data[::2]` -> `data[0: len(data): 2]`
`data[::3]` -> `data[0: len(data): 3]`
`data[::4]` -> `data[0: len(data): 4]`
`data[::5]` -> `data[0: len(data): 5]`

### Slicing with Negative Indices
In Python, we can slice with negative indices. We can slice with negative indices by using the following syntax.

```python title="syntax.py" showLineNumbers{1} {1}
tuple[start:stop:step]
```

Example:
```python title="tuple_index.py" showLineNumbers{1} {1-5}
data = ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j')
print(data[-1::-2])
print(data[-2::-2])
print(data[:-3:-2])
print(data[-4::-2])
```

Output:

```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\username>python tuple_index.py
('j', 'h', 'f', 'd', 'b')
('i', 'g', 'e', 'c', 'a')
('j',)
('g', 'e', 'c', 'a')
```

In this example, we declare a tuple and assign it to the variable `data`. We then print the tuple elements using the range of negative index numbers and index numbers and step. The output shows that the tuple elements are accessed using the range of negative index numbers and index numbers and step.

`data[-1::-2]` -> `data[-1: len(data): -2]`
`data[-2::-2]` -> `data[-2: len(data): -2]`
`data[:-3:-2]` -> `data[0: -3: -2]`
`data[-4::-2]` -> `data[-4: len(data): -2]`

## Conclusion
In this tutorial, we learned how to access the tuple in Python. We learned how to access the tuple elements using the index number. We learned how to access the tuple elements using the negative index number. We learned how to access the tuple elements using the range of index numbers. We learned how to access the tuple elements using the range of negative index numbers. For more information on tuples, visit the [Python Tuple](https://docs.python.org/3/tutorial/datastructures.html#tuples-and-sequences) documentation page.