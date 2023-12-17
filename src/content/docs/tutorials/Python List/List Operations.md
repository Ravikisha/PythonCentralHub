---
title: List Operations
description: Learn about changing list items in Python. How to insert, append, and remove items from a list. How to change a list item at a specific index. How to change multiple list items at once. How to change a list item to a different type. 
sidebar: 
    order: 50
---

List is a mutable data type. This means that you can change the list after it has been created. In this tutorial, you will learn how to change list items in Python. You can change a list item at a specific index, change multiple list items at once, or change a list item to a different type.

## Change List Item at Specific Index
You can change a list item at a specific index by assigning a new value to the index. For example, you can change the first item in the list to a different value by assigning a new value to the index 0.

<!-- ```python title="empty_list.py" showLineNumbers{1} {1}
empty_list = []
print(empty_list)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python empty_list.py
[]
``` -->

```python title="syntax.py" showLineNumbers{1} {1}
list[index] = new_value
```

The following example shows how to change the first item in the list to a different value.

```python title="change_first_item.py" showLineNumbers{1} {1,4}
numbers = [1, 2, 3, 4, 5]
print(numbers)

numbers[0] = 10
print(numbers)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python change_first_item.py
[1, 2, 3, 4, 5]
[10, 2, 3, 4, 5]
```

In the example above, we changed the first item in the list to 10. The rest of the items in the list remain the same.

## Change Multiple List Items
You can change multiple list items at once by assigning a new list to a slice of the list. For example, you can change the first three items in the list to different values by assigning a new list to the slice `0:3`.

```python title="syntax.py" showLineNumbers{1} {1}
list[start:end] = new_list
```

The following example shows how to change the first three items in the list to different values.

```python title="change_multiple_items.py" showLineNumbers{1} {1,4}
numbers = [1, 2, 3, 4, 5]
print(numbers)

numbers[0:3] = [10, 20, 30]
print(numbers)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python change_multiple_items.py
[1, 2, 3, 4, 5]
[10, 20, 30, 4, 5]
```

In the example above, we changed the first three items in the list to 10, 20, and 30. The rest of the items in the list remain the same.

## Change List Item to Different Type
You can change a list item to a different type by assigning a new value to the index. For example, you can change the first item in the list to a string by assigning a string to the index 0.

```python title="syntax.py" showLineNumbers{1} {1}
list[index] = new_value
```

The following example shows how to change the first item in the list to a string.

```python title="change_item_type.py" showLineNumbers{1} {1,4}
numbers = [1, 2, 3, 4, 5]
print(numbers)

numbers[0] = "one"
print(numbers)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python change_item_type.py
[1, 2, 3, 4, 5]
['one', 2, 3, 4, 5]
```

In the example above, we changed the first item in the list to a string. The rest of the items in the list remain the same.

## Insert List Item
You can insert a new list item at a specific index by using the `insert()` method. The `insert()` method takes two arguments: the index where you want to insert the new item and the new item.

```python title="syntax.py" showLineNumbers{1} {1}
list.insert(index, new_item)
```

The following example shows how to insert a new item at the beginning of the list.

```python title="insert_item.py" showLineNumbers{1} {1,4}
numbers = [1, 2, 3, 4, 5]
print(numbers)

numbers.insert(0, 10)
print(numbers)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python insert_item.py
[1, 2, 3, 4, 5]
[10, 1, 2, 3, 4, 5]
```

In the example above, we inserted a new item at the beginning of the list. The rest of the items in the list were shifted to the right.

## Append List Item
You can append a new list item to the end of the list by using the `append()` method. The `append()` method takes one argument: the new item.

```python title="syntax.py" showLineNumbers{1} {1}
list.append(new_item)
```

The following example shows how to append a new item to the end of the list.

```python title="append_item.py" showLineNumbers{1} {1,4}
numbers = [1, 2, 3, 4, 5]
print(numbers)

numbers.append(10)
print(numbers)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python append_item.py
[1, 2, 3, 4, 5]
[1, 2, 3, 4, 5, 10]
```

In the example above, we appended a new item to the end of the list.

## Insert Item at Negative Index
You can insert a new list item at a negative index by using the `insert()` method. The `insert()` method takes two arguments: the index where you want to insert the new item and the new item.

```python title="syntax.py" showLineNumbers{1} {1}
list.insert(index, new_item)
```

The following example shows how to insert a new item at the end of the list.

```python title="insert_item_at_negative_index.py" showLineNumbers{1} {1,4}
numbers = [1, 2, 3, 4, 5]
print(numbers)

numbers.insert(-1, 10)
print(numbers)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python insert_item_at_negative_index.py
[1, 2, 3, 4, 5]
[1, 2, 3, 4, 10, 5]
```

In the example above, we inserted a new item at the end of the list. The rest of the items in the list were shifted to the right.

## Remove List Item
You can remove a list item by using the `remove()` method. The `remove()` method takes one argument: the item you want to remove.

```python title="syntax.py" showLineNumbers{1} {1}
list.remove(item)
```

The following example shows how to remove an item from the list.

```python title="remove_item.py" showLineNumbers{1} {1,4}
numbers = [1, 2, 3, 4, 5]
print(numbers)

numbers.remove(3)
print(numbers)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python remove_item.py
[1, 2, 3, 4, 5]
[1, 2, 4, 5]
```

In the example above, we removed the item 3 from the list.

## Remove List Item at Specific Index
You can remove a list item at a specific index by using the `pop()` method. The `pop()` method takes one argument: the index of the item you want to remove.

```python title="syntax.py" showLineNumbers{1} {1}
list.pop(index)
```

The following example shows how to remove an item at a specific index from the list.

```python title="remove_item_at_index.py" showLineNumbers{1} {1,4}
numbers = [1, 2, 3, 4, 5]
print(numbers)

numbers.pop(3)
print(numbers)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python remove_item_at_index.py
[1, 2, 3, 4, 5]
[1, 2, 3, 5]
```

In the example above, we removed the item at index 3 from the list.

## Remove All List Items
You can remove all list items by using the `clear()` method. The `clear()` method takes no arguments.

```python title="syntax.py" showLineNumbers{1} {1}
list.clear()
```

The following example shows how to remove all items from the list.

```python title="remove_all_items.py" showLineNumbers{1} {1,4}
numbers = [1, 2, 3, 4, 5]
print(numbers)

numbers.clear()
print(numbers)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python remove_all_items.py
[1, 2, 3, 4, 5]
[]
```

In the example above, we removed all items from the list.

## Remove List Item using del
You can remove a list item by using the `del` keyword. The `del` keyword takes one argument: the item you want to remove.

```python title="syntax.py" showLineNumbers{1} {1}
del list[index]
```

The following example shows how to remove an item from the list.

```python title="remove_item_using_del.py" showLineNumbers{1} {1,4}
numbers = [1, 2, 3, 4, 5]
print(numbers)

del numbers[3]
print(numbers)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python remove_item_using_del.py
[1, 2, 3, 4, 5]
[1, 2, 3, 5]
```

In the example above, we removed the item 4 from the list.

## Remove List Item using del with Slice
You can remove multiple list items by using the `del` keyword with a slice. The `del` keyword takes one argument: the slice you want to remove.

```python title="syntax.py" showLineNumbers{1} {1}
del list[start:end]
```

The following example shows how to remove multiple items from the list.

```python title="remove_multiple_items_using_del.py" showLineNumbers{1} {1,4}
numbers = [1, 2, 3, 4, 5]
print(numbers)

del numbers[1:3]
print(numbers)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python remove_multiple_items_using_del.py
[1, 2, 3, 4, 5]
[1, 4, 5]
```

In the example above, we removed the items 2 and 3 from the list.

## Change List Item in Loop
You can change list items in a loop by using the `enumerate()` function. The `enumerate()` function takes one argument: the list you want to loop over. The `enumerate()` function returns a list of tuples. Each tuple contains the index and the item at that index.

```python title="syntax.py" showLineNumbers{1} {1-2}
for index, item in enumerate(list):
    # do something with index and item
```

The following example shows how to change list items in a loop.

```python title="change_items_in_loop.py" showLineNumbers{1} {1,4-5}
numbers = [1, 2, 3, 4, 5]
print(numbers)

for index, item in enumerate(numbers):
    numbers[index] = item * 10
print(numbers)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python change_items_in_loop.py
[1, 2, 3, 4, 5]
[10, 20, 30, 40, 50]
```

In the example above, we changed all items in the list to 10 times their original value.

:::note
Enumerate `enumerate()` function returns a list of tuples. Each tuple contains the index and the item at that index. You can use the `enumerate()` function to loop over a list and change list items in a loop.

```python title="enumerate.py" showLineNumbers{1} {1, 3-7}
numbers = [1, 2, 3, 4, 5]

for index, item in enumerate(numbers):
    print(index, item)
```

Output:

```cmd title="command" showLineNumbers{1} {2-6}
C:\Users\username>python enumerate.py
0 1
1 2
2 3
3 4
4 5
```

In the example above, we looped over the list and printed the index and the item at that index.
:::

## Change List Item in List Comprehension
You can change list items in a list comprehension by using the `enumerate()` function. The `enumerate()` function takes one argument: the list you want to loop over. The `enumerate()` function returns a list of tuples. Each tuple contains the index and the item at that index.

```python title="syntax.py" showLineNumbers{1} {1}
[expression for index, item in enumerate(list)]
```

The following example shows how to change list items in a list comprehension.

```python title="change_items_in_list_comprehension.py" showLineNumbers{1} {1,4}
numbers = [1, 2, 3, 4, 5]
print(numbers)

numbers = [item * 10 for index, item in enumerate(numbers)]
print(numbers)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python change_items_in_list_comprehension.py
[1, 2, 3, 4, 5]
[10, 20, 30, 40, 50]
```

In the example above, we changed all items in the list to 10 times their original value.

## Change List Item in List Comprehension with Condition
You can change list items in a list comprehension with a condition by using the `enumerate()` function. The `enumerate()` function takes one argument: the list you want to loop over. The `enumerate()` function returns a list of tuples. Each tuple contains the index and the item at that index.

```python title="syntax.py" showLineNumbers{1} {1}
[expression for index, item in enumerate(list) if condition]
```

The following example shows how to change list items in a list comprehension with a condition.

```python title="change_items_in_list_comprehension_with_condition.py" showLineNumbers{1} {1,4}
numbers = [1, 2, 3, 4, 5]
print(numbers)

numbers = [item * 10 for index, item in enumerate(numbers) if item % 2 == 0]
print(numbers)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python change_items_in_list_comprehension_with_condition.py
[1, 2, 3, 4, 5]
[20, 40]
```

In the example above, we changed all even items in the list to 10 times their original value.

## Sort List
You can sort a list by using the `sort()` method. The `sort()` method takes no arguments.

```python title="syntax.py" showLineNumbers{1} {1}
list.sort()
```

The following example shows how to sort a list.

```python title="sort_list.py" showLineNumbers{1} {1,4}
numbers = [5, 2, 4, 1, 3]
print(numbers)

numbers.sort()
print(numbers)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python sort_list.py
[5, 2, 4, 1, 3]
[1, 2, 3, 4, 5]
```

In the example above, we sorted the list in ascending order.

## Sort List in Descending Order
You can sort a list in descending order by using the `sort()` method with the argument `reverse=True`.

```python title="syntax.py" showLineNumbers{1} {1}
list.sort(reverse=True)
```

The following example shows how to sort a list in descending order.

```python title="sort_list_in_descending_order.py" showLineNumbers{1} {1,4}
numbers = [5, 2, 4, 1, 3]
print(numbers)

numbers.sort(reverse=True)
print(numbers)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python sort_list_in_descending_order.py
[5, 2, 4, 1, 3]
[5, 4, 3, 2, 1]
```

In the example above, we sorted the list in descending order.

## Sort List using Sorted
You can sort a list by using the `sorted()` function. The `sorted()` function takes one argument: the list you want to sort.

```python title="syntax.py" showLineNumbers{1} {1}
sorted(list)
```

The following example shows how to sort a list.

```python title="sort_list_using_sorted.py" showLineNumbers{1} {1,4}
numbers = [5, 2, 4, 1, 3]
print(numbers)

numbers = sorted(numbers)
print(numbers)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python sort_list_using_sorted.py
[5, 2, 4, 1, 3]
[1, 2, 3, 4, 5]
```

In the example above, we sorted the list in ascending order.

:::tip
Sorted `sorted()` function returns a new sorted list. The original list remains unchanged. You can use the `sorted()` function to sort a list.
It is only work on Python 3.6 or higher.
:::

## Sort List using Sorted in Descending Order
You can sort a list in descending order by using the `sorted()` function with the argument `reverse=True`.

```python title="syntax.py" showLineNumbers{1} {1}
sorted(list, reverse=True)
```

The following example shows how to sort a list in descending order.

```python title="sort_list_using_sorted_in_descending_order.py" showLineNumbers{1} {1,4}
numbers = [5, 2, 4, 1, 3]
print(numbers)

numbers = sorted(numbers, reverse=True)
print(numbers)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python sort_list_using_sorted_in_descending_order.py
[5, 2, 4, 1, 3]
[5, 4, 3, 2, 1]
```

In the example above, we sorted the list in descending order.

## Sort List with Key
You can sort a list with a key by using the `sort()` method with the argument `key`. The `sort()` method takes one argument: the key function.

```python title="syntax.py" showLineNumbers{1} {1}
list.sort(key=key_function)
```

The following example shows how to sort a list with a key.

```python title="sort_list_with_key.py" showLineNumbers{1} {1,4-5}
numbers = [5, 2, 4, 1, 3]
print(numbers)

numbers.sort(key=lambda x: x % 2 == 0)
print(numbers)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python sort_list_with_key.py
[5, 2, 4, 1, 3]
[5, 1, 3, 2, 4]
```

In the example above, we sorted the list with a key. The key function returns `True` if the item is even and `False` if the item is odd.

## Sort List with Key in Descending Order
You can sort a list with a key in descending order by using the `sort()` method with the argument `key` and `reverse=True`. The `sort()` method takes two arguments: the key function and the reverse flag.

```python title="syntax.py" showLineNumbers{1} {1}
list.sort(key=key_function, reverse=True)
```

The following example shows how to sort a list with a key in descending order.

```python title="sort_list_with_key_in_descending_order.py" showLineNumbers{1} {1,4-5}
numbers = [5, 2, 4, 1, 3]
print(numbers)

numbers.sort(key=lambda x: x % 2 == 0, reverse=True)
print(numbers)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python sort_list_with_key_in_descending_order.py
[5, 2, 4, 1, 3]
[4, 2, 5, 1, 3]
```

In the example above, we sorted the list with a key in descending order. The key function returns `True` if the item is even and `False` if the item is odd.

## Sort List with Key using Sorted
You can sort a list with a key by using the `sorted()` function with the argument `key`. The `sorted()` function takes two arguments: the list you want to sort and the key function.

```python title="syntax.py" showLineNumbers{1} {1}
sorted(list, key=key_function)
```

The following example shows how to sort a list with a key.

```python title="sort_list_with_key_using_sorted.py" showLineNumbers{1} {1,4-5}
numbers = [5, 2, 4, 1, 3]
print(numbers)

numbers = sorted(numbers, key=lambda x: x % 2 == 0)
print(numbers)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python sort_list_with_key_using_sorted.py
[5, 2, 4, 1, 3]
[5, 1, 3, 2, 4]
```

In the example above, we sorted the list with a key. The key function returns `True` if the item is even and `False` if the item is odd.



## Conclusion
You can change list items in Python. You can change a list item at a specific index, change multiple list items at once, or change a list item to a different type. You can also insert, append, and remove items from a list. You can change list items in a loop or in a list comprehension. For more learning resources, see Python Central Hub.