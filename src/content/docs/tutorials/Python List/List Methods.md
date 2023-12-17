---
title: List Methods
description: Learn how to use list methods in Python. Here you will find a list of all the methods that you can use with lists. you will also find examples of how to use them. you can find insert, append, extend, remove, pop, clear, index, count, sort, reverse, copy, and more.
sidebar: 
    order: 51
---

# List Methods
The list data type has a set of built-in methods that you can use on lists. In this tutorial, you will learn how to use list methods in Python. Here you will find a list of all the methods that you can use with lists. you will also find examples of how to use them. you can find insert, append, extend, remove, pop, clear, index, count, sort, reverse, copy, and more. 

## Table of Methods
There are many methods that you can use with lists. Here is a list of all the methods that you can use with lists.

|S.No|Method|Description|Example|
|----|------|-----------|-------|
|1|[append()](#append)|Adds an element at the end of the list|`list.append(element)`|
|2|[clear()](#clear)|Removes all the elements from the list|`list.clear()`|
|3|[copy()](#copy)|Returns a copy of the list|`list.copy()`|
|4|[count()](#count)|Returns the number of elements with the specified value|`list.count(value)`|
|5|[extend()](#extend)|Add the elements of a list (or any iterable), to the end of the current list|`list.extend(iterable)`|
|6|[index()](#index)|Returns the index of the first element with the specified value|`list.index(value)`|
|7|[insert()](#insert)|Adds an element at the specified position|`list.insert(position, element)`|
|8|[pop()](#pop)|Removes the element at the specified position|`list.pop(position)`|
|9|[remove()](#remove)|Removes the first item with the specified value|`list.remove(value)`|
|10|[reverse()](#reverse)|Reverses the order of the list|`list.reverse()`|
|11|[sort()](#sort)|Sorts the list|`list.sort()`|
|12|[len()](#len)|Returns the length of the list|`len(list)`|
|13|[max()](#max)|Returns the largest item in the list|`max(list)`|
|14|[min()](#min)|Returns the smallest item in the list|`min(list)`|
|15|[sum()](#sum)|Returns the sum of all items in the list|`sum(list)`|
|16|[all()](#all)|Returns True if all items in the list are true|`all(list)`|
|17|[any()](#any)|Returns True if any item in the list is true|`any(list)`|
|18|[enumerate()](#enumerate)|Returns an enumerate object. It contains the index and value of all the items in the list|`enumerate(list)`|
|19|[filter()](#filter)|Use a filter function to exclude items in an iterable object|`filter(function, iterable)`|
|20|[map()](#map)|Use a map function to execute a specified function for each item in an iterable. The item is sent to the function as a parameter|`map(function, iterable)`|
|21|[reversed()](#reversed)|Returns a reversed iterator|`reversed(list)`|
|22|[sorted()](#sorted)|Returns a sorted list|`sorted(list)`|
|23|[zip()](#zip)|Returns an iterator, from two or more iterators|`zip(iterator1, iterator2, iterator3, ...)`|
|24|[del](#del)|Removes the specified index|`del list[index]`|
|25|[in](#in)|Returns True if a sequence with the specified value is present in the list|`element in list`|
|26|[not in](#not-in)|Returns True if a sequence with the specified value is not present in the list|`element not in list`|


## append()
The `append()` method adds an element at the end of the list. The syntax of the `append()` method is: `list.append(element)`. Here is an example:
```python title="append.py" showLineNumbers{1} {2}
fruits = ['apple', 'banana', 'cherry']
fruits.append("orange")
print(fruits)
```

Output:
```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python append.py
['apple', 'banana', 'cherry', 'orange']
```

## clear()
The `clear()` method removes all the elements from the list. The syntax of the `clear()` method is: `list.clear()`. Here is an example:
```python title="clear.py" showLineNumbers{1} {2}
fruits = ['apple', 'banana', 'cherry']
fruits.clear()
print(fruits)
```

Output:
```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python clear.py
[]
```

## copy()
The `copy()` method returns a copy of the list. The syntax of the `copy()` method is: `list.copy()`. Here is an example:
```python title="copy.py" showLineNumbers{1} {2}
fruits = ['apple', 'banana', 'cherry']
fruits_copy = fruits.copy()
print(fruits_copy)
```

Output:
```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python copy.py
['apple', 'banana', 'cherry']
```

## count()
The `count()` method returns the number of elements with the specified value. The syntax of the `count()` method is: `list.count(value)`. Here is an example:
```python title="count.py" showLineNumbers{1} {2}
fruits = ['apple', 'banana', 'cherry', 'banana']
count = fruits.count("banana")
print(count)
```

Output:
```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python count.py
2
```

## extend()
The `extend()` method adds the elements of a list (or any iterable), to the end of the current list. The syntax of the `extend()` method is: `list.extend(iterable)`. Here is an example:
```python title="extend.py" showLineNumbers{1} {2}
fruits = ['apple', 'banana', 'cherry']
more_fruits = ['orange', 'mango', 'grapes']
fruits.extend(more_fruits)
print(fruits)
```

Output:
```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python extend.py
['apple', 'banana', 'cherry', 'orange', 'mango', 'grapes']
```

## index()
The `index()` method returns the index of the first element with the specified value. The syntax of the `index()` method is: `list.index(value)`. Here is an example:
```python title="index.py" showLineNumbers{1} {2}
fruits = ['apple', 'banana', 'cherry']
index = fruits.index("banana")
print(index)
```

Output:
```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python index.py
1
```

## insert()
The `insert()` method adds an element at the specified position. The syntax of the `insert()` method is: `list.insert(position, element)`. Here is an example:
```python title="insert.py" showLineNumbers{1} {2}
fruits = ['apple', 'banana', 'cherry']
fruits.insert(1, "orange")
print(fruits)
```

Output:
```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python insert.py
['apple', 'orange', 'banana', 'cherry']
```

## pop()
The `pop()` method removes the element at the specified position. The syntax of the `pop()` method is: `list.pop(position)`. Here is an example:
```python title="pop.py" showLineNumbers{1} {2}
fruits = ['apple', 'banana', 'cherry']
fruits.pop(1)
print(fruits)
```

Output:
```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python pop.py
['apple', 'cherry']
```

## remove()
The `remove()` method removes the first item with the specified value. The syntax of the `remove()` method is: `list.remove(value)`. Here is an example:
```python title="remove.py" showLineNumbers{1} {2}
fruits = ['apple', 'banana', 'cherry']
fruits.remove("banana")
print(fruits)
```

Output:
```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python remove.py
['apple', 'cherry']
```

## reverse()
The `reverse()` method reverses the order of the list. The syntax of the `reverse()` method is: `list.reverse()`. Here is an example:
```python title="reverse.py" showLineNumbers{1} {2}
fruits = ['apple', 'banana', 'cherry']
fruits.reverse()
print(fruits)
```

Output:
```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python reverse.py
['cherry', 'banana', 'apple']
```

## sort()
The `sort()` method sorts the list. The syntax of the `sort()` method is: `list.sort()`. Here is an example:
```python title="sort.py" showLineNumbers{1} {2}
fruits = ['apple', 'banana', 'cherry']
fruits.sort()
print(fruits)
```

Output:
```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python sort.py
['apple', 'banana', 'cherry']
```

## len()
The `len()` method returns the length of the list. The syntax of the `len()` method is: `len(list)`. Here is an example:
```python title="len.py" showLineNumbers{1} {2}
fruits = ['apple', 'banana', 'cherry']
length = len(fruits)
print(length)
```

Output:
```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python len.py
3
```

## max()
The `max()` method returns the largest item in the list. The syntax of the `max()` method is: `max(list)`. Here is an example:
```python title="max.py" showLineNumbers{1} {2}
numbers = [1, 2, 3, 4, 5]
max_number = max(numbers)
print(max_number)
```

Output:
```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python max.py
5
```

## min()
The `min()` method returns the smallest item in the list. The syntax of the `min()` method is: `min(list)`. Here is an example:
```python title="min.py" showLineNumbers{1} {2}
numbers = [1, 2, 3, 4, 5]
min_number = min(numbers)
print(min_number)
```

Output:
```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python min.py
1
```

## sum()
The `sum()` method returns the sum of all items in the list. The syntax of the `sum()` method is: `sum(list)`. Here is an example:
```python title="sum.py" showLineNumbers{1} {2}
numbers = [1, 2, 3, 4, 5]
sum_numbers = sum(numbers)
print(sum_numbers)
```

Output:
```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python sum.py
15
```

## all()
The `all()` method returns True if all items in the list are true. The syntax of the `all()` method is: `all(list)`. Here is an example:
```python title="all.py" showLineNumbers{1} {2}
numbers = [1, 2, 3, 4, 5]
all_numbers = all(numbers)
print(all_numbers)
```

Output:
```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python all.py
True
```

## any()
The `any()` method returns True if any item in the list is true. The syntax of the `any()` method is: `any(list)`. Here is an example:
```python title="any.py" showLineNumbers{1} {2}
numbers = [1, 2, 3, 4, 5]
any_numbers = any(numbers)
print(any_numbers)
```

Output:
```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python any.py
True
```

## enumerate()
The `enumerate()` method returns an enumerate object. It contains the index and value of all the items in the list. The syntax of the `enumerate()` method is: `enumerate(list)`. Here is an example:
```python title="enumerate.py" showLineNumbers{1} {2}
numbers = [1, 2, 3, 4, 5]
enumerate_numbers = enumerate(numbers)
print(enumerate_numbers)
print(list(enumerate_numbers))
```

Output:
```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python enumerate.py
<enumerate object at 0x0000020F7F7F4F00>
[(0, 1), (1, 2), (2, 3), (3, 4), (4, 5)]
```

## filter()
The `filter()` method uses a filter function to exclude items in an iterable object. The syntax of the `filter()` method is: `filter(function, iterable)`. Here is an example:
```python title="filter.py" showLineNumbers{1} {1-2,5}
def is_even(number):
    return number % 2 == 0

numbers = [1, 2, 3, 4, 5]
even_numbers = filter(is_even, numbers)
print(even_numbers)
print(list(even_numbers))
```

Output:
```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python filter.py
<filter object at 0x0000020F7F7F4F00>
[2, 4]
```

## map()
The `map()` method uses a map function to execute a specified function for each item in an iterable. The item is sent to the function as a parameter. The syntax of the `map()` method is: `map(function, iterable)`. Here is an example:
```python title="map.py" showLineNumbers{1} {1-2,5}
def square(number):
    return number * number

numbers = [1, 2, 3, 4, 5]
squared_numbers = map(square, numbers)
print(squared_numbers)
print(list(squared_numbers))
```

Output:
```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python map.py
<map object at 0x0000020F7F7F4F00>
[1, 4, 9, 16, 25]
```

## reversed()
The `reversed()` method returns a reversed iterator. The syntax of the `reversed()` method is: `reversed(list)`. Here is an example:
```python title="reversed.py" showLineNumbers{1} {2}
numbers = [1, 2, 3, 4, 5]
reversed_numbers = reversed(numbers)
print(reversed_numbers)
print(list(reversed_numbers))
```

Output:
```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python reversed.py
<list_reverseiterator object at 0x0000020F7F7F4F00>
[5, 4, 3, 2, 1]
```

## sorted()
The `sorted()` method returns a sorted list. The syntax of the `sorted()` method is: `sorted(list)`. Here is an example:
```python title="sorted.py" showLineNumbers{1} {2}
numbers = [5, 2, 3, 1, 4]
sorted_numbers = sorted(numbers)
print(sorted_numbers)
```

Output:
```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python sorted.py
[1, 2, 3, 4, 5]
```

## zip()
The `zip()` method returns an iterator, from two or more iterators. The syntax of the `zip()` method is: `zip(iterator1, iterator2, iterator3, ...)`. Here is an example:
```python title="zip.py" showLineNumbers{1} {3}
numbers = [1, 2, 3, 4, 5]
fruits = ['apple', 'banana', 'cherry']
zipped = zip(numbers, fruits)
print(zipped)
print(list(zipped))
```

Output:
```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python zip.py
<zip object at 0x0000020F7F7F4F00>
[(1, 'apple'), (2, 'banana'), (3, 'cherry')]
```

## del
The `del` keyword removes the specified index. The syntax of the `del` keyword is: `del list[index]`. Here is an example:
```python title="del.py" showLineNumbers{1} {2}
fruits = ['apple', 'banana', 'cherry']
del fruits[1]
print(fruits)
```

Output:
```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python del.py
['apple', 'cherry']
```

## in
The `in` keyword returns True if a sequence with the specified value is present in the list. The syntax of the `in` keyword is: `element in list`. Here is an example:
```python title="in.py" showLineNumbers{1} {2-3}
fruits = ['apple', 'banana', 'cherry']
print("banana" in fruits)
print("orange" in fruits)
```

Output:
```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python in.py
True
False
```

## not in
The `not in` keyword returns True if a sequence with the specified value is not present in the list. The syntax of the `not in` keyword is: `element not in list`. Here is an example:
```python title="not-in.py" showLineNumbers{1} {2-3}
fruits = ['apple', 'banana', 'cherry']
print("banana" not in fruits)
print("orange" not in fruits)
```

Output:
```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python not-in.py
False
True
```

## Conclusion
In this tutorial, you learned how to use list methods in Python. Here you found a list of all the methods that you can use with lists. you also found examples of how to use them. you can find insert, append, extend, remove, pop, clear, index, count, sort, reverse, copy, and more. Now you can use these methods in your Python programs. For more information, visit the [official Python documentation](https://docs.python.org/3/tutorial/datastructures.html#more-on-lists).
