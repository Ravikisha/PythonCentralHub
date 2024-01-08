---
title: OS Methods
description: Learn how to use the OS module to handle files and directories. OS methods are used to create, delete, rename, and move files and directories. 
sidebar: 
    order: 79
---

## OS Methods
This tutorial will teach you how to use the OS module to handle files and directories. OS methods are used to create, delete, rename, and move files and directories.

## Table of Methods
|S.No|Method|Description|Example|
|----|------|-----------|-------|
|1|os.getcwd()|Returns the current working directory.|`os.getcwd()`|
|2|os.chdir(path)|Changes the current working directory to the specified path.|`os.chdir('C:\\Users\\User\\Desktop')`|
|3|os.listdir(path)|Returns a list of all files and directories in the specified path.|`os.listdir('C:\\Users\\User\\Desktop')`|
|4|os.mkdir(path)|Creates a directory in the specified path.|`os.mkdir('C:\\Users\\User\\Desktop\\New Folder')`|
|5|os.makedirs(path)|Creates a directory in the specified path. If the parent directories do not exist, they will be created.|`os.makedirs('C:\\Users\\User\\Desktop\\New Folder\\New Folder')`|
|6|os.remove(path)|Deletes the file at the specified path.|`os.remove('C:\\Users\\User\\Desktop\\New Folder\\New Folder\\file.txt')`|
|7|os.rmdir(path)|Deletes the directory at the specified path.|`os.rmdir('C:\\Users\\User\\Desktop\\New Folder\\New Folder')`|
|8|os.removedirs(path)|Deletes the directory at the specified path. If the parent directories are empty, they will be deleted.|`os.removedirs('C:\\Users\\User\\Desktop\\New Folder\\New Folder')`|
|9|os.rename(src, dst)|Renames the file or directory at the specified source path to the specified destination path.|`os.rename('C:\\Users\\User\\Desktop\\New Folder\\New Folder\\file.txt', 'C:\\Users\\User\\Desktop\\New Folder\\New Folder\\new_file.txt')`|
|10|os.replace(src, dst)|Renames the file or directory at the specified source path to the specified destination path. If the destination path already exists, it will be replaced.|`os.replace('C:\\Users\\User\\Desktop\\New Folder\\New Folder\\file.txt', 'C:\\Users\\User\\Desktop\\New Folder\\New Folder\\new_file.txt')`|
|11|os.walk(path)|Returns a generator that yields a tuple of three values for each directory in the specified path. The first value is the path of the directory, the second value is a list of the names of the subdirectories in the directory, and the third value is a list of the names of the files in the directory.|`os.walk('C:\\Users\\User\\Desktop\\New Folder')`|
|12|os.path.exists(path)|Returns True if the file or directory at the specified path exists, otherwise returns False.|`os.path.exists('C:\\Users\\User\\Desktop\\New Folder\\New Folder\\file.txt')`|
|13|os.path.isfile(path)|Returns True if the file at the specified path exists, otherwise returns False.|`os.path.isfile('C:\\Users\\User\\Desktop\\New Folder\\New Folder\\file.txt')`|
|14|os.path.isdir(path)|Returns True if the directory at the specified path exists, otherwise returns False.|`os.path.isdir('C:\\Users\\User\\Desktop\\New Folder\\New Folder')`|
|15|os.path.getsize(path)|Returns the size of the file at the specified path in bytes.|`os.path.getsize('C:\\Users\\User\\Desktop\\New Folder\\New Folder\\file.txt')`|
|16|os.path.getmtime(path)|Returns the time of the last modification of the file at the specified path.|`os.path.getmtime('C:\\Users\\User\\Desktop\\New Folder\\New Folder\\file.txt')`|
|17|os.path.getctime(path)|Returns the time of the creation of the file at the specified path.|`os.path.getctime('C:\\Users\\User\\Desktop\\New Folder\\New Folder\\file.txt')`|
|18|os.path.getatime(path)|Returns the time of the last access of the file at the specified path.|`os.path.getatime('C:\\Users\\User\\Desktop\\New Folder\\New Folder\\file.txt')`|
|19|os.path.abspath(path)|Returns the absolute path of the file or directory at the specified path.|`os.path.abspath('C:\\Users\\User\\Desktop\\New Folder\\New Folder\\file.txt')`|
|20|os.path.dirname(path)|Returns the directory name of the file or directory at the specified path.|`os.path.dirname('C:\\Users\\User\\Desktop\\New Folder\\New Folder\\file.txt')`|
|21|os.path.basename(path)|Returns the base name of the file or directory at the specified path.|`os.path.basename('C:\\Users\\User\\Desktop\\New Folder\\New Folder\\file.txt')`|
|22|os.path.split(path)|Returns a tuple of two values. The first value is the directory name of the file or directory at the specified path, and the second value is the base name of the file or directory at the specified path.|`os.path.split('C:\\Users\\User\\Desktop\\New Folder\\New Folder\\file.txt')`|
|23|os.path.join(path1, path2)|Joins the specified paths.|`os.path.join('C:\\Users\\User\\Desktop\\New Folder', 'New Folder')`|
|24|os.path.splitext(path)|Splits the specified path into a tuple of two values. The first value is the path without the extension, and the second value is the extension.|`os.path.splitext('C:\\Users\\User\\Desktop\\New Folder\\New Folder\\file.txt')`|
|25|os.path.normpath(path)|Normalizes the specified path.|`os.path.normpath('C:\\Users\\User\\Desktop\\New Folder\\New Folder\\file.txt')`|
|26|os.path.relpath(path)|Returns the relative path from the current working directory to the specified path.|`os.path.relpath('C:\\Users\\User\\Desktop\\New Folder\\New Folder\\file.txt')`|
|27|os.path.commonpath(paths)|Returns the common path of the specified paths.|`os.path.commonpath(['C:\\Users\\User\\Desktop\\New Folder\\New Folder\\file.txt', 'C:\\Users\\User\\Desktop\\New Folder\\New Folder\\new_file.txt'])`|
|28|os.path.commonprefix(paths)|Returns the common prefix of the specified paths.|`os.path.commonprefix(['C:\\Users\\User\\Desktop\\New Folder\\New Folder\\file.txt', 'C:\\Users\\User\\Desktop\\New Folder\\New Folder\\new_file.txt'])`|
|29|os.path.expanduser(path)|Expands the specified path to the user's home directory.|`os.path.expanduser('~\\Desktop\\New Folder\\New Folder\\file.txt')`|
|30|os.path.expandvars(path)|Expands the specified path to the environment variables.|`os.path.expandvars('%USERPROFILE%\\Desktop\\New Folder\\New Folder\\file.txt')`|
|31|os.path.samefile(path1, path2)|Returns True if the specified paths refer to the same file, otherwise returns False.|`os.path.samefile('C:\\Users\\User\\Desktop\\New Folder\\New Folder\\file.txt', 'C:\\Users\\User\\Desktop\\New Folder\\New Folder\\new_file.txt')`|
|32|os.path.sameopenfile(fp1, fp2)|Returns True if the specified file objects refer to the same file, otherwise returns False.|`os.path.sameopenfile(open('C:\\Users\\User\\Desktop\\New Folder\\New Folder\\file.txt'), open('C:\\Users\\User\\Desktop\\New Folder\\New Folder\\new_file.txt'))`|
|33|os.path.samestat(stat1, stat2)|Returns True if the specified stat objects refer to the same file, otherwise returns False.|`os.path.samestat(os.stat('C:\\Users\\User\\Desktop\\New Folder\\New Folder\\file.txt'), os.stat('C:\\Users\\User\\Desktop\\New Folder\\New Folder\\new_file.txt'))`|
|34|os.path.isabs(path)|Returns True if the specified path is an absolute path, otherwise returns False.|`os.path.isabs('C:\\Users\\User\\Desktop\\New Folder\\New Folder\\file.txt')`|
|35|os.path.ismount(path)|Returns True if the specified path is a mount point, otherwise returns False.|`os.path.ismount('C:\\Users\\User\\Desktop\\New Folder\\New Folder\\file.txt')`|

<!-- ```python title="open.py" showLineNumbers{1} {1, 3-4}
file = open("file.txt", "r")

print(file.read())
```

Output:
```cmd title="command" showLineNumbers{1} {2-6}
C:\Users\username>python open.py
Hello World
```

In the above example, we open a file named "file.txt" in read mode. The file object is stored in the variable file. The read() method reads the entire content of the file and returns it as a string. -->

## os.getcwd() Method
The os.getcwd() method returns the current working directory.

```python title="os_getcwd.py" showLineNumbers{1} {1,3}
import os

print(os.getcwd())
```

Output:
```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python os_getcwd.py
C:\Users\username
```

In the above example, we import the os module and use the os.getcwd() method to get the current working directory.

## os.chdir() Method
The os.chdir() method changes the current working directory to the specified path.

```python title="os_chdir.py" showLineNumbers{1} {1,3}
import os

os.chdir('C:\\Users\\User\\Desktop')
print(os.getcwd())
```

Output:
```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python os_chdir.py
C:\Users\username\Desktop
```

In the above example, we import the os module and use the os.chdir() method to change the current working directory to the Desktop directory.

## os.listdir() Method
The os.listdir() method returns a list of all files and directories in the specified path.

```python title="os_listdir.py" showLineNumbers{1} {1,3}
import os

print(os.listdir('C:\\Users\\User\\Desktop'))
```

Output:
```cmd title="command" showLineNumbers{1} {2-6}
C:\Users\username>python os_listdir.py
['New Folder', 'file.txt']
```

In the above example, we import the os module and use the os.listdir() method to get a list of all files and directories in the Desktop directory.

## os.mkdir() Method
The os.mkdir() method creates a directory in the specified path.

```python title="os_mkdir.py" showLineNumbers{1} {1,3}
import os

os.mkdir('C:\\Users\\User\\Desktop\\New Folder')
```

Output:
```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python os_mkdir.py
```

In the above example, we import the os module and use the os.mkdir() method to create a directory named "New Folder" in the Desktop directory.

## os.makedirs() Method
The os.makedirs() method creates a directory in the specified path. If the parent directories do not exist, they will be created.

```python title="os_makedirs.py" showLineNumbers{1} {1,3}
import os

os.makedirs('C:\\Users\\User\\Desktop\\New Folder\\New Folder')
```

Output:
```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python os_makedirs.py
```

In the above example, we import the os module and use the os.makedirs() method to create a directory named "New Folder" in the Desktop directory. Since the parent directory "New Folder" does not exist, it will be created.

## os.remove() Method
The os.remove() method deletes the file at the specified path.

```python title="os_remove.py" showLineNumbers{1} {1,3}
import os

os.remove('C:\\Users\\User\\Desktop\\New Folder\\New Folder\\file.txt')
```

Output:
```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python os_remove.py
```

In the above example, we import the os module and use the os.remove() method to delete the file named "file.txt" in the "New Folder" directory.

## os.rmdir() Method
The os.rmdir() method deletes the directory at the specified path.

```python title="os_rmdir.py" showLineNumbers{1} {1,3}
import os

os.rmdir('C:\\Users\\User\\Desktop\\New Folder\\New Folder')
```

Output:
```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python os_rmdir.py
```

In the above example, we import the os module and use the os.rmdir() method to delete the directory named "New Folder" in the Desktop directory.

## os.removedirs() Method
The os.removedirs() method deletes the directory at the specified path. If the parent directories are empty, they will be deleted.

```python title="os_removedirs.py" showLineNumbers{1} {1,3}
import os

os.removedirs('C:\\Users\\User\\Desktop\\New Folder\\New Folder')
```

Output:
```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python os_removedirs.py
```

In the above example, we import the os module and use the os.removedirs() method to delete the directory named "New Folder" in the Desktop directory. Since the parent directory "New Folder" is empty, it will be deleted.

## os.rename() Method
The os.rename() method renames the file or directory at the specified source path to the specified destination path.

```python title="os_rename.py" showLineNumbers{1} {1,3}
import os

os.rename('C:\\Users\\User\\Desktop\\New Folder\\New Folder\\file.txt', 'C:\\Users\\User\\Desktop\\New Folder\\New Folder\\new_file.txt')
```

Output:
```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python os_rename.py
```

In the above example, we import the os module and use the os.rename() method to rename the file named "file.txt" to "new_file.txt" in the "New Folder" directory.

## os.replace() Method
The os.replace() method renames the file or directory at the specified source path to the specified destination path. If the destination path already exists, it will be replaced.

```python title="os_replace.py" showLineNumbers{1} {1,3}
import os

os.replace('C:\\Users\\User\\Desktop\\New Folder\\New Folder\\file.txt', 'C:\\Users\\User\\Desktop\\New Folder\\New Folder\\new_file.txt')
```

Output:
```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python os_replace.py
```

In the above example, we import the os module and use the os.replace() method to rename the file named "file.txt" to "new_file.txt" in the "New Folder" directory. Since the file "new_file.txt" already exists, it will be replaced.

## os.walk() Method
The os.walk() method returns a generator that yields a tuple of three values for each directory in the specified path. The first value is the path of the directory, the second value is a list of the names of the subdirectories in the directory, and the third value is a list of the names of the files in the directory.

```python title="os_walk.py" showLineNumbers{1} {1,3-7}
import os

for root, dirs, files in os.walk('C:\\Users\\User\\Desktop\\New Folder'):
    print(root)
    print(dirs)
    print(files)
```

Output:
```cmd title="command" showLineNumbers{1} {2-14}
C:\Users\username>python os_walk.py
C:\Users\username\Desktop\New Folder
['New Folder']
['file.txt']
C:\Users\username\Desktop\New Folder\New Folder
[]
['new_file.txt']
```

In the above example, we import the os module and use the os.walk() method to get a generator that yields a tuple of three values for each directory in the "New Folder" directory. The first value is the path of the directory, the second value is a list of the names of the subdirectories in the directory, and the third value is a list of the names of the files in the directory.


