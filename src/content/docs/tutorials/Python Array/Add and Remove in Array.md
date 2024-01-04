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

