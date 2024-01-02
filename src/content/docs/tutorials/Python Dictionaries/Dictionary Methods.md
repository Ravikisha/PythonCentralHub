---
title: Dictionary Methods
description: Learn about the methods available for dictionaries in Python. We will cover the following methods - clear, copy, fromkeys, get, items, keys, pop, popitem, setdefault, update, and values.
sidebar: 
    order: 69
---

## Dictionary Methods
In Python, a dictionary is a collection of key-value pairs. Each key is connected to a value, and you can use a key to access the value associated with that key. A key’s value can be a number, a string, a list, or even another dictionary. In fact, you can use any object that you can create in Python as a value in a dictionary. We have a set of methods that can be used with dictionaries. We will cover the following methods - clear, copy, fromkeys, get, items, keys, pop, popitem, setdefault, update, and values.

## Table of Methods
| S.No. | Method | Description | Example |
| --- | --- | --- | --- |
| 1 | clear() | Removes all the elements from the dictionary | `my_dict.clear()` |
| 2 | copy() | Returns a copy of the dictionary | `my_dict.copy()` |
| 3 | fromkeys() | Returns a dictionary with the specified keys and value | `my_dict.fromkeys(keys, value)` |
| 4 | get() | Returns the value of the specified key | `my_dict.get(key)` |
| 5 | items() | Returns a list containing a tuple for each key value pair | `my_dict.items()` |
| 6 | keys() | Returns a list containing the dictionary's keys | `my_dict.keys()` |
| 7 | pop() | Removes the element with the specified key | `my_dict.pop(key)` |
| 8 | popitem() | Removes the last inserted key-value pair | `my_dict.popitem()` |
| 9 | setdefault() | Returns the value of the specified key. If the key does not exist: insert the key, with the specified value | `my_dict.setdefault(key, value)` |
| 10 | update() | Updates the dictionary with the specified key-value pairs | `my_dict.update(key, value)` |
| 11 | values() | Returns a list of all the values in the dictionary | `my_dict.values()` |
| 12 | has_key() | Returns True if a key exists in the dictionary | `my_dict.has_key(key)` |
| 13 | len() | Returns the number of items in the dictionary | `len(my_dict)` |
| 14 | del | Removes the item with the specified key | `del my_dict[key]` |
| 15 | in | Returns True if a key exists in the dictionary | `key in my_dict` |
| 16 | not in | Returns True if a key does not exist in the dictionary | `key not in my_dict` |


## clear()
The `clear()` method removes all the elements from a dictionary.

```python title="clear.py" showLineNumbers{1} {1-3}
data = {'a': 1, 'b': 2, 'c': 3}
data.clear()
print(data)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python clear.py
{}
```

In this example, we declare a dictionary and assign it to the variable `data`. We then use the `clear()` method to remove all the elements from the dictionary. The output shows that the dictionary is empty.

## copy()
The `copy()` method returns a copy of the specified dictionary.

```python title="copy.py" showLineNumbers{1} {1-3}
data = {'a': 1, 'b': 2, 'c': 3}
new_data = data.copy()
print(new_data)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python copy.py
{'a': 1, 'b': 2, 'c': 3}
```

In this example, we declare a dictionary and assign it to the variable `data`. We then use the `copy()` method to create a copy of the dictionary and assign it to the variable `new_data`. The output shows that the dictionary is copied.

## fromkeys()
The `fromkeys()` method returns a dictionary with the specified keys and value.

```python title="fromkeys.py" showLineNumbers{1} {1-3}
keys = ('a', 'b', 'c')
value = 0
data = dict.fromkeys(keys, value)
print(data)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python fromkeys.py
{'a': 0, 'b': 0, 'c': 0}
```

In this example, we declare a tuple and assign it to the variable `keys`. We then declare a variable `value` and assign it the value `0`. We then use the `fromkeys()` method to create a dictionary with the specified keys and value and assign it to the variable `data`. The output shows that the dictionary is created.

## get()
The `get()` method returns the value of the specified key.

```python title="get.py" showLineNumbers{1} {1-3}
data = {'a': 1, 'b': 2, 'c': 3}
value = data.get('a')
print(value)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python get.py
1
```

In this example, we declare a dictionary and assign it to the variable `data`. We then use the `get()` method to get the value of the key `a` and assign it to the variable `value`. The output shows that the value is returned.

## items()
The `items()` method returns a list containing a tuple for each key value pair.

```python title="items.py" showLineNumbers{1} {1-3}
data = {'a': 1, 'b': 2, 'c': 3}
items = data.items()
print(items)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python items.py
dict_items([('a', 1), ('b', 2), ('c', 3)])
```

In this example, we declare a dictionary and assign it to the variable `data`. We then use the `items()` method to get the items of the dictionary and assign it to the variable `items`. The output shows that the items are returned.

## keys()
The `keys()` method returns a list containing the dictionary's keys.

```python title="keys.py" showLineNumbers{1} {1-3}
data = {'a': 1, 'b': 2, 'c': 3}
keys = data.keys()
print(keys)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python keys.py
dict_keys(['a', 'b', 'c'])
```

In this example, we declare a dictionary and assign it to the variable `data`. We then use the `keys()` method to get the keys of the dictionary and assign it to the variable `keys`. The output shows that the keys are returned.

## pop()
The `pop()` method removes the element with the specified key.

```python title="pop.py" showLineNumbers{1} {1-3}
data = {'a': 1, 'b': 2, 'c': 3}
data.pop('a')
print(data)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python pop.py
{'b': 2, 'c': 3}
```

In this example, we declare a dictionary and assign it to the variable `data`. We then use the `pop()` method to remove the element with the key `a`. The output shows that the element is removed.

## popitem()
The `popitem()` method removes the last inserted key-value pair.

```python title="popitem.py" showLineNumbers{1} {1-3}
data = {'a': 1, 'b': 2, 'c': 3}
data.popitem()
print(data)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python popitem.py
{'a': 1, 'b': 2}
```

In this example, we declare a dictionary and assign it to the variable `data`. We then use the `popitem()` method to remove the last inserted key-value pair. The output shows that the key-value pair is removed.

## setdefault()
The `setdefault()` method returns the value of the specified key. If the key does not exist: insert the key, with the specified value.

```python title="setdefault.py" showLineNumbers{1} {1-8}
data = {'a': 1, 'b': 2, 'c': 3}
value = data.setdefault('a', 0)
print(value)
value = data.setdefault('d', 4)
print(value)
print(data)
```

Output:

```cmd title="command" showLineNumbers{1} {2-8}
C:\Users\username>python setdefault.py
1
4
{'a': 1, 'b': 2, 'c': 3, 'd': 4}
```

In this example, we declare a dictionary and assign it to the variable `data`. We then use the `setdefault()` method to get the value of the key `a` and assign it to the variable `value`. The output shows that the value is returned. We then use the `setdefault()` method to get the value of the key `d` and assign it to the variable `value`. The output shows that the value is returned and the key-value pair is added to the dictionary.

## update()
The `update()` method updates the dictionary with the specified key-value pairs.

```python title="update.py" showLineNumbers{1} {1-3}
data = {'a': 1, 'b': 2, 'c': 3}
data.update({'d': 4, 'e': 5})
print(data)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python update.py
{'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5}
```

In this example, we declare a dictionary and assign it to the variable `data`. We then use the `update()` method to update the dictionary with the specified key-value pairs. The output shows that the dictionary is updated.

## values()
The `values()` method returns a list of all the values in the dictionary.

```python title="values.py" showLineNumbers{1} {1-3}
data = {'a': 1, 'b': 2, 'c': 3}
values = data.values()
print(values)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python values.py
dict_values([1, 2, 3])
```

In this example, we declare a dictionary and assign it to the variable `data`. We then use the `values()` method to get the values of the dictionary and assign it to the variable `values`. The output shows that the values are returned.

## has_key()
The `has_key()` method returns True if a key exists in the dictionary.

```python title="has_key.py" showLineNumbers{1} {1-3}
data = {'a': 1, 'b': 2, 'c': 3}
print(data.has_key('a'))
print(data.has_key('d'))
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python has_key.py
True
False
```

In this example, we declare a dictionary and assign it to the variable `data`. We then use the `has_key()` method to check if the key `a` exists in the dictionary. The output shows that the key exists. We then use the `has_key()` method to check if the key `d` exists in the dictionary. The output shows that the key does not exist.

## len()
The `len()` method returns the number of items in the dictionary.

```python title="len.py" showLineNumbers{1} {1-3}
data = {'a': 1, 'b': 2, 'c': 3}
print(len(data))
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python len.py
3
```

In this example, we declare a dictionary and assign it to the variable `data`. We then use the `len()` method to get the number of items in the dictionary. The output shows that the number of items is returned.

## del
The `del` keyword removes the item with the specified key.

```python title="del.py" showLineNumbers{1} {1-3}
data = {'a': 1, 'b': 2, 'c': 3}
del data['a']
print(data)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python del.py
{'b': 2, 'c': 3}
```

In this example, we declare a dictionary and assign it to the variable `data`. We then use the `del` keyword to remove the item with the key `a`. The output shows that the item is removed.

## in
The `in` keyword returns True if a key exists in the dictionary.

```python title="in.py" showLineNumbers{1} {1-3}
data = {'a': 1, 'b': 2, 'c': 3}
print('a' in data)
print('d' in data)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python in.py
True
False
```

In this example, we declare a dictionary and assign it to the variable `data`. We then use the `in` keyword to check if the key `a` exists in the dictionary. The output shows that the key exists. We then use the `in` keyword to check if the key `d` exists in the dictionary. The output shows that the key does not exist.

## not in
The `not in` keyword returns True if a key does not exist in the dictionary.

```python title="not_in.py" showLineNumbers{1} {1-3}
data = {'a': 1, 'b': 2, 'c': 3}
print('a' not in data)
print('d' not in data)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python not_in.py
False
True
```

In this example, we declare a dictionary and assign it to the variable `data`. We then use the `not in` keyword to check if the key `a` does not exist in the dictionary. The output shows that the key exists. We then use the `not in` keyword to check if the key `d` does not exist in the dictionary. The output shows that the key does not exist.

## Conclusion
In this tutorial, we have covered the methods available for dictionaries in Python. We have covered the following methods - clear, copy, fromkeys, get, items, keys, pop, popitem, setdefault, update, and values. For more information on dictionaries, you can refer to the [official documentation](https://docs.python.org/3/tutorial/datastructures.html#dictionaries). For more tutorials on Python, you can refer to the Python Central Hub.