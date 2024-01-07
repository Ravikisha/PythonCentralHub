---
title: File Operations
description: Learn how to perform file operations in Python. How to create, rename, delete, and move files and directories.
sidebar: 
    order: 77
---

<!-- ```python title="append.py" showLineNumbers{1} {1, 3-4}
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

In the above example, we create an array of five elements and append a new element at the end of the array. The new element is added at the end of the array. -->

## Create a File
We are creating a file named `test.txt` using `os` module. The `os` module provides functions for interacting with the operating system. The `os` module comes under Python's standard utility modules. We are using the `os` module to create a file in the current directory.

```python title="create_file.py" showLineNumbers{1} {1}
open('test.txt', 'w').close()
```

Output:
```cmd title="command" showLineNumbers{1} {1}
C:\Users\username>python create_file.py
```

In the above example, we are using the `open()` function to create a file. The `open()` function takes two arguments. The first argument is the name of the file and the second argument is the mode. The mode is used to specify the purpose of opening the file. The `w` mode is used to open the file for writing. The `open()` function returns a file object. We are using the `close()` method to close the file object.

## Rename a File
We are renaming the file `test.txt` to `new_test.txt` using the `os` module. The `os` module provides functions for interacting with the operating system. The `os` module comes under Python's standard utility modules. We are using the `os` module to rename a file in the current directory.

**Syntax:**
```python title="rename_file.py" showLineNumbers{1} {1, 3-4}
os.rename(src, dst)
```

**Example:**

```python title="rename_file.py" showLineNumbers{1} {1, 3-4}
import os

os.rename('test.txt', 'new_test.txt')
```

Output:
```cmd title="command" showLineNumbers{1} {1}
C:\Users\username>python rename_file.py
```

In the above example, we are using the `rename()` function to rename a file. The `rename()` function takes two arguments. The first argument is the old name of the file and the second argument is the new name of the file.

## Delete a File
We are deleting the file `new_test.txt` using the `os` module. The `os` module provides functions for interacting with the operating system. The `os` module comes under Python's standard utility modules. We are using the `os` module to delete a file in the current directory.

**Syntax:**
```python title="delete_file.py" showLineNumbers{1} {1, 3-4}
os.remove(path)
```

**Example:**

```python title="delete_file.py" showLineNumbers{1} {1, 3-4}
import os

os.remove('new_test.txt')
```

Output:
```cmd title="command" showLineNumbers{1} {1}
C:\Users\username>python delete_file.py
```

In the above example, we are using the `remove()` function to delete a file. The `remove()` function takes one argument. The argument is the name of the file to be deleted.

## 