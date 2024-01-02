---
title: Nested Dictionary
description: Learn how to create a nested dictionary in Python. How to access and modify nested dictionary values. How to iterate over nested dictionary items. How to convert a nested dictionary to a flat dictionary. How to convert a nested dictionary to a list of tuples. How to convert a nested dictionary to a list of lists. How to convert a nested dictionary to a list of dictionaries.
sidebar: 
    order: 68
---

## Nested Dictionaries
Nested dictionaries are dictionaries that contain other dictionaries. 

```python title="dict_nested.py" showLineNumbers{1} {1-5}
data = {'a': {'b': 1, 'c': 2}, 'd': {'e': 3, 'f': 4}}
print(data)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python dict_nested.py
{'a': {'b': 1, 'c': 2}, 'd': {'e': 3, 'f': 4}}
```

In this example, we declare a dictionary and assign it to the variable `data`. We then print the variable `data`. The output shows that the variable `data` is a dictionary.

### Accessing Nested Dictionaries
Accessing nested dictionaries is a way to access the values of a nested dictionary.

```python title="dict_nested_access.py" showLineNumbers{1} {1-5}
data = {'a': {'b': 1, 'c': 2}, 'd': {'e': 3, 'f': 4}}
print(data['a']['b'])
print(data['d']['e'])
```

Output:

```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\username>python dict_nested_access.py
1
3
```

In this example, we declare a dictionary and assign it to the variable `data`. We then print the variable `data`. The output shows that the variable `data` is a dictionary.

### Accessing Nested Dictionaries Using get() Method
Accessing nested dictionaries using the `get()` method is a way to access the values of a nested dictionary.

```python title="dict_nested_get.py" showLineNumbers{1} {1-5}
data = {'a': {'b': 1, 'c': 2}, 'd': {'e': 3, 'f': 4}}
print(data.get('a').get('b'))
print(data.get('d').get('e'))
```

Output:

```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\username>python dict_nested_get.py
1
3
```

In this example, we declare a dictionary and assign it to the variable `data`. We then print the variable `data`. The output shows that the variable `data` is a dictionary.

### Looping Through Nested Dictionaries
Looping through nested dictionaries is a way to iterate through the keys, values, or items of a nested dictionary. 

```python title="dict_nested_loop.py" showLineNumbers{1} {1-5}
data = {'a': {'b': 1, 'c': 2}, 'd': {'e': 3, 'f': 4}}
for key, value in data.items():
    print(key, value)
```

Output:

```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\username>python dict_nested_loop.py
a {'b': 1, 'c': 2}
d {'e': 3, 'f': 4}
```

In this example, we declare a dictionary and assign it to the variable `data`. We then loop through the dictionary items using a `for` loop. We then print the dictionary key and value. The output shows that the dictionary items are printed.

### Looping Through Nested Dictionaries Using Deeply Nested Dictionaries
Looping through nested dictionaries using deeply nested dictionaries is a way to iterate through the keys, values, or items of a nested dictionary. 

```python title="dict_nested_deep_loop.py" showLineNumbers{1} {1-5}
data = {'a': {'b': {'c': 1, 'd': 2}, 'e': {'f': 3, 'g': 4}}, 'h': {'i': {'j': 5, 'k': 6}, 'l': {'m': 7, 'n': 8}}}
for key, value in data.items():
    for key2, value2 in value.items():
        for key3, value3 in value2.items():
            print("Level 1: " + key + " => Level 2: " + key2 + " => Level 3: " + key3 + " => Value: " + str(value3))
```

Output:

```cmd title="command" showLineNumbers{1} {2-10}
C:\Users\username>python dict_nested_deep_loop.py
Level 1: a => Level 2: b => Level 3: c => Value: 1
Level 1: a => Level 2: b => Level 3: d => Value: 2
Level 1: a => Level 2: e => Level 3: f => Value: 3
Level 1: a => Level 2: e => Level 3: g => Value: 4
Level 1: h => Level 2: i => Level 3: j => Value: 5
Level 1: h => Level 2: i => Level 3: k => Value: 6
Level 1: h => Level 2: l => Level 3: m => Value: 7
Level 1: h => Level 2: l => Level 3: n => Value: 8
```

In this example, we declare a dictionary and assign it to the variable `data`. We then loop through the dictionary items using a `for` loop. We then print the dictionary key and value. The output shows that the dictionary items are printed.

### Adding Nested Dictionaries
Adding nested dictionaries is a way to add a nested dictionary to a dictionary. 

```python title="dict_nested_add.py" showLineNumbers{1} {1-5}
data = {'a': 1, 'b': 2, 'c': 3}
data['d'] = {'e': 4, 'f': 5}
print(data)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python dict_nested_add.py
{'a': 1, 'b': 2, 'c': 3, 'd': {'e': 4, 'f': 5}}
```

In this example, we declare a dictionary and assign it to the variable `data`. We then add a nested dictionary to the dictionary. We then print the variable `data`. The output shows that the variable `data` is a dictionary.

### Updating Nested Dictionaries
Updating nested dictionaries is a way to update a nested dictionary in a dictionary. 

```python title="dict_nested_update.py" showLineNumbers{1} {1-5}
data = {'a': 1, 'b': 2, 'c': 3}
data['d'] = {'e': 4, 'f': 5}
data['d']['e'] = 6
print(data)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python dict_nested_update.py
{'a': 1, 'b': 2, 'c': 3, 'd': {'e': 6, 'f': 5}}
```

In this example, we declare a dictionary and assign it to the variable `data`. We then add a nested dictionary to the dictionary. We then update the nested dictionary in the dictionary. We then print the variable `data`. The output shows that the variable `data` is a dictionary.

### Deleting Nested Dictionaries
Deleting nested dictionaries is a way to delete a nested dictionary in a dictionary.

```python title="dict_nested_delete.py" showLineNumbers{1} {1-5}
data = {'a': 1, 'b': 2, 'c': 3}
data['d'] = {'e': 4, 'f': 5}
print(data)
del data['d']
print(data)
```

Output:

```cmd title="command" showLineNumbers{1} {2-4}
C:\Users\username>python dict_nested_delete.py
{'a': 1, 'b': 2, 'c': 3, 'd': {'e': 4, 'f': 5}}
{'a': 1, 'b': 2, 'c': 3}
```

In this example, we declare a dictionary and assign it to the variable `data`. We then add a nested dictionary to the dictionary. We then print the variable `data`. We then delete the nested dictionary in the dictionary. We then print the variable `data`. The output shows that the variable `data` is a dictionary.

### Clearing Nested Dictionaries
Clearing nested dictionaries is a way to clear a nested dictionary in a dictionary.

```python title="dict_nested_clear.py" showLineNumbers{1} {1-5}
data = {'a': 1, 'b': 2, 'c': 3}
data['d'] = {'e': 4, 'f': 5}
print(data)
data['d'].clear()
print(data)
```

Output:

```cmd title="command" showLineNumbers{1} {2-4}
C:\Users\username>python dict_nested_clear.py
{'a': 1, 'b': 2, 'c': 3, 'd': {'e': 4, 'f': 5}}
{'a': 1, 'b': 2, 'c': 3, 'd': {}}
```

In this example, we declare a dictionary and assign it to the variable `data`. We then add a nested dictionary to the dictionary. We then print the variable `data`. We then clear the nested dictionary in the dictionary. We then print the variable `data`. The output shows that the variable `data` is a dictionary.

### Copying Nested Dictionaries
Copying nested dictionaries is a way to create a copy of a nested dictionary. 

```python title="dict_nested_copy.py" showLineNumbers{1} {1-5}
data1 = {'a': 1, 'b': 2, 'c': 3}
data1['d'] = {'e': 4, 'f': 5}
data2 = data1.copy()
print(data1)
print(data2)
```

Output:

```cmd title="command" showLineNumbers{1} {2-6}
C:\Users\username>python dict_nested_copy.py
{'a': 1, 'b': 2, 'c': 3, 'd': {'e': 4, 'f': 5}}
{'a': 1, 'b': 2, 'c': 3, 'd': {'e': 4, 'f': 5}}
```

In this example, we declare a dictionary and assign it to the variable `data1`. We then add a nested dictionary to the dictionary. We then declare a second dictionary and assign it to the variable `data2`. We then print the variable `data1` and `data2`. The output shows that the variable `data1` and `data2` are dictionaries.

### Updating Nested Dictionaries Using update() Method
Updating nested dictionaries using the `update()` method is a way to update a nested dictionary in a dictionary.

```python title="dict_nested_update_method.py" showLineNumbers{1} {1-5}
data = {'a': 1, 'b': 2, 'c': 3}
data['d'] = {'e': 4, 'f': 5}
print(data)
data['d'].update({'e': 6})
print(data)
```

Output:

```cmd title="command" showLineNumbers{1} {2-4}
C:\Users\username>python dict_nested_update_method.py
{'a': 1, 'b': 2, 'c': 3, 'd': {'e': 4, 'f': 5}}
{'a': 1, 'b': 2, 'c': 3, 'd': {'e': 6, 'f': 5}}
```

In this example, we declare a dictionary and assign it to the variable `data`. We then add a nested dictionary to the dictionary. We then print the variable `data`. We then update the nested dictionary in the dictionary using the `update()` method. We then print the variable `data`. The output shows that the variable `data` is a dictionary.

### Deleting Nested Dictionaries Using del Keyword
Deleting nested dictionaries using the `del` keyword is a way to delete a nested dictionary in a dictionary. 

```python title="dict_nested_del_keyword.py" showLineNumbers{1} {1-5}
data = {'a': 1, 'b': 2, 'c': 3}
data['d'] = {'e': 4, 'f': 5}
print(data)
del data['d']
print(data)
```

Output:

```cmd title="command" showLineNumbers{1} {2-4}
C:\Users\username>python dict_nested_del_keyword.py
{'a': 1, 'b': 2, 'c': 3, 'd': {'e': 4, 'f': 5}}
{'a': 1, 'b': 2, 'c': 3}
```

In this example, we declare a dictionary and assign it to the variable `data`. We then add a nested dictionary to the dictionary. We then print the variable `data`. We then delete the nested dictionary in the dictionary using the `del` keyword. We then print the variable `data`. The output shows that the variable `data` is a dictionary.

### Deleting Nested Dictionaries Using pop() Method
Deleting nested dictionaries using the `pop()` method is a way to delete a nested dictionary in a dictionary. 

```python title="dict_nested_pop_method.py" showLineNumbers{1} {1-5}
data = {'a': 1, 'b': 2, 'c': 3}
data['d'] = {'e': 4, 'f': 5}
print(data)
data.pop('d')
print(data)
```

Output:

```cmd title="command" showLineNumbers{1} {2-4}
C:\Users\username>python dict_nested_pop_method.py
{'a': 1, 'b': 2, 'c': 3, 'd': {'e': 4, 'f': 5}}
{'a': 1, 'b': 2, 'c': 3}
```

In this example, we declare a dictionary and assign it to the variable `data`. We then add a nested dictionary to the dictionary. We then print the variable `data`. We then delete the nested dictionary in the dictionary using the `pop()` method. We then print the variable `data`. The output shows that the variable `data` is a dictionary.

### Deleting Nested Dictionaries Using popitem() Method
Deleting nested dictionaries using the `popitem()` method is a way to delete a nested dictionary in a dictionary. 

```python title="dict_nested_popitem_method.py" showLineNumbers{1} {1-5}
data = {'a': 1, 'b': 2, 'c': 3}
data['d'] = {'e': 4, 'f': 5}
print(data)
data.popitem()
print(data)
```

Output:

```cmd title="command" showLineNumbers{1} {2-4}
C:\Users\username>python dict_nested_popitem_method.py
{'a': 1, 'b': 2, 'c': 3, 'd': {'e': 4, 'f': 5}}
{'a': 1, 'b': 2, 'c': 3}
```

In this example, we declare a dictionary and assign it to the variable `data`. We then add a nested dictionary to the dictionary. We then print the variable `data`. We then delete the nested dictionary in the dictionary using the `popitem()` method. We then print the variable `data`. The output shows that the variable `data` is a dictionary.

### Checking if Nested Dictionaries Exist
Checking if nested dictionaries exist is a way to check if a nested dictionary exists in a dictionary.

```python title="dict_nested_exist.py" showLineNumbers{1} {1-10}
data = {'a': 1, 'b': 2, 'c': 3}
if 'd' in data:
    print("d exists")
else:
    print("d does not exist")
data['d'] = {'e': 4, 'f': 5}
if 'd' in data:
    print("d exists")
else:
    print("d does not exist")
```

Output:

```cmd title="command" showLineNumbers{1} {2-11}
C:\Users\username>python dict_nested_exist.py
d does not exist
d exists
```

In this example, we declare a dictionary and assign it to the variable `data`. We then check if the key `d` exists in the dictionary. We then print the result. We then add a nested dictionary to the dictionary. We then check if the key `d` exists in the dictionary. We then print the result. The output shows that the variable `data` is a dictionary.

### Converting Nested Dictionaries to Flat Dictionaries
Converting nested dictionaries to flat dictionaries is a way to convert a nested dictionary to a flat dictionary. 

```python title="dict_nested_flat.py" showLineNumbers{1} {1-5}
data = {'a': {'b': 1, 'c': 2}, 'd': {'e': 3, 'f': 4}}
flat_data = {}
for key, value in data.items():
    for key2, value2 in value.items():
        flat_data[key2] = value2
print(flat_data)
```

Output:

```cmd title="command" showLineNumbers{1} {2-6}
C:\Users\username>python dict_nested_flat.py
{'b': 1, 'c': 2, 'e': 3, 'f': 4}
```

In this example, we declare a dictionary and assign it to the variable `data`. We then declare an empty dictionary and assign it to the variable `flat_data`. We then loop through the dictionary items using a `for` loop. We then loop through the nested dictionary items using a `for` loop. We then add the nested dictionary items to the flat dictionary. We then print the variable `flat_data`. The output shows that the variable `flat_data` is a dictionary.

### Converting Nested Dictionaries to List of Tuples
Converting nested dictionaries to a list of tuples is a way to convert a nested dictionary to a list of tuples. 

```python title="dict_nested_list_tuples.py" showLineNumbers{1} {1-5}
data = {'a': {'b': 1, 'c': 2}, 'd': {'e': 3, 'f': 4}}
list_tuples = []
for key, value in data.items():
    for key2, value2 in value.items():
        list_tuples.append((key2, value2))
print(list_tuples)
```

Output:

```cmd title="command" showLineNumbers{1} {2-6}
C:\Users\username>python dict_nested_list_tuples.py
[('b', 1), ('c', 2), ('e', 3), ('f', 4)]
```

In this example, we declare a dictionary and assign it to the variable `data`. We then declare an empty list and assign it to the variable `list_tuples`. We then loop through the dictionary items using a `for` loop. We then loop through the nested dictionary items using a `for` loop. We then add the nested dictionary items to the list. We then print the variable `list_tuples`. The output shows that the variable `list_tuples` is a list of tuples.

### Converting Nested Dictionaries to List of Lists
Converting nested dictionaries to a list of lists is a way to convert a nested dictionary to a list of lists.

```python title="dict_nested_list_lists.py" showLineNumbers{1} {1-5}
data = {'a': {'b': 1, 'c': 2}, 'd': {'e': 3, 'f': 4}}
list_lists = []
for key, value in data.items():
    for key2, value2 in value.items():
        list_lists.append([key2, value2])
print(list_lists)
```

Output:

```cmd title="command" showLineNumbers{1} {2-6}
C:\Users\username>python dict_nested_list_lists.py
[['b', 1], ['c', 2], ['e', 3], ['f', 4]]
```

In this example, we declare a dictionary and assign it to the variable `data`. We then declare an empty list and assign it to the variable `list_lists`. We then loop through the dictionary items using a `for` loop. We then loop through the nested dictionary items using a `for` loop. We then add the nested dictionary items to the list. We then print the variable `list_lists`. The output shows that the variable `list_lists` is a list of lists.

### Converting Nested Dictionaries to List of Dictionaries
Converting nested dictionaries to a list of dictionaries is a way to convert a nested dictionary to a list of dictionaries.

```python title="dict_nested_list_dicts.py" showLineNumbers{1} {1-5}
data = {'a': {'b': 1, 'c': 2}, 'd': {'e': 3, 'f': 4}}
list_dicts = []
for key, value in data.items():
    for key2, value2 in value.items():
        list_dicts.append({key2: value2})
print(list_dicts)
```

Output:

```cmd title="command" showLineNumbers{1} {2-6}
C:\Users\username>python dict_nested_list_dicts.py
[{'b': 1}, {'c': 2}, {'e': 3}, {'f': 4}]
```

In this example, we declare a dictionary and assign it to the variable `data`. We then declare an empty list and assign it to the variable `list_dicts`. We then loop through the dictionary items using a `for` loop. We then loop through the nested dictionary items using a `for` loop. We then add the nested dictionary items to the list. We then print the variable `list_dicts`. The output shows that the variable `list_dicts` is a list of dictionaries.

### Converting Nested Dictionaries to JSON
Converting nested dictionaries to JSON is a way to convert a nested dictionary to JSON.

```python title="dict_nested_json.py" showLineNumbers{1} {1-5}
import json
data = {'a': {'b': 1, 'c': 2}, 'd': {'e': 3, 'f': 4}}
json_data = json.dumps(data)
print(json_data)
```

Output:

```cmd title="command" showLineNumbers{1} {2-4}
C:\Users\username>python dict_nested_json.py
{"a": {"b": 1, "c": 2}, "d": {"e": 3, "f": 4}}
```

In this example, we import the `json` module. We then declare a dictionary and assign it to the variable `data`. We then convert the dictionary to JSON using the `dumps()` method. We then print the variable `json_data`. The output shows that the variable `json_data` is a JSON string.

### Converting Nested Dictionaries to YAML
Converting nested dictionaries to YAML is a way to convert a nested dictionary to YAML.

```python title="dict_nested_yaml.py" showLineNumbers{1} {1-5}
import yaml
data = {'a': {'b': 1, 'c': 2}, 'd': {'e': 3, 'f': 4}}
yaml_data = yaml.dump(data)
print(yaml_data)
```

Output:

```cmd title="command" showLineNumbers{1} {2-8}
C:\Users\username>python dict_nested_yaml.py
a:
  b: 1
  c: 2
d:
  e: 3
  f: 4
```

In this example, we import the `yaml` module. We then declare a dictionary and assign it to the variable `data`. We then convert the dictionary to YAML using the `dump()` method. We then print the variable `yaml_data`. The output shows that the variable `yaml_data` is a YAML string.

## Conclusion
Nested dictionaries are dictionaries that contain other dictionaries. Nested dictionaries can be accessed, modified, and iterated over. Nested dictionaries can be converted to flat dictionaries, lists of tuples, lists of lists, lists of dictionaries, JSON, and YAML. For more information on dictionaries, Check out the Python Central Hub.
