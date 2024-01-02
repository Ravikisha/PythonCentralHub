---
title: Dictionary Operations
description: Learn how to perform operations on Python dictionaries. We are going to learn dictionary view objects, dictionary comprehension, and how to merge dictionaries. Looping through dictionaries is also covered. Copying dictionaries is also covered. 
sidebar: 
    order: 67
---

## Dictionary Operations
We are going to learn dictionary view objects, dictionary comprehension, and how to merge dictionaries. Looping through dictionaries is also covered. Copying dictionaries is also covered. Nested dictionaries are also covered. In this tutorial, we will learn how to perform operations on Python dictionaries. 

## Dictionary View Objects
Dictionary view objects are objects that provide a dynamic view of dictionary keys and values. Dictionary view objects are returned by the methods `keys()`, `values()`, and `items()`. Dictionary view objects are dynamic, meaning that they change when the dictionary changes. Dictionary view objects are iterable, meaning that you can loop through them. Dictionary view objects are also set-like, meaning that they do not allow duplicate elements. Dictionary view objects are not dictionaries, but they behave like them.

### Dictionary Keys View Object
The dictionary keys view object is returned by the `keys()` method. The dictionary keys view object is a set-like object that provides a dynamic view of the dictionary keys. The dictionary keys view object is iterable, meaning that you can loop through it. The dictionary keys view object is not a dictionary, but it behaves like one. The dictionary keys view object is dynamic, meaning that it changes when the dictionary changes. The dictionary keys view object is set-like, meaning that it does not allow duplicate elements. The dictionary keys view object is not a set, but it behaves like one.

```python title="dict_keys.py" showLineNumbers{1} {1-2}
data = {'a': 1, 'b': 2, 'c': 3}
keys = data.keys()
print(keys)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python dict_keys.py
dict_keys(['a', 'b', 'c'])
```

In this example, we declare a dictionary and assign it to the variable `data`. We then call the `keys()` method on the dictionary and assign the result to the variable `keys`. We then print the variable `keys`. The output shows that the variable `keys` is a dictionary keys view object.

### Dictionary Values View Object
The dictionary values view object is returned by the `values()` method. The dictionary values view object is a set-like object that provides a dynamic view of the dictionary values. The dictionary values view object is iterable, meaning that you can loop through it. The dictionary values view object is not a dictionary, but it behaves like one. The dictionary values view object is dynamic, meaning that it changes when the dictionary changes. The dictionary values view object is set-like, meaning that it does not allow duplicate elements. The dictionary values view object is not a set, but it behaves like one.

```python title="dict_values.py" showLineNumbers{1} {1-2}
data = {'a': 1, 'b': 2, 'c': 3}
values = data.values()
print(values)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python dict_values.py
dict_values([1, 2, 3])
```

In this example, we declare a dictionary and assign it to the variable `data`. We then call the `values()` method on the dictionary and assign the result to the variable `values`. We then print the variable `values`. The output shows that the variable `values` is a dictionary values view object.

### Dictionary Items View Object
The dictionary items view object is returned by the `items()` method. The dictionary items view object is a set-like object that provides a dynamic view of the dictionary items. The dictionary items view object is iterable, meaning that you can loop through it. The dictionary items view object is not a dictionary, but it behaves like one. The dictionary items view object is dynamic, meaning that it changes when the dictionary changes. The dictionary items view object is set-like, meaning that it does not allow duplicate elements. The dictionary items view object is not a set, but it behaves like one.

```python title="dict_items.py" showLineNumbers{1} {1-2}
data = {'a': 1, 'b': 2, 'c': 3}
items = data.items()
print(items)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python dict_items.py
dict_items([('a', 1), ('b', 2), ('c', 3)])
```

In this example, we declare a dictionary and assign it to the variable `data`. We then call the `items()` method on the dictionary and assign the result to the variable `items`. We then print the variable `items`. The output shows that the variable `items` is a dictionary items view object.

## Dictionary Comprehension
Dictionary comprehension is a way to create dictionaries using an iterable. Dictionary comprehension is similar to list comprehension. Dictionary comprehension is a way to create dictionaries using an iterable. Dictionary comprehension is similar to list comprehension. 

```python title="dict_comprehension.py" showLineNumbers{1} {1-2}
data = {x: x * x for x in range(1, 6)}
print(data)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python dict_comprehension.py
{1: 1, 2: 4, 3: 9, 4: 16, 5: 25}
```

In this example, we declare a dictionary using dictionary comprehension and assign it to the variable `data`. We then print the variable `data`. The output shows that the variable `data` is a dictionary.

## Merging Dictionaries
Merging dictionaries is a way to combine two or more dictionaries into one dictionary. Merging dictionaries is a way to combine two or more dictionaries into one dictionary. 

```python title="dict_merge.py" showLineNumbers{1} {1-3}
data1 = {'a': 1, 'b': 2, 'c': 3}
data2 = {'d': 4, 'e': 5, 'f': 6}
data3 = {**data1, **data2}
print(data3)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python dict_merge.py
{'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5, 'f': 6}
```


In this example, we declare two dictionaries and assign them to the variables `data1` and `data2`. We then declare a third dictionary and assign it to the variable `data3`. We then merge the two dictionaries into the third dictionary using the `**` operator. We then print the variable `data3`. The output shows that the variable `data3` is a dictionary.


### Merging Dictionaries Using update() Method
Merging dictionaries using the `update()` method is a way to combine two or more dictionaries into one dictionary. Merging dictionaries using the `update()` method is a way to combine two or more dictionaries into one dictionary. 

```python title="dict_update.py" showLineNumbers{1} {1-3}
data1 = {'a': 1, 'b': 2, 'c': 3}
data2 = {'d': 4, 'e': 5, 'f': 6}
data3 = data1.copy()
data3.update(data2)
print(data3)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python dict_update.py
{'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5, 'f': 6}
```

In this example, we declare two dictionaries and assign them to the variables `data1` and `data2`. We then declare a third dictionary and assign it to the variable `data3`. We then merge the two dictionaries into the third dictionary using the `update()` method. We then print the variable `data3`. The output shows that the variable `data3` is a dictionary.


## Looping Through Dictionaries
Looping through dictionaries is a way to iterate through the keys, values, or items of a dictionary. Looping through dictionaries is a way to iterate through the keys, values, or items of a dictionary.

### Looping Through Dictionary Keys
Looping through dictionary keys is a way to iterate through the keys of a dictionary. Looping through dictionary keys is a way to iterate through the keys of a dictionary.

```python title="dict_keys_loop.py" showLineNumbers{1} {1-3}
data = {'a': 1, 'b': 2, 'c': 3}
for key in data.keys():
    print(key)
```

Output:

```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\username>python dict_keys_loop.py
a
b
c
```

In this example, we declare a dictionary and assign it to the variable `data`. We then loop through the dictionary keys using a `for` loop. We then print the dictionary key. The output shows that the dictionary keys are printed.

### Looping Through Dictionary Values
Looping through dictionary values is a way to iterate through the values of a dictionary. Looping through dictionary values is a way to iterate through the values of a dictionary.

```python title="dict_values_loop.py" showLineNumbers{1} {1-3}
data = {'a': 1, 'b': 2, 'c': 3}
for value in data.values():
    print(value)
```

Output:

```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\username>python dict_values_loop.py
1
2
3
```

In this example, we declare a dictionary and assign it to the variable `data`. We then loop through the dictionary values using a `for` loop. We then print the dictionary value. The output shows that the dictionary values are printed.

### Looping Through Dictionary Items
Looping through dictionary items is a way to iterate through the items of a dictionary. Looping through dictionary items is a way to iterate through the items of a dictionary.

```python title="dict_items_loop.py" showLineNumbers{1} {1-3}
data = {'a': 1, 'b': 2, 'c': 3}
for key, value in data.items():
    print(key, value)
```

Output:

```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\username>python dict_items_loop.py
a 1
b 2
c 3
```

In this example, we declare a dictionary and assign it to the variable `data`. We then loop through the dictionary items using a `for` loop. We then print the dictionary key and value. The output shows that the dictionary items are printed.

### Lopping using in Keyword
Lopping using the `in` keyword is a way to iterate through the keys of a dictionary. Lopping using the `in` keyword is a way to iterate through the keys of a dictionary.

```python title="dict_in_loop.py" showLineNumbers{1} {1-3}
data = {'a': 1, 'b': 2, 'c': 3}
for key in data:
    print(key)
```

Output:

```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\username>python dict_in_loop.py
a
b
c
```

In this example, we declare a dictionary and assign it to the variable `data`. We then loop through the dictionary keys using a `for` loop. We then print the dictionary key. The output shows that the dictionary keys are printed.

### Looping using enumerate() Function
Looping using the `enumerate()` function is a way to iterate through the keys of a dictionary. Looping using the `enumerate()` function is a way to iterate through the keys of a dictionary.

```python title="dict_enumerate_loop.py" showLineNumbers{1} {1-3}
data = {'a': 1, 'b': 2, 'c': 3}
for index, key in enumerate(data):
    print(index, key)
```

Output:

```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\username>python dict_enumerate_loop.py
0 a
1 b
2 c
```

In this example, we declare a dictionary and assign it to the variable `data`. We then loop through the dictionary keys using a `for` loop. We then print the dictionary key. The output shows that the dictionary keys are printed.

### Lopping using range() Function
Lopping using the `range()` function is a way to iterate through the keys of a dictionary. Lopping using the `range()` function is a way to iterate through the keys of a dictionary.

```python title="dict_range_loop.py" showLineNumbers{1} {1-3}
data = {'a': 1, 'b': 2, 'c': 3}
length = len(data)
for i in range(length):
    print(list(data.keys())[i] + " => " + str(list(data.values())[i]))
```

Output:

```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\username>python dict_range_loop.py
a => 1
b => 2
c => 3
```

In this example, we declare a dictionary and assign it to the variable `data`. We then declare a variable and assign it to the length of the dictionary. We then loop through the dictionary keys using a `for` loop. We then print the dictionary key and value. The output shows that the dictionary keys and values are printed.

## Copying Dictionaries
Copying dictionaries is a way to create a copy of a dictionary. Copying dictionaries is a way to create a copy of a dictionary.

### Direct Copy
Direct copy is a way to create a copy of a dictionary. Direct copy is a way to create a copy of a dictionary.

```python title="dict_direct_copy.py" showLineNumbers{1} {1-3}
data1 = {'a': 1, 'b': 2, 'c': 3}
data2 = data1
print(data2)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python dict_direct_copy.py
{'a': 1, 'b': 2, 'c': 3}
```

In this example, we declare a dictionary and assign it to the variable `data1`. We then declare a second dictionary and assign it to the variable `data2`. We then print the variable `data2`. The output shows that the variable `data2` is a dictionary.

:::caution
Direct copy is not a copy of a dictionary. Direct copy is a reference to a dictionary. If you change the original dictionary, the copy will also change. If you change the copy, the original dictionary will also change.

```python title="dict_direct_copy_change.py" showLineNumbers{1} {1-5}
data1 = {'a': 1, 'b': 2, 'c': 3}
data2 = data1
data2['d'] = 4
print(data1)
print(data2)
```

Output:

```cmd title="command" showLineNumbers{1} {2-7}
C:\Users\username>python dict_direct_copy_change.py
{'a': 1, 'b': 2, 'c': 3, 'd': 4}
{'a': 1, 'b': 2, 'c': 3, 'd': 4}
```

In this example, we declare a dictionary and assign it to the variable `data1`. We then declare a second dictionary and assign it to the variable `data2`. We then add an item to the second dictionary. We then print the variable `data1` and `data2`. The output shows that the variable `data1` and `data2` are dictionaries. The output also shows that the variable `data1` and `data2` are the same dictionary.
:::

### copy() Method
Shallow copy is a way to create a copy of a dictionary. Shallow copy is a way to create a copy of a dictionary.

```python title="dict_shallow_copy.py" showLineNumbers{1} {1-5}
data1 = {'a': 1, 'b': 2, 'c': 3}
data2 = data1.copy()
data2['d'] = 4
print(data1)
print(data2)
```

Output:

```cmd title="command" showLineNumbers{1} {2-7}
C:\Users\username>python dict_shallow_copy.py
{'a': 1, 'b': 2, 'c': 3}
{'a': 1, 'b': 2, 'c': 3, 'd': 4}
```

In this example, we declare a dictionary and assign it to the variable `data1`. We then declare a second dictionary and assign it to the variable `data2`. We then add an item to the second dictionary. We then print the variable `data1` and `data2`. The output shows that the variable `data1` and `data2` are dictionaries. The output also shows that the variable `data1` and `data2` are not the same dictionary.

### deepcopy() Method
Deep copy is a way to create a copy of a dictionary. Deep copy is a way to create a copy of a dictionary.

```python title="dict_deep_copy.py" showLineNumbers{1} {1-5}
import copy
data1 = {'a': 1, 'b': 2, 'c': 3}
data2 = copy.deepcopy(data1)
data2['d'] = 4
print(data1)
print(data2)
```

Output:

```cmd title="command" showLineNumbers{1} {2-7}
C:\Users\username>python dict_deep_copy.py
{'a': 1, 'b': 2, 'c': 3}
{'a': 1, 'b': 2, 'c': 3, 'd': 4}
```

In this example, we import the `copy` module. We then declare a dictionary and assign it to the variable `data1`. We then declare a second dictionary and assign it to the variable `data2`. We then add an item to the second dictionary. We then print the variable `data1` and `data2`. The output shows that the variable `data1` and `data2` are dictionaries. The output also shows that the variable `data1` and `data2` are not the same dictionary.

## Conclusion
In this tutorial, we learned how to perform operations on Python dictionaries. We learned dictionary view objects, dictionary comprehension, and how to merge dictionaries. Looping through dictionaries is also covered. Copying dictionaries is also covered. We are now able to perform operations on Python dictionaries. For more information on Python dictionaries, visit the [official Python dictionaries documentation](https://docs.python.org/3/tutorial/datastructures.html#dictionaries). For more tutorials on Python, visit the Python Central Hub.