---
title: Unpack the Tuple
description: Learn how to unpack the tuple in Python. The unpacking of the tuple is a very useful feature in Python. It allows us to assign the values of the tuple to the variables. 
sidebar: 
    order: 55
---

## Understanding the Tuple Unpacking

What you understand by unpacking the tuple? It is a process of assigning the values of the tuple to the variables. The unpacking of the tuple is a very useful feature in Python. It allows us to assign the values of the tuple to the variables.

<!-- ```python title="tuple_index.py" showLineNumbers{1} {1-5}
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


## Creating a Tuple
First, We need to learn how to create a tuple. We can create a tuple using the following syntax.

1. Using the `()` brackets.
    You can create a tuple using the `()` brackets. The tuple elements are separated by the comma (,) operator. The following example shows how to create a tuple using the `()` brackets.

    ```python title="tuple.py" showLineNumbers{1} {1}
    data = ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j')
    print(data)
    ```

    Output:

    ```cmd title="command" showLineNumbers{1} {2-5}
    C:\Users\username>python tuple.py
    ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j')
    ```

2. Using the `tuple()` constructor.
   You can also create a tuple using the `tuple()` constructor. The following example shows how to create a tuple using the `tuple()` constructor.

    ```python title="tuple_constructor.py" showLineNumbers{1} {1}
    data = tuple(('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j'))
    print(data)
    ```

    Output:

    ```cmd title="command" showLineNumbers{1} {2-5}
    C:\Users\username>python tuple_constructor.py
    ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j')
    ```
3. using the `,` operator.
    You can also create a tuple using the `,` operator. The following example shows how to create a tuple using the `,` operator.

    ```python title="tuple_comma.py" showLineNumbers{1} {1}
    data = 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j'
    print(data)
    ```

    Output:

    ```cmd title="command" showLineNumbers{1} {2-5}
    C:\Users\username>python tuple_comma.py
    ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j')
    ```

## Unpacking the Tuple
Unpacking the tuple is a process of assigning the values of the tuple to the variables. The unpacking of the tuple is a very useful feature in Python. It allows us to assign the values of the tuple to the variables.

```python title="tuple_unpack.py" showLineNumbers{1} {1-15}
data = ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j')
a, b, c, d, e, f, g, h, i, j = data
print(a)
print(b)
print(c)
print(d)
print(e)
print(f)
print(g)
print(h)
print(i)
print(j)
```

Output:

```cmd title="command" showLineNumbers{1} {2-11}
C:\Users\username>python tuple_unpack.py
a
b
c
d
e
f
g
h
i
j
```

In this example, we declare a tuple and assign it to the variable `data`. We then unpack the tuple and assign the values of the tuple to the variables `a`, `b`, `c`, `d`, `e`, `f`, `g`, `h`, `i`, `j`. We then print the values of the variables. The output shows that the values of the tuple are assigned to the variables.

## Unpacking the Tuple using the Asterisk Operator
We can also unpack the tuple using the asterisk operator.

```python title="tuple_unpack_asterisk.py" showLineNumbers{1} {1-15}
data = ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j')
a, b, c, *d = data
print(a)
print(b)
print(c)
print(d)
```

Output:

```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\username>python tuple_unpack_asterisk.py
a
b
c
['d', 'e', 'f', 'g', 'h', 'i', 'j']
```

In this example, we declare a tuple and assign it to the variable `data`. We then unpack the tuple and assign the values of the tuple to the variables `a`, `b`, `c`, `d`. We then print the values of the variables. The output shows that the values of the tuple are assigned to the variables. `*` operator is used to unpack the tuple and assign the remaining values to the variable `d`.

### Another Way
We can also unpack the tuple using the asterisk operator.

```python title="tuple_unpack_asterisk_another_way.py" showLineNumbers{1} {1-15}
data = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
a,b,c,*d,e = data
print(a)
print(b)
print(c)
print(d)
print(e)
```

Output:

```cmd title="command" showLineNumbers{1} {2-6}
C:\Users\username>python tuple_unpack_asterisk_another_way.py
1
2
3
[4, 5, 6, 7, 8, 9]
10
```

In this example, we declare a tuple and assign it to the variable `data`. We then unpack the tuple and assign the values of the tuple to the variables `a`, `b`, `c`, `d`, `e`. We then print the values of the variables. The output shows that the values of the tuple are assigned to the variables. `*` operator is used to unpack the tuple and assign the remaining values to the variable `d`. The last value of the tuple is assigned to the variable `e`.

:::danger
The number of variables must be equal to the number of values in the tuple. If the number of variables is greater than the number of values in the tuple, then it will raise an error. If the number of variables is less than the number of values in the tuple, then it will raise an error.

```python title="tuple_unpack_error.py" {1-14}
data = ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j')
a, b, c, d, e, f, g, h, i, j, k = data
print(a)
print(b)
print(c)
print(d)
print(e)
print(f)
print(g)
print(h)
print(i)
print(j)
print(k)
```

Output:

```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\username>python tuple_unpack_error.py
Traceback (most recent call last):
  File "tuple_unpack_error.py", line 2, in <module>
    a, b, c, d, e, f, g, h, i, j, k = data
ValueError: not enough values to unpack (expected 11, got 10)
```

In this example, we declare a tuple and assign it to the variable `data`. We then unpack the tuple and assign the values of the tuple to the variables `a`, `b`, `c`, `d`, `e`, `f`, `g`, `h`, `i`, `j`, `k`. We then print the values of the variables. The output shows that the values of the tuple are assigned to the variables. The number of variables is greater than the number of values in the tuple, so it raises an error.

```python title="tuple_unpack_error.py" {1-14}
data = ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j')
a, b, c, d, e, f, g, h, i = data
print(a)
print(b)
print(c)
print(d)
print(e)
print(f)
print(g)
print(h)
print(i)
```

Output:

```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\username>python tuple_unpack_error.py
Traceback (most recent call last):
  File "tuple_unpack_error.py", line 2, in <module>
    a, b, c, d, e, f, g, h, i = data
ValueError: too many values to unpack (expected 9)
```