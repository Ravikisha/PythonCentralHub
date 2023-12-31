---
title: Set Operations
description: Learn how to perform set operations in Python. Learn how to perform union, intersection, difference, and symmetric difference operations on sets. Learn how to use the union(), intersection(), difference(), and symmetric_difference() methods to perform set operations. Learn how to use the |, &, -, and ^ operators to perform set operations.
sidebar: 
    order: 60
---

## Python Set Operations
Python provides different methods and operators to perform set operations. In this tutorial, we will learn how to perform set operations in Python.

## Add Items to Set
Adding items to the set is very easy. We can use items using two methods. We can use the `add()` method to add a single item to the set. We can use the `update()` method to add multiple items to the set.

### add() Method
We can use the `add()` method to add a single item to the set. The `add()` method takes a single argument and adds it to the set. The `add()` method does not return any value. The `add()` method does not add an item to the set if it is already present in the set.

```python title="set_add.py" showLineNumbers{1} {1-2}
data = {'a', 'b', 'c', 'd', 'e', 'f', 'g'}
data.add('h')
print(data)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python set_add.py
{'a', 'e', 'b', 'd', 'g', 'h', 'f', 'c'}
```

In this example, we declare a set and assign it to the variable `data`. We then add an item to the set using the `add()` method. The output shows that the item is added to the set.

### update() Method
We can use the `update()` method to add multiple items to the set. The `update()` method takes a single argument and adds it to the set. The `update()` method does not return any value. The `update()` method does not add an item to the set if it is already present in the set.

```python title="set_update.py" showLineNumbers{1} {1-3}
data = {'a', 'b', 'c', 'd', 'e', 'f', 'g'}
data2 = {'h', 'i', 'j', 'k', 'l', 'm', 'n'}
data.update(data2)
print(data)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python set_update.py
{'a', 'e', 'd', 'g', 'l', 'j', 'n', 'm', 'b', 'i', 'h', 'f', 'k', 'c'}
```

In this example, we declare two sets and assign them to the variables `data` and `data2`. We then add the items of the `data2` set to the `data` set using the `update()` method. The output shows that the items are added to the set.

### Add Items from Another Data Type
Another way to add multiple items from another data type to the set is to use the `update()` method with another data type. We can pass a list, tuple, dictionary, or another set to the `update()` method to add multiple items to the set.

#### Add Items from List
We can pass a list to the `update()` method to add multiple items from the list to the set.

```python title="set_update.py" showLineNumbers{1} {1-3}
data = {'a', 'b', 'c', 'd', 'e', 'f', 'g'}
data2 = ['h', 'i', 'j', 'k', 'l', 'm', 'n']
data.update(data2)
print(data)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python set_update.py
{'a', 'g', 'l', 'j', 'n', 'm', 'b', 'f', 'k', 'e', 'd', 'i', 'h', 'c'}
```

In this example, we declare a set and assign it to the variable `data`. We then declare a list and assign it to the variable `data2`. We then add the items of the `data2` list to the `data` set using the `update()` method. The output shows that the items are added to the set.


#### Add Items from Tuple
We can pass a tuple to the `update()` method to add multiple items from the tuple to the set.

```python title="set_update.py" showLineNumbers{1} {1-3}
data = {'a', 'b', 'c', 'd', 'e', 'f', 'g'}
data2 = ('h', 'i', 'j', 'k', 'l', 'm', 'n')
data.update(data2)
print(data)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python set_update.py
{'a', 'g', 'l', 'j', 'n', 'm', 'b', 'f', 'k', 'e', 'd', 'i', 'h', 'c'}
```

In this example, we declare a set and assign it to the variable `data`. We then declare a tuple and assign it to the variable `data2`. We then add the items of the `data2` tuple to the `data` set using the `update()` method. The output shows that the items are added to the set.

#### Add Items from String
We can pass a string to the `update()` method to add multiple items from the string to the set.

```python title="set_update.py" showLineNumbers{1} {1-3}
data = {'a', 'b', 'c', 'd', 'e', 'f', 'g'}
data2 = 'hijklmn'
data.update(data2)
print(data)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python set_update.py
{'a', 'g', 'l', 'j', 'n', 'm', 'b', 'f', 'k', 'e', 'd', 'i', 'h', 'c'}
```

In this example, we declare a set and assign it to the variable `data`. We then declare a string and assign it to the variable `data2`. We then add the items of the `data2` string to the `data` set using the `update()` method. The output shows that the items are added to the set.

### union() Method
We can use the `union()` method to add multiple items to the set. The `union()` method takes a single argument and adds it to the set. The `union()` method does not return any value. The `union()` method does not add an item to the set if it is already present in the set.

```python title="set_union.py" showLineNumbers{1} {1-3}
data = {'a', 'b', 'c', 'd', 'e', 'f', 'g'}
data2 = {'h', 'i', 'j', 'k', 'l', 'm', 'n'}
print(data.union(data2))
print(data)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python set_union.py
{'a', 'e', 'd', 'g', 'l', 'j', 'n', 'm', 'b', 'i', 'h', 'f', 'k', 'c'}
{'a', 'e', 'b', 'd', 'g', 'f', 'c'}
```

In this example, we declare two sets and assign them to the variables `data` and `data2`. We then add the items of the `data2` set to the `data` set using the `union()` method. The output shows that the items are added to the set. The `union()` method does not change the original set.

### union() Method with Another Data Type
Another way to add multiple items from another data type to the set is to use the `union()` method with another data type. We can pass a list, tuple, dictionary, or another set to the `union()` method to add multiple items to the set.

#### union() Method with List
We can pass a list to the `union()` method to add multiple items from the list to the set.

```python title="set_union.py" showLineNumbers{1} {1-3}
data = {'a', 'b', 'c', 'd', 'e', 'f', 'g'}
data2 = ['h', 'i', 'j', 'k', 'l', 'm', 'n']
print(data.union(data2))
print(data)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python set_union.py
{'a', 'e', 'd', 'g', 'l', 'j', 'n', 'm', 'b', 'i', 'h', 'f', 'k', 'c'}
{'a', 'e', 'b', 'd', 'g', 'f', 'c'}
```

In this example, we declare a set and assign it to the variable `data`. We then declare a list and assign it to the variable `data2`. We then add the items of the `data2` list to the `data` set using the `union()` method. The output shows that the items are added to the set. The `union()` method does not change the original set.

#### union() Method with Tuple
We can pass a tuple to the `union()` method to add multiple items from the tuple to the set.

```python title="set_union.py" showLineNumbers{1} {1-3}
data = {'a', 'b', 'c', 'd', 'e', 'f', 'g'}
data2 = ('h', 'i', 'j', 'k', 'l', 'm', 'n')
print(data.union(data2))
print(data)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python set_union.py
{'a', 'e', 'd', 'g', 'l', 'j', 'n', 'm', 'b', 'i', 'h', 'f', 'k', 'c'}
{'a', 'e', 'b', 'd', 'g', 'f', 'c'}
```

In this example, we declare a set and assign it to the variable `data`. We then declare a tuple and assign it to the variable `data2`. We then add the items of the `data2` tuple to the `data` set using the `union()` method. The output shows that the items are added to the set. The `union()` method does not change the original set.

#### union() Method with String
We can pass a string to the `union()` method to add multiple items from the string to the set.

```python title="set_union.py" showLineNumbers{1} {1-3}
data = {'a', 'b', 'c', 'd', 'e', 'f', 'g'}
data2 = 'hijklmn'
print(data.union(data2))
print(data)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python set_union.py
{'a', 'e', 'd', 'g', 'l', 'j', 'n', 'm', 'b', 'i', 'h', 'f', 'k', 'c'}
{'a', 'e', 'b', 'd', 'g', 'f', 'c'}
```

In this example, we declare a set and assign it to the variable `data`. We then declare a string and assign it to the variable `data2`. We then add the items of the `data2` string to the `data` set using the `union()` method. The output shows that the items are added to the set. The `union()` method does not change the original set.

### | Operator
We can use the `|` operator to add multiple items to the set. The `|` operator takes a single argument and adds it to the set. The `|` operator does not return any value. The `|` operator does not add an item to the set if it is already present in the set.

```python title="set_union.py" showLineNumbers{1} {1-3}
data = {'a', 'b', 'c', 'd', 'e', 'f', 'g'}
data2 = {'h', 'i', 'j', 'k', 'l', 'm', 'n'}
print(data | data2)
print(data)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python set_union.py
{'a', 'e', 'd', 'g', 'l', 'j', 'n', 'm', 'b', 'i', 'h', 'f', 'k', 'c'}
{'a', 'e', 'b', 'd', 'g', 'f', 'c'}
```

In this example, we declare two sets and assign them to the variables `data` and `data2`. We then add the items of the `data2` set to the `data` set using the `|` operator. The output shows that the items are added to the set. The `|` operator does not change the original set.

:::tip
The `|` operator is the same as the `union()` method. The `|` operator does not change the original set. The `union()` method does not change the original set. This also work with different data types.
:::


