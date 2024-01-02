---
title: Frozen Set
description: Learn about Frozen Set in Python. Frozen Set is an immutable version of Set. It is an unordered collection of unique elements. Frozen Set is immutable, so we cannot add or remove elements from it. It is hashable, so we can use it as a key in a dictionary.
sidebar: 
    order: 63
---

## Exploring Frozensets in Python: A Comprehensive Guide

Frozensets in Python are an immutable version of sets. While sets are mutable, meaning you can add, remove, or update elements after creation, frozensets are fixed and unchangeable once created. In this comprehensive guide, we will delve into the characteristics of frozensets, how to create and manipulate them, their use cases, and how they differ from regular sets.

## Characteristics of Frozensets

### Immutability

The most significant characteristic of frozensets is their immutability. Once a frozenset is created, you cannot add, remove, or modify its elements. This makes frozensets suitable for scenarios where data integrity and immutability are crucial.

### Hashability

Frozensets are hashable, meaning they can be used as keys in dictionaries or elements in other sets. The immutability of frozensets ensures a consistent hash value, making them suitable for scenarios where hashability is required.

### Lack of Methods for Mutation

Unlike regular sets, frozensets lack methods that would allow mutation, such as `add()`, `remove()`, or `discard()`. Operations that would alter the frozenset result in an error.

## Creating Frozensets

Creating a frozenset is similar to creating a regular set, but instead of using curly braces `{}`, you use the `frozenset()` constructor:

```python title="frozenset.py" showLineNumbers{1} {1}
frozen_set = frozenset([1, 2, 3, 4, 5])
print(frozen_set)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python frozenset.py
frozenset({1, 2, 3, 4, 5})
```

Alternatively, you can use the `frozenset()` constructor directly:

```python title="frozenset.py" showLineNumbers{1} {1}
another_frozen_set = frozenset({3, 4, 5, 6, 7})
print(another_frozen_set)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python frozenset.py
frozenset({3, 4, 5, 6, 7})
```

Once created, the elements of a frozenset cannot be modified:

```python title="frozenset.py" showLineNumbers{1} {2}
frozen_set = frozenset([1, 2, 3, 4, 5])
frozen_set.add(6)  # AttributeError: 'frozenset' object has no attribute 'add'
```

Output:

```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\username>python frozenset.py
Traceback (most recent call last):
  File "frozenset.py", line 2, in <module>
    frozen_set.add(6)  # AttributeError: 'frozenset' object has no attribute 'add'
AttributeError: 'frozenset' object has no attribute 'add'
```

## Operations on Frozensets

While frozensets lack methods for mutation, they support various operations similar to regular sets:

### Union of Frozensets

The union of two frozensets results in a new frozenset containing unique elements from both:

```python title="frozenset.py" showLineNumbers{1} {1-4}
frozen_set = frozenset([1, 2, 3, 4, 5])
another_frozen_set = frozenset({3, 4, 5, 6, 7})
union_result = frozen_set.union(another_frozen_set)
print(union_result)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python frozenset.py
frozenset({1, 2, 3, 4, 5, 6, 7})
```

In this example, we use the `union()` method to create a new frozenset containing elements from both `frozen_set` and `another_frozen_set`.


### Intersection of Frozensets

The intersection of two frozensets contains elements that are common to both:

```python title="frozenset.py" showLineNumbers{1} {1-3}
frozen_set = frozenset([1, 2, 3, 4, 5])
another_frozen_set = frozenset({3, 4, 5, 6, 7})
intersection_result = frozen_set.intersection(another_frozen_set)
print(intersection_result)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python frozenset.py
frozenset({3, 4, 5})
```

In this example, we use the `intersection()` method to create a new frozenset containing elements common to both `frozen_set` and `another_frozen_set`.

### Difference of Frozensets

The difference between two frozensets contains elements present in the first but not in the second:

```python title="frozenset.py" showLineNumbers{1} {1-3}
frozen_set = frozenset([1, 2, 3, 4, 5])
another_frozen_set = frozenset({3, 4, 5, 6, 7})
difference_result = frozen_set.difference(another_frozen_set)
print(difference_result)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python frozenset.py
frozenset({1, 2})
```

In this example, we use the `difference()` method to create a new frozenset containing elements present in `frozen_set` but not in `another_frozen_set`.

### Symmetric Difference of Frozensets

The symmetric difference of two frozensets contains elements that are unique to each frozenset:

```python title="frozenset.py" showLineNumbers{1} {1-3}
frozen_set = frozenset([1, 2, 3, 4, 5])
another_frozen_set = frozenset({3, 4, 5, 6, 7})
symmetric_difference_result = frozen_set.symmetric_difference(another_frozen_set)
print(symmetric_difference_result)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python frozenset.py
frozenset({1, 2, 6, 7})
```

In this example, we use the `symmetric_difference()` method to create a new frozenset containing elements that are unique to each frozenset.

### Subset and Superset Check

You can check if one frozenset is a subset or superset of another:

```python title="frozenset.py" showLineNumbers{1} {1-5}
frozen_set = frozenset([1, 2, 3, 4, 5])
is_subset = {1, 2}.issubset(frozen_set) 
is_superset = frozen_set.issuperset({1, 2}) 
print(is_subset) 
print(is_superset)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python frozenset.py
True
True
```

In this example, we use the `issubset()` and `issuperset()` methods to check if `{1, 2}` is a subset of `frozen_set` and if `frozen_set` is a superset of `{1, 2}`.

### Frozenset Methods

Frozensets offer methods for common operations:

- `copy()`: Creates a shallow copy of the frozenset.
- `difference_update()`: Updates the frozenset with the difference of itself and another set or frozenset.
- `intersection_update()`: Updates the frozenset with the intersection of itself and another set or frozenset.
- `symmetric_difference_update()`: Updates the frozenset with the symmetric difference of itself and another set or frozenset.

```python title="frozenset.py" showLineNumbers{1} {1-20}
frozen_set = frozenset([1, 2, 3, 4, 5])
another_frozen_set = frozenset({3, 4, 5, 6, 7})
copy_of_frozen_set = frozen_set.copy()
print("Copy of frozen set:", copy_of_frozen_set)
frozen_set.difference_update(another_frozen_set)
print("Difference of frozen set:", frozen_set)
frozen_set = frozenset([1, 2, 3, 4, 5])
frozen_set.intersection_update(another_frozen_set)
print("Intersection of frozen set:", frozen_set)
frozen_set = frozenset([1, 2, 3, 4, 5])
frozen_set.symmetric_difference_update(another_frozen_set)
print("Symmetric difference of frozen set:", frozen_set)
```

Output:

```cmd title="command" showLineNumbers{1} {2-21}
C:\Users\username>python frozenset.py
Copy of frozen set: frozenset({1, 2, 3, 4, 5})
Difference of frozen set: frozenset({1, 2})
Intersection of frozen set: frozenset({3, 4, 5})
Symmetric difference of frozen set: frozenset({1, 2, 6, 7})
```


## Use Cases for Frozensets

Frozensets are particularly useful in scenarios where immutability and hashability are essential. Here are some common use cases:

### As Keys in Dictionaries

Since frozensets are hashable and immutable, they can be used as keys in dictionaries:

```python title="frozenset.py" showLineNumbers{1} {1-5}
# Using frozensets as keys in a dictionary
data = {
    frozenset({1, 2, 3}): 'Set A',
    frozenset({4, 5, 6}): 'Set B'
}
print(data[frozenset({1, 2, 3})])
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python frozenset.py
Set A
```

In this example, we use frozensets as keys in a dictionary. The output shows that the value of the key `frozenset({1, 2, 3})` is `Set A`.

### Storing Configuration Settings

Frozensets can be employed to represent configuration settings, ensuring that the configuration remains constant throughout the program:

```python title="frozenset.py" showLineNumbers{1} {1-4}
# Using frozensets for configuration settings
configuration = frozenset(['debug_mode', 'max_connections', 'timeout'])
```

### Membership Testing

Frozensets are efficient for membership testing, especially in

 scenarios where the collection of items needs to remain unchanged:

```python title="frozenset.py" showLineNumbers{1} {1-4}
# Membership testing with frozensets
allowed_roles = frozenset(['admin', 'user', 'editor'])
user_role = 'admin'

if user_role in allowed_roles:
    print("Access granted!")
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python frozenset.py
Access granted!
```

In this example, we use a frozenset to store a collection of allowed roles. We then check if the user role is in the frozenset. Since the user role is `admin`, which is in the frozenset, the output shows that access is granted.

### Network Graphs

In graph theory, frozensets can represent vertices or edges in a graph. For example, a frozenset of vertices can represent the nodes in a network:

```python title="frozenset.py" showLineNumbers{1} {1-4}
# Representing a network graph with frozensets
network_graph = {
    frozenset({'node_A', 'node_B'}): {'weight': 5},
    frozenset({'node_B', 'node_C'}): {'weight': 3},
    frozenset({'node_C', 'node_A'}): {'weight': 7}
}
```

## Conclusion

Frozensets in Python provide a valuable tool for scenarios where immutability and hashability are crucial. Whether you need to create keys for dictionaries, represent unchangeable sets of data, or ensure the integrity of configuration settings, frozensets offer a versatile and efficient solution. Understanding their characteristics and use cases will empower you to make informed decisions in your Python programming. As you explore more advanced topics in Python, frozensets will continue to be a valuable addition to your programming toolkit. Happy coding!