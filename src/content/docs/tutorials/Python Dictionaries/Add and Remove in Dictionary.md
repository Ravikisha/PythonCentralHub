---
title: Add and Remove in Dictionary
description: Learn how to add and remove items in a dictionary. In this tutorial, we will learn how to add and remove items in a dictionary. We will also learn how to update the value of an existing key. We will also learn how to remove a key-value pair from a dictionary. We will also learn how to remove all items from a dictionary. We will also learn how to delete a dictionary. 
sidebar: 
    order: 66
---

## Add items in a dictionary
In Python, we can add items in a dictionary using the following ways.

### Add a new key-value pair using [] operator
We can add a new key-value pair in a dictionary using the `[]` operator. If the key already exists in the dictionary, then the value of the key is updated. If the key does not exist in the dictionary, then a new key-value pair is added to the dictionary.

```python title="dict_add.py" showLineNumbers{1} {1-2}
data = {'a': 1, 'b': 2, 'c': 3, 'd': 4}
data['e'] = 5
print(data)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python dict_add.py
{'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5}
```

In this example, we declare a dictionary and assign it to the variable `data`. We then add a new key-value pair to the dictionary using the `[]` operator. The output shows that the new key-value pair is added to the dictionary.

### Add a new key-value pair using update() method
We can add a new key-value pair in a dictionary using the `update()` method. If the key already exists in the dictionary, then the value of the key is updated. If the key does not exist in the dictionary, then a new key-value pair is added to the dictionary.

```python title="dict_update.py" showLineNumbers{1} {1-2}
data = {'a': 1, 'b': 2, 'c': 3, 'd': 4}
data.update({'e': 5})
print(data)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python dict_update.py
{'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5}
```

In this example, we declare a dictionary and assign it to the variable `data`. We then add a new key-value pair to the dictionary using the `update()` method. The output shows that the new key-value pair is added to the dictionary.

### Adding pairs with Iterable
We can add a new key-value pair in a dictionary using the `update()` method. If the key already exists in the dictionary, then the value of the key is updated. If the key does not exist in the dictionary, then a new key-value pair is added to the dictionary.

```python title="dict_update_iterable.py" showLineNumbers{1} {1-2}
data = {'a': 1, 'b': 2, 'c': 3, 'd': 4}
data.update([('e', 5), ('f', 6)])
print(data)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python dict_update_iterable.py
{'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5, 'f': 6}
```

In this example, we declare a dictionary and assign it to the variable `data`. We then add a new key-value pair to the dictionary using the `update()` method. The output shows that the new key-value pair is added to the dictionary.

### Adding pairs with keyword arguments
We can add a new key-value pair in a dictionary using the `update()` method. If the key already exists in the dictionary, then the value of the key is updated. If the key does not exist in the dictionary, then a new key-value pair is added to the dictionary.

```python title="dict_update_keyword.py" showLineNumbers{1} {1-2}
data = {'a': 1, 'b': 2, 'c': 3, 'd': 4}
data.update(e=5, f=6)
print(data)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python dict_update_keyword.py
{'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5, 'f': 6}
```

In this example, we declare a dictionary and assign it to the variable `data`. We then add a new key-value pair to the dictionary using the `update()` method. The output shows that the new key-value pair is added to the dictionary.

### Using the Unpacking operator (**)
We can add a new key-value pair in a dictionary using the `update()` method. If the key already exists in the dictionary, then the value of the key is updated. If the key does not exist in the dictionary, then a new key-value pair is added to the dictionary. We are using the unpacking operator(`**`) to add a new key-value pair in a dictionary.

```python title="dict_update_unpacking.py" showLineNumbers{1} {1-3}
data = {'a': 1, 'b': 2, 'c': 3, 'd': 4}
data2 = {'e': 5, 'f': 6}
data.update(**data2)
print(data)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python dict_update_unpacking.py
{'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5, 'f': 6}
```

In this example, we declare a dictionary and assign it to the variable `data`. We then add a new key-value pair to the dictionary using the `update()` method. The output shows that the new key-value pair is added to the dictionary.

### Create a new dictionary using the Unpacking operator (**) and update() method
We can add a new key-value pair in a dictionary using the `update()` method. If the key already exists in the dictionary, then the value of the key is updated. If the key does not exist in the dictionary, then a new key-value pair is added to the dictionary. We are using the unpacking operator(`**`) to add a new key-value pair in a dictionary.

```python title="dict_update_unpacking_new.py" showLineNumbers{1} {1-3}
data = {'a': 1, 'b': 2, 'c': 3, 'd': 4}
data2 = {'e': 5, 'f': 6}
data3 = {**data, **data2}
print(data3)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python dict_update_unpacking_new.py
{'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5, 'f': 6}
```

In this example, we declare a dictionary and assign it to the variable `data`. We then add a new key-value pair to the dictionary using the `update()` method. The output shows that the new key-value pair is added to the dictionary.

### Add a new key-value pair using setdefault() method
We can add a new key-value pair in a dictionary using the `setdefault()` method. If the key already exists in the dictionary, then the value of the key is updated. If the key does not exist in the dictionary, then a new key-value pair is added to the dictionary.

```python title="dict_setdefault.py" showLineNumbers{1} {1-2}
data = {'a': 1, 'b': 2, 'c': 3, 'd': 4}
data.setdefault('e', 5)
print(data)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python dict_setdefault.py
{'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5}
```

In this example, we declare a dictionary and assign it to the variable `data`. We then add a new key-value pair to the dictionary using the `setdefault()` method. The output shows that the new key-value pair is added to the dictionary.

### Using the Union operator (|) 
We can add a new key-value pair in a dictionary using the Union operator(`|`). If the key already exists in the dictionary, then the value of the key is updated. If the key does not exist in the dictionary, then a new key-value pair is added to the dictionary. We are using the union operator(`|`) to add a new key-value pair in a dictionary.

```python title="dict_setdefault_union.py" showLineNumbers{1} {1-3}
data = {'a': 1, 'b': 2, 'c': 3, 'd': 4}
data2 = {'e': 5, 'f': 6}
data3 = data | data2
print(data3)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python dict_setdefault_union.py
{'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5, 'f': 6}
```

In this example, we declare a dictionary and assign it to the variable `data`. We are going to add a new key-value pair to the dictionary using the union operator(`|`). We can also merge two dictionaries using the union operator(`|`). 

### Using the Union Equal operator (|=)
We can add a new key-value pair in a dictionary using the Union Equal operator(`|=`). If the key already exists in the dictionary, then the value of the key is updated. If the key does not exist in the dictionary, then a new key-value pair is added to the dictionary. We are using the union equal operator(`|=`) to add a new key-value pair in a dictionary.

```python title="dict_setdefault_union_equal.py" showLineNumbers{1} {1-3}
data = {'a': 1, 'b': 2, 'c': 3, 'd': 4}
data2 = {'e': 5, 'f': 6}
data |= data2
print(data)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python dict_setdefault_union_equal.py
{'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5, 'f': 6}
```

In this example, we declare a dictionary and assign it to the variable `data`. We are going to add a new key-value pair to the dictionary using the union equal operator(`|=`). We can also merge two dictionaries using the union equal operator(`|=`).

## Remove items from a dictionary
In Python, we can remove items from a dictionary using the following ways.

### Remove a key-value pair using pop() method
We can remove a key-value pair from a dictionary using the `pop()` method. The `pop()` method removes the key-value pair from the dictionary and returns the value of the key. If the key does not exist in the dictionary, then the `pop()` method raises a `KeyError` exception.

```python title="dict_pop.py" showLineNumbers{1} {1-2}
data = {'a': 1, 'b': 2, 'c': 3, 'd': 4}
value = data.pop('a')
print(value)
print(data)
```

Output:

```cmd title="command" showLineNumbers{1} {2-4}
C:\Users\username>python dict_pop.py
1
{'b': 2, 'c': 3, 'd': 4}
```

In this example, we declare a dictionary and assign it to the variable `data`. We then remove a key-value pair from the dictionary using the `pop()` method. The output shows that the key-value pair is removed from the dictionary.

### Removing a key-value pair using pop() method with default value
We can remove a key-value pair from a dictionary using the `pop()` method. The `pop()` method removes the key-value pair from the dictionary and returns the value of the key. If the key does not exist in the dictionary, then the `pop()` method returns the default value.

```python title="dict_pop_default.py" showLineNumbers{1} {1-2}
data = {'a': 1, 'b': 2, 'c': 3, 'd': 4}
value = data.pop('e', 5)
print(value)
print(data)
```

Output:

```cmd title="command" showLineNumbers{1} {2-4}
C:\Users\username>python dict_pop_default.py
5
{'a': 1, 'b': 2, 'c': 3, 'd': 4}
```

In this example, we declare a dictionary and assign it to the variable `data`. We then remove a key-value pair from the dictionary using the `pop()` method. The output shows that the key-value pair is removed from the dictionary.

### Removing a key-value pair where the key does not exist using pop() method 
We can remove a key-value pair from a dictionary using the `pop()` method. The `pop()` method removes the key-value pair from the dictionary and returns the value of the key. If the key does not exist in the dictionary, then the `pop()` method raises a `KeyError` exception.

```python title="dict_pop_keyerror.py" showLineNumbers{1} {1-2}
data = {'a': 1, 'b': 2, 'c': 3, 'd': 4}
value = data.pop('e')
print(value)
print(data)
```

Output:

```cmd title="command" showLineNumbers{1} {2-6}
C:\Users\username>python dict_pop_keyerror.py
Traceback (most recent call last):
  File "dict_pop_keyerror.py", line 2, in <module>
    value = data.pop('e')
KeyError: 'e'
```

In this example, we declare a dictionary and assign it to the variable `data`. We then remove a key-value pair from the dictionary using the `pop()` method. The output shows that the key-value pair is removed from the dictionary.

### Remove a key-value pair using popitem() method
We can remove a key-value pair from a dictionary using the `popitem()` method. The `popitem()` method removes the key-value pair from the dictionary and returns the key-value pair as a tuple. If the dictionary is empty, then the `popitem()` method raises a `KeyError` exception.

```python title="dict_popitem.py" showLineNumbers{1} {1-2}
data = {'a': 1, 'b': 2, 'c': 3, 'd': 4}
key, value = data.popitem()
print(key, value)
print(data)
```

Output:

```cmd title="command" showLineNumbers{1} {2-4}
C:\Users\username>python dict_popitem.py
d 4
{'a': 1, 'b': 2, 'c': 3}
```

In this example, we declare a dictionary and assign it to the variable `data`. We then remove a key-value pair from the dictionary using the `popitem()` method. The output shows that the key-value pair is removed from the dictionary.

### Remove a key-value pair using del keyword
We can remove a key-value pair from a dictionary using the `del` keyword. The `del` keyword removes the key-value pair from the dictionary. If the key does not exist in the dictionary, then the `del` keyword raises a `KeyError` exception.

```python title="dict_del.py" showLineNumbers{1} {1-2}
data = {'a': 1, 'b': 2, 'c': 3, 'd': 4}
del data['a']
print(data)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python dict_del.py
{'b': 2, 'c': 3, 'd': 4}
```

In this example, we declare a dictionary and assign it to the variable `data`. We then remove a key-value pair from the dictionary using the `del` keyword. The output shows that the key-value pair is removed from the dictionary.

### clear() method
We can remove all items from a dictionary using the `clear()` method. The `clear()` method removes all items from the dictionary.

```python title="dict_clear.py" showLineNumbers{1} {1-2}
data = {'a': 1, 'b': 2, 'c': 3, 'd': 4}
data.clear()
print(data)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python dict_clear.py
{}
```

In this example, we declare a dictionary and assign it to the variable `data`. We then remove all items from the dictionary using the `clear()` method. The output shows that all items are removed from the dictionary.

### Delete a dictionary using del keyword
We can delete a dictionary using the `del` keyword. The `del` keyword deletes the dictionary.

```python title="dict_del_dict.py" showLineNumbers{1} {1-2}
data = {'a': 1, 'b': 2, 'c': 3, 'd': 4}
del data
print(data)
```

Output:

```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\username>python dict_del_dict.py
Traceback (most recent call last):
  File "dict_del_dict.py", line 3, in <module>
    print(data)
NameError: name 'data' is not defined
```

In this example, we declare a dictionary and assign it to the variable `data`. We then delete the dictionary using the `del` keyword. The output shows that the dictionary is deleted.

## Conclusion
In this tutorial, we learned how to add and remove items in a dictionary. We learned how to add a new key-value pair in a dictionary using the `[]` operator. We learned how to add a new key-value pair in a dictionary using the `update()` method. We learned how to add a new key-value pair in a dictionary using the `setdefault()` method. We learned how to add a new key-value pair in a dictionary using the union operator(`|`). We learned how to add a new key-value pair in a dictionary using the union equal operator(`|=`). We learned how to remove a key-value pair from a dictionary using the `pop()` method. We learned how to remove a key-value pair from a dictionary using the `popitem()` method. We learned how to remove a key-value pair from a dictionary using the `del` keyword. We learned how to remove all items from a dictionary using the `clear()` method. We learned how to delete a dictionary using the `del` keyword. For more information, visit the [official Python documentation](https://docs.python.org/3/tutorial/datastructures.html#dictionaries). For more tutorials, visit our Python Central Hub.
