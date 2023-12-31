---
title: Access the Set
description: Learn 
sidebar: 
    order: 59
---
<!-- 

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

In this example, we declare a tuple and assign it to the variable `data`. We then print the tuple elements using the index number. The output shows that the tuple elements are accessed using the index number. -->

## Access the Set
In python, we can not access the set elements using the index number. Because the set is an unordered collection of items. So, we can not access the set elements using the index number. But we can access the set elements using the `for` loop. 

```python title="tuple_index.py" showLineNumbers{1} {1-5}
data = {'a', 'b', 'c', 'd', 'e', 'f', 'g'}
for i in data:
    print(i)
```

Output:

```cmd title="command" showLineNumbers{1} {2-8}
C:\Users\username>python tuple_index.py
a
b
c
d
e
f
g
```

In this example, we declare a set and assign it to the variable `data`. We then print the set elements using the `for` loop. The output shows that the set elements are accessed using the `for` loop.

:::danger
We can not access the set elements using the index number. If we try to access the set elements using the index number, we will get an error.

```python title="tuple_index.py" showLineNumbers{1} {1-5}
data = {'a', 'b', 'c', 'd', 'e', 'f', 'g'}
print(data[0])
```

Output:

```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\username>python tuple_index.py
Traceback (most recent call last):
  File "tuple_index.py", line 2, in <module>
    print(data[0])
TypeError: 'set' object is not subscriptable
```

In this example, we try to access the set elements using the index number. But we get an error. The error shows that the set object is not subscriptable.
:::

### Access the Set using the for loop
In python, we can access the set elements using the `for` loop. We can use the `for` loop to access the set elements. 

```python title="tuple_index.py" showLineNumbers{1} {1-5}
data = {'a', 'b', 'c', 'd', 'e', 'f', 'g'}
for i in data:
    print(i)
```

Output:

```cmd title="command" showLineNumbers{1} {2-8}
C:\Users\username>python tuple_index.py
a
b
c
d
e
f
g
```

In this example, we declare a set and assign it to the variable `data`. We then print the set elements using the `for` loop. The output shows that the set elements are accessed using the `for` loop.

### Access the Set using the while loop
In python, we can access the set elements using the `while` loop. We can use the `while` loop to access the set elements. 

```python title="tuple_index.py" showLineNumbers{1} {1-5}
data = {'a', 'b', 'c', 'd', 'e', 'f', 'g'}
i = 0
while i < len(data):
    print(data[i])
    i += 1
```

Output:

```cmd title="command" showLineNumbers{1} {2-9}
C:\Users\username>python tuple_index.py
a
b
c
d
e
f
g
```

In this example, we declare a set and assign it to the variable `data`. We then print the set elements using the `while` loop. The output shows that the set elements are accessed using the `while` loop.

### Access the Set using the enumerate() function
In python, we can access the set elements using the `enumerate()` function. We can use the `enumerate()` function to access the set elements. 

```python title="tuple_index.py" showLineNumbers{1} {1-5}
data = {'a', 'b', 'c', 'd', 'e', 'f', 'g'}
for i, j in enumerate(data):
    print(i, j)
```

Output:

```cmd title="command" showLineNumbers{1} {2-8}
C:\Users\username>python tuple_index.py
0 a
1 b
2 c
3 d
4 e
5 f
6 g
```

In this example, we declare a set and assign it to the variable `data`. We then print the set elements using the `enumerate()` function. The output shows that the set elements are accessed using the `enumerate()` function.

### Access the Set using the list() function
In python, we can access the set elements using the `list()` function. We can use the `list()` function to access the set elements. 

```python title="tuple_index.py" showLineNumbers{1} {1-5}
data = {'a', 'b', 'c', 'd', 'e', 'f', 'g'}
data_list = list(data)
print(data_list[0])
print(data_list[1])
print(data_list[2])
```

Output:

```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\username>python tuple_index.py
a
b
c
```

In this example, we declare a set and assign it to the variable `data`. We then convert the set into a list using the `list()` function. We then print the list elements using the index number. The output shows that the list elements are accessed using the index number.

### Access the Set using the tuple() function
In python, we can access the set elements using the `tuple()` function. We can use the `tuple()` function to access the set elements. 

```python title="tuple_index.py" showLineNumbers{1} {1-5}
data = {'a', 'b', 'c', 'd', 'e', 'f', 'g'}
data_tuple = tuple(data)
print(data_tuple[0])
print(data_tuple[1])
print(data_tuple[2])
```

Output:

```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\username>python tuple_index.py
a
b
c
```

In this example, we declare a set and assign it to the variable `data`. We then convert the set into a tuple using the `tuple()` function. We then print the tuple elements using the index number. The output shows that the tuple elements are accessed using the index number.

### Access element using in keyword
In python, we can access the set elements using the `in` keyword. We can use the `in` keyword to access the set elements. 

```python title="tuple_index.py" showLineNumbers{1} {1-5}
data = {'a', 'b', 'c', 'd', 'e', 'f', 'g'}
if 'a' in data:
    print('a is in the set')
else:
    print('a is not in the set')
```

Output:

```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\username>python tuple_index.py
a is in the set
```

In this example, we declare a set and assign it to the variable `data`. We then check if the element `a` is in the set or not using the `in` keyword. The output shows that the element `a` is in the set.

### Access element using not in keyword
In python, we can access the set elements using the `not in` keyword. We can use the `not in` keyword to access the set elements. 

```python title="tuple_index.py" showLineNumbers{1} {1-5}
data = {'a', 'b', 'c', 'd', 'e', 'f', 'g'}
if 'm' not in data:
    print('m is not in the set')
else:
    print('m is in the set')
```

Output:

```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\username>python tuple_index.py
m is not in the set
```

In this example, we declare a set and assign it to the variable `data`. We then check if the element `m` is in the set or not using the `not in` keyword. The output shows that the element `m` is not in the set.

## Conclusion
In this tutorial, we learned how to access the set elements in python. We learn how to access the set elements using the `for` loop, `while` loop, `enumerate()` function, `list()` function, `tuple()` function, `in` keyword, and `not in` keyword. For more information, visit the [official website](https://docs.python.org/3/tutorial/datastructures.html#sets) of the python set. For more tutorials, visit our Python Central Hub.