---
title: Tuple Operations
description: Learn how to perform various operations on the tuple in Python. The tuple is an immutable data type in Python. It means we can not modify the tuple elements. We can perform various operations on the tuple in Python. 
sidebar: 
    order: 56
---

Tuple is an immutable data type in Python. It means we can not modify the tuple elements. We can perform various operations on the tuple in Python. We will learn how to perform various operations on the tuple in Python.

## Traversing a Tuple
There are multiple ways to traverse a tuple in Python. We can use the `for` loop to traverse a tuple. We can also use the `while` loop to traverse a tuple. We can also use the `enumerate()` function to traverse a tuple. we are going to learn all the methods to traverse a tuple in Python.
<!-- 
```python title="syntax.py" showLineNumbers{1} {1}
list[index] = new_value
```

The following example shows how to change the first item in the list to a different value.

```python title="change_first_item.py" showLineNumbers{1} {1,4}
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

### Using for Loop
We can use the `for` loop to traverse a tuple in Python. We will use the `for` loop to traverse the tuple elements one by one. We will use the `for` loop with the `in` keyword to traverse the tuple elements. 

The following example shows how to traverse a tuple using the `for` loop.

```python title="traverse_tuple.py" showLineNumbers{1} {1,4}
numbers = (1, 2, 3, 4, 5)

for number in numbers:
    print(number)
```

Output:

```cmd title="command" showLineNumbers{1} {2-6}
C:\Users\username>python traverse_tuple.py
1
2
3
4
5
```

In the example above, we have a tuple of numbers. We used the `for` loop to traverse the tuple elements one by one. We used the `for` loop with the `in` keyword to traverse the tuple elements.

### Using while Loop
We can also use the `while` loop to traverse a tuple in Python. We will use the `while` loop to traverse the tuple elements one by one. We will use the `while` loop with the `len()` function to traverse the tuple elements.

The following example shows how to traverse a tuple using the `while` loop.

```python title="traverse_tuple.py" showLineNumbers{1} {1,3, 5-8}
numbers = (1, 2, 3, 4, 5)

index = 0

while index < len(numbers):
    print(numbers[index])
    index += 1
```

Output:

```cmd title="command" showLineNumbers{1} {2-8}
C:\Users\username>python traverse_tuple.py
1
2
3
4
5
```

In the example above, we have a tuple of numbers. We used the `while` loop to traverse the tuple elements one by one. We used the `while` loop with the `len()` function to traverse the tuple elements.

### Using enumerate() Function
We can also use the `enumerate()` function to traverse a tuple in Python. We will use the `enumerate()` function to traverse the tuple elements one by one. We will use the `enumerate()` function with the `for` loop to traverse the tuple elements.

The following example shows how to traverse a tuple using the `enumerate()` function.

```python title="traverse_tuple.py" showLineNumbers{1} {1,3-4}
numbers = (1, 2, 3, 4, 5)

for index, number in enumerate(numbers):
    print(number)
```

Output:

```cmd title="command" showLineNumbers{1} {2-6}
C:\Users\username>python traverse_tuple.py
1
2
3
4
5
```

In the example above, we have a tuple of numbers. We used the `enumerate()` function to traverse the tuple elements one by one. We used the `enumerate()` function with the `for` loop to traverse the tuple elements.

### Using range() Function
We can also use the `range()` function to traverse a tuple in Python. We will use the `range()` function to traverse the tuple elements one by one. We will use the `range()` function with the `for` loop to traverse the tuple elements.

The following example shows how to traverse a tuple using the `range()` function.

```python title="traverse_tuple.py" showLineNumbers{1} {1,3-4}
numbers = (1, 2, 3, 4, 5)

for index in range(len(numbers)):
    print(numbers[index])
```

Output:

```cmd title="command" showLineNumbers{1} {2-6}
C:\Users\username>python traverse_tuple.py
1
2
3
4
5
```

In the example above, we have a tuple of numbers. We used the `range()` function to traverse the tuple elements one by one. We used the `range()` function with the `for` loop to traverse the tuple elements.

