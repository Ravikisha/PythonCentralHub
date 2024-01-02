---
title: Access the dictionary
description: Learn how to access the dictionary in Python. In this tutorial, you will learn how to access the dictionary in Python. You also known as how to access the dictionary in Python using the key. You will also learn how to access the dictionary in Python using the get() method. You change the value of the dictionary in Python.
sidebar: 
    order: 65
---

## Accessing Dictionary Items
You can access dictionary items by their keys. If you try to access a key that does not exist, you will get a `KeyError` exception. 

### Accessing a Key that Exists
You can access dictionary items by their keys. The following example accesses the key `name` of the dictionary `dict1`:

```python title="dict.py" showLineNumbers{1} {1-3}
dict1 = {"name": "John", "age": 30, "city": "New York"}
print(dict1["name"])
```

Output:

```cmd title="command" showLineNumbers{1} {2-4}
C:\Users\username>python dict.py
John
```

In this example, we access the key `name` of the dictionary `dict1`. We then print the value of the key to the console. The output shows that the value of the key is `John`.

:::danger

### Accessing a Key that Does Not Exist

If you try to access a key that does not exist, you will get a `KeyError` exception. The following example accesses a key that does not exist:

```python title="dict.py" showLineNumbers{1} {1-3}
dict1 = {"name": "John", "age": 30, "city": "New York"}
print(dict1["address"])
```

Output:

```cmd title="command" showLineNumbers{1} {2-7}
C:\Users\username>python dict.py
Traceback (most recent call last):
  File "dict.py", line 2, in <module>
    print(dict1["address"])
KeyError: 'address'
```

In this example, we try to access the key `address` of the dictionary `dict1`. We then print the value of the key to the console. The output shows that we get a `KeyError` exception because the key does not exist.

:::

### Accessing a Key using the get() Method
You can access dictionary items by their keys using the `get()` method. If you try to access a key that does not exist, you will get `None`. The following example accesses the key `name` of the dictionary `dict1`:

```python title="dict.py" showLineNumbers{1} {1-3}
dict1 = {"name": "John", "age": 30, "city": "New York"}
print(dict1.get("name"))
```

Output:

```cmd title="command" showLineNumbers{1} {2-4}
C:\Users\username>python dict.py
John
```

In this example, we access the key `name` of the dictionary `dict1`. We then print the value of the key to the console. The output shows that the value of the key is `John`.

### Accessing a Key that Does Not Exist using the get() Method
You can access dictionary items by their keys using the `get()` method. If you try to access a key that does not exist, you will get `None`. The following example accesses a key that does not exist:

```python title="dict.py" showLineNumbers{1} {1-3}
dict1 = {"name": "John", "age": 30, "city": "New York"}
print(dict1.get("address"))
```

Output:

```cmd title="command" showLineNumbers{1} {2-4}
C:\Users\username>python dict.py
None
```

In this example, we try to access the key `address` of the dictionary `dict1`. We then print the value of the key to the console. The output shows that we get `None` because the key does not exist.

## Length of a Dictionary
The length of a dictionary is the number of key-value pairs it contains. You can use the `len()` function to get the length of a dictionary. The following example gets the length of the dictionary `dict1`:

```python title="dict.py" showLineNumbers{1} {1-3}
dict1 = {"name": "John", "age": 30, "city": "New York"}
print(len(dict1))
```

Output:

```cmd title="command" showLineNumbers{1} {2-4}
C:\Users\username>python dict.py
3
```

In this example, we get the length of the dictionary `dict1`. We then print the length of the dictionary to the console. The output shows that the length of the dictionary is `3`.

## Iterating Over a Dictionary
You can iterate over a dictionary using a `for` loop. When you iterate over a dictionary, you get the keys of the dictionary. The following example iterates over the dictionary `dict1`:

```python title="dict.py" showLineNumbers{1} {1-4}
dict1 = {"name": "John", "age": 30, "city": "New York"}
for key in dict1:
    print(key + " => " + str(dict1[key]))
```

Output:

```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\username>python dict.py
name => John
age => 30
city => New York
```

In this example, we iterate over the dictionary `dict1`. We then print the keys and values of the dictionary to the console. The output shows that we get the keys of the dictionary.

### Accessing the Dictionary Items using the keys() Method
You can access the dictionary items using the `keys()` method. The following example accesses the dictionary items using the `keys()` method:

```python title="dict.py" showLineNumbers{1} {1-4}
dict1 = {"name": "John", "age": 30, "city": "New York"}
for key in dict1.keys():
    print(key + " => " + str(dict1[key]))
```

Output:

```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\username>python dict.py
name => John
age => 30
city => New York
```

In this example, we iterate over the dictionary `dict1`. We then print the keys and values of the dictionary to the console. The output shows that we get the keys of the dictionary.

### Accessing the Dictionary Items using the values() Method
You can access the dictionary items using the `values()` method. The following example accesses the dictionary items using the `values()` method:

```python title="dict.py" showLineNumbers{1} {1-4}
dict1 = {"name": "John", "age": 30, "city": "New York"}
for value in dict1.values():
    print(value)
```

Output:

```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\username>python dict.py
John
30
New York
```

In this example, we iterate over the dictionary `dict1`. We then print the values of the dictionary to the console. The output shows that we get the values of the dictionary.

### Accessing the Dictionary Items using the items() Method
You can access the dictionary items using the `items()` method. The following example accesses the dictionary items using the `items()` method:

```python title="dict.py" showLineNumbers{1} {1-4}
dict1 = {"name": "John", "age": 30, "city": "New York"}
for key, value in dict1.items():
    print(key + " => " + str(value))
```

Output:

```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\username>python dict.py
name => John
age => 30
city => New York
```

In this example, we iterate over the dictionary `dict1`. We then print the keys and values of the dictionary to the console. The output shows that we get the keys and values of the dictionary.

## Checking if a Key Exists
You can check if a key exists in a dictionary using the `in` operator. The following example checks if the key `name` exists in the dictionary `dict1`:

```python title="dict.py" showLineNumbers{1} {1-3}
dict1 = {"name": "John", "age": 30, "city": "New York"}
if "name" in dict1:
    print("The key 'name' exists in the dictionary")
```

Output:

```cmd title="command" showLineNumbers{1} {2-4}
C:\Users\username>python dict.py
The key 'name' exists in the dictionary
```

In this example, we check if the key `name` exists in the dictionary `dict1`. We then print a message to the console. The output shows that the key exists in the dictionary.

### Checking if a Key Does Not Exist
You can check if a key does not exist in a dictionary using the `not in` operator. The following example checks if the key `address` does not exist in the dictionary `dict1`:

```python title="dict.py" showLineNumbers{1} {1-3}
dict1 = {"name": "John", "age": 30, "city": "New York"}
if "address" not in dict1:
    print("The key 'address' does not exist in the dictionary")
```

Output:

```cmd title="command" showLineNumbers{1} {2-4}
C:\Users\username>python dict.py
The key 'address' does not exist in the dictionary
```

In this example, we check if the key `address` does not exist in the dictionary `dict1`. We then print a message to the console. The output shows that the key does not exist in the dictionary.

### Checking if a Value Exists
You can check if a value exists in a dictionary using the `in` operator. The following example checks if the value `John` exists in the dictionary `dict1`:

```python title="dict.py" showLineNumbers{1} {1-3}
dict1 = {"name": "John", "age": 30, "city": "New York"}
if "John" in dict1.values():
    print("The value 'John' exists in the dictionary")
```

Output:

```cmd title="command" showLineNumbers{1} {2-4}
C:\Users\username>python dict.py
The value 'John' exists in the dictionary
```

In this example, we check if the value `John` exists in the dictionary `dict1`. We then print a message to the console. The output shows that the value exists in the dictionary.

### Checking if a Value Does Not Exist
You can check if a value does not exist in a dictionary using the `not in` operator. The following example checks if the value `Jane` does not exist in the dictionary `dict1`:

```python title="dict.py" showLineNumbers{1} {1-3}
dict1 = {"name": "John", "age": 30, "city": "New York"}
if "Jane" not in dict1.values():
    print("The value 'Jane' does not exist in the dictionary")
```

Output:

```cmd title="command" showLineNumbers{1} {2-4}
C:\Users\username>python dict.py
The value 'Jane' does not exist in the dictionary
```

In this example, we check if the value `Jane` does not exist in the dictionary `dict1`. We then print a message to the console. The output shows that the value does not exist in the dictionary.

### Checking if a Key Exists using the get() Method
You can check if a key exists in a dictionary using the `get()` method. The following example checks if the key `name` exists in the dictionary `dict1`:

```python title="dict.py" showLineNumbers{1} {1-3}
dict1 = {"name": "John", "age": 30, "city": "New York"}
if dict1.get("name"):
    print("The key 'name' exists in the dictionary")
```

Output:

```cmd title="command" showLineNumbers{1} {2-4}
C:\Users\username>python dict.py
The key 'name' exists in the dictionary
```

In this example, we check if the key `name` exists in the dictionary `dict1`. We then print a message to the console. The output shows that the key exists in the dictionary.

### Checking if a Key Does Not Exist using the get() Method
You can check if a key does not exist in a dictionary using the `get()` method. The following example checks if the key `address` does not exist in the dictionary `dict1`:

```python title="dict.py" showLineNumbers{1} {1-3}
dict1 = {"name": "John", "age": 30, "city": "New York"}
if not dict1.get("address"):
    print("The key 'address' does not exist in the dictionary")
```

Output:

```cmd title="command" showLineNumbers{1} {2-4}
C:\Users\username>python dict.py
The key 'address' does not exist in the dictionary
```

In this example, we check if the key `address` does not exist in the dictionary `dict1`. We then print a message to the console. The output shows that the key does not exist in the dictionary.


## Changing Dictionary Items
You can change the value of a dictionary item by using its key.

### Changing a Key that Exists
You can change the value of a dictionary item by using its key. The following example changes the value of the key `name` of the dictionary `dict1`:

```python title="dict.py" showLineNumbers{1} {1-4}
dict1 = {"name": "John", "age": 30, "city": "New York"}
dict1["name"] = "Jane"
print(dict1)
```

Output:

```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\username>python dict.py
{'name': 'Jane', 'age': 30, 'city': 'New York'}
```

In this example, we change the value of the key `name` of the dictionary `dict1`. We then print the dictionary to the console. The output shows that the value of the key is changed to `Jane`.

### Changing a Key that Does Not Exist
You can change the value of a dictionary item by using its key. The following example changes the value of the key `address` of the dictionary `dict1`:

```python title="dict.py" showLineNumbers{1} {1-4}
dict1 = {"name": "John", "age": 30, "city": "New York"}
dict1["address"] = "London"
print(dict1)
```

Output:

```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\username>python dict.py
{'name': 'John', 'age': 30, 'city': 'New York', 'address': 'London'}
```

In this example, we change the value of the key `address` of the dictionary `dict1`. We then print the dictionary to the console. The output shows that the value of the key is changed to `London`.

### Changing a Key using the update() Method
You can change the value of a dictionary item by using its key. The following example changes the value of the key `name` of the dictionary `dict1`:

```python title="dict.py" showLineNumbers{1} {1-4}
dict1 = {"name": "John", "age": 30, "city": "New York"}
dict1.update({"name": "Jane"})
print(dict1)
```

Output:

```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\username>python dict.py
{'name': 'Jane', 'age': 30, 'city': 'New York'}
```

In this example, we change the value of the key `name` of the dictionary `dict1`. We then print the dictionary to the console. The output shows that the value of the key is changed to `Jane`.

### Changing a Key that Does Not Exist using the update() Method
You can change the value of a dictionary item by using its key. The following example changes the value of the key `address` of the dictionary `dict1`:

```python title="dict.py" showLineNumbers{1} {1-4}
dict1 = {"name": "John", "age": 30, "city": "New York"}
dict1.update({"address": "London"})
print(dict1)
```

Output:

```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\username>python dict.py
{'name': 'John', 'age': 30, 'city': 'New York', 'address': 'London'}
```

In this example, we change the value of the key `address` of the dictionary `dict1`. We then print the dictionary to the console. The output shows that the value of the key is changed to `London`.

## Conclusion
In this tutorial, you have learned how to access the dictionary in Python. You also known as how to access the dictionary in Python using the key. You will also learn how to access the dictionary in Python using the get() method. You change the value of the dictionary in Python. For more tutorials, visit our Python Central Hub.
