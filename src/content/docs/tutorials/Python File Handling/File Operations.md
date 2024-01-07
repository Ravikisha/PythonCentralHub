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

## Create a Directory
We are creating a directory named `test` using the `os` module. The `os` module provides functions for interacting with the operating system. The `os` module comes under Python's standard utility modules. We are using the `os` module to create a directory in the current directory.

**Syntax:**
```python title="create_directory.py" showLineNumbers{1} {1, 3-4}
os.mkdir(path)
```

**Example:**

```python title="create_directory.py" showLineNumbers{1} {1, 3-4}
import os

os.mkdir('test')
```

Output:
```cmd title="command" showLineNumbers{1} {1}
C:\Users\username>python create_directory.py
```

In the above example, we are using the `mkdir()` function to create a directory. The `mkdir()` function takes one argument. The argument is the name of the directory to be created.

## Rename a Directory
We are renaming the directory `test` to `new_test` using the `os` module. The `os` module provides functions for interacting with the operating system. The `os` module comes under Python's standard utility modules. We are using the `os` module to rename a directory in the current directory.

**Syntax:**
```python title="rename_directory.py" showLineNumbers{1} {1, 3-4}
os.rename(src, dst)
```

**Example:**

```python title="rename_directory.py" showLineNumbers{1} {1, 3-4}
import os

os.rename('test', 'new_test')
```

Output:
```cmd title="command" showLineNumbers{1} {1}
C:\Users\username>python rename_directory.py
```

In the above example, we are using the `rename()` function to rename a directory. The `rename()` function takes two arguments. The first argument is the old name of the directory and the second argument is the new name of the directory.

## Delete a Directory
We are deleting the directory `new_test` using the `os` module. The `os` module provides functions for interacting with the operating system. The `os` module comes under Python's standard utility modules. We are using the `os` module to delete a directory in the current directory.

**Syntax:**
```python title="delete_directory.py" showLineNumbers{1} {1, 3-4}
os.rmdir(path)
```

**Example:**

```python title="delete_directory.py" showLineNumbers{1} {1, 3-4}
import os

os.rmdir('new_test')
```

Output:
```cmd title="command" showLineNumbers{1} {1}
C:\Users\username>python delete_directory.py
```

In the above example, we are using the `rmdir()` function to delete a directory. The `rmdir()` function takes one argument. The argument is the name of the directory to be deleted.

## Move a File
We are moving the file `test.txt` to the directory `test` using the `shutil` module. The `shutil` module provides functions for copying and moving files and directories. The `shutil` module comes under Python's standard utility modules. We are using the `shutil` module to move a file in the current directory.

**Syntax:**
```python title="move_file.py" showLineNumbers{1} {1, 3-4}
shutil.move(src, dst)
```

**Example:**

```python title="move_file.py" showLineNumbers{1} {1, 3-4}
import shutil

shutil.move('test.txt', 'test')
```

Output:
```cmd title="command" showLineNumbers{1} {1}
C:\Users\username>python move_file.py
```

In the above example, we are using the `move()` function to move a file. The `move()` function takes two arguments. The first argument is the name of the file to be moved and the second argument is the name of the directory to which the file is to be moved.

## Move a Directory
We are moving the directory `test` to the directory `new_test` using the `shutil` module. The `shutil` module provides functions for copying and moving files and directories. The `shutil` module comes under Python's standard utility modules. We are using the `shutil` module to move a directory in the current directory.

**Syntax:**
```python title="move_directory.py" showLineNumbers{1} {1, 3-4}
shutil.move(src, dst)
```

**Example:**

```python title="move_directory.py" showLineNumbers{1} {1, 3-4}
import shutil

shutil.move('test', 'new_test')
```

Output:
```cmd title="command" showLineNumbers{1} {1}
C:\Users\username>python move_directory.py
```

In the above example, we are using the `move()` function to move a directory. The `move()` function takes two arguments. The first argument is the name of the directory to be moved and the second argument is the name of the directory to which the directory is to be moved.

## Copy a File
We are copying the file `test.txt` to the directory `test` using the `shutil` module. The `shutil` module provides functions for copying and moving files and directories. The `shutil` module comes under Python's standard utility modules. We are using the `shutil` module to copy a file in the current directory.

**Syntax:**
```python title="copy_file.py" showLineNumbers{1} {1, 3-4}
shutil.copy(src, dst)
```

**Example:**

```python title="copy_file.py" showLineNumbers{1} {1, 3-4}
import shutil

shutil.copy('test.txt', 'test')
```

Output:
```cmd title="command" showLineNumbers{1} {1}
C:\Users\username>python copy_file.py
```

In the above example, we are using the `copy()` function to copy a file. The `copy()` function takes two arguments. The first argument is the name of the file to be copied and the second argument is the name of the directory to which the file is to be copied.

## Copy a Directory
We are copying the directory `test` to the directory `new_test` using the `shutil` module. The `shutil` module provides functions for copying and moving files and directories. The `shutil` module comes under Python's standard utility modules. We are using the `shutil` module to copy a directory in the current directory.

**Syntax:**
```python title="copy_directory.py" showLineNumbers{1} {1, 3-4}
shutil.copytree(src, dst)
```

**Example:**

```python title="copy_directory.py" showLineNumbers{1} {1, 3-4}
import shutil

shutil.copytree('test', 'new_test')
```

Output:
```cmd title="command" showLineNumbers{1} {1}
C:\Users\username>python copy_directory.py
```

In the above example, we are using the `copytree()` function to copy a directory. The `copytree()` function takes two arguments. The first argument is the name of the directory to be copied and the second argument is the name of the directory to which the directory is to be copied.

## List Files and Directories
We are listing the files and directories in the current directory using the `os` module. The `os` module provides functions for interacting with the operating system. The `os` module comes under Python's standard utility modules. We are using the `os` module to list the files and directories in the current directory.

**Syntax:**
```python title="list_files_and_directories.py" showLineNumbers{1} {1, 3-4}
os.listdir(path)
```

**Example:**

```python title="list_files_and_directories.py" showLineNumbers{1} {1, 3-4}
import os

print(os.listdir())
```

Output:
```cmd title="command" showLineNumbers{1} {1-2}
C:\Users\username>python list_files_and_directories.py
['append.py', 'create_directory.py', 'create_file.py', 'delete_directory.py', 'delete_file.py', 'File Operations.md', 'File%20Operations.md', 'move_directory.py', 'move_file.py', 'rename_directory.py', 'rename_file.py']
```

In the above example, we are using the `listdir()` function to list the files and directories in the current directory. The `listdir()` function takes one argument. The argument is the name of the directory whose files and directories are to be listed. If no argument is passed to the `listdir()` function, then it lists the files and directories in the current directory.

## Check if a File Exists
We are checking if the file `test.txt` exists in the current directory using the `os` module. The `os` module provides functions for interacting with the operating system. The `os` module comes under Python's standard utility modules. We are using the `os` module to check if a file exists in the current directory.

**Syntax:**
```python title="check_if_file_exists.py" showLineNumbers{1} {1, 3-4}
os.path.exists(path)
```

**Example:**

```python title="check_if_file_exists.py" showLineNumbers{1} {1, 3-4}
import os

print(os.path.exists('test.txt'))
```

Output:
```cmd title="command" showLineNumbers{1} {1-2}
C:\Users\username>python check_if_file_exists.py
True
```

In the above example, we are using the `exists()` function to check if a file exists. The `exists()` function takes one argument. The argument is the name of the file whose existence is to be checked.

## Check if a Directory Exists
We are checking if the directory `test` exists in the current directory using the `os` module. The `os` module provides functions for interacting with the operating system. The `os` module comes under Python's standard utility modules. We are using the `os` module to check if a directory exists in the current directory.

**Syntax:**
```python title="check_if_directory_exists.py" showLineNumbers{1} {1, 3-4}
os.path.exists(path)
```

**Example:**

```python title="check_if_directory_exists.py" showLineNumbers{1} {1, 3-4}
import os

print(os.path.exists('test'))
```

Output:
```cmd title="command" showLineNumbers{1} {1-2}
C:\Users\username>python check_if_directory_exists.py
True
```

In the above example, we are using the `exists()` function to check if a directory exists. The `exists()` function takes one argument. The argument is the name of the directory whose existence is to be checked.

## Get the Current Working Directory
We are getting the current working directory using the `os` module. The `os` module provides functions for interacting with the operating system. The `os` module comes under Python's standard utility modules. We are using the `os` module to get the current working directory.

**Syntax:**
```python title="get_current_working_directory.py" showLineNumbers{1} {1, 3-4}
os.getcwd()
```

**Example:**

```python title="get_current_working_directory.py" showLineNumbers{1} {1, 3-4}
import os

print(os.getcwd())
```

Output:
```cmd title="command" showLineNumbers{1} {1-2}
C:\Users\username>python get_current_working_directory.py
C:\Users\username
```

In the above example, we are using the `getcwd()` function to get the current working directory. The `getcwd()` function takes no argument.

## Change the Current Working Directory
We are changing the current working directory to the directory `test` using the `os` module. The `os` module provides functions for interacting with the operating system. The `os` module comes under Python's standard utility modules. We are using the `os` module to change the current working directory.

**Syntax:**
```python title="change_current_working_directory.py" showLineNumbers{1} {1, 3-4}
os.chdir(path)
```

**Example:**

```python title="change_current_working_directory.py" showLineNumbers{1} {1, 3-4}
import os

os.chdir('test')
```

Output:
```cmd title="command" showLineNumbers{1} {1}
C:\Users\username>python change_current_working_directory.py
```

In the above example, we are using the `chdir()` function to change the current working directory. The `chdir()` function takes one argument. The argument is the name of the directory to which the current working directory is to be changed.

## Get the Size of a File
We are getting the size of the file `test.txt` using the `os` module. The `os` module provides functions for interacting with the operating system. The `os` module comes under Python's standard utility modules. We are using the `os` module to get the size of a file.

**Syntax:**
```python title="get_file_size.py" showLineNumbers{1} {1, 3-4}
os.path.getsize(path)
```

**Example:**

```python title="get_file_size.py" showLineNumbers{1} {1, 3-4}
import os

print(os.path.getsize('test.txt'))
```

Output:
```cmd title="command" showLineNumbers{1} {1-2}
C:\Users\username>python get_file_size.py
0
```

In the above example, we are using the `getsize()` function to get the size of a file. The `getsize()` function takes one argument. The argument is the name of the file whose size is to be obtained.

## Get the Size of a Directory
We are getting the size of the directory `test` using the `shutil` module. The `shutil` module provides functions for copying and moving files and directories. The `shutil` module comes under Python's standard utility modules. We are using the `shutil` module to get the size of a directory.

**Syntax:**
```python title="get_directory_size.py" showLineNumbers{1} {1, 3-4}
shutil.disk_usage(path)
```

**Example:**

```python title="get_directory_size.py" showLineNumbers{1} {1, 3-4}
import shutil

print(shutil.disk_usage('test'))
```

Output:
```cmd title="command" showLineNumbers{1} {1-2}
C:\Users\username>python get_directory_size.py
usage(total=97676207104, used=97676207104, free=0)
```

In the above example, we are using the `disk_usage()` function to get the size of a directory. The `disk_usage()` function takes one argument. The argument is the name of the directory whose size is to be obtained.

## Conclusion
In this tutorial, we learned how to perform file operations in Python. We learned how to create, rename, delete, and move files and directories. We also learned how to list files and directories, check if a file or directory exists, get the current working directory, change the current working directory, and get the size of a file or directory. Now you can perform file operations in Python. For more information, visit the [official documentation](https://docs.python.org/3/library/os.html) of the `os` module and the [official documentation](https://docs.python.org/3/library/shutil.html) of the `shutil` module. For more tutorials, visit our Python Central Hub.