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

## os.path.exists() Method
The os.path.exists() method returns True if the file or directory at the specified path exists, otherwise returns False.

```python title="os_path_exists.py" showLineNumbers{1} {1,3-4}
import os

print(os.path.exists('C:\\Users\\User\\Desktop\\New Folder\\New Folder\\file.txt'))
print(os.path.exists('C:\\Users\\User\\Desktop\\New Folder\\New Folder\\new_file.txt'))
```

Output:
```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python os_path_exists.py
True
False
```

In the above example, we import the os module and use the os.path.exists() method to check if the files "file.txt" and "new_file.txt" exist in the "New Folder" directory.

## os.path.isfile() Method
The os.path.isfile() method returns True if the file at the specified path exists, otherwise returns False.

```python title="os_path_isfile.py" showLineNumbers{1} {1,3-4}
import os

print(os.path.isfile('C:\\Users\\User\\Desktop\\New Folder\\New Folder\\file.txt'))
print(os.path.isfile('C:\\Users\\User\\Desktop\\New Folder\\New Folder\\new_file.txt'))
```

Output:
```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python os_path_isfile.py
True
False
```

In the above example, we import the os module and use the os.path.isfile() method to check if the files "file.txt" and "new_file.txt" exist in the "New Folder" directory.

## os.path.isdir() Method
The os.path.isdir() method returns True if the directory at the specified path exists, otherwise returns False.

```python title="os_path_isdir.py" showLineNumbers{1} {1,3-4}
import os

print(os.path.isdir('C:\\Users\\User\\Desktop\\New Folder\\New Folder'))
print(os.path.isdir('C:\\Users\\User\\Desktop\\New Folder\\New Folder\\New Folder'))
```

Output:
```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python os_path_isdir.py
True
False
```

In the above example, we import the os module and use the os.path.isdir() method to check if the directories "New Folder" and "New Folder" exist in the "New Folder" directory.

## os.path.getsize() Method
The os.path.getsize() method returns the size of the file at the specified path in bytes.

```python title="os_path_getsize.py" showLineNumbers{1} {1,3-4}
import os

print(os.path.getsize('C:\\Users\\User\\Desktop\\New Folder\\New Folder\\file.txt'))
print(os.path.getsize('C:\\Users\\User\\Desktop\\New Folder\\New Folder\\new_file.txt'))
```

Output:
```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python os_path_getsize.py
11
0
```

In the above example, we import the os module and use the os.path.getsize() method to get the size of the files "file.txt" and "new_file.txt" in the "New Folder" directory.

## os.path.getmtime() Method
The os.path.getmtime() method returns the time of the last modification of the file at the specified path.

```python title="os_path_getmtime.py" showLineNumbers{1} {1,3-4}
import os

print(os.path.getmtime('C:\\Users\\User\\Desktop\\New Folder\\New Folder\\file.txt'))
print(os.path.getmtime('C:\\Users\\User\\Desktop\\New Folder\\New Folder\\new_file.txt'))
```

Output:
```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python os_path_getmtime.py
1634178000.0
1634178000.0
```

In the above example, we import the os module and use the os.path.getmtime() method to get the time of the last modification of the files "file.txt" and "new_file.txt" in the "New Folder" directory.

## os.path.getctime() Method
The os.path.getctime() method returns the time of the creation of the file at the specified path.

```python title="os_path_getctime.py" showLineNumbers{1} {1,3-4}
import os

print(os.path.getctime('C:\\Users\\User\\Desktop\\New Folder\\New Folder\\file.txt'))
print(os.path.getctime('C:\\Users\\User\\Desktop\\New Folder\\New Folder\\new_file.txt'))
```

Output:
```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python os_path_getctime.py
1634178000.0
1634178000.0
```

In the above example, we import the os module and use the os.path.getctime() method to get the time of the creation of the files "file.txt" and "new_file.txt" in the "New Folder" directory.

## os.path.getatime() Method
The os.path.getatime() method returns the time of the last access of the file at the specified path.

```python title="os_path_getatime.py" showLineNumbers{1} {1,3-4}
import os

print(os.path.getatime('C:\\Users\\User\\Desktop\\New Folder\\New Folder\\file.txt'))
print(os.path.getatime('C:\\Users\\User\\Desktop\\New Folder\\New Folder\\new_file.txt'))
```

Output:
```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python os_path_getatime.py
1634178000.0
1634178000.0
```

In the above example, we import the os module and use the os.path.getatime() method to get the time of the last access of the files "file.txt" and "new_file.txt" in the "New Folder" directory.

## os.path.abspath() Method
The os.path.abspath() method returns the absolute path of the file or directory at the specified path.

```python title="os_path_abspath.py" showLineNumbers{1} {1,3-4}
import os

print(os.path.abspath('C:\\Users\\User\\Desktop\\New Folder\\New Folder\\file.txt'))
print(os.path.abspath('C:\\Users\\User\\Desktop\\New Folder\\New Folder\\new_file.txt'))
```

Output:
```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python os_path_abspath.py
C:\Users\username\Desktop\New Folder\New Folder\file.txt
C:\Users\username\Desktop\New Folder\New Folder\new_file.txt
```

In the above example, we import the os module and use the os.path.abspath() method to get the absolute path of the files "file.txt" and "new_file.txt" in the "New Folder" directory.

## os.path.dirname() Method
The os.path.dirname() method returns the directory name of the file or directory at the specified path.

```python title="os_path_dirname.py" showLineNumbers{1} {1,3-4}
import os

print(os.path.dirname('C:\\Users\\User\\Desktop\\New Folder\\New Folder\\file.txt'))
print(os.path.dirname('C:\\Users\\User\\Desktop\\New Folder\\New Folder\\new_file.txt'))
```

Output:
```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python os_path_dirname.py
C:\Users\username\Desktop\New Folder\New Folder
C:\Users\username\Desktop\New Folder\New Folder
```

In the above example, we import the os module and use the os.path.dirname() method to get the directory name of the files "file.txt" and "new_file.txt" in the "New Folder" directory.

## os.path.basename() Method
The os.path.basename() method returns the base name of the file or directory at the specified path.

```python title="os_path_basename.py" showLineNumbers{1} {1,3-4}
import os

print(os.path.basename('C:\\Users\\User\\Desktop\\New Folder\\New Folder\\file.txt'))
print(os.path.basename('C:\\Users\\User\\Desktop\\New Folder\\New Folder\\new_file.txt'))
```

Output:
```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python os_path_basename.py
file.txt
new_file.txt
```

In the above example, we import the os module and use the os.path.basename() method to get the base name of the files "file.txt" and "new_file.txt" in the "New Folder" directory.

## os.path.split() Method
The os.path.split() method returns a tuple of two values. The first value is the directory name of the file or directory at the specified path, and the second value is the base name of the file or directory at the specified path.

```python title="os_path_split.py" showLineNumbers{1} {1,3-4}
import os

print(os.path.split('C:\\Users\\User\\Desktop\\New Folder\\New Folder\\file.txt'))
print(os.path.split('C:\\Users\\User\\Desktop\\New Folder\\New Folder\\new_file.txt'))
```

Output:
```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python os_path_split.py
('C:\\Users\\username\\Desktop\\New Folder\\New Folder', 'file.txt')
('C:\\Users\\username\\Desktop\\New Folder\\New Folder', 'new_file.txt')
```

In the above example, we import the os module and use the os.path.split() method to get a tuple of two values. The first value is the directory name of the files "file.txt" and "new_file.txt" in the "New Folder" directory, and the second value is the base name of the files "file.txt" and "new_file.txt" in the "New Folder" directory.

## os.path.join() Method
The os.path.join() method joins the specified paths.

```python title="os_path_join.py" showLineNumbers{1} {1,3-5}
import os

print(os.path.join('C:\\Users\\User\\Desktop\\New Folder', 'New Folder'))
print(os.path.join('C:\\Users\\User\\Desktop\\New Folder', 'New Folder', 'file.txt'))
print(os.path.join('C:\\Users\\User\\Desktop\\New Folder', 'New Folder', 'new_file.txt'))
```

Output:
```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\username>python os_path_join.py
C:\Users\username\Desktop\New Folder\New Folder
C:\Users\username\Desktop\New Folder\New Folder\file.txt
C:\Users\username\Desktop\New Folder\New Folder\new_file.txt
```

In the above example, we import the os module and use the os.path.join() method to join the specified paths.

## os.path.splitext() Method
The os.path.splitext() method splits the specified path into a tuple of two values. The first value is the path without the extension, and the second value is the extension.

```python title="os_path_splitext.py" showLineNumbers{1} {1,3-4}
import os

print(os.path.splitext('C:\\Users\\User\\Desktop\\New Folder\\New Folder\\file.txt'))
print(os.path.splitext('C:\\Users\\User\\Desktop\\New Folder\\New Folder\\new_file.txt'))
```

Output:
```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python os_path_splitext.py
('C:\\Users\\username\\Desktop\\New Folder\\New Folder\\file', '.txt')
('C:\\Users\\username\\Desktop\\New Folder\\New Folder\\new_file', '.txt')
```

In the above example, we import the os module and use the os.path.splitext() method to get a tuple of two values. The first value is the path without the extension of the files "file.txt" and "new_file.txt" in the "New Folder" directory, and the second value is the extension of the files "file.txt" and "new_file.txt" in the "New Folder" directory.

## os.path.normpath() Method
The os.path.normpath() method normalizes the specified path.

```python title="os_path_normpath.py" showLineNumbers{1} {1,3-4}
import os

print(os.path.normpath('C:\\Users\\User\\Desktop\\New Folder\\New Folder\\file.txt'))
print(os.path.normpath('C:\\Users\\User\\Desktop\\New Folder\\New Folder\\new_file.txt'))
```

Output:
```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python os_path_normpath.py
C:\Users\username\Desktop\New Folder\New Folder\file.txt
C:\Users\username\Desktop\New Folder\New Folder\new_file.txt
```

In the above example, we import the os module and use the os.path.normpath() method to normalize the paths of the files "file.txt" and "new_file.txt" in the "New Folder" directory.

## os.path.relpath() Method
The os.path.relpath() method returns the relative path from the current working directory to the specified path.

```python title="os_path_relpath.py" showLineNumbers{1} {1,3-4}
import os

print(os.path.relpath('C:\\Users\\User\\Desktop\\New Folder\\New Folder\\file.txt'))
print(os.path.relpath('C:\\Users\\User\\Desktop\\New Folder\\New Folder\\new_file.txt'))
```

Output:
```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python os_path_relpath.py
..\
..\new_file.txt
```

In the above example, we import the os module and use the os.path.relpath() method to get the relative path from the current working directory to the files "file.txt" and "new_file.txt" in the "New Folder" directory.

## os.path.commonpath() Method
The os.path.commonpath() method returns the common path of the specified paths.

```python title="os_path_commonpath.py" showLineNumbers{1} {1,3-4}
import os

print(os.path.commonpath(['C:\\Users\\User\\Desktop\\New Folder\\New Folder\\file.txt', 'C:\\Users\\User\\Desktop\\New Folder\\New Folder\\new_file.txt']))
print(os.path.commonpath(['C:\\Users\\User\\Desktop\\New Folder\\New Folder\\file.txt', 'C:\\Users\\User\\Desktop\\New Folder\\New Folder\\new_file.txt', 'C:\\Users\\User\\Desktop\\New Folder\\New Folder\\new_file.txt']))
```

Output:
```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python os_path_commonpath.py
C:\Users\username\Desktop\New Folder\New Folder
C:\Users\username\Desktop\New Folder\New Folder
```

In the above example, we import the os module and use the os.path.commonpath() method to get the common path of the specified paths.

## os.path.commonprefix() Method
The os.path.commonprefix() method returns the common prefix of the specified paths.

```python title="os_path_commonprefix.py" showLineNumbers{1} {1,3-4}
import os

print(os.path.commonprefix(['C:\\Users\\User\\Desktop\\New Folder\\New Folder\\file.txt', 'C:\\Users\\User\\Desktop\\New Folder\\New Folder\\new_file.txt']))
print(os.path.commonprefix(['C:\\Users\\User\\Desktop\\New Folder\\New Folder\\file.txt', 'C:\\Users\\User\\Desktop\\New Folder\\New Folder\\new_file.txt', 'C:\\Users\\User\\Desktop\\New Folder\\New Folder\\new_file.txt']))
```

Output:
```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python os_path_commonprefix.py
C:\Users\username\Desktop\New Folder\New Folder\
C:\Users\username\Desktop\New Folder\New Folder\
```

In the above example, we import the os module and use the os.path.commonprefix() method to get the common prefix of the specified paths.

## os.path.expanduser() Method
The os.path.expanduser() method expands the specified path to the user's home directory.

```python title="os_path_expanduser.py" showLineNumbers{1} {1,3-4}
import os

print(os.path.expanduser('~\\Desktop\\New Folder\\New Folder\\file.txt'))
print(os.path.expanduser('~\\Desktop\\New Folder\\New Folder\\new_file.txt'))
```

Output:
```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python os_path_expanduser.py
C:\Users\username\Desktop\New Folder\New Folder\file.txt
C:\Users\username\Desktop\New Folder\New Folder\new_file.txt
```

In the above example, we import the os module and use the os.path.expanduser() method to expand the paths of the files "file.txt" and "new_file.txt" in the "New Folder" directory to the user's home directory.

## os.path.expandvars() Method
The os.path.expandvars() method expands the specified path to the environment variables.

```python title="os_path_expandvars.py" showLineNumbers{1} {1,3-4}
import os

print(os.path.expandvars('%USERPROFILE%\\Desktop\\New Folder\\New Folder\\file.txt'))
print(os.path.expandvars('%USERPROFILE%\\Desktop\\New Folder\\New Folder\\new_file.txt'))
```

Output:
```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python os_path_expandvars.py
C:\Users\username\Desktop\New Folder\New Folder\file.txt
C:\Users\username\Desktop\New Folder\New Folder\new_file.txt
```

In the above example, we import the os module and use the os.path.expandvars() method to expand the paths of the files "file.txt" and "new_file.txt" in the "New Folder" directory to the environment variables.

## os.path.samefile() Method
The os.path.samefile() method returns True if the specified paths refer to the same file, otherwise returns False.

```python title="os_path_samefile.py" showLineNumbers{1} {1,3-4}
import os

print(os.path.samefile('C:\\Users\\User\\Desktop\\New Folder\\New Folder\\file.txt', 'C:\\Users\\User\\Desktop\\New Folder\\New Folder\\new_file.txt'))
print(os.path.samefile('C:\\Users\\User\\Desktop\\New Folder\\New Folder\\file.txt', 'C:\\Users\\User\\Desktop\\New Folder\\New Folder\\file.txt'))
```

Output:
```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python os_path_samefile.py
False
True
```

In the above example, we import the os module and use the os.path.samefile() method to check if the paths of the files "file.txt" and "new_file.txt" in the "New Folder" directory refer to the same file.

## os.path.sameopenfile() Method
The os.path.sameopenfile() method returns True if the specified file objects refer to the same file, otherwise returns False.

```python title="os_path_sameopenfile.py" showLineNumbers{1} {1,3-4}
import os

print(os.path.sameopenfile(open('C:\\Users\\User\\Desktop\\New Folder\\New Folder\\file.txt'), open('C:\\Users\\User\\Desktop\\New Folder\\New Folder\\new_file.txt')))
print(os.path.sameopenfile(open('C:\\Users\\User\\Desktop\\New Folder\\New Folder\\file.txt'), open('C:\\Users\\User\\Desktop\\New Folder\\New Folder\\file.txt')))
```

Output:
```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python os_path_sameopenfile.py
False
True
```

In the above example, we import the os module and use the os.path.sameopenfile() method to check if the file objects of the files "file.txt" and "new_file.txt" in the "New Folder" directory refer to the same file.

## os.path.samestat() Method
The os.path.samestat() method returns True if the specified stat objects refer to the same file, otherwise returns False.

```python title="os_path_samestat.py" showLineNumbers{1} {1,3-4}
import os

print(os.path.samestat(os.stat('C:\\Users\\User\\Desktop\\New Folder\\New Folder\\file.txt'), os.stat('C:\\Users\\User\\Desktop\\New Folder\\New Folder\\new_file.txt')))
print(os.path.samestat(os.stat('C:\\Users\\User\\Desktop\\New Folder\\New Folder\\file.txt'), os.stat('C:\\Users\\User\\Desktop\\New Folder\\New Folder\\file.txt')))
```

Output:
```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python os_path_samestat.py
False
True
```

In the above example, we import the os module and use the os.path.samestat() method to check if the stat objects of the files "file.txt" and "new_file.txt" in the "New Folder" directory refer to the same file.

## os.path.isabs() Method
The os.path.isabs() method returns True if the specified path is an absolute path, otherwise returns False.

```python title="os_path_isabs.py" showLineNumbers{1} {1,3-4}
import os

print(os.path.isabs('C:\\Users\\User\\Desktop\\New Folder\\New Folder\\file.txt'))
print(os.path.isabs('New Folder\\New Folder\\file.txt'))
```

Output:
```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python os_path_isabs.py
True
False
```

In the above example, we import the os module and use the os.path.isabs() method to check if the paths of the files "file.txt" and "new_file.txt" in the "New Folder" directory are absolute paths.

## os.path.ismount() Method
The os.path.ismount() method returns True if the specified path is a mount point, otherwise returns False.

```python title="os_path_ismount.py" showLineNumbers{1} {1,3-10}
import os

print(os.path.ismount('C:\\Users\\User\\Desktop\\New Folder\\New Folder\\file.txt'))
print(os.path.ismount('C:\\Users\\User\\Desktop\\New Folder\\New Folder'))
print(os.path.ismount('C:\\Users\\User\\Desktop\\New Folder'))
print(os.path.ismount('C:\\Users\\User\\Desktop'))
print(os.path.ismount('C:\\Users\\User'))
print(os.path.ismount('C:\\Users'))
print(os.path.ismount('C:\\'))
print(os.path.ismount('C:'))
```

Output:
```cmd title="command" showLineNumbers{1} {2-9}
C:\Users\username>python os_path_ismount.py
False
False
False
False
False
False
True
False
```

In the above example, we import the os module and use the os.path.ismount() method to check if the paths of the files "file.txt" and "new_file.txt" in the "New Folder" directory are mount points.

## os.path Module Constants
The os.path module provides the following constants.

|S.No.|Constant|Description|Example|
|:----|:-------|:----------|:------|
|1|os.path.sep|Returns the path separator.|`os.path.sep`|
|2|os.path.altsep|Returns the alternate path separator.|`os.path.altsep`|
|3|os.path.extsep|Returns the extension separator.|`os.path.extsep`|
|4|os.path.pathsep|Returns the path separator used in PATH environment variables.|`os.path.pathsep`|
|5|os.path.defpath|Returns the default search path for executables.|`os.path.defpath`|
|6|os.path.devnull|Returns the null device.|`os.path.devnull`|
|7|os.path.supports_unicode_filenames|Returns True if the operating system supports Unicode filenames, otherwise returns False.|`os.path.supports_unicode_filenames`|
|8|os.path.curdir|Returns the current directory.|`os.path.curdir`|
|9|os.path.pardir|Returns the parent directory.|`os.path.pardir`|

### os.path.sep Constant
The os.path.sep constant returns the path separator.

```python title="os_path_sep.py" showLineNumbers{1} {1,3}
import os

print(os.path.sep)
```

Output:
```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python os_path_sep.py
\
```

In the above example, we import the os module and use the os.path.sep constant to get the path separator.

### os.path.altsep Constant
The os.path.altsep constant returns the alternate path separator.

```python title="os_path_altsep.py" showLineNumbers{1} {1,3}
import os

print(os.path.altsep)
```

Output:
```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python os_path_altsep.py
/
```

In the above example, we import the os module and use the os.path.altsep constant to get the alternate path separator.

### os.path.extsep Constant
The os.path.extsep constant returns the extension separator.

```python title="os_path_extsep.py" showLineNumbers{1} {1,3}
import os

print(os.path.extsep)
```

Output:
```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python os_path_extsep.py
.
```

In the above example, we import the os module and use the os.path.extsep constant to get the extension separator.

### os.path.pathsep Constant
The os.path.pathsep constant returns the path separator used in PATH environment variables.

```python title="os_path_pathsep.py" showLineNumbers{1} {1,3}
import os

print(os.path.pathsep)
```

Output:
```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python os_path_pathsep.py
;
```

In the above example, we import the os module and use the os.path.pathsep constant to get the path separator used in PATH environment variables.

### os.path.defpath Constant
The os.path.defpath constant returns the default search path for executables.

```python title="os_path_defpath.py" showLineNumbers{1} {1,3}
import os

print(os.path.defpath)
```

Output:
```cmd title="command" showLineNumbers{1} {2-20}
C:\Users\username>python os_path_defpath.py
.;C:\bin
```

In the above example, we import the os module and use the os.path.defpath constant to get the default search path for executables.

### os.path.devnull Constant
The os.path.devnull constant returns the null device.

```python title="os_path_devnull.py" showLineNumbers{1} {1,3}
import os

print(os.path.devnull)
```

Output:
```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python os_path_devnull.py
nul
```

In the above example, we import the os module and use the os.path.devnull constant to get the null device.

### os.path.supports_unicode_filenames Constant
The os.path.supports_unicode_filenames constant returns True if the operating system supports Unicode filenames, otherwise returns False.

```python title="os_path_supports_unicode_filenames.py" showLineNumbers{1} {1,3}
import os

print(os.path.supports_unicode_filenames)
```

Output:
```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python os_path_supports_unicode_filenames.py
True
```

In the above example, we import the os module and use the os.path.supports_unicode_filenames constant to check if the operating system supports Unicode filenames.

### os.path.curdir Constant
The os.path.curdir constant returns the current directory.

```python title="os_path_curdir.py" showLineNumbers{1} {1,3}
import os

print(os.path.curdir)
```

Output:
```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python os_path_curdir.py
.
```

In the above example, we import the os module and use the os.path.curdir constant to get the current directory.

### os.path.pardir Constant
The os.path.pardir constant returns the parent directory.

```python title="os_path_pardir.py" showLineNumbers{1} {1,3}
import os

print(os.path.pardir)
```

Output:
```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python os_path_pardir.py
..
```

In the above example, we import the os module and use the os.path.pardir constant to get the parent directory.

## os Module Constants
The os module provides the following constants.

|S.No.|Constant|Description|Example|
|:----|:-------|:----------|:------|
|1|os.name|Returns the name of the operating system.|`os.name`|
|2|os.curdir|Returns the current directory.|`os.curdir`|
|3|os.pardir|Returns the parent directory.|`os.pardir`|
|4|os.sep|Returns the path separator.|`os.sep`|
|5|os.extsep|Returns the extension separator.|`os.extsep`|
|6|os.altsep|Returns the alternate path separator.|`os.altsep`|
|7|os.pathsep|Returns the path separator used in PATH environment variables.|`os.pathsep`|
|8|os.linesep|Returns the line separator.|`os.linesep`|
|9|os.defpath|Returns the default search path for executables.|`os.defpath`|
|10|os.devnull|Returns the null device.|`os.devnull`|
|11|os.environ|Returns a dictionary of the environment variables.|`os.environ`|
|12|os.supports_bytes_environ|Returns True if the operating system supports environment variables as bytes, otherwise returns False.|`os.supports_bytes_environ`|
|13|os.supports_dir_fd|Returns True if the operating system supports the dir_fd parameter, otherwise returns False.|`os.supports_dir_fd`|
|14|os.supports_effective_ids|Returns True if the operating system supports the effective_ids parameter, otherwise returns False.|`os.supports_effective_ids`|
|15|os.supports_fd|Returns True if the operating system supports the fd parameter, otherwise returns False.|`os.supports_fd`|
|16|os.supports_follow_symlinks|Returns True if the operating system supports the follow_symlinks parameter, otherwise returns False.|`os.supports_follow_symlinks`|

## os.name Constant
The os.name constant returns the name of the operating system.

```python title="os_name.py" showLineNumbers{1} {1,3}
import os

print(os.name)
```

Output:
```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python os_name.py
nt
```

In the above example, we import the os module and use the os.name constant to get the name of the operating system.

## os.curdir Constant
The os.curdir constant returns the current directory.

```python title="os_curdir.py" showLineNumbers{1} {1,3}
import os

print(os.curdir)
```

Output:
```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python os_curdir.py
.
```

In the above example, we import the os module and use the os.curdir constant to get the current directory.

## os.pardir Constant
The os.pardir constant returns the parent directory.

```python title="os_pardir.py" showLineNumbers{1} {1,3}
import os

print(os.pardir)
```

Output:
```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python os_pardir.py
..
```

In the above example, we import the os module and use the os.pardir constant to get the parent directory.

## os.sep Constant
The os.sep constant returns the path separator.

```python title="os_sep.py" showLineNumbers{1} {1,3}
import os

print(os.sep)
```

Output:
```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python os_sep.py
\
```

In the above example, we import the os module and use the os.sep constant to get the path separator.

## os.extsep Constant
The os.extsep constant returns the extension separator.

```python title="os_extsep.py" showLineNumbers{1} {1,3}
import os

print(os.extsep)
```

Output:
```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python os_extsep.py
.
```

In the above example, we import the os module and use the os.extsep constant to get the extension separator.

## os.altsep Constant
The os.altsep constant returns the alternate path separator.

```python title="os_altsep.py" showLineNumbers{1} {1,3}
import os

print(os.altsep)
```

Output:
```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python os_altsep.py
/
```

In the above example, we import the os module and use the os.altsep constant to get the alternate path separator.

## os.pathsep Constant
The os.pathsep constant returns the path separator used in PATH environment variables.

```python title="os_pathsep.py" showLineNumbers{1} {1,3}
import os

print(os.pathsep)
```

Output:
```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python os_pathsep.py
;
```

In the above example, we import the os module and use the os.pathsep constant to get the path separator used in PATH environment variables.

## os.linesep Constant
The os.linesep constant returns the line separator.

```python title="os_linesep.py" showLineNumbers{1} {1,3}
import os

print(os.linesep)
```

Output:
```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python os_linesep.py


```

In the above example, we import the os module and use the os.linesep constant to get the line separator.

## os.defpath Constant
The os.defpath constant returns the default search path for executables.

```python title="os_defpath.py" showLineNumbers{1} {1,3}
import os

print(os.defpath)
```

Output:
```cmd title="command" showLineNumbers{1} {2-20}
C:\Users\username>python os_defpath.py
.;C:\bin
```

In the above example, we import the os module and use the os.defpath constant to get the default search path for executables.

## os.devnull Constant
The os.devnull constant returns the null device.

```python title="os_devnull.py" showLineNumbers{1} {1,3}
import os

print(os.devnull)
```

Output:
```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python os_devnull.py
nul
```

In the above example, we import the os module and use the os.devnull constant to get the null device.

## os.environ Constant
The os.environ constant returns a dictionary of the environment variables.

```python title="os_environ.py" showLineNumbers{1} {1,3}
import os

print(os.environ)
```

Output:
```cmd title="command" showLineNumbers{1} {2-20}
C:\Users\username>python os_environ.py
environ({'ALLUSERSPROFILE': 'C:\\ProgramData', 'APPDATA': 'C:\\Users\\ravi\\AppData\\Roaming', 'CHOCOLATEYINSTALL': 'C:\\ProgramData\\chocolatey', 'CLASS_PATH': 'C:\\mysql-connector-j-8.0.33.jar', 'CLINK_DIR': 'C:\\Program Files (x86)\\clink', 'CLINK_DUMMY_CAPTURE_ENV': ' ', 'COLUMNS': '110', 'COMMONPROGRAMFILES': 'C:\\Program Files\\Common Files', 'COMMONPROGRAMFILES(X86)': 'C:\\Program Files (x86)\\Common Files', 'COMMONPROGRAMW6432': 'C:\\Program Files\\Common Files', 'COMPUTERNAME': 'RAVI', 'COMSPEC': 'C:\\Windows\\system32\\cmd.exe', 'DRIVERDATA': 'C:\\Windows\\System32\\Drivers\\DriverData', 'EFC_24904': '1', 'GOPATH': 'C:\\Users\\ravi\\go', 'HOME': 'C:\\Users\\ravi', 'HOMEDRIVE': 'C:', 'HOMEPATH': '\\Users\\ravi', 'INTELLIJ IDEA COMMUNITY EDITION': 'C:\\Program Files\\JetBrains\\IntelliJ IDEA Community Edition 2023.2.2\\bin;', 'LINES': '25', 'LOCALAPPDATA': 'C:\\Users\\ravi\\AppData\\Local', 'LOGONSERVER': '\\\\RAVI', 'NUMBER_OF_PROCESSORS': '8', 'ONEDRIVE': 'C:\\Users\\ravi\\OneDrive', 'ONEDRIVECONSUMER': 'C:\\Users\\ravi\\OneDrive'})
```

In the above example, we import the os module and use the os.environ constant to get a dictionary of the environment variables.

## os.supports_bytes_environ Constant
The os.supports_bytes_environ constant returns True if the operating system supports environment variables as bytes, otherwise returns False.

```python title="os_supports_bytes_environ.py" showLineNumbers{1} {1,3}
import os

print(os.supports_bytes_environ)
```

Output:
```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python os_supports_bytes_environ.py
True
```

In the above example, we import the os module and use the os.supports_bytes_environ constant to check if the operating system supports environment variables as bytes.

## os.supports_dir_fd Constant
The os.supports_dir_fd constant returns True if the operating system supports the dir_fd parameter, otherwise returns False.

```python title="os_supports_dir_fd.py" showLineNumbers{1} {1,3}
import os

print(os.supports_dir_fd)
```

Output:
```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python os_supports_dir_fd.py
True
```

In the above example, we import the os module and use the os.supports_dir_fd constant to check if the operating system supports the dir_fd parameter.

## os.supports_effective_ids Constant
The os.supports_effective_ids constant returns True if the operating system supports the effective_ids parameter, otherwise returns False.

```python title="os_supports_effective_ids.py" showLineNumbers{1} {1,3}
import os

print(os.supports_effective_ids)
```

Output:
```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python os_supports_effective_ids.py
True
```

In the above example, we import the os module and use the os.supports_effective_ids constant to check if the operating system supports the effective_ids parameter.

## os.supports_fd Constant
The os.supports_fd constant returns True if the operating system supports the fd parameter, otherwise returns False.

```python title="os_supports_fd.py" showLineNumbers{1} {1,3}
import os

print(os.supports_fd)
```

Output:
```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python os_supports_fd.py
True
```

In the above example, we import the os module and use the os.supports_fd constant to check if the operating system supports the fd parameter.

## os.supports_follow_symlinks Constant
The os.supports_follow_symlinks constant returns True if the operating system supports the follow_symlinks parameter, otherwise returns False.

```python title="os_supports_follow_symlinks.py" showLineNumbers{1} {1,3}
import os

print(os.supports_follow_symlinks)
```

Output:
```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python os_supports_follow_symlinks.py
True
```

In the above example, we import the os module and use the os.supports_follow_symlinks constant to check if the operating system supports the follow_symlinks parameter.

## Conclusion
In this tutorial, we have learned about the os module in Python. We have also learned about the os.path module and its methods and constants with examples. Finally, we have learned about the os module and its constants with examples. Now you can use the os module and its methods and constants in your Python program to perform various operating system-related tasks. For more information, visit the [official documentation](https://docs.python.org/3/library/os.html) of the os module. For more tutorials, visit Python Central Hub.