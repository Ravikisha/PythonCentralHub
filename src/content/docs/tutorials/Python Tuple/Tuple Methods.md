---
title: Tuple Methods
description: Learn how to use tuple methods in Python. How many methods are available for tuples? What are they? How do you use them? Find out here. We are going to use multiple examples to demonstrate how to use tuple methods in Python.
sidebar: 
    order: 57
---


<!-- ```python title="change_first_item.py" showLineNumbers{1} {1,4}
numbers = [1, 2, 3, 4, 5]
print(numbers)

numbers[0] = 10
print(numbers)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python change_first_item.py
[1, 2, 3, 4, 5]
[10, 2, 3, 4, 5]
```

In the example above, we changed the first item in the list to 10. The rest of the items in the list remain the same. -->

## Tuple Methods
The tuple data type has only two methods. They are `count()` and `index()`. Let's look at each of them in detail. you will learn how to use them with examples.

## Table of Methods

|S.No|Method|Description|Example|
|----|------|-----------|-------|
|1|count()|Returns the number of times a specified value occurs in a tuple|`tuple.count(value)`|
|2|index()|Searches the tuple for a specified value and returns the position of where it was found|`tuple.index(value)`|
|3|len()|Returns the number of items in a tuple|`len(tuple)`|
|4|sorted()|Returns a new sorted list from elements in the tuple|`sorted(tuple)`|
|5|sum()|Sums the items of an iterable from left to right and returns the total|`sum(tuple)`|
|6|any()|Returns True if any element of the tuple is true. If the tuple is empty, returns False|`any(tuple)`|
|7|all()|Returns True if all elements of the tuple are true. If the tuple is empty, returns True|`all(tuple)`|
|8|enumerate()|Returns an enumerate object. It contains the index and value of all the items of tuple as a pair|`enumerate(tuple)`|
|9|filter()|Constructs iterator from elements of tuple for which function returns true|`filter(function, tuple)`|
|10|map()|Applies function to every item of iterable and returns a list of the results|`map(function, tuple)`|

## count() Method
The `count()` method returns the number of times a specified value appears in the tuple.

Here is an example:

```python title="tuple_methods.py" showLineNumbers{1} {1,3-7}
numbers = (1, 2, 3, 4, 5, 1, 2, 3, 1, 2, 1)

print(numbers.count(1))
print(numbers.count(2))
print(numbers.count(3))
print(numbers.count(4))
print(numbers.count(5))
```

Output:

```cmd title="command" showLineNumbers{1} {2-11}
C:\Users\username>python tuple_methods.py
4
3
2
1
1
```

In the example above, we have a tuple of numbers. We use the `count()` method to count the number of times each number appears in the tuple.

## index() Method
The `index()` method searches the tuple for a specified value and returns the position of where it was found.

Here is an example:

```python title="tuple_methods.py" showLineNumbers{1} {1,3-7}
numbers = (1, 2, 3, 4, 5, 1, 2, 3, 1, 2, 1)

print(numbers.index(1))
print(numbers.index(2))
print(numbers.index(3))
print(numbers.index(4))
print(numbers.index(5))
```

Output:

```cmd title="command" showLineNumbers{1} {2-11}
C:\Users\username>python tuple_methods.py
0
1
2
3
4
```

In the example above, we have a tuple of numbers. We use the `index()` method to find the position of each number in the tuple.

## len() Method
The `len()` method returns the number of items in a tuple.

Here is an example:

```python title="tuple_methods.py" showLineNumbers{1} {1,3-4}
numbers = (1, 2, 3, 4, 5, 1, 2, 3, 1, 2, 1)

print(len(numbers))
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python tuple_methods.py
11
```

In the example above, we have a tuple of numbers. We use the `len()` method to find the number of items in the tuple.

## sorted() Method
The `sorted()` method returns a new sorted list from elements in the tuple.

Here is an example:

```python title="tuple_methods.py" showLineNumbers{1} {1,3-4}
numbers = (1, 2, 3, 4, 5, 1, 2, 3, 1, 2, 1)

print(sorted(numbers))
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python tuple_methods.py
[1, 1, 1, 1, 2, 2, 2, 3, 3, 4, 5]
```

In the example above, we have a tuple of numbers. We use the `sorted()` method to sort the numbers in the tuple.

## sum() Method
The `sum()` method sums the items of an iterable from left to right and returns the total.

Here is an example:

```python title="tuple_methods.py" showLineNumbers{1} {1,3-4}
numbers = (1, 2, 3, 4, 5, 1, 2, 3, 1, 2, 1)

print(sum(numbers))
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python tuple_methods.py
25
```

In the example above, we have a tuple of numbers. We use the `sum()` method to sum the numbers in the tuple.

## any() Method
The `any()` method returns True if any element of the tuple is true. If the tuple is empty, it returns False.

Here is an example:

```python title="tuple_methods.py" showLineNumbers{1} {1,3-4}
numbers = (1, 2, 3, 4, 5, 1, 2, 3, 1, 2, 1)

print(any(numbers))
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python tuple_methods.py
True
```

In the example above, we have a tuple of numbers. We use the `any()` method to check if any of the numbers in the tuple is true.

## all() Method
The `all()` method returns True if all elements of the tuple are true. If the tuple is empty, it returns True.

Here is an example:

```python title="tuple_methods.py" showLineNumbers{1} {1,3-4}
numbers = (1, 2, 3, 4, 5, 1, 2, 3, 1, 2, 1)

print(all(numbers))
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python tuple_methods.py
True
```

In the example above, we have a tuple of numbers. We use the `all()` method to check if all of the numbers in the tuple are true.

## enumerate() Method
The `enumerate()` method returns an enumerate object. It contains the index and value of all the items of tuple as a pair.

Here is an example:

```python title="tuple_methods.py" showLineNumbers{1} {1,3-5}
numbers = (1, 2, 3, 4, 5, 1, 2, 3, 1, 2, 1)

for index, value in enumerate(numbers):
    print(index, value)
```

Output:

```cmd title="command" showLineNumbers{1} {2-12}
C:\Users\username>python tuple_methods.py
0 1
1 2
2 3
3 4
4 5
5 1
6 2
7 3
8 1
9 2
10 1
```

In the example above, we have a tuple of numbers. We use the `enumerate()` method to get the index and value of each number in the tuple.

## filter() Method
The `filter()` method constructs an iterator from elements of tuple for which function returns true.

Here is an example:

```python title="tuple_methods.py" showLineNumbers{1} {1,3-4, 6}
numbers = (1, 2, 3, 4, 5, 1, 2, 3, 1, 2, 1)

def is_even(number):
    return number % 2 == 0

even_numbers = tuple(filter(is_even, numbers))
print(even_numbers)
```

Output:

```cmd title="command" showLineNumbers{1} {2-4}
C:\Users\username>python tuple_methods.py
(2, 4, 2, 2)
```

In the example above, we have a tuple of numbers. We use the `filter()` method to filter out the even numbers from the tuple.

## map() Method
The `map()` method applies function to every item of iterable and returns a list of the results.

Here is an example:

```python title="tuple_methods.py" showLineNumbers{1} {1,3-4, 6}
numbers = (1, 2, 3, 4, 5, 1, 2, 3, 1, 2, 1)

def square(number):
    return number ** 2

squared_numbers = tuple(map(square, numbers))
print(squared_numbers)
```

Output:

```cmd title="command" showLineNumbers{1} {2-4}
C:\Users\username>python tuple_methods.py
(1, 4, 9, 16, 25, 1, 4, 9, 1, 4, 1)
```

In the example above, we have a tuple of numbers. We use the `map()` method to square each number in the tuple.

