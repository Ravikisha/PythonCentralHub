---
title: Set Methods
description: Learn how to use the methods of the Python Set object. In this tutorial, you will learn how to add, remove, and update elements in a set. You will also learn how to perform set operations such as union, intersection, and difference. 
sidebar: 
    order: 62
---

## Set Methods
Set methods are used to perform operations on sets. In this tutorial, you will learn how to use the methods of the Python Set object. You will learn how to add, remove, and update elements in a set. You will also learn how to perform set operations such as union, intersection, and difference.

## Table of Set Methods
|S.No.|Method|Description|Example|
|----|------|-----------|-------|
|1|add()|Adds an element to the set|`set.add(element)`|
|2|clear()|Removes all elements from the set|`set.clear()`|
|3|copy()|Returns a copy of the set|`set.copy()`|
|4|difference()|Returns a set containing the difference between two or more sets|`set.difference(set1, set2, ...)`|
|5|difference_update()|Removes the items in this set that are also included in another, specified set|`set.difference_update(set1, set2, ...)`|
|6|discard()|Remove the specified item|`set.discard(element)`|
|7|intersection()|Returns a set, that is the intersection of two other sets|`set.intersection(set1, set2, ...)`|
|8|intersection_update()|Removes the items in this set that are not present in other, specified set(s)|`set.intersection_update(set1, set2, ...)`|
|9|isdisjoint()|Returns whether two sets have a intersection or not|`set.isdisjoint(set)`|
|10|issubset()|Returns whether another set contains this set or not|`set.issubset(set)`|
|11|issuperset()|Returns whether this set contains another set or not|`set.issuperset(set)`|
|12|pop()|Removes an element from the set|`set.pop()`|
|13|remove()|Removes the specified element|`set.remove(element)`|
|14|symmetric_difference()|Returns a set with the symmetric differences of two sets|`set.symmetric_difference(set)`|
|15|symmetric_difference_update()|inserts the symmetric differences from this set and another|`set.symmetric_difference_update(set)`|
|16|union()|Return a set containing the union of sets|`set.union(set1, set2, ...)`|
|17|update()|Update the set with the union of this set and others|`set.update(set1, set2, ...)`|
|18|len()|Returns the length of the set|`len(set)`|

## add() Method
The `add()` method adds an element to the set. If the element already exists, the add() method does not add the element.

Here is an example:

```python title="set_add.py" showLineNumbers{1} {1-3}
data = {'a', 'b', 'c', 'd', 'e', 'f', 'g'}
data.add('h')
print(data)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python set_add.py
{'a', 'b', 'd', 'f', 'h', 'g', 'c', 'e'}
```

In this example, we declare a set and assign it to the variable `data`. We then add the item `h` to the set using the `add()` method. The output shows that the item is added to the set.

## clear() Method
The `clear()` method removes all elements from the set.

Here is an example:

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

In this example, we declare a set and assign it to the variable `data`. We then remove all the items from the set using the `clear()` method. The output shows that the set is empty.

## copy() Method
The `copy()` method returns a copy of the set.

Here is an example:

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
{'a', 'b', 'd', 'f', 'g', 'c', 'e'}
{'a', 'b', 'd', 'f', 'h', 'g', 'c', 'e'}
```

In this example, we declare a set and assign it to the variable `data`. We then copy the set to the variable `data2` using the `copy()` method. We add the item `h` to the `data2` set. The output shows that the item is added to the `data2` set but not to the `data` set.

## difference() Method
The `difference()` method returns a set containing the difference between two or more sets.

Here is an example:

```python title="set_difference.py" showLineNumbers{1} {1-4}
data = {'a', 'b', 'c', 'd', 'e', 'f', 'g'}
data2 = {'a', 'b', 'c', 'h', 'i', 'j', 'k'}
data3 = data.difference(data2)
print(data3)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python set_difference.py
{'f', 'g', 'd', 'e'}
```

In this example, we declare two sets and assign them to the variables `data` and `data2`. We then find the difference between the two sets using the `difference()` method. The output shows that the items in the `data` set that are not in the `data2` set are returned.

## difference_update() Method
The `difference_update()` method removes the items in this set that are also included in another, specified set.

Here is an example:

```python title="set_difference_update.py" showLineNumbers{1} {1-4}
data = {'a', 'b', 'c', 'd', 'e', 'f', 'g'}
data2 = {'a', 'b', 'c', 'h', 'i', 'j', 'k'}
data.difference_update(data2)
print(data)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python set_difference_update.py
{'d', 'f', 'g', 'e'}
```

In this example, we declare two sets and assign them to the variables `data` and `data2`. We then remove the items in the `data` set that are also included in the `data2` set using the `difference_update()` method. The output shows that the items in the `data` set that are also included in the `data2` set are removed.

## discard() Method
The `discard()` method removes the specified item from the set.

Here is an example:

```python title="set_discard.py" showLineNumbers{1} {1-4}
data = {'a', 'b', 'c', 'd', 'e', 'f', 'g'}
data.discard('a')
print(data)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python set_discard.py
{'d', 'f', 'g', 'c', 'e', 'b'}
```

In this example, we declare a set and assign it to the variable `data`. We then remove the item `a` from the set using the `discard()` method. The output shows that the item is removed from the set.

## intersection() Method
The `intersection()` method returns a set that is the intersection of two or more sets.

Here is an example:

```python title="set_intersection.py" showLineNumbers{1} {1-4}
data = {'a', 'b', 'c', 'd', 'e', 'f', 'g'}
data2 = {'a', 'b', 'c', 'h', 'i', 'j', 'k'}
data3 = data.intersection(data2)
print(data3)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python set_intersection.py
{'a', 'b', 'c'}
```

In this example, we declare two sets and assign them to the variables `data` and `data2`. We then find the intersection of the two sets using the `intersection()` method. The output shows that the items in the `data` set that are also in the `data2` set are returned.

## intersection_update() Method
The `intersection_update()` method removes the items in this set that are not present in other, specified set(s).

Here is an example:

```python title="set_intersection_update.py" showLineNumbers{1} {1-4}
data = {'a', 'b', 'c', 'd', 'e', 'f', 'g'}
data2 = {'a', 'b', 'c', 'h', 'i', 'j', 'k'}
data.intersection_update(data2)
print(data)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python set_intersection_update.py
{'a', 'b', 'c'}
```

In this example, we declare two sets and assign them to the variables `data` and `data2`. We then remove the items in the `data` set that are not present in the `data2` set using the `intersection_update()` method. The output shows that the items in the `data` set that are not present in the `data2` set are removed.

## isdisjoint() Method
The `isdisjoint()` method returns whether two sets have a intersection or not.

Here is an example:

```python title="set_isdisjoint.py" showLineNumbers{1} {1-4}
data = {'a', 'b', 'c', 'd', 'e', 'f', 'g'}
data2 = {'h', 'i', 'j', 'k', 'l', 'm', 'n'}
data3 = data.isdisjoint(data2)
print(data3)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python set_isdisjoint.py
True
```

In this example, we declare two sets and assign them to the variables `data` and `data2`. We then check if the two sets have a intersection using the `isdisjoint()` method. The output shows that the two sets do not have a intersection.

## issubset() Method
The `issubset()` method returns whether another set contains this set or not.

Here is an example:

```python title="set_issubset.py" showLineNumbers{1} {1-4}
data = {'a', 'b', 'c', 'd', 'e', 'f', 'g'}
data2 = {'a', 'b', 'c'}
data3 = data2.issubset(data)
print(data3)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python set_issubset.py
True
```

In this example, we declare two sets and assign them to the variables `data` and `data2`. We then check if the `data2` set contains the `data` set using the `issubset()` method. The output shows that the `data2` set contains the `data` set.

## issuperset() Method
The `issuperset()` method returns whether this set contains another set or not.

Here is an example:

```python title="set_issuperset.py" showLineNumbers{1} {1-4}
data = {'a', 'b', 'c', 'd', 'e', 'f', 'g'}
data2 = {'a', 'b', 'c'}
data3 = data.issuperset(data2)
print(data3)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python set_issuperset.py
True
```

In this example, we declare two sets and assign them to the variables `data` and `data2`. We then check if the `data` set contains the `data2` set using the `issuperset()` method. The output shows that the `data` set contains the `data2` set.

## pop() Method
The `pop()` method removes an element from the set.

Here is an example:

```python title="set_pop.py" showLineNumbers{1} {1-4}
data = {'a', 'b', 'c', 'd', 'e', 'f', 'g'}
data.pop()
print(data)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python set_pop.py
{'d', 'f', 'g', 'c', 'e', 'b'}
```

In this example, we declare a set and assign it to the variable `data`. We then remove an element from the set using the `pop()` method. The output shows that an element is removed from the set.

## remove() Method
The `remove()` method removes the specified element from the set.

Here is an example:

```python title="set_remove.py" showLineNumbers{1} {1-4}
data = {'a', 'b', 'c', 'd', 'e', 'f', 'g'}
data.remove('a')
print(data)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python set_remove.py
{'d', 'f', 'g', 'c', 'e', 'b'}
```

In this example, we declare a set and assign it to the variable `data`. We then remove the element `a` from the set using the `remove()` method. The output shows that the element is removed from the set.

## symmetric_difference() Method
The `symmetric_difference()` method returns a set with the symmetric differences of two sets.

Here is an example:

```python title="set_symmetric_difference.py" showLineNumbers{1} {1-4}
data = {'a', 'b', 'c', 'd', 'e', 'f', 'g'}
data2 = {'a', 'b', 'c', 'h', 'i', 'j', 'k'}
data3 = data.symmetric_difference(data2)
print(data3)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python set_symmetric_difference.py
{'d', 'j', 'e', 'k', 'f', 'i', 'h', 'g'}
```

In this example, we declare two sets and assign them to the variables `data` and `data2`. We then find the symmetric differences of the two sets using the `symmetric_difference()` method. The output shows that the items in the `data` set that are not in the `data2` set and the items in the `data2` set that are not in the `data` set are returned.

## symmetric_difference_update() Method
The `symmetric_difference_update()` method inserts the symmetric differences from this set and another.

Here is an example:

```python title="set_symmetric_difference_update.py" showLineNumbers{1} {1-4}
data = {'a', 'b', 'c', 'd', 'e', 'f', 'g'}
data2 = {'a', 'b', 'c', 'h', 'i', 'j', 'k'}
data.symmetric_difference_update(data2)
print(data)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python set_symmetric_difference_update.py
{'d', 'j', 'e', 'k', 'f', 'i', 'h', 'g'}
```

In this example, we declare two sets and assign them to the variables `data` and `data2`. We then insert the symmetric differences from the `data` set and the `data2` set using the `symmetric_difference_update()` method. The output shows that the items in the `data` set that are not in the `data2` set and the items in the `data2` set that are not in the `data` set are inserted.

## union() Method
The `union()` method returns a set containing the union of sets.

Here is an example:

```python title="set_union.py" showLineNumbers{1} {1-4}
data = {'a', 'b', 'c', 'd', 'e', 'f', 'g'}
data2 = {'h', 'i', 'j', 'k', 'l', 'm', 'n'}
data3 = data.union(data2)
print(data3)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python set_union.py
{'m', 'd', 'n', 'j', 'h', 'e', 'a', 'b', 'f', 'l', 'k', 'i', 'g', 'c'}
```

In this example, we declare two sets and assign them to the variables `data` and `data2`. We then find the union of the two sets using the `union()` method. The output shows that the items in the `data` set and the items in the `data2` set are returned.

## update() Method
The `update()` method updates the set with the union of this set and others.

Here is an example:

```python title="set_update.py" showLineNumbers{1} {1-4}
data = {'a', 'b', 'c', 'd', 'e', 'f', 'g'}
data2 = {'h', 'i', 'j', 'k', 'l', 'm', 'n'}
data.update(data2)
print(data)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python set_update.py
{'m', 'd', 'n', 'j', 'h', 'e', 'a', 'b', 'f', 'l', 'k', 'i', 'g', 'c'}
```

In this example, we declare two sets and assign them to the variables `data` and `data2`. We then update the set with the union of the `data` set and the `data2` set using the `update()` method. The output shows that the items in the `data` set and the items in the `data2` set are updated.

## len() Method
The `len()` method returns the length of the set.

Here is an example:

```python title="set_len.py" showLineNumbers{1} {1-3}
data = {'a', 'b', 'c', 'd', 'e', 'f', 'g'}
print(len(data))
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python set_len.py
7
```

In this example, we declare a set and assign it to the variable `data`. We then find the length of the set using the `len()` method. The output shows that the length of the set is returned.

## Conclusion
In this tutorial, you have learned how to use the methods of the Python Set object. You have learned how to add, remove, and update elements in a set. You have also learned how to perform set operations such as union, intersection, and difference. For more information on sets, visit the Python Central Hub.