---
title: File Handling in Python
description: Learn how to read and write files in Python. how to open, close, read, write, and delete files in Python. how to use the with statement to open files. how to use the os module to delete files.
sidebar: 
    order: 75
---

## Comprehensive Guide to File Handling in Python
File handling is a crucial aspect of programming, allowing you to read from and write to files. Python provides a set of functions and methods that make file handling straightforward. In this comprehensive guide, we will explore various aspects of file handling in Python, covering reading, writing, and manipulating files.

## Opening a File in Python
We can open a file in Python using the `open()` function. This function accepts two arguments, the name of the file and the mode in which we want to open the file. The mode can be read mode, write mode, append mode, etc. The default mode is read mode.

**Syntax:**
```python title="open.py" showLineNumbers{1} {1}
file_object = open(file_name, [access_mode], [buffering])
```

Here,
- `file_name` is the name of the file that we want to access.
- `access_mode` is the mode in which we want to open the file, i.e., read, write, append, etc.
- `buffering` is an optional integer used to set the buffering policy.
- `file_object` is the object that we can use to access the file.

## File Opening Modes
There are different modes in which we can open a file. These modes are:

|S.No.|Mode|Description|
|:---:|:---:|:---|
|1|`r`|Opens a file in read-only mode. The file pointer is placed at the beginning of the file. This is the default mode.|
|2|`rb`|Opens a file in read-only mode in binary format. The file pointer is placed at the beginning of the file. This is the default mode.|
|3|`r+`|Opens a file for both reading and writing. The file pointer placed at the beginning of the file.|
|4|`rb+`|Opens a file for both reading and writing in binary format. The file pointer placed at the beginning of the file.|
|5|`w`|Opens a file for writing only. Overwrites the file if the file exists. If the file does not exist, creates a new file for writing.|
|6|`wb`|Opens a file for writing only in binary format. Overwrites the file if the file exists. If the file does not exist, creates a new file for writing.|
|7|`w+`|Opens a file for both writing and reading. Overwrites the existing file if the file exists. If the file does not exist, creates a new file for reading and writing.|
|8|`wb+`|Opens a file for both writing and reading in binary format. Overwrites the existing file if the file exists. If the file does not exist, creates a new file for reading and writing.|
|9|`a`|Opens a file for appending. The file pointer is at the end of the file if the file exists. That is, the file is in the append mode. If the file does not exist, it creates a new file for writing.|
|10|`ab`|Opens a file for appending in binary format. The file pointer is at the end of the file if the file exists. That is, the file is in the append mode. If the file does not exist, it creates a new file for writing.|
|11|`a+`|Opens a file for both appending and reading. The file pointer is at the end of the file if the file exists. The file opens in the append mode. If the file does not exist, it creates a new file for reading and writing.|
|12|`ab+`|Opens a file for both appending and reading in binary format. The file pointer is at the end of the file if the file exists. The file opens in the append mode. If the file does not exist, it creates a new file for reading and writing.|
|13|`x`|Opens a file for exclusive creation. If the file already exists, the operation fails.|
|14|`xb`|Opens a file for exclusive creation in binary format. If the file already exists, the operation fails.|
|15|`x+`|Opens a file for exclusive creation. If the file already exists, the operation fails.|
|16|`xb+`|Opens a file for exclusive creation in binary format. If the file already exists, the operation fails.|
|17|`t`|Opens in text mode. (default)|
|18|`b`|Opens in binary mode.|
|19|`+`|Opens a file for updating (reading and writing)|
|20|`U`|Universal newline mode.|

## Closing a File in Python
When we are done with operations to be performed on the file, we need to properly close the file. Closing a file will free up the resources that were tied with the file and is done using the `close()` method. Python has a garbage collector to clean up unreferenced objects but we must not rely on it to close the file.

**Syntax:**
```python title="close.py" showLineNumbers{1} {1}
file_object.close()
```

## Reading a File in Python
There are various methods available for this purpose. We can use the `read(size)` method to read in the size number of data. If the size parameter is not specified, it reads and returns up to the end of the file.

**Syntax:**
```python title="read.py" showLineNumbers{1} {1}
file_object.read([size])
```

Here,
- `file_object` is the file object that we want to read.
- `size` is an optional numeric argument. When it is provided, it reads that many characters from the file. If the size parameter is not specified, it reads and returns up to the end of the file.
- The `read()` method returns the specified number of bytes from the file. If we omit the size argument, it returns and displays all the data from the file.

**Example:**
```python title="read.py" showLineNumbers{1} {1-4}
file_object = open("test.txt", "r")
data = file_object.read()
print(data)
file_object.close()
```

Output:
```cmd title="command" showLineNumbers{1} {2-6}
C:\Users\username>python read.py
Hello, World!
This is a test file.
```

## Conclusion
Understanding file handling in Python is essential for a wide range of applications. Whether you're reading data from a file, writing to it, or manipulating its content, Python's file handling capabilities offer flexibility and ease of use. By following the principles outlined in this guide, you can efficiently work with files in Python, enabling you to build robust and scalable applications. Happy coding! For more tutorials, visit our Python Central Hub.