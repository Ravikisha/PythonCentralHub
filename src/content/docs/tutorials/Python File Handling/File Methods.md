---
title: File Methods
description: Learn about the different methods that can be used to read and write to files. 
sidebar: 
    order: 78
---

## File  Methods
This tutorial will cover the different methods that can be used to read and write to files.

## Table of Methods
|S.No.|Method|Description|Example|
|---|---|---|---|
|1|open()|Opens a file and returns a file object|`file = open("file.txt", "r")`|
|2|close()|Closes a file|`file.close()`|
|3|read()|Reads the entire file and returns a string|`file.read()`|
|4|readline()|Reads a single line from the file|`file.readline()`|
|5|readlines()|Reads all the lines from the file and returns a list|`file.readlines()`|
|6|write()|Writes a string to the file|`file.write("Hello World")`|
|7|writelines()|Writes a list of strings to the file|`file.writelines(["Hello", "World"])`|
|8|seek()|Changes the current position of the file pointer|`file.seek(0)`|
|9|tell()|Returns the current position of the file pointer|`file.tell()`|
|10|truncate()|Truncates the file to the given size|`file.truncate(10)`|
|11|flush()|Flushes the internal buffer|`file.flush()`|
|12|fileno()|Returns the file descriptor|`file.fileno()`|
|13|isatty()|Returns True if the file is connected to a terminal|`file.isatty()`|

## File Modes
The file modes are used to specify the purpose of opening a file. The following table lists the different file modes available in Python.

|S.No.|Mode|Description|
|---|---|---|
|1|`r`|Opens a file for reading only. The file pointer is placed at the beginning of the file. This is the default mode.|
|2|`rb`|Opens a file for reading only in binary format. The file pointer is placed at the beginning of the file. This is the default mode.|
|3|`r+`|Opens a file for both reading and writing. The file pointer placed at the beginning of the file.|
|4|`rb+`|Opens a file for both reading and writing in binary format. The file pointer placed at the beginning of the file.|
|5|`w`|Opens a file for writing only. Overwrites the file if the file exists. If the file does not exist, creates a new file for writing.|
|6|`wb`|Opens a file for writing only in binary format. Overwrites the file if the file exists. If the file does not exist, creates a new file for writing.|
|7|`w+`|Opens a file for both writing and reading. Overwrites the existing file if the file exists. If the file does not exist, creates a new file for reading and writing.|
|8|`wb+`|Opens a file for both writing and reading in binary format. Overwrites the existing file if the file exists. If the file does not exist, creates a new file for reading and writing.|
|9|`a`|Opens a file for appending. The file pointer is at the end of the file if the file exists. If the file does not exist, it creates a new file for writing.|
|10|`ab`|Opens a file for appending in binary format. The file pointer is at the end of the file if the file exists. If the file does not exist, it creates a new file for writing.|
|11|`a+`|Opens a file for both appending and reading. The file pointer is at the end of the file if the file exists. If the file does not exist, it creates a new file for reading and writing.|
|12|`ab+`|Opens a file for both appending and reading in binary format. The file pointer is at the end of the file if the file exists. If the file does not exist, it creates a new file for reading and writing.|
|13|`x`|Creates a new file. If the file already exists, the operation fails.|
|14|`x+`|Creates a new file. If the file already exists, the operation fails.|
|15|`xb`|Creates a new file in binary format. If the file already exists, the operation fails.|
|16|`xb+`|Creates a new file in binary format. If the file already exists, the operation fails.|
|17|`t`|Opens in text mode. (default)|
|18|`b`|Opens in binary mode.|
|19|`+`|Opens a file for updating (reading and writing)|
|20|`U`|Universal newline mode.|
|21|`rU`|Opens a file for reading in universal newline mode. (deprecated)|
|22|`wU`|Opens a file for writing in universal newline mode. (deprecated)|
|23|`rbU`|Opens a file for reading in universal newline mode. (deprecated)|
|24|`wbU`|Opens a file for writing in universal newline mode. (deprecated)|

## File Object Attributes
The following table lists the different file object attributes available in Python.

|S.No.|Attribute|Description|
|---|---|---|
|1|`closed`|Returns True if the file is closed, False otherwise.|
|2|`encoding`|Returns the encoding of the file.|
|3|`mode`|Returns the mode of the file.|
|4|`name`|Returns the name of the file.|
|5|`newlines`|Returns a tuple of all the line terminators in the file.|
|6|`softspace`|Returns False if space explicitly required with print, True otherwise.|

## open() Method
The open() method opens a file and returns a file object. The following example opens a file named "file.txt" in read mode and prints its content.

```txt title="file.txt" showLineNumbers{1} {1}
Hello World
```

```python title="open.py" showLineNumbers{1} {1, 3-4}
file = open("file.txt", "r")

print(file.read())
```

Output:
```cmd title="command" showLineNumbers{1} {2-6}
C:\Users\username>python open.py
Hello World
```

In the above example, we open a file named "file.txt" in read mode. The file object is stored in the variable file. The read() method reads the entire content of the file and returns it as a string.

## close() Method
The close() method closes a file. A closed file cannot be read or written any more. Any operation, which requires that the file be opened will raise a ValueError after the file has been closed. Calling close() more than once is allowed.

```txt title="file.txt" showLineNumbers{1} {1}
Hello World
```

```python title="close.py" showLineNumbers{1} {1, 3-4}
file = open("file.txt", "r")

print(file.read())
file.close()
```

Output:
```cmd title="command" showLineNumbers{1} {2-6}
C:\Users\username>python close.py
Hello World
```

In the above example, we open a file named "file.txt" in read mode. The file object is stored in the variable file. The read() method reads the entire content of the file and returns it as a string. The close() method closes the file.

## read() Method
The read() method reads the entire content of the file and returns it as a string. The following example opens a file named "file.txt" in read mode and prints its content.

```txt title="file.txt" showLineNumbers{1} {1}
Hello World
```

```python title="read.py" showLineNumbers{1} {1, 3-4}
file = open("file.txt", "r")

print(file.read())
```

Output:
```cmd title="command" showLineNumbers{1} {2-6}
C:\Users\username>python read.py
Hello World
```

In the above example, we open a file named "file.txt" in read mode. The file object is stored in the variable file. The read() method reads the entire content of the file and returns it as a string.

## readline() Method
The readline() method reads a single line from the file. The following example opens a file named "file.txt" in read mode and prints its first line.

```txt title="file.txt" showLineNumbers{1} {1}
Hello World
```

```python title="readline.py" showLineNumbers{1} {1, 3-4}
file = open("file.txt", "r")

print(file.readline())
```

Output:
```cmd title="command" showLineNumbers{1} {2-6}
C:\Users\username>python readline.py
Hello World
```

In the above example, we open a file named "file.txt" in read mode. The file object is stored in the variable file. The readline() method reads the first line of the file and returns it as a string.

## readlines() Method
The readlines() method reads all the lines from the file and returns a list. The following example opens a file named "file.txt" in read mode and prints all its lines.

```txt title="file.txt" showLineNumbers{1} {1}
Hello World
Hii World
```

```python title="readlines.py" showLineNumbers{1} {1, 3-4}
file = open("file.txt", "r")

print(file.readlines())
```

Output:
```cmd title="command" showLineNumbers{1} {2-6}
C:\Users\username>python readlines.py
['Hello World\n', 'Hii World']
```

In the above example, we open a file named "file.txt" in read mode. The file object is stored in the variable file. The readlines() method reads all the lines from the file and returns a list.

## write() Method
The write() method writes a string to the file. The following example opens a file named "file.txt" in write mode and writes a string to it.

```python title="write.py" showLineNumbers{1} {1, 3-4}
file = open("file.txt", "w")

file.write("Hello World")
```

Output:
```cmd title="command" showLineNumbers{1} {2-6}
C:\Users\username>python write.py
```

```txt title="file.txt" showLineNumbers{1} {1}
Hello World
```

In the above example, we open a file named "file.txt" in write mode. The file object is stored in the variable file. The write() method writes a string to the file.

## writelines() Method
The writelines() method writes a list of strings to the file. The following example opens a file named "file.txt" in write mode and writes a list of strings to it.

```python title="writelines.py" showLineNumbers{1} {1, 3-4}
file = open("file.txt", "w")

file.writelines(["Hello", "World"])
```

Output:
```cmd title="command" showLineNumbers{1} {2-6}
C:\Users\username>python writelines.py
```

```txt title="file.txt" showLineNumbers{1} {1}
HelloWorld
```

In the above example, we open a file named "file.txt" in write mode. The file object is stored in the variable file. The writelines() method writes a list of strings to the file.

## seek() Method
The seek() method changes the current position of the file pointer. The following example opens a file named "file.txt" in read mode and changes the current position of the file pointer.

```txt title="file.txt" showLineNumbers{1} {1}
Hello World
```

```python title="seek.py" showLineNumbers{1} {1, 3-4}
file = open("file.txt", "r")

file.seek(6)
print(file.read())
```

Output:
```cmd title="command" showLineNumbers{1} {2-6}
C:\Users\username>python seek.py
World
```

In the above example, we open a file named "file.txt" in read mode. The file object is stored in the variable file. The seek() method changes the current position of the file pointer to 6. The read() method reads the content of the file from the current position of the file pointer.

## tell() Method
The tell() method returns the current position of the file pointer. The following example opens a file named "file.txt" in read mode and prints the current position of the file pointer.

```txt title="file.txt" showLineNumbers{1} {1}
Hello World
```

```python title="tell.py" showLineNumbers{1} {1, 3-4}
file = open("file.txt", "r")

file.seek(6)
print(file.tell())
```

Output:
```cmd title="command" showLineNumbers{1} {2-6}
C:\Users\username>python tell.py
6
```

In the above example, we open a file named "file.txt" in read mode. The file object is stored in the variable file. The seek() method changes the current position of the file pointer to 6. The tell() method returns the current position of the file pointer.

## truncate() Method
The truncate() method truncates the file to the given size. The following example opens a file named "file.txt" in read mode and truncates it to 10 bytes.

```txt title="file.txt" showLineNumbers{1} {1}
Hello World
```

```python title="truncate.py" showLineNumbers{1} {1, 3-4}
file = open("file.txt", "r+")

file.truncate(10)
print(file.read())
```

Output:
```cmd title="command" showLineNumbers{1} {2-6}
C:\Users\username>python truncate.py
Hello Wor
```

In the above example, we open a file named "file.txt" in read mode. The file object is stored in the variable file. The truncate() method truncates the file to 10 bytes. The read() method reads the content of the file.

## flush() Method
The flush() method flushes the internal buffer. The following example opens a file named "file.txt" in write mode and flushes the internal buffer.

```python title="flush.py" showLineNumbers{1} {1, 3-4}
file = open("file.txt", "w")

file.write("Hello World")
file.flush()
```

Output:
```cmd title="command" showLineNumbers{1} {2-6}
C:\Users\username>python flush.py
```

```txt title="file.txt" showLineNumbers{1} {1}
Hello World
```

In the above example, we open a file named "file.txt" in write mode. The file object is stored in the variable file. The write() method writes a string to the file. The flush() method flushes the internal buffer.

## fileno() Method
The fileno() method returns the file descriptor. The following example opens a file named "file.txt" in read mode and prints its file descriptor.

```txt title="file.txt" showLineNumbers{1} {1}
Hello World
```

```python title="fileno.py" showLineNumbers{1} {1, 3-4}
file = open("file.txt", "r")

print(file.fileno())
```

Output:
```cmd title="command" showLineNumbers{1} {2-6}
C:\Users\username>python fileno.py
3
```

In the above example, we open a file named "file.txt" in read mode. The file object is stored in the variable file. The fileno() method returns the file descriptor.

## isatty() Method
The isatty() method returns True if the file is connected to a terminal, False otherwise. The following example opens a file named "file.txt" in read mode and prints True if the file is connected to a terminal, False otherwise.

```txt title="file.txt" showLineNumbers{1} {1}
Hello World
```

```python title="isatty.py" showLineNumbers{1} {1, 3-4}
file = open("file.txt", "r")

print(file.isatty())
```

Output:
```cmd title="command" showLineNumbers{1} {2-6}
C:\Users\username>python isatty.py
False
```

In the above example, we open a file named "file.txt" in read mode. The file object is stored in the variable file. The isatty() method returns False because the file is not connected to a terminal.

## closed Attribute
The closed attribute returns True if the file is closed, False otherwise. The following example opens a file named "file.txt" in read mode and prints True if the file is closed, False otherwise.

```txt title="file.txt" showLineNumbers{1} {1}
Hello World
```

```python title="closed.py" showLineNumbers{1} {1, 3-5}
file = open("file.txt", "r")

print(file.closed)
file.close()
print(file.closed)
```

Output:
```cmd title="command" showLineNumbers{1} {2-6}
C:\Users\username>python closed.py
False
True
```

In the above example, we open a file named "file.txt" in read mode. The file object is stored in the variable file. The closed attribute returns False because the file is not closed. The close() method closes the file. The closed attribute returns True because the file is closed.

## encoding Attribute
The encoding attribute returns the encoding of the file. The following example opens a file named "file.txt" in read mode and prints its encoding.

```txt title="file.txt" showLineNumbers{1} {1}
Hello World
```

```python title="encoding.py" showLineNumbers{1} {1, 3-4}
file = open("file.txt", "r")

print(file.encoding)
```

Output:
```cmd title="command" showLineNumbers{1} {2-6}
C:\Users\username>python encoding.py
cp1252
```

In the above example, we open a file named "file.txt" in read mode. The file object is stored in the variable file. The encoding attribute returns the encoding of the file.

## mode Attribute
The mode attribute returns the mode of the file. The following example opens a file named "file.txt" in read mode and prints its mode.

```txt title="file.txt" showLineNumbers{1} {1}
Hello World
```

```python title="mode.py" showLineNumbers{1} {1, 3-4}
file = open("file.txt", "r")

print(file.mode)
```

Output:
```cmd title="command" showLineNumbers{1} {2-6}
C:\Users\username>python mode.py
r
```

In the above example, we open a file named "file.txt" in read mode. The file object is stored in the variable file. The mode attribute returns the mode of the file.

## name Attribute
The name attribute returns the name of the file. The following example opens a file named "file.txt" in read mode and prints its name.

```txt title="file.txt" showLineNumbers{1} {1}
Hello World
```

```python title="name.py" showLineNumbers{1} {1, 3-4}
file = open("file.txt", "r")

print(file.name)
```

Output:
```cmd title="command" showLineNumbers{1} {2-6}
C:\Users\username>python name.py
file.txt
```

In the above example, we open a file named "file.txt" in read mode. The file object is stored in the variable file. The name attribute returns the name of the file.

## newlines Attribute
The newlines attribute returns a tuple of all the line terminators in the file. The following example opens a file named "file.txt" in read mode and prints its line terminators.

```txt title="file.txt" showLineNumbers{1} {1}
Hello World
Hii World
```

```python title="newlines.py" showLineNumbers{1} {1, 3-4}
file = open("file.txt", "r")

print(file.newlines)
```

Output:
```cmd title="command" showLineNumbers{1} {2-6}
C:\Users\username>python newlines.py
('\r\n', '\r\n')
```

In the above example, we open a file named "file.txt" in read mode. The file object is stored in the variable file. The newlines attribute returns a tuple of all the line terminators in the file.

## softspace Attribute
The softspace attribute returns False if space explicitly required with print, True otherwise. The following example opens a file named "file.txt" in read mode and prints False if space explicitly required with print, True otherwise.

```txt title="file.txt" showLineNumbers{1} {1}
Hello World
```

```python title="softspace.py" showLineNumbers{1} {1, 3-4}
file = open("file.txt", "r")

print(file.softspace)
print("Hello World")
print(file.softspace)
```

Output:
```cmd title="command" showLineNumbers{1} {2-6}
C:\Users\username>python softspace.py
False
Hello World
True
```

In the above example, we open a file named "file.txt" in read mode. The file object is stored in the variable file. The softspace attribute returns False because space explicitly required with print. The print() function prints "Hello World". The softspace attribute returns True because space is not explicitly required with print.

## Conclusion
In this tutorial, you learned about the different methods that can be used to read and write to files. In the next tutorial, you will learn about the different file attributes that can be used to get information about a file. For more information on the file methods, refer to the [official documentation](https://docs.python.org/3/library/io.html#io.IOBase). For more tutorials, visit our Python Central Hub.