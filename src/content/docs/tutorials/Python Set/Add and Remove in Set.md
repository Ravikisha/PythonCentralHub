---
title: Add and Remove Items from Set
description: Learn how to add and remove items from the set in Python. We will learn how to add items to the set, remove items from the set, and remove the set. We will also learn how to perform set operations in Python. We will learn how to perform union, intersection, and symmetric difference operations in Python. We will also learn how to perform union, intersection, and symmetric difference operations in Python.
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


## Remove Items from Set
Removing items from the set is very easy. We can use items using two methods. We can use the `remove()` method to remove a single item from the set. We can use the `discard()` method to remove multiple items from the set.

### remove() Method
We can use the `remove()` method to remove a single item from the set. The `remove()` method takes a single argument and removes it from the set. The `remove()` method does not return any value. The `remove()` method raises an error if the item is not present in the set.

```python title="set_remove.py" showLineNumbers{1} {1-3}
data = {'a', 'b', 'c', 'd', 'e', 'f', 'g'}
data.remove('f')
print(data)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python set_remove.py
{'a', 'e', 'b', 'd', 'g', 'c'}
```

In this example, we declare a set and assign it to the variable `data`. We then remove an item from the set using the `remove()` method. The output shows that the item is removed from the set.

:::danger
The `remove()` method raises an error if the item is not present in the set.

```python title="set_remove_error.py" showLineNumbers{1} {1-3}
data = {'a', 'b', 'c', 'd', 'e', 'f', 'g'}
data.remove('h')
print(data)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python set_remove_error.py
Traceback (most recent call last):
  File "set_remove_error.py", line 2, in <module>
    data.remove('h')
KeyError: 'h'
```

In this example, we declare a set and assign it to the variable `data`. We then remove an item from the set using the `remove()` method. The output shows that the item is removed from the set. The `remove()` method raises an error if the item is not present in the set.

:::

### discard() Method
We can use the `discard()` method to remove multiple items from the set. The `discard()` method takes a single argument and removes it from the set. The `discard()` method does not return any value. The `discard()` method does not raise an error if the item is not present in the set.

```python title="set_discard.py" showLineNumbers{1} {1-3}
data = {'a', 'b', 'c', 'd', 'e', 'f', 'g'}
data.discard('f')
print(data)
data.discard('h')
print(data)
```

Output:

```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\username>python set_discard.py
{'a', 'e', 'b', 'd', 'g', 'c'}
{'a', 'e', 'b', 'd', 'g', 'c'}
```

In this example, we declare a set and assign it to the variable `data`. We then remove an item from the set using the `discard()` method. The output shows that the item is removed from the set. We then remove an item from the set using the `discard()` method. The output shows that the item is not removed from the set.

:::tip
The `discard()` method does not raise an error if the item is not present in the set.

```python title="set_discard_error.py" showLineNumbers{1} {1-3}
data = {'a', 'b', 'c', 'd', 'e', 'f', 'g'}
data.discard('h')
print(data)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python set_discard_error.py
{'a', 'e', 'b', 'd', 'g', 'f', 'c'}
```

In this example, we declare a set and assign it to the variable `data`. We then remove an item from the set using the `discard()` method. The output shows that the item is not removed from the set. The `discard()` method does not raise an error if the item is not present in the set.

:::

### pop() Method
We can use the `pop()` method to remove an item from the set. The `pop()` method does not take any argument and removes an item from the set. The `pop()` method returns the removed item. The `pop()` method removes the last item from the set.

```python title="set_pop.py" showLineNumbers{1} {1-3}
data = {'a', 'b', 'c', 'd', 'e', 'f', 'g'}
print(data.pop())
print(data)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python set_pop.py
a
{'e', 'b', 'd', 'g', 'f', 'c'}
```

In this example, we declare a set and assign it to the variable `data`. We then remove an item from the set using the `pop()` method. The output shows that the item is removed from the set. The `pop()` method removes the last item from the set.

### clear() Method
We can use the `clear()` method to remove all items from the set. The `clear()` method does not take any argument and removes all items from the set. The `clear()` method does not return any value.

```python title="set_clear.py" showLineNumbers{1} {1-3}
data = {'a', 'b', 'c', 'd', 'e', 'f', 'g'}
data.clear()
print(data)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python set_clear.py
set()
```

In this example, we declare a set and assign it to the variable `data`. We then remove all items from the set using the `clear()` method. The output shows that the items are removed from the set.

### del Keyword
We can use the `del` keyword to remove the set. The `del` keyword does not take any argument and removes the set. The `del` keyword does not return any value.

```python title="set_del.py" showLineNumbers{1} {1-3}
data = {'a', 'b', 'c', 'd', 'e', 'f', 'g'}
del data
print(data)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python set_del.py
Traceback (most recent call last):
  File "set_del.py", line 3, in <module>
    print(data)
NameError: name 'data' is not defined
```

In this example, we declare a set and assign it to the variable `data`. We then remove the set using the `del` keyword. The output shows that the set is removed. The `del` keyword does not return any value.

### difference_update() Method
We can use the `difference_update()` method to remove multiple items from the set. The `difference_update()` method takes a single argument and removes it from the set. The `difference_update()` method does not return any value. The `difference_update()` method does not raise an error if the item is not present in the set.

```python title="set_difference_update.py" showLineNumbers{1} {1-3}
data = {'a', 'b', 'c', 'd', 'e', 'f', 'g'}
data2 = {'d', 'e', 'f', 'g', 'h', 'i', 'j'}
data.difference_update(data2)
print(data)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python set_difference_update.py
{'a', 'b', 'c'}
```

In this example, we declare two sets and assign them to the variables `data` and `data2`. We then remove the items of the `data2` set from the `data` set using the `difference_update()` method. The output shows that the items are removed from the set.  The `difference_update()` method does change the original set.

:::note
The `difference_update()` method also works vice versa. The `difference_update()` method removes the items of the first set from the second set.

```python title="set_difference_update.py" showLineNumbers{1} {1-3}
data = {'a', 'b', 'c', 'd', 'e', 'f', 'g'}
data2 = {'d', 'e', 'f', 'g', 'h', 'i', 'j'}
data2.difference_update(data)
print(data2)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python set_difference_update.py
{'i', 'h', 'j'}
```

In this example, we declare two sets and assign them to the variables `data` and `data2`. We then remove the items of the `data` set from the `data2` set using the `difference_update()` method. The output shows that the items are removed from the set.  The `difference_update()` method does change the original set.

:::

### difference() Method
We can use the `difference()` method to remove multiple items from the set. The `difference()` method takes a single argument and removes it from the set. The `difference()` method does not return any value. The `difference()` method does not raise an error if the item is not present in the set.

```python title="set_difference.py" showLineNumbers{1} {1-3}
data = {'a', 'b', 'c', 'd', 'e', 'f', 'g'}
data2 = {'d', 'e', 'f', 'g', 'h', 'i', 'j'}
print(data.difference(data2))
print(data)
```

Output:

```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\username>python set_difference.py
{'a', 'b', 'c'}
{'a', 'e', 'b', 'd', 'g', 'f', 'c'}
```

In this example, we declare two sets and assign them to the variables `data` and `data2`. We then remove the items of the `data2` set from the `data` set using the `difference()` method. The output shows that the items are removed from the set. The `difference()` method does not change the original set.

:::note
The `difference()` method also works vice versa. The `difference()` method removes the items of the first set from the second set.

```python title="set_difference.py" showLineNumbers{1} {1-3}
data = {'a', 'b', 'c', 'd', 'e', 'f', 'g'}
data2 = {'d', 'e', 'f', 'g', 'h', 'i', 'j'}
print(data2.difference(data))
print(data2)
```

Output:

```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\username>python set_difference.py
{'j', 'i', 'h'}
{'e', 'd', 'g', 'i', 'h', 'f', 'j'}
```

In this example, we declare two sets and assign them to the variables `data` and `data2`. We then remove the items of the `data` set from the `data2` set using the `difference()` method. The output shows that the items are removed from the set. The `difference()` method does not change the original set.

:::


### intersection_update() Method
We can use the `intersection_update()` method to remove multiple items from the set. The `intersection_update()` method takes a single argument and removes it from the set. The `intersection_update()` method does not return any value. The `intersection_update()` method does not raise an error if the item is not present in the set.

```python title="set_intersection_update.py" showLineNumbers{1} {1-3}
data = {'a', 'b', 'c', 'd', 'e', 'f', 'g'}
data2 = {'d', 'e', 'f', 'g', 'h', 'i', 'j'}
data.intersection_update(data2)
print(data)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python set_intersection_update.py
{'e', 'd', 'g', 'f'}
```

In this example, we declare two sets and assign them to the variables `data` and `data2`. We then remove the items of the `data2` set from the `data` set using the `intersection_update()` method. The output shows that the items are removed from the set.  The `intersection_update()` method does change the original set.

:::note
The `intersection_update()` method also works vice versa. The `intersection_update()` method removes the items of the first set from the second set.

```python title="set_intersection_update.py" showLineNumbers{1} {1-3}
data = {'a', 'b', 'c', 'd', 'e', 'f', 'g'}
data2 = {'d', 'e', 'f', 'g', 'h', 'i', 'j'}
data2.intersection_update(data)
print(data2)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python set_intersection_update.py
{'e', 'd', 'g', 'f'}
```

In this example, we declare two sets and assign them to the variables `data` and `data2`. We then remove the items of the `data` set from the `data2` set using the `intersection_update()` method. The output shows that the items are removed from the set.  The `intersection_update()` method does change the original set.
:::

### intersection() Method
We can use the `intersection()` method to remove multiple items from the set. The `intersection()` method takes a single argument and removes it from the set. The `intersection()` method does not return any value. The `intersection()` method does not raise an error if the item is not present in the set.

```python title="set_intersection.py" showLineNumbers{1} {1-3}
data = {'a', 'b', 'c', 'd', 'e', 'f', 'g'}
data2 = {'d', 'e', 'f', 'g', 'h', 'i', 'j'}
print(data.intersection(data2))
print(data)
```

Output:

```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\username>python set_intersection.py
{'e', 'd', 'g', 'f'}
{'a', 'e', 'b', 'd', 'g', 'f', 'c'}
```

In this example, we declare two sets and assign them to the variables `data` and `data2`. We then remove the items of the `data2` set from the `data` set using the `intersection()` method. The output shows that the items are removed from the set. The `intersection()` method does not change the original set.

:::note
The `intersection()` method also works vice versa. The `intersection()` method removes the items of the first set from the second set.

```python title="set_intersection.py" showLineNumbers{1} {1-3}
data = {'a', 'b', 'c', 'd', 'e', 'f', 'g'}
data2 = {'d', 'e', 'f', 'g', 'h', 'i', 'j'}
print(data2.intersection(data))
print(data2)
```

Output:

```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\username>python set_intersection.py
{'e', 'd', 'g', 'f'}
{'e', 'd', 'g', 'i', 'h', 'f', 'j'}
```

In this example, we declare two sets and assign them to the variables `data` and `data2`. We then remove the items of the `data` set from the `data2` set using the `intersection()` method. The output shows that the items are removed from the set. The `intersection()` method does not change the original set.
:::

### symmetric_difference_update() Method
We can use the `symmetric_difference_update()` method to remove multiple items from the set. The `symmetric_difference_update()` method takes a single argument and removes it from the set. The `symmetric_difference_update()` method does not return any value. The `symmetric_difference_update()` method does not raise an error if the item is not present in the set.

```python title="set_symmetric_difference_update.py" showLineNumbers{1} {1-3}
data = {'a', 'b', 'c', 'd', 'e', 'f', 'g'}
data2 = {'d', 'e', 'f', 'g', 'h', 'i', 'j'}
data.symmetric_difference_update(data2)
print(data)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python set_symmetric_difference_update.py
{'a', 'j', 'b', 'i', 'h', 'c'}
```

In this example, we declare two sets and assign them to the variables `data` and `data2`. We then remove the items of the `data2` set from the `data` set using the `symmetric_difference_update()` method. The output shows that the items are removed from the set.  The `symmetric_difference_update()` method does change the original set.

:::note
The `symmetric_difference_update()` method also works vice versa. The `symmetric_difference_update()` method removes the items of the first set from the second set.

```python title="set_symmetric_difference_update.py" showLineNumbers{1} {1-3}
data = {'a', 'b', 'c', 'd', 'e', 'f', 'g'}
data2 = {'d', 'e', 'f', 'g', 'h', 'i', 'j'}
data2.symmetric_difference_update(data)
print(data2)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python set_symmetric_difference_update.py
{'a', 'j', 'b', 'i', 'h', 'c'}
```

In this example, we declare two sets and assign them to the variables `data` and `data2`. We then remove the items of the `data` set from the `data2` set using the `symmetric_difference_update()` method. The output shows that the items are removed from the set.  The `symmetric_difference_update()` method does change the original set.

:::

### symmetric_difference() Method
We can use the `symmetric_difference()` method to remove multiple items from the set. The `symmetric_difference()` method takes a single argument and removes it from the set. The `symmetric_difference()` method does not return any value. The `symmetric_difference()` method does not raise an error if the item is not present in the set.

```python title="set_symmetric_difference.py" showLineNumbers{1} {1-3}
data = {'a', 'b', 'c', 'd', 'e', 'f', 'g'}
data2 = {'d', 'e', 'f', 'g', 'h', 'i', 'j'}
print(data.symmetric_difference(data2))
print(data)
```

Output:

```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\username>python set_symmetric_difference.py
{'a', 'j', 'b', 'i', 'h', 'c'}
{'a', 'e', 'b', 'd', 'g', 'f', 'c'}
```

In this example, we declare two sets and assign them to the variables `data` and `data2`. We then remove the items of the `data2` set from the `data` set using the `symmetric_difference()` method. The output shows that the items are removed from the set. The `symmetric_difference()` method does not change the original set.

:::note
The `symmetric_difference()` method also works vice versa. The `symmetric_difference()` method removes the items of the first set from the second set.

```python title="set_symmetric_difference.py" showLineNumbers{1} {1-3}
data = {'a', 'b', 'c', 'd', 'e', 'f', 'g'}
data2 = {'d', 'e', 'f', 'g', 'h', 'i', 'j'}
print(data2.symmetric_difference(data))
print(data2)
```

Output:

```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\username>python set_symmetric_difference.py
{'a', 'j', 'b', 'i', 'h', 'c'}
{'e', 'd', 'g', 'i', 'h', 'f', 'j'}
```

In this example, we declare two sets and assign them to the variables `data` and `data2`. We then remove the items of the `data` set from the `data2` set using the `symmetric_difference()` method. The output shows that the items are removed from the set. The `symmetric_difference()` method does not change the original set.

:::

### & Operator
We can use the `&` operator to remove multiple items from the set. The `&` operator takes a single argument and removes it from the set. The `&` operator does not return any value. The `&` operator does not raise an error if the item is not present in the set.

```python title="set_symmetric_difference.py" showLineNumbers{1} {1-3}
data = {'a', 'b', 'c', 'd', 'e', 'f', 'g'}
print(data & {'d', 'e', 'f', 'g', 'h', 'i', 'j'})
print(data)
```

Output:

```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\username>python set_symmetric_difference.py
{'e', 'd', 'g', 'f'}
{'a', 'e', 'b', 'd', 'g', 'f', 'c'}
```

In this example, we declare a set and assign it to the variable `data`. We then remove the items of the `data2` set from the `data` set using the `&` operator. The output shows that the items are removed from the set. The `&` operator does not change the original set.

## Conclusion
In this tutorial, we have learned about the Python set. We have learned how to create a set. We have learned how to add items to the set. We have learned how to remove items from the set. We have learned how to use different methods to add and remove items from the set. We have learned how to use different operators to add and remove items from the set. For more tutorials on Python, please visit our Python Central Hub.