---
title: Array Methods
description: Learn how to use the array methods in Python. In this tutorial, we will learn how to use the array methods in Python with the help of examples.
sidebar: 
    order: 74
---

## Array Methods
The array methods are the built-in methods in Python. These methods are used to perform different operations on the array. In this tutorial, we will learn how to use the array methods in Python with the help of examples.

## Table of Methods
There are various methods available in Python to perform different operations on the array. The following table lists some of the important methods available in Python.

|S.No.|Method|Description|Example|
|:----|:-----|:----------|:------|
|1|append()|Adds an element at the end of the array|`arr.append(5)`|
|2|insert()|Adds an element at the specified position|`arr.insert(2, 5)`|
|3|remove()|Removes the first occurrence of the element with the specified value|`arr.remove(5)`|
|4|pop()|Removes the element at the specified position|`arr.pop(2)`|
|5|clear()|Removes all the elements from the array|`arr.clear()`|
|6|index()|Returns the index of the first element with the specified value|`arr.index(5)`|
|7|count()|Returns the number of elements with the specified value|`arr.count(5)`|
|8|sort()|Sorts the array|`arr.sort()`|
|9|reverse()|Reverses the order of the array|`arr.reverse()`|
|10|copy()|Returns a copy of the array|`arr.copy()`|
|11|extend()|Adds the elements of an array to the end of the current array|`arr.extend(arr2)`|
|12|fromlist()|Appends the contents of the list to the array|`arr.fromlist(list)`|
|13|tolist()|Converts the array to an ordinary list with the same items|`arr.tolist()`|
|14|tofile()|Writes all the array elements to a file|`arr.tofile(f)`|
|15|typecode()|Returns the type code of the array|`arr.typecode`|
|16|itemsize()|Returns the size of each element of the array in bytes|`arr.itemsize`|
|17|buffer_info()|Returns a tuple containing the address in which array is stored and the number of elements in it|`arr.buffer_info()`|
|18|byteswap()|Reverses the order of the bytes in the array|`arr.byteswap()`|
|19|frombytes()|Appends bytes from the string to the array|`arr.frombytes(s)`|
|20|fromfile()|Reads the array from the file, according to the dtype|`arr.fromfile(f, n)`|
|21|fromstring()|Appends items from the string into the array|`arr.fromstring(s)`|
|22|fromunicode()|Appends items from the unicode string into the array|`arr.fromunicode(s)`|
|23|tobytes()|Converts the array to an array of machine values and returns the bytes representation|`arr.tobytes()`|


## append() Method
The `append()` method adds an element at the end of the array. The syntax of the `append()` method is:

```python title="append.py" showLineNumbers{1} {1, 3-4}
import array as arr

my_array = arr.array('i', [1, 2, 3, 4, 5])
my_array.append(6)

print(my_array)
```

Output:
```cmd title="command" showLineNumbers{1} {2-6}
C:\Users\username>python append.py
array('i', [1, 2, 3, 4, 5, 6])
```

In the above example, we create an array of five elements and append a new element at the end of the array. The new element is added at the end of the array.

## insert() Method
The `insert()` method adds an element at the specified position. The syntax of the `insert()` method is:

```python title="insert.py" showLineNumbers{1} {1, 3-5}
import array as arr

my_array = arr.array('i', [1, 2, 3, 4, 5])
my_array.insert(2, 6)

print(my_array)
```

Output:
```cmd title="command" showLineNumbers{1} {2-6}
C:\Users\username>python insert.py
array('i', [1, 2, 6, 3, 4, 5])
```

In the above example, we create an array of five elements and insert a new element at the second position. The new element is added at the second position and the remaining elements are shifted to the right.

## remove() Method
The `remove()` method removes the first occurrence of the element with the specified value. The syntax of the `remove()` method is:

```python title="remove.py" showLineNumbers{1} {1, 3-5}
import array as arr

my_array = arr.array('i', [1, 2, 3, 4, 5])
my_array.remove(4)

print(my_array)
```

Output:
```cmd title="command" showLineNumbers{1} {2-6}
C:\Users\username>python remove.py
array('i', [1, 2, 3, 5])
```

In the above example, we create an array of five elements and remove the element with the value 4. The first occurrence of the element with the value 4 is removed from the array.

## pop() Method
The `pop()` method removes the element at the specified position. The syntax of the `pop()` method is:

```python title="pop.py" showLineNumbers{1} {1, 3-5}
import array as arr

my_array = arr.array('i', [1, 2, 3, 4, 5])
my_array.pop(2)

print(my_array)
```

Output:
```cmd title="command" showLineNumbers{1} {2-6}
C:\Users\username>python pop.py
array('i', [1, 2, 4, 5])
```

In the above example, we create an array of five elements and remove the element at the second position. The element at the second position is removed from the array.

## clear() Method
The `clear()` method removes all the elements from the array. The syntax of the `clear()` method is:

```python title="clear.py" showLineNumbers{1} {1, 3-5}
import array as arr

my_array = arr.array('i', [1, 2, 3, 4, 5])
my_array.clear()

print(my_array)
```

Output:
```cmd title="command" showLineNumbers{1} {2-6}
C:\Users\username>python clear.py
array('i')
```

In the above example, we create an array of five elements and remove all the elements from the array. The array becomes empty after removing all the elements.

## index() Method
The `index()` method returns the index of the first occurrence of the element with the specified value. The syntax of the `index()` method is:

```python title="index.py" showLineNumbers{1} {1, 3-5}
import array as arr

my_array = arr.array('i', [1, 2, 3, 2, 4, 5])
print(my_array.index(2))
```

Output:
```cmd title="command" showLineNumbers{1} {2-4}
C:\Users\username>python index.py
1
```

In the above example, we create an array of six elements and find the index of the first occurrence of the element with the value 2. The index of the first occurrence of the element with the value 2 is 1.

## count() Method
The `count()` method returns the number of elements with the specified value. The syntax of the `count()` method is:

```python title="count.py" showLineNumbers{1} {1, 3-5}
import array as arr

my_array = arr.array('i', [1, 2, 3, 2, 4, 5])
print(my_array.count(2))
```

Output:
```cmd title="command" showLineNumbers{1} {2-4}
C:\Users\username>python count.py
2
```

In the above example, we create an array of six elements and count the number of elements with the value 2. The number of elements with the value 2 is 2.

## sort() Method
The `sort()` method sorts the array. The syntax of the `sort()` method is:

```python title="sort.py" showLineNumbers{1} {1, 3-5}
import array as arr

my_array = arr.array('i', [3, 2, 5, 4, 1])
my_array.sort()

print(my_array)
```

Output:
```cmd title="command" showLineNumbers{1} {2-6}
C:\Users\username>python sort.py
array('i', [1, 2, 3, 4, 5])
```

In the above example, we create an array of five elements and sort the array. The elements of the array are sorted in ascending order.

## reverse() Method
The `reverse()` method reverses the order of the array. The syntax of the `reverse()` method is:

```python title="reverse.py" showLineNumbers{1} {1, 3-5}
import array as arr

my_array = arr.array('i', [1, 2, 3, 4, 5])
my_array.reverse()

print(my_array)
```

Output:
```cmd title="command" showLineNumbers{1} {2-6}
C:\Users\username>python reverse.py
array('i', [5, 4, 3, 2, 1])
```

In the above example, we create an array of five elements and reverse the order of the array. The elements of the array are reversed.

## copy() Method
The `copy()` method returns a copy of the array. The syntax of the `copy()` method is:

```python title="copy.py" showLineNumbers{1} {1, 3-5}
import array as arr

my_array = arr.array('i', [1, 2, 3, 4, 5])
new_array = my_array.copy()

print(new_array)
```

Output:
```cmd title="command" showLineNumbers{1} {2-6}
C:\Users\username>python copy.py
array('i', [1, 2, 3, 4, 5])
```

In the above example, we create an array of five elements and copy the array to a new array. The new array is a copy of the original array.

## extend() Method
The `extend()` method adds the elements of an iterable to the end of the array. The syntax of the `extend()` method is:

```python title="extend.py" showLineNumbers{1} {1, 3-5}
import array as arr

my_array = arr.array('i', [1, 2, 3, 4, 5])
my_array.extend([6, 7, 8])

print(my_array)
```

Output:
```cmd title="command" showLineNumbers{1} {2-6}
C:\Users\username>python extend.py
array('i', [1, 2, 3, 4, 5, 6, 7, 8])
```

In the above example, we create an array of five elements and extend the array with three new elements. The three new elements are added at the end of the array.

## fromlist() Method
The `fromlist()` method appends the contents of the list to the array. The syntax of the `fromlist()` method is:

```python title="fromlist.py" showLineNumbers{1} {1, 3-5, 6}
import array as arr

my_array = arr.array('i', [1, 2, 3, 4, 5])
my_list = [6, 7, 8]

my_array.fromlist(my_list)

print(my_array)
```

Output:
```cmd title="command" showLineNumbers{1} {2-7}
C:\Users\username>python fromlist.py
array('i', [1, 2, 3, 4, 5, 6, 7, 8])
```

In the above example, we create an array of five elements and append the contents of the list to the array. The contents of the list are added at the end of the array.

## tolist() Method
The `tolist()` method converts the array to an ordinary list with the same items. The syntax of the `tolist()` method is:

```python title="tolist.py" showLineNumbers{1} {1, 3, 5}
import array as arr

my_array = arr.array('i', [1, 2, 3, 4, 5])

print(my_array.tolist())
```

Output:
```cmd title="command" showLineNumbers{1} {2-4}
C:\Users\username>python tolist.py
[1, 2, 3, 4, 5]
```

In the above example, we create an array of five elements and convert the array to a list. The array is converted to a list with the same items.

## tofile() Method
The `tofile()` method writes all the array elements to a file. The syntax of the `tofile()` method is:

```python title="tofile.py" showLineNumbers{1} {1, 3, 5-9}
import array as arr

my_array = arr.array('i', [1, 2, 3, 4, 5])

f = open('my_array.txt', 'w')
my_array.tofile(f)
f.close()
```

Output:
```cmd title="command" showLineNumbers{1} {2-6}
C:\Users\username>python tofile.py
```

```txt title="my_array.txt" showLineNumbers{1} {1-5}
1 2 3 4 5
```

In the above example, we create an array of five elements and write the array elements to a file. The array elements are written to the file in the same order.

## typecode() Method
The `typecode()` method returns the type code of the array. The syntax of the `typecode()` method is:

```python title="typecode.py" showLineNumbers{1} {1, 3, 5}
import array as arr

my_array = arr.array('i', [1, 2, 3, 4, 5])

print(my_array.typecode)
```

Output:
```cmd title="command" showLineNumbers{1} {2-4}
C:\Users\username>python typecode.py
i
```

In the above example, we create an array of five elements and print the type code of the array. The type code of the array is `i`.

## itemsize() Method
The `itemsize()` method returns the size of each element of the array in bytes. The syntax of the `itemsize()` method is:

```python title="itemsize.py" showLineNumbers{1} {1, 3, 5}
import array as arr

my_array = arr.array('i', [1, 2, 3, 4, 5])

print(my_array.itemsize)
```

Output:
```cmd title="command" showLineNumbers{1} {2-4}
C:\Users\username>python itemsize.py
4
```

In the above example, we create an array of five elements and print the size of each element of the array in bytes. The size of each element of the array is 4 bytes.

## buffer_info() Method
The `buffer_info()` method returns a tuple containing the address in which array is stored and the number of elements in it. The syntax of the `buffer_info()` method is:

```python title="buffer_info.py" showLineNumbers{1} {1, 3, 5}
import array as arr

my_array = arr.array('i', [1, 2, 3, 4, 5])

print(my_array.buffer_info())
```

Output:
```cmd title="command" showLineNumbers{1} {2-4}
C:\Users\username>python buffer_info.py
(140714816, 5)
```

In the above example, we create an array of five elements and print the address in which the array is stored and the number of elements in it. The address in which the array is stored is 140714816 and the number of elements in the array is 5.

## byteswap() Method
The `byteswap()` method reverses the order of the bytes in the array. The syntax of the `byteswap()` method is:

```python title="byteswap.py" showLineNumbers{1} {1, 3, 5}
import array as arr

my_array = arr.array('i', [1, 2, 3, 4, 5])

my_array.byteswap()

print(my_array)
```

Output:
```cmd title="command" showLineNumbers{1} {2-6}
C:\Users\username>python byteswap.py
array('i', [16777216, 33554432, 50331648, 67108864, 83886080])
```

In the above example, we create an array of five elements and reverse the order of the bytes in the array. The order of the bytes in the array is reversed.


## frombytes() Method
The `frombytes()` method appends bytes from the string to the array. The syntax of the `frombytes()` method is:

```python title="frombytes.py" showLineNumbers{1} {1, 3, 5-9}
import array as arr

my_array = arr.array('i', [1, 2, 3, 4, 5])

s = my_array.tostring()
my_array.frombytes(s)
print(my_array)
```

Output:
```cmd title="command" showLineNumbers{1} {2-6}
C:\Users\username>python frombytes.py
array('i', [1, 2, 3, 4, 5, 1, 2, 3, 4, 5])
```

In the above example, we create an array of five elements and append bytes from the string to the array. The bytes from the string are appended to the array.

## fromfile() Method
The `fromfile()` method reads the array from the file, according to the dtype. The syntax of the `fromfile()` method is:

```python title="fromfile.py" showLineNumbers{1} {1, 3, 5-7}
import array as arr

my_array = arr.array('i', [1, 2, 3, 4, 5])

f = open('my_array.txt', 'r')
my_array.fromfile(f, 5)
f.close()

print(my_array)
```

Output:
```cmd title="command" showLineNumbers{1} {2-8}
C:\Users\username>python fromfile.py
array('i', [1, 2, 3, 4, 5])
```

```txt title="my_array.txt" showLineNumbers{1} {1-5}
1 2 3 4 5
```

In the above example, we create an array of five elements and read the array from the file. The array is read from the file and stored in the array.

## fromstring() Method
The `fromstring()` method appends items from the string into the array. The syntax of the `fromstring()` method is:

```python title="fromstring.py" showLineNumbers{1} {1, 3, 5-9}
import array as arr

my_array = arr.array('i', [1, 2, 3, 4, 5])

s = my_array.tostring()
my_array.fromstring(s)
print(my_array)
```

Output:
```cmd title="command" showLineNumbers{1} {2-6}
C:\Users\username>python fromstring.py
array('i', [1, 2, 3, 4, 5, 1, 2, 3, 4, 5])
```

In the above example, we create an array of five elements and append items from the string into the array. The items from the string are appended to the array.

## fromunicode() Method
The `fromunicode()` method appends items from the unicode string into the array. The syntax of the `fromunicode()` method is:

```python title="fromunicode.py" showLineNumbers{1} {1, 3, 5-9}
import array as arr

my_array = arr.array('i', [1, 2, 3, 4, 5])

s = my_array.tostring()
my_array.fromunicode(s)
print(my_array)
```

Output:
```cmd title="command" showLineNumbers{1} {2-6}
C:\Users\username>python fromunicode.py
array('i', [1, 2, 3, 4, 5, 1, 2, 3, 4, 5])
```

In the above example, we create an array of five elements and append items from the unicode string into the array. The items from the unicode string are appended to the array.

## tobytes() Method
The `tobytes()` method converts the array to an array of machine values and returns the bytes representation. The syntax of the `tobytes()` method is:

```python title="tobytes.py" showLineNumbers{1} {1, 3, 5}
import array as arr

my_array = arr.array('i', [1, 2, 3, 4, 5])

print(my_array.tobytes())
```

Output:
```cmd title="command" showLineNumbers{1} {2-4}
C:\Users\username>python tobytes.py
b'\x01\x00\x00\x00\x02\x00\x00\x00\x03\x00\x00\x00\x04\x00\x00\x00\x05\x00\x00\x00'
```

In the above example, we create an array of five elements and convert the array to an array of machine values and returns the bytes representation. The array is converted to an array of machine values and returns the bytes representation.

## Conclusion
In this tutorial, we have learned how to use the array methods in Python with the help of examples. The array methods are the built-in methods in Python. These methods are used to perform different operations on the array. For more information, visit the [official documentation](https://docs.python.org/3/library/array.html) of the array methods. For more tutorials, visit our Python Central Hub.