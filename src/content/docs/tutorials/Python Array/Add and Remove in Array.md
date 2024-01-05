---
title: Add and Remove in Array
description: Learn how to add and remove elements in an array. We will also learn how to add and remove elements at the beginning and end of an array.
sidebar: 
    order: 72
---
<!-- ```python title="list_indexing.py" showLineNumbers{1} {1,3-7}
my_list = ['a', 'b', 'c', 'd', 'e']

print(my_list[0])
print(my_list[1])
print(my_list[2])
print(my_list[3])
```

Output:
```cmd title="command" showLineNumbers{1} {2-6}
C:\Users\username>python list_indexing.py
a
b
c
d
```

In the above example, we create a list of five elements and print the first four elements using their indices. Note that the last element is not printed because it has an index of 4, which is out of range for the list. -->

## Add in Array
In Python, we can add elements to an array. We can add elements to the end of an array using the `append()` method. We can also add elements to the beginning of an array using the `insert()` method.

### append() Method
The `append()` method adds an element to the end of an array. The syntax of the `append()` method is as follows:
```python title="Syntax" showLineNumbers{1} {1}
array_name.append(element)
```

The `append()` method takes one argument, which is the element to be added to the array. The `append()` method adds the element to the end of the array.

Let's see an example of the `append()` method.
```python title="array_append.py" showLineNumbers{1} {1,3-5}
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

In the above example, we create an array of five elements and add a sixth element to the end of the array using the `append()` method.

### insert() Method
The `insert()` method adds an element to the beginning of an array. The syntax of the `insert()` method is as follows:

```python title="Syntax" showLineNumbers{1} {1}
array_name.insert(index, element)
```

The `insert()` method takes two arguments. The first argument is the index at which the element is to be inserted. The second argument is the element to be inserted.

Let's see an example of the `insert()` method.
```python title="array_insert.py" showLineNumbers{1} {1,3-5}
import array as arr

my_array = arr.array('i', [1, 2, 3, 4, 5])
my_array.insert(0, 0)
print(my_array)
```

Output:
```cmd title="command" showLineNumbers{1} {2-6}
C:\Users\username>python array_insert.py
array('i', [0, 1, 2, 3, 4, 5])
```

In the above example, we create an array of five elements and add a sixth element to the beginning of the array using the `insert()` method.

Another example of the `insert()` method.
```python title="array_insert.py" showLineNumbers{1} {1,3-5}
import array as arr

my_array = arr.array('i', [1, 2, 3, 4, 5])
my_array.insert(3, 6)
print(my_array)
```

Output:
```cmd title="command" showLineNumbers{1} {2-6}
C:\Users\username>python array_insert.py
array('i', [1, 2, 3, 6, 4, 5])
```

In the above example, we create an array of five elements and add a sixth element to the fourth index of the array using the `insert()` method.

### extend() Method
The `extend()` method adds multiple elements to the end of an array. The syntax of the `extend()` method is as follows:
```python title="Syntax" showLineNumbers{1} {1}
array_name.extend(iterable)
```

The `extend()` method takes one argument, which is an iterable. The `extend()` method adds all the elements of the iterable to the end of the array.

Let's see an example of the `extend()` method.
```python title="array_extend.py" showLineNumbers{1} {1,3-5}
import array as arr

my_array = arr.array('i', [1, 2, 3, 4, 5])
my_array.extend([6, 7, 8])
print(my_array)
```

Output:
```cmd title="command" showLineNumbers{1} {2-6}
C:\Users\username>python array_extend.py
array('i', [1, 2, 3, 4, 5, 6, 7, 8])
```

In the above example, we create an array of five elements and add three more elements to the end of the array using the `extend()` method.

### += Operator
The `+=` operator adds multiple elements to the end of an array. The syntax of the `+=` operator is as follows:
```python title="Syntax" showLineNumbers{1} {1}
array_name += iterable
```

The `+=` operator takes one argument, which is an iterable. The `+=` operator adds all the elements of the iterable to the end of the array.

Let's see an example of the `+=` operator.
```python title="array_extend.py" showLineNumbers{1} {1,3-6}
import array as arr

my_array = arr.array('i', [1, 2, 3, 4, 5])
my_array2 = arr.array('i', [6, 7, 8])
my_array += my_array2
print(my_array)
```

Output:
```cmd title="command" showLineNumbers{1} {2-6}
C:\Users\username>python array_extend.py
array('i', [1, 2, 3, 4, 5, 6, 7, 8])
```

In the above example, we create an array of five elements and add three more elements to the end of the array using the `+=` operator.

:::danger
The `+=` operator can also be used to add a single element to the end of an array. It only works with array, it does not work with list.

```python title="array_extend.py" showLineNumbers{1} {1,3-5}
import array as arr

my_array = arr.array('i', [1, 2, 3, 4, 5])
my_array += [6]
print(my_array)
```

Output:
```cmd title="command" showLineNumbers{1} {2-6}
C:\Users\username>python array_extend.py
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
TypeError: can only extend array with array (not "list")
```

In the above example, we create an array of five elements and add a sixth element to the end of the array using the `+=` operator. But it gives an error because the `+=` operator does not work with list.
:::

## Remove in Array
In Python, we can remove elements from an array. We can remove elements from the end of an array using the `pop()` method. We can also remove elements from the beginning of an array using the `pop()` method.

### pop() Method
The `pop()` method removes an element from array. It takes one argument, which is the index of the element to be removed. Default is the last element. It returns the removed element. The syntax of the `pop()` method is as follows:
```python title="Syntax" showLineNumbers{1} {1}
element = array_name.pop(index=-1)
```

The `pop()` method takes one argument, which is the index of the element to be removed. Default is the last element. The `pop()` method returns the removed element.

Let's see an example of the `pop()` method.
```python title="array_pop.py" showLineNumbers{1} {1,3-6}
import array as arr

my_array = arr.array('i', [1, 2, 3, 4, 5])
element = my_array.pop()
print(element)
print(my_array)
```

Output:
```cmd title="command" showLineNumbers{1} {2-7}
C:\Users\username>python array_pop.py
5
array('i', [1, 2, 3, 4])
```

In the above example, we create an array of five elements and remove the last element from the array using the `pop()` method.

Another example of the `pop()` method.
```python title="array_pop.py" showLineNumbers{1} {1,3-6}
import array as arr

my_array = arr.array('i', [1, 2, 3, 4, 5])
element = my_array.pop(3)
print(element)
print(my_array)
```

Output:
```cmd title="command" showLineNumbers{1} {2-7}
C:\Users\username>python array_pop.py
4
array('i', [1, 2, 3, 5])
```

In the above example, we create an array of five elements and remove the fourth element from the array using the `pop()` method.

### remove() Method
The `remove()` method removes an element from array. It takes one argument, which is the element to be removed. It returns `None`. The syntax of the `remove()` method is as follows:
```python title="Syntax" showLineNumbers{1} {1}
array_name.remove(element)
```

The `remove()` method takes one argument, which is the element to be removed. The `remove()` method returns `None`.

Let's see an example of the `remove()` method.
```python title="array_remove.py" showLineNumbers{1} {1,3-6}
import array as arr

my_array = arr.array('i', [1, 2, 3, 4, 5])
my_array.remove(3)
print(my_array)
```

Output:
```cmd title="command" showLineNumbers{1} {2-6}
C:\Users\username>python array_remove.py
array('i', [1, 2, 4, 5])
```

In the above example, we create an array of five elements and remove the third element from the array using the `remove()` method.

### del Statement
The `del` statement removes an element from array. It takes one argument, which is the index of the element to be removed. The syntax of the `del` statement is as follows:
```python title="Syntax" showLineNumbers{1} {1}
del array_name[index]
```

The `del` statement takes one argument, which is the index of the element to be removed.

Let's see an example of the `del` statement.
```python title="array_del.py" showLineNumbers{1} {1,3-6}
import array as arr

my_array = arr.array('i', [1, 2, 3, 4, 5])
del my_array[3]
print(my_array)
```

Output:
```cmd title="command" showLineNumbers{1} {2-6}
C:\Users\username>python array_del.py
array('i', [1, 2, 3, 5])
```

In the above example, we create an array of five elements and remove the fourth element from the array using the `del` statement.

### clear() Method
The `clear()` method removes all elements from array. It takes no argument. It returns `None`. The syntax of the `clear()` method is as follows:
```python title="Syntax" showLineNumbers{1} {1}
array_name.clear()
```

The `clear()` method takes no argument. The `clear()` method returns `None`.

Let's see an example of the `clear()` method.
```python title="array_clear.py" showLineNumbers{1} {1,3-6}
import array as arr

my_array = arr.array('i', [1, 2, 3, 4, 5])
my_array.clear()
print(my_array)
```

Output:
```cmd title="command" showLineNumbers{1} {2-4}
C:\Users\username>python array_clear.py
array('i')
```

In the above example, we create an array of five elements and remove all elements from the array using the `clear()` method.

## Update in Array
In Python, we can update elements in an array. We can update elements in an array using their indices.

### Update by Index
In Python, we can update elements in an array using their indices. We can update elements in an array using their indices. The syntax of updating an element in an array is as follows:
```python title="Syntax" showLineNumbers{1} {1}
array_name[index] = new_value
```

The `=` operator is used to update an element in an array. The `=` operator takes two arguments. The first argument is the index of the element to be updated. The second argument is the new value of the element.

Let's see an example of updating an element in an array.
```python title="array_update.py" showLineNumbers{1} {1,3-6}
import array as arr

my_array = arr.array('i', [1, 2, 3, 4, 5])
my_array[3] = 6
print(my_array)
```

Output:
```cmd title="command" showLineNumbers{1} {2-4}
C:\Users\username>python array_update.py
array('i', [1, 2, 3, 6, 5])
```

In the above example, we create an array of five elements and update the fourth element of the array.

### Update by Slice
In Python, we can update elements in an array using their indices. We can update elements in an array using their indices. The syntax of updating an element in an array is as follows:
```python title="Syntax" showLineNumbers{1} {1}
array_name[start_index:end_index] = new_value
```

The `=` operator is used to update an element in an array. The `=` operator takes two arguments. The first argument is the slice of the array to be updated. The second argument is the new value of the slice.

Let's see an example of updating an element in an array.
```python title="array_update.py" showLineNumbers{1} {1,3-6}
import array as arr

my_array = arr.array('i', [1, 2, 3, 4, 5])
my_array[1:3] = arr.array('i', [6, 7])
print(my_array)
```

Output:
```cmd title="command" showLineNumbers{1} {2-4}
C:\Users\username>python array_update.py
array('i', [1, 6, 7, 4, 5])
```

In the above example, we create an array of five elements and update the second and third elements of the array.

### Update by Multiple number
In Python, we can multiply elements in an array using their indices. We can multiply elements in an array using their indices. The syntax of multiplying an element in an array is as follows:
```python title="Syntax" showLineNumbers{1} {1}
array_name[index] *= number
```

The `*=` operator is used to multiply array. The `*=` operator repeats the element in the array by the number of times specified by the number.

Let's see an example of multiplying array.
```python title="array_update.py" showLineNumbers{1} {1,3-6}
import array as arr

my_array = arr.array('i', [1, 2, 3, 4, 5])
my_array *= 2
print(my_array)
```

Output:
```cmd title="command" showLineNumbers{1} {2-4}
C:\Users\username>python array_update.py
array('i', [1, 2, 3, 4, 5, 1, 2, 3, 4, 5])
```

In the above example, we create an array of five elements and multiply the array by 2.

## Conclusion
In this tutorial, we learned how to add and remove elements in an array. We also learned how to add and remove elements at the beginning and end of an array. We also learned how to update elements in an array. We also learned how to update elements in an array using their indices. We also learned how to multiply elements in an array using their indices. For more tutorials like this check out Python Central Hub.