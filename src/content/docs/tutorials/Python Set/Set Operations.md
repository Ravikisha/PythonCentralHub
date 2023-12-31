---
title: Set Operations
description: Learn how to perform set operations in Python. We will cover the union, intersection, difference, and symmetric difference operations. We will also cover the subset and superset operations. We are also going to talk about loops and how to use them to iterate over sets. how to join sets, and how to check if an item exists in a set and also copy a set.
sidebar: 
    order: 61
---

In this tutorial, we are going to learn how to perform set operations in Python. We will cover the union, intersection, difference, and symmetric difference operations. We will also cover the subset and superset operations. We are also going to talk about loops and how to use them to iterate over sets. how to join sets, and how to check if an item exists in a set and also copy a set.

## Set Operations
In the set theory, there are several operations that we can perform on sets. In this section, we are going to learn how to perform these operations in Python.

### Union (|) Operation
The union operation returns a new set that contains all the elements that are in either set. In Python, we can use the `|` operator to perform the union operation.

```python title="set_union.py" showLineNumbers{1} {1-3}
data = {'a', 'b', 'c', 'd', 'e', 'f', 'g'}
data2 = {'h', 'i', 'j', 'k', 'l', 'm', 'n'}
data3 = data | data2
print(data3)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python set_union.py
{'m', 'd', 'n', 'j', 'h', 'e', 'a', 'b', 'f', 'l', 'k', 'i', 'g', 'c'}
```

In this example, we declare two sets and assign them to the variables `data` and `data2`. We then use the `|` operator to perform the union operation on the two sets and assign the result to the variable `data3`. The output shows that the items are added to the set.


### Intersection (&) Operation
The intersection operation returns a new set that contains the elements that are common in both sets. In Python, we can use the `&` operator to perform the intersection operation.

```python title="set_intersection.py" showLineNumbers{1} {1-3}
data = {'a', 'b', 'c', 'd', 'e', 'f', 'g'}
data2 = {'d', 'e', 'f', 'g', 'h', 'i', 'j'}
data3 = data & data2
print(data3)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python set_intersection.py
{'f', 'g', 'd', 'e'}
```

In this example, we declare two sets and assign them to the variables `data` and `data2`. We then use the `&` operator to perform the intersection operation on the two sets and assign the result to the variable `data3`. The output shows that the items are added to the set.

### Difference (-) Operation
The difference operation returns a new set that contains the elements that are in the first set but not in the second set. In Python, we can use the `-` operator to perform the difference operation.

```python title="set_difference.py" showLineNumbers{1} {1-3}
data = {'a', 'b', 'c', 'd', 'e', 'f', 'g'}
data2 = {'d', 'e', 'f', 'g', 'h', 'i', 'j'}
data3 = data - data2
print(data3)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python set_difference.py
{'a', 'b', 'c'}
```

In this example, we declare two sets and assign them to the variables `data` and `data2`. We then use the `-` operator to perform the difference operation on the two sets and assign the result to the variable `data3`. The output shows that the items are added to the set.

### Symmetric Difference (^) Operation
The symmetric difference operation returns a new set that contains the elements that are in either set but not in both sets. In Python, we can use the `^` operator to perform the symmetric difference operation.

```python title="set_symmetric_difference.py" showLineNumbers{1} {1-3}
data = {'a', 'b', 'c', 'd', 'e', 'f', 'g'}
data2 = {'d', 'e', 'f', 'g', 'h', 'i', 'j'}
data3 = data ^ data2
print(data3)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python set_symmetric_difference.py
{'j', 'b', 'c', 'a', 'i', 'h'}
```

In this example, we declare two sets and assign them to the variables `data` and `data2`. We then use the `^` operator to perform the symmetric difference operation on the two sets and assign the result to the variable `data3`. The output shows that the items are added to the set.

### Subset (<=) Operation
The subset operation returns `True` if all the elements of the first set are in the second set. In Python, we can use the `<=` operator to perform the subset operation.

```python title="set_subset.py" showLineNumbers{1} {1-3}
data = {'a', 'b', 'c', 'd', 'e', 'f', 'g'}
data2 = {'d', 'e', 'f', 'g', 'h', 'i', 'j'}
data3 = data <= data2
print(data3)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python set_subset.py
False
```

In this example, we declare two sets and assign them to the variables `data` and `data2`. We then use the `<=` operator to perform the subset operation on the two sets and assign the result to the variable `data3`. The output shows that the items are added to the set.

### Superset (>=) Operation
The superset operation returns `True` if all the elements of the second set are in the first set. In Python, we can use the `>=` operator to perform the superset operation.

```python title="set_superset.py" showLineNumbers{1} {1-3}
data = {'a', 'b', 'c', 'd', 'e', 'f', 'g'}
data2 = {'d', 'e', 'f', 'g', 'h', 'i', 'j'}
data3 = data >= data2
print(data3)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python set_superset.py
False
```

In this example, we declare two sets and assign them to the variables `data` and `data2`. We then use the `>=` operator to perform the superset operation on the two sets and assign the result to the variable `data3`. The output shows that the items are added to the set.

## Set Loops
In Python, we can use loops to iterate over sets. In this section, we are going to learn how to use loops to iterate over sets.

### For Loop
In Python, we can use the `for` loop to iterate over sets. In the `for` loop, we can use the `in` keyword to check if an item exists in a set.

```python title="set_for_loop.py" showLineNumbers{1} {1-3}
data = {'a', 'b', 'c', 'd', 'e', 'f', 'g'}
for item in data:
    print(item)
```

Output:

```cmd title="command" showLineNumbers{1} {2-8}
C:\Users\username>python set_for_loop.py
a
b
d
f
g
c
e
```

In this example, we declare a set and assign it to the variable `data`. We then use the `for` loop to iterate over the set and print the items.

### While Loop
In Python, we can use the `while` loop to iterate over sets. In the `while` loop, we can use the `in` keyword to check if an item exists in a set.

```python title="set_while_loop.py" showLineNumbers{1} {1-5}
data = {'a', 'b', 'c', 'd', 'e', 'f', 'g'}
i = 0
while i < len(data):
    print(data[i])
    i += 1
```

Output:

```cmd title="command" showLineNumbers{1} {2-8}
C:\Users\username>python set_while_loop.py
a
b
d
f
g
c
e
```

In this example, we declare a set and assign it to the variable `data`. We then use the `while` loop to iterate over the set and print the items.

### Adding Elements to a Set Using Loops
In Python, we can use loops to add elements to a set. In this section, we are going to learn how to use loops to add elements to a set.

```python title="set_add_elements.py" showLineNumbers{1} {1-3}
data = set()
for i in range(1, 11):
    data.add(i)
print(data)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python set_add_elements.py
{1, 2, 3, 4, 5, 6, 7, 8, 9, 10}
```

In this example, we declare an empty set and assign it to the variable `data`. We then use the `for` loop to iterate over the range of numbers from 1 to 10 and add the numbers to the set using the `add()` method. The output shows that the items are added to the set.

## Set Join
Joining two sets is called a union operation. In Python, we can use the `|`, `update()`, and `union()` methods to join two sets.

### Using the `|` Operator
In Python, we can use the `|` operator to join two sets.

```python title="set_join.py" showLineNumbers{1} {1-3}
data = {'a', 'b', 'c', 'd', 'e', 'f', 'g'}
data2 = {'d', 'e', 'f', 'g', 'h', 'i', 'j'}
data3 = data | data2
print(data3)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python set_join.py
{'d', 'j', 'e', 'a', 'b', 'f', 'i', 'h', 'g', 'c'}
```

In this example, we declare two sets and assign them to the variables `data` and `data2`. We then use the `|` operator to join the two sets and assign the result to the variable `data3`. The output shows that the items are added to the set.

### Using the `update()` Method
In Python, we can use the `update()` method to join two sets.

```python title="set_update.py" showLineNumbers{1} {1-3}
data = {'a', 'b', 'c', 'd', 'e', 'f', 'g'}
data2 = {'d', 'e', 'f', 'g', 'h', 'i', 'j'}
data.update(data2)
print(data)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python set_update.py
{'d', 'j', 'e', 'a', 'b', 'f', 'i', 'h', 'g', 'c'}
```

In this example, we declare two sets and assign them to the variables `data` and `data2`. We then use the `update()` method to join the two sets and assign the result to the variable `data3`. The output shows that the items are added to the set.

### Using the `union()` Method
In Python, we can use the `union()` method to join two sets.

```python title="set_union.py" showLineNumbers{1} {1-3}
data = {'a', 'b', 'c', 'd', 'e', 'f', 'g'}
data2 = {'d', 'e', 'f', 'g', 'h', 'i', 'j'}
data3 = data.union(data2)
print(data3)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python set_union.py
{'d', 'j', 'e', 'a', 'b', 'f', 'i', 'h', 'g', 'c'}
```

In this example, we declare two sets and assign them to the variables `data` and `data2`. We then use the `union()` method to join the two sets and assign the result to the variable `data3`. The output shows that the items are added to the set.

## Unpacking Sets
In Python, we can use the `*` operator to unpack sets. In this section, we are going to learn how to use the `*` operator to unpack sets.

```python title="set_unpack.py" showLineNumbers{1} {1-3}
data = {'a', 'b', 'c', 'd', 'e', 'f', 'g'}
data2 = {'d', 'e', 'f', 'g', 'h', 'i', 'j'}
data3 = {*data, *data2}
print(data3)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python set_unpack.py
{'d', 'j', 'e', 'a', 'b', 'f', 'i', 'h', 'g', 'c'}
```

In this example, we declare two sets and assign them to the variables `data` and `data2`. We then use the `*` operator to unpack the two sets and assign the result to the variable `data3`. The output shows that the items are added to the set.

## Set Copy
In Python, we can use the `copy()` method to copy a set. In this section, we are going to learn how to use the `copy()` method to copy a set.

:::caution
When we copy a set, we are creating a new set that contains the same items as the original set. If we change the items of the original set, the items of the copied set will not change. However, if we change the items of the copied set, the items of the original set will change.

```python title="set_copy.py" showLineNumbers{1} {1-3}
data = {'a', 'b', 'c', 'd', 'e', 'f', 'g'}
data2 = data
data2.add('h')
print(data)
print(data2)
```

Output:

```cmd title="command" showLineNumbers{1} {2-4}
C:\Users\username>python set_copy.py
{'d', 'e', 'a', 'b', 'f', 'g', 'h', 'c'}
{'d', 'e', 'a', 'b', 'f', 'g', 'h', 'c'}
```

In this example, we declare a set and assign it to the variable `data`. We then assign the `data` set to the variable `data2`. We then add the item `h` to the `data2` set. The output shows that the item `h` is added to both sets.
:::

Now, let's see how to copy a set using the `copy()` method.

```python title="set_copy.py" showLineNumbers{1} {1-3}
data = {'a', 'b', 'c', 'd', 'e', 'f', 'g'}
data2 = data.copy()
data2.add('h')
print(data)
print(data2)
```

Output:

```cmd title="command" showLineNumbers{1} {2-4}
C:\Users\username>python set_copy.py
{'d', 'e', 'a', 'b', 'f', 'g', 'c'}
{'d', 'e', 'a', 'b', 'f', 'g', 'h', 'c'}
```

In this example, we declare a set and assign it to the variable `data`. We then use the `copy()` method to copy the `data` set to the variable `data2`. We then add the item `h` to the `data2` set. The output shows that the item `h` is added to the `data2` set only.

## Set Membership
In Python, we can use the `in` keyword to check if an item exists in a set. In this section, we are going to learn how to use the `in` keyword to check if an item exists in a set.

```python title="set_membership.py" showLineNumbers{1} {1-7}
data = {'a', 'b', 'c', 'd', 'e', 'f', 'g'}
if 'a' in data:
    print('a exists in the set')
else:
    print('a does not exist in the set')
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python set_membership.py
a exists in the set
```

In this example, we declare a set and assign it to the variable `data`. We then use the `in` keyword to check if the item `a` exists in the set. The output shows that the item `a` exists in the set.

## Set Length
In Python, we can use the `len()` method to get the length of a set. In this section, we are going to learn how to use the `len()` method to get the length of a set.

```python title="set_length.py" showLineNumbers{1} {1-3}
data = {'a', 'b', 'c', 'd', 'e', 'f', 'g'}
print(len(data))
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python set_length.py
7
```

In this example, we declare a set and assign it to the variable `data`. We then use the `len()` method to get the length of the set. The output shows that the length of the set is 7.

## Conclusion
In this tutorial, we learned how to perform set operations in Python. We covered the union, intersection, difference, and symmetric difference operations. We also covered the subset and superset operations. We also talked about loops and how to use them to iterate over sets. We also learned how to join sets, and how to check if an item exists in a set and also copy a set. Now you can use sets in your Python programs. To learn more about sets, visit the [Python sets](https://docs.python.org/3/tutorial/datastructures.html#sets) page. For more tutorials, visit our Python Central Hub.