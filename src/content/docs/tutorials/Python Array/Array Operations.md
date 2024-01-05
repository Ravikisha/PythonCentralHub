---
title: Array Operations
description: Learn how to perform operations on arrays. how to perform loop, copy, reverse, sort, search, and join operations on arrays.
sidebar: 
    order: 73
---

## Array Operations
In this tutorial, you will learn how to perform operations on arrays. how to perform loop, copy, reverse, sort, search, and join operations on arrays.

## Looping Array Elements
You can access the array elements by using the loop statement.

<!-- ```python title="array_append.py" showLineNumbers{1} {1,3-5}
import array as arr

my_array = arr.array('i', [1, 2, 3, 4, 5])
my_array.append(6)
print(my_array)
```

Output:
```cmd title="command" showLineNumbers{1} {2-6}
C:\Users\username>python array_append.py
array('i', [1, 2, 3, 4, 5, 6])
```

In the above example, we create an array of five elements and add a sixth element to the end of the array using the `append()` method. -->

### For Loop
The for loop is used to iterate over the array elements. The for loop is used to iterate over the array elements.

```python title="array_for_loop.py" showLineNumbers{1} {1, 3, 5-6}
import array as arr

my_array = arr.array('i', [1, 2, 3, 4, 5])

for i in my_array:
    print(i)
```

Output:

```cmd title="command" showLineNumbers{1} {2-8}
C:\Users\username>python array_for_loop.py
1
2
3
4
5
```

In the above example, we create an array of five elements and iterate over the array elements using the for loop.

### While Loop
The while loop is used to iterate over the array elements until the given condition is true.

```python title="array_while_loop.py" showLineNumbers{1} {1, 3, 5-7}
import array as arr

my_array = arr.array('i', [1, 2, 3, 4, 5])

i = 0
while i < len(my_array):
    print(my_array[i])
    i += 1
```

Output:

```cmd title="command" showLineNumbers{1} {2-8}
C:\Users\username>python array_while_loop.py
1
2
3
4
5
```

In the above example, we create an array of five elements and iterate over the array elements using the while loop.

### Using Range() Function
The range() function returns a sequence of numbers starting from zero to the specified number minus one.

```python title="array_range.py" showLineNumbers{1} {1, 3, 5-7}
import array as arr

my_array = arr.array('i', [1, 2, 3, 4, 5])

for i in range(len(my_array)):
    print(my_array[i])
```

Output:

```cmd title="command" showLineNumbers{1} {2-8}
C:\Users\username>python array_range.py
1
2
3
4
5
```

In the above example, we create an array of five elements and iterate over the array elements using the range() function.

## Copying Array
You can copy the array elements to another array using the `copy()` method and `deepcopy()` function.

### = operator
The `=` operator is used to copy the array elements to another array.

```python title="array_copy.py" showLineNumbers{1} {1, 3-4, 10}
import array as arr

my_array = arr.array('i', [1, 2, 3, 4, 5])
new_array = my_array

print("Before updating")
print(my_array)
print(new_array)

new_array[0] = 6

print("After updating")
print(my_array)
print(new_array)
```

Output:

```cmd title="command" showLineNumbers{1} {2-14}
C:\Users\username>python array_copy.py
Before updating
array('i', [1, 2, 3, 4, 5])
array('i', [1, 2, 3, 4, 5])
After updating
array('i', [6, 2, 3, 4, 5])
array('i', [6, 2, 3, 4, 5])
```

In the above example, we create an array of five elements and copy the array elements to another array using the `=` operator. After updating, we change the first element of the new array. The first element of the original array is also changed.

### copy() method
The `copy()` method returns a shallow copy of the array.

```python title="array_copy.py" showLineNumbers{1} {1, 3-4, 10}
import array as arr

my_array = arr.array('i', [1, 2, 3, 4, 5])
new_array = my_array.copy()

print("Before updating")
print(my_array)
print(new_array)

new_array[0] = 6

print("After updating")
print(my_array)
print(new_array)
```

Output:

```cmd title="command" showLineNumbers{1} {2-14}
C:\Users\username>python array_copy.py
Before updating
array('i', [1, 2, 3, 4, 5])
array('i', [1, 2, 3, 4, 5])
After updating
array('i', [1, 2, 3, 4, 5])
array('i', [6, 2, 3, 4, 5])
```

In the above example, we create an array of five elements and copy the array elements to another array using the `copy()` method. After updating, we change the first element of the new array. The first element of the original array is not changed.

### deepcopy() function
The `deepcopy()` function returns a deep copy of the array.

```python title="array_deepcopy.py" showLineNumbers{1} {1-2, 4-5, 11}
import array as arr
import copy

my_array = arr.array('i', [1, 2, 3, 4, 5])
new_array = copy.deepcopy(my_array)

print("Before updating")
print(my_array)
print(new_array)

new_array[0] = 6

print("After updating")
print(my_array)
print(new_array)
```

Output:

```cmd title="command" showLineNumbers{1} {2-16}
C:\Users\username>python array_deepcopy.py
Before updating
array('i', [1, 2, 3, 4, 5])
array('i', [1, 2, 3, 4, 5])
After updating
array('i', [1, 2, 3, 4, 5])
array('i', [6, 2, 3, 4, 5])
```

In the above example, we create an array of five elements and copy the array elements to another array using the `deepcopy()` function. After updating, we change the first element of the new array. The first element of the original array is not changed.



