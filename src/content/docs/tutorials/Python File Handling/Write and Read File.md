---
title: Write and Read File
description: Learn how to write and read files in Python. how to open, close, read, write, and delete files in Python. how to use the with statement to open files. how to use the os module to delete files. how to use the os module to delete files.
sidebar: 
    order: 76
---

## Writing Files in Python
Writing files in Python is a fundamental skill that allows you to store and manipulate data. Whether you're creating new files, appending content to existing ones, or writing binary data, Python provides versatile methods for file writing. In this comprehensive guide, we'll explore various aspects of writing files in Python.

## Opening a File in Write Mode
We can open a file in write mode using the `open()` function. This function accepts two arguments, the name of the file and the mode in which we want to open the file. The mode can be read mode, write mode, append mode, etc. The default mode is read mode.

**Syntax:**
```python title="open.py" showLineNumbers{1} {1}
file_object = open(file_name, [access_mode], [buffering])
```

Here,
- `file_name` is the name of the file that we want to access.
- `access_mode` is the mode in which we want to open the file, i.e., read, write, append, etc.
- `buffering` is an optional integer used to set the buffering policy.
- `file_object` is the object that we can use to access the file.

## File Opening Write Modes
There are different modes in which we can open a file. These modes are:

|S.No.|Mode|Description|
|:---:|:---:|:---|
|1|`w`|Opens a file for writing only. Overwrites the file if the file exists. If the file does not exist, creates a new file for writing.|
|2|`wb`|Opens a file for writing only in binary format. Overwrites the file if the file exists. If the file does not exist, creates a new file for writing.|
|3|`w+`|Opens a file for both writing and reading. Overwrites the existing file if the file exists. If the file does not exist, creates a new file for reading and writing.|
|4|`wb+`|Opens a file for both writing and reading in binary format. Overwrites the existing file if the file exists. If the file does not exist, creates a new file for reading and writing.|
|5|`a`|Opens a file for appending. The file pointer is at the end of the file if the file exists. That is, the file is in the append mode. If the file does not exist, it creates a new file for writing.|
|6|`ab`|Opens a file for appending in binary format. The file pointer is at the end of the file if the file exists. That is, the file is in the append mode. If the file does not exist, it creates a new file for writing.|
|7|`a+`|Opens a file for both appending and reading. The file pointer is at the end of the file if the file exists. The file opens in the append mode. If the file does not exist, it creates a new file for reading and writing.|
|8|`ab+`|Opens a file for both appending and reading in binary format. The file pointer is at the end of the file if the file exists. The file opens in the append mode. If the file does not exist, it creates a new file for reading and writing.|

## Writing to a File in Python
We can write to a file in Python using the `write()` method. This method writes a string to the file. The string can be a string literal or a variable that contains a string.

**Syntax:**
```python title="write.py" showLineNumbers{1} {1}
file_object.write(string)
```

Here, `string` is the string data that we want to write to the file.

**Example: Writing to a File**
```python title="write.py" showLineNumbers{1} {2,5,8}
# Open a file in write mode
file_object = open("file.txt", "w")

# Write to the file
file_object.write("Hello World")

# Close the file
file_object.close()
```

Output:

```cmd title="command" showLineNumbers{1} {1}
C:\Users\username>python write.py
```

```txt title="file.txt" showLineNumbers{1} {1}
Hello World
```

In the above example, we open a file in write mode using the `open()` function. Then, we write the string `"Hello World"` to the file using the `write()` method. Finally, we close the file using the `close()` method.

## Writing Multiple Lines to a File
We can write multiple lines to a file using the `write()` method. To do so, we need to add a newline character (`\n`) at the end of each line.

**Example: Writing Multiple Lines to a File**
```python title="write.py" showLineNumbers{1} {2,5,8,11}
# Open a file in write mode
file_object = open("file.txt", "w")

# Write to the file
file_object.write("Hello World\n")

# Write another line to the file
file_object.write("This is a test file\n")

# Close the file
file_object.close()
```

Output:

```cmd title="command" showLineNumbers{1} {1}
C:\Users\username>python write.py
```

```txt title="file.txt" showLineNumbers{1} {1}
Hello World
This is a test file
```

In the above example, we write two lines to the file. We add a newline character (`\n`) at the end of each line to write the lines to the file.

## Writing a List to a File
We can write a list to a file using the `write()` method. To do so, we need to convert the list to a string using the `str()` function.

**Example: Writing a List to a File**
```python title="write.py" showLineNumbers{1} {2,5,8,11}
# Open a file in write mode
file_object = open("file.txt", "w")

# Create a list
my_list = ["Hello", "World", "This", "is", "a", "test", "file"]

# Write to the file
file_object.write(str(my_list))

# Close the file
file_object.close()
```

Output:

```cmd title="command" showLineNumbers{1} {1}
C:\Users\username>python write.py
```

```txt title="file.txt" showLineNumbers{1} {1}
['Hello', 'World', 'This', 'is', 'a', 'test', 'file']
```

In the above example, we create a list and write it to the file. We convert the list to a string using the `str()` function before writing it to the file.

:::note
We can also use the `writelines()` method to write a list to a file. This method writes a sequence of strings to the file. It does not add a newline character (`\n`) at the end of each line.

**Example: Writing a List to a File**
```python title="writelines.py" showLineNumbers{1} {2,5,8,11}
# Open a file in write mode
file_object = open("file.txt", "w")

# Create a list
my_list = ["Hello", "World", "This", "is", "a", "test", "file"]

# Write to the file
file_object.writelines(my_list)

# Close the file
file_object.close()
```

Output:

```cmd title="command" showLineNumbers{1} {1}
C:\Users\username>python writelines.py
```

```txt title="file.txt" showLineNumbers{1} {1}
HelloWorldThisisatestfile
```

In the above example, we create a list and write it to the file using the `writelines()` method. We do not add a newline character (`\n`) at the end of each line.
:::

:::tip
You can try other types of sequences, such as tuples, sets, etc., to write to a file by converting them to a string using the `str()` function.
:::

## Writing to a File Using the with Statement
We can also write to a file using the `with` statement. This statement creates a temporary variable (`file_object` in the example below) that we can use to access the file inside the indented block of the `with` statement. When we exit the `with` statement, the file is automatically closed.

**Example: Writing to a File Using the with Statement**
```python title="with.py" showLineNumbers{1} {2-4}
# Open a file in write mode
with open("file.txt", "w") as file_object:
    # Write to the file
    file_object.write("Hello World")

# The file is automatically closed
```

Output:

```cmd title="command" showLineNumbers{1} {1}
C:\Users\username>python with.py
```

```txt title="file.txt" showLineNumbers{1} {1}
Hello World
```

In the above example, we open a file in write mode using the `with` statement. Then, we write the string `"Hello World"` to the file using the `write()` method. Finally, we exit the `with` statement, and the file is automatically closed.

## Appending to a File in Python
We can append to a file in Python using the `write()` method. This method writes a string to the file. The string can be a string literal or a variable that contains a string. We need to use `a` as the mode while opening the file.

**Syntax:**
```python title="append.py" showLineNumbers{1} {1}
file_object = open(file_name, "a")
file_object.write(string)
```

Here,
- `file_name` is the name of the file that we want to access.
- `string` is the string data that we want to write to the file.
- `file_object` is the object that we can use to access the file.
- `a` is the mode in which we want to open the file, i.e., append mode.

**Example: Appending to a File**
There is a file named `file.txt` with the following content:
```txt title="file.txt" showLineNumbers{1} {1}
Hello World
```

```python title="append.py" showLineNumbers{1} {2,5,8}
# Open a file in append mode
file_object = open("file.txt", "a")

# Write to the file
file_object.write("\nThis is a test file")

# Close the file
file_object.close()
```

Output:

```cmd title="command" showLineNumbers{1} {1}
C:\Users\username>python append.py
```

```txt title="file.txt" showLineNumbers{1} {1-3}
Hello World
This is a test file
```

In the above example, we open a file in append mode using the `open()` function. Then, we write the string `"Hello World"` to the file using the `write()` method. Finally, we close the file using the `close()` method.

## Appending Multiple Lines to a File
We can append multiple lines to a file using the `write()` method. To do so, we need to add a newline character (`\n`) at the end of each line.

**Example: Appending Multiple Lines to a File**
There is a file named `file.txt` with the following content:
```txt title="file.txt" showLineNumbers{1} {1}
This is a head
```

```python title="append.py" showLineNumbers{1} {2,5,8,11}
# Open a file in append mode
file_object = open("file.txt", "a")

# Write to the file
file_object.write("\nHello World\n")

# Write another line to the file
file_object.write("This is a test file\n")

# Close the file
file_object.close()
```

Output:

```cmd title="command" showLineNumbers{1} {1}
C:\Users\username>python append.py
```

```txt title="file.txt" showLineNumbers{1} {1-3}
This is a head
Hello World
This is a test file
```

In the above example, we write two lines to the file. We add a newline character (`\n`) at the end of each line to write the lines to the file.

## Writing in Binary Mode
We can write to a file in binary mode using the `write()` method. This method writes a string to the file. The string can be a string literal or a variable that contains a string. We need to use `wb` as the mode while opening the file.

**Syntax:**
```python title="binary.py" showLineNumbers{1} {1}
file_object = open(file_name, "wb")
file_object.write(string)
```

Here,
- `file_name` is the name of the file that we want to access.
- `string` is the string data that we want to write to the file.
- `file_object` is the object that we can use to access the file.
- `wb` is the mode in which we want to open the file, i.e., binary mode.
- The `write()` method writes a string to the file.

**Example: Writing in Binary Mode**
```python title="binary.py" showLineNumbers{1} {2,5,8}
# Open a file in binary mode
file_object = open("file.txt", "wb")

# Write to the file
file_object.write("Hello World".encode())

# Close the file
file_object.close()
```

Output:

```cmd title="command" showLineNumbers{1} {1}
C:\Users\username>python binary.py
```

```txt title="file.txt" showLineNumbers{1} {1}
Hello World
```

In the above example, we open a file in binary mode using the `open()` function. Then, we write the string `"Hello World"` to the file using the `write()` method. Finally, we close the file using the `close()` method.

## Using w+ Mode to Write to a File
We can use the `w+` mode to write to a file. This mode opens the file for both writing and reading. It overwrites the existing file if the file exists. If the file does not exist, it creates a new file for reading and writing.

### seek() Method
We can use the `seek()` method to move the file pointer to a specific position in the file. This method accepts two arguments, the offset and the position. The position is optional and defaults to `0`.

**Syntax:**
```python title="seek.py" showLineNumbers{1} {1}
file_object.seek(offset, [position])
```

Here,
- `file_object` is the file object that we want to read.
- `offset` is the number of bytes to be moved.
- `position` is the reference position from where the bytes are to be moved. It is optional and defaults to `0`.
- The `seek()` method moves the file pointer to a specific position in the file.
- The `tell()` method returns the current position of the file pointer.
- The `write()` method writes a string to the file.

:::note
`position` can have one of the following values:
- `0` - It is the default value. It sets the reference position to the beginning of the file.
- `1` - It sets the reference position to the current position of the file pointer.
- `2` - It sets the reference position to the end of the file.
:::


**Example: Using seek() Method**
```python title="seek.py" showLineNumbers{1} {2,5,8,11,14-15,18}
# Open a file in write mode
file_object = open("file.txt", "w+")

# Write to the file
file_object.write("Hello World")

# Move the file pointer to the word "World"
file_object.seek(6, 0) # the second argument is optional and defaults to 0. It uses the absolute file positioning.

# Read the file
data = file_object.read(5)

# Print the data
print(data)

# Usage of tell() method
print(file_object.tell())
```

Output:

```cmd title="command" showLineNumbers{1} {1}
C:\Users\username>python seek.py
World
11
```

In the above example, we open a file in write mode using the `open()` function. Then, we write the string `"Hello World"` to the file using the `write()` method. Next, we move the file pointer to the word `"World"` using the `seek()` method. Then, we read the next five characters using the `read()` method. Finally, we print the data and the current position of the file pointer using the `tell()` method.
:::

**Example: Using seek() Method**
```python title="seek.py" showLineNumbers{1} {2,5,8,11,14-15,18}
# Open a file in write mode
file_object = open("file.txt", "w+")

# Write to the file
file_object.write("Hello World")

# Move the file pointer to the word "World"
file_object.seek(6)

# Read the file
data = file_object.read(5)

# Change the word "World" to "Python"
file_object.seek(6)
file_object.write("Python")

# Move the file pointer to the beginning of the file
file_object.seek(0)
```

Output:

```cmd title="command" showLineNumbers{1} {1}
C:\Users\username>python seek.py
```

```txt title="file.txt" showLineNumbers{1} {1}
Hello Python
```

In the above example, we open a file in write mode using the `open()` function. Then, we write the string `"Hello World"` to the file using the `write()` method. Next, we move the file pointer to the word `"World"` using the `seek()` method. Then, we read the next five characters using the `read()` method. Next, we move the file pointer to the word `"World"` using the `seek()` method. Then, we write the string `"Python"` to the file using the `write()` method. Finally, we move the file pointer to the beginning of the file using the `seek()` method.

## Reading Files in Python
Reading files in Python is a fundamental operation that allows you to retrieve and process data stored in files. Whether you're dealing with text files, binary files, or reading line by line, Python provides versatile methods for file reading. In this comprehensive guide, we'll explore various aspects of reading files in Python.

**Syntax:**
```python title="read.py" showLineNumbers{1} {1}
file_object.read([size])
```

Here,
- `file_object` is the file object that we want to read.
- `size` is an optional numeric argument. When it is provided, it reads that many characters from the file. If the size parameter is not specified, it reads and returns up to the end of the file.
- The `read()` method returns the specified number of bytes from the file. If we omit the size argument, it returns and displays all the data from the file.

## Opening a File in Write Mode
We can open a file in write mode using the `open()` function. This function accepts two arguments, the name of the file and the mode in which we want to open the file. The mode can be read mode, write mode, append mode, etc. The default mode is read mode.

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

**Example: Reading a File**
There is a file named `file.txt` with the following content:
```txt title="file.txt" showLineNumbers{1} {1}
Hello World
This is a test file
```

```python title="read.py" showLineNumbers{1} {2,5,8}
# Open a file in read mode
file_object = open("file.txt", "r")

# Read the file
data = file_object.read()

# Close the file
file_object.close()

# Print the data
print(data)
```

Output:

```cmd title="command" showLineNumbers{1} {2-6}
C:\Users\username>python read.py
Hello World
This is a test file
```

In the above example, we open a file in read mode using the `open()` function. Then, we read the file using the `read()` method. Finally, we close the file using the `close()` method.

## Reading a File Line by Line
We can read a file line by line using the `readline()` method. This method reads a string from the file. The string can be a string literal or a variable that contains a string.

**Syntax:**
```python title="readline.py" showLineNumbers{1} {1}
file_object.readline()
```

Here,
- `file_object` is the file object that we want to read.
- The `readline()` method returns the next line from the file.
- The `readlines()` method returns a list of all the lines in the file.

**Example: Reading a File Line by Line**
There is a file named `file.txt` with the following content:
```txt title="file.txt" showLineNumbers{1} {1}
Hello World
This is a test file
```

```python title="readline.py" showLineNumbers{1} {2,5-6,9}
# Open a file in read mode
file_object = open("file.txt", "r")

# Read the file line by line
line1 = file_object.readline()
line2 = file_object.readline()

# Close the file
file_object.close()

# Print the data
print(line1)
print(line2)
```

Output:

```cmd title="command" showLineNumbers{1} {2-6}
C:\Users\username>python readline.py
Hello World
This is a test file
```

In the above example, we open a file in read mode using the `open()` function. Then, we read the file line by line using the `readline()` method. Finally, we close the file using the `close()` method.

**Example: Reading a File Line by Line using readlines() Method**
There is a file named `file.txt` with the following content:
```txt title="file.txt" showLineNumbers{1} {1}
Hello World
This is a test file
```

```python title="readlines.py" showLineNumbers{1} {2,5,8}
# Open a file in read mode
file_object = open("file.txt", "r")

# Read the file line by line
lines = file_object.readlines()

# Close the file
file_object.close()

# Print the data
print(lines)
```

Output:

```cmd title="command" showLineNumbers{1} {2-6}
C:\Users\username>python readlines.py
['Hello World\n', 'This is a test file\n']
```

In the above example, we open a file in read mode using the `open()` function. Then, we read the file line by line using the `readlines()` method. Finally, we close the file using the `close()` method.

## Reading a File Using the with Statement
We can also read a file using the `with` statement. This statement creates a temporary variable (`file_object` in the example below) that we can use to access the file inside the indented block of the `with` statement. When we exit the `with` statement, the file is automatically closed.

**Example: Reading a File Using the with Statement**
There is a file named `file.txt` with the following content:
```txt title="file.txt" showLineNumbers{1} {1}
Hello World
This is a test file
```

```python title="with.py" showLineNumbers{1} {2-5}
# Open a file in read mode
with open("file.txt", "r") as file_object:
    # Read the file
    data = file_object.read()
    print(data)

# The file is automatically closed
```

Output:

```cmd title="command" showLineNumbers{1} {2-6}
C:\Users\username>python with.py
Hello World
This is a test file
```

In the above example, we open a file in read mode using the `with` statement. Then, we read the file using the `read()` method. Finally, we exit the `with` statement, and the file is automatically closed.

## Reading in Binary Mode
We can read a file in binary mode using the `read()` method. This method reads a string from the file. The string can be a string literal or a variable that contains a string. We need to use `rb` as the mode while opening the file.

**Syntax:**
```python title="binary.py" showLineNumbers{1} {1}
file_object = open(file_name, "rb")
file_object.read([size])
```

Here,
- `file_object` is the file object that we want to read.
- `size` is an optional numeric argument. When it is provided, it reads that many characters from the file. If the size parameter is not specified, it reads and returns up to the end of the file.
- The `read()` method returns the specified number of bytes from the file. If we omit the size argument, it returns and displays all the data from the file.
- The `write()` method writes a string to the file.


**Example: Reading in Binary Mode**
There is a file named `file.txt` with the following content:
```txt title="file.txt" showLineNumbers{1} {1}
Hello World
```

```python title="binary.py" showLineNumbers{1} {2,5,8}
# Open a file in binary mode
file_object = open("file.txt", "rb")

# Read the file
data = file_object.read()

# Close the file
file_object.close()

# Print the data
print(data)
```

Output:

```cmd title="command" showLineNumbers{1} {2-6}
C:\Users\username>python binary.py
b'Hello World\n'
```

In the above example, we open a file in binary mode using the `open()` function. Then, we read the file using the `read()` method. Finally, we close the file using the `close()` method.

## Reading in Binary Mode Using the with Statement
We can also read a file in binary mode using the `with` statement. This statement creates a temporary variable (`file_object` in the example below) that we can use to access the file inside the indented block of the `with` statement. When we exit the `with` statement, the file is automatically closed.

**Example: Reading in Binary Mode Using the with Statement**
There is a file named `file.txt` with the following content:
```txt title="file.txt" showLineNumbers{1} {1}
Hello World
```

```python title="with.py" showLineNumbers{1} {2-5}
# Open a file in binary mode
with open("file.txt", "rb") as file_object:
    # Read the file
    data = file_object.read()
    print(data)

# The file is automatically closed
```

Output:

```cmd title="command" showLineNumbers{1} {2-6}
C:\Users\username>python with.py
b'Hello World\n'
```

In the above example, we open a file in binary mode using the `with` statement. Then, we read the file using the `read()` method. Finally, we exit the `with` statement, and the file is automatically closed.

## Reading a File Line by Line Using the with Statement
We can also read a file line by line using the `with` statement. This statement creates a temporary variable (`file_object` in the example below) that we can use to access the file inside the indented block of the `with` statement. When we exit the `with` statement, the file is automatically closed.

**Example: Reading a File Line by Line Using the with Statement**
There is a file named `file.txt` with the following content:
```txt title="file.txt" showLineNumbers{1} {1}
Hello World
This is a test file
```

```python title="with.py" showLineNumbers{1} {2-5}
# Open a file in read mode
with open("file.txt", "r") as file_object:
    # Read the file line by line
    line1 = file_object.readline()
    line2 = file_object.readline()
    print(line1)
    print(line2)

# The file is automatically closed
```

Output:

```cmd title="command" showLineNumbers{1} {2-6}
C:\Users\username>python with.py
Hello World
This is a test file
```

In the above example, we open a file in read mode using the `with` statement. Then, we read the file line by line using the `readline()` method. Finally, we exit the `with` statement, and the file is automatically closed.

## Read Integer from a File
We can read an integer from a file using the `read()` method. In this example, we read an integer from a file using the `read()` method from bytes data.

**Example: Read Integer from a File**
```python title="write.py" showLineNumbers{1} {2,5,8}
# Open a file in write mode
file_object = open("file.txt", "wb")

# Write to the file
file_object.write(123.to_bytes(2, byteorder="big"))

# Close the file
file_object.close()
```

```python title="read.py" showLineNumbers{1} {2,5,8}
# Open a file in read mode
file_object = open("file.txt", "rb")

# Read the file
data = file_object.read()

# Close the file
file_object.close()

# Print the data
print(int.from_bytes(data, byteorder="big"))
```

Output:

```cmd title="command" showLineNumbers{1} {1-6}
C:\Users\username>python write.py
C:\Users\username>python read.py
123
```

In the above example, we open a file in write mode using the `open()` function. Then, we write the integer `123` to the file using the `write()` method. Finally, we close the file using the `close()` method.

## Read Float from a File
We can read a float from a file using the `read()` method. In this example, we read a float from a file using the `read()` method from bytes data.

**Example: Read Float from a File**

```python title="write.py" showLineNumbers{1} {1,4,7,10}
import struct

# Open a file in write mode
file_object = open("file.txt", "wb")

# Write to the file
file_object.write(struct.pack("f", 123.456))

# Close the file
file_object.close()
```

```python title="read.py" showLineNumbers{1} {1,4,7,10}
import struct

# Open a file in read mode
file_object = open("file.txt", "rb")

# Read the file
data = file_object.read()

# Close the file
file_object.close()

# Print the data
print(struct.unpack("f", data)[0])
```

Output:

```cmd title="command" showLineNumbers{1} {1-5}
C:\Users\username>python write.py
C:\Users\username>python read.py
123.456
```

In the above example, we open a file in write mode using the `open()` function. Then, we write the float `123.456` to the file using the `write()` method. Finally, we close the file using the `close()` method.

## Using r+ mode to Read and Write to a File
We can use the `r+` mode to read and write to a file. This mode opens the file for both reading and writing. It overwrites the existing file if the file exists. If the file does not exist, it creates a new file for reading and writing.

### seek() Method
We can use the `seek()` method to move the file pointer to a specific position in the file. This method accepts two arguments, the offset and the position. The position is optional and defaults to `0`.

**Syntax:**
```python title="seek.py" showLineNumbers{1} {1}
file_object.seek(offset, [position])
```

Here,
- `file_object` is the file object that we want to read.
- `offset` is the number of bytes to be moved.
- `position` is the reference position from where the bytes are to be moved. It is optional and defaults to `0`.
- The `seek()` method moves the file pointer to a specific position in the file.

**Example: Using seek() Method**
There is a file named `file.txt` with the following content:
```txt title="file.txt" showLineNumbers{1} {1}
Hello World
This is a test file
```

```python title="seek.py" showLineNumbers{1} {2,5,8,11,14-15,18}
# Open a file in write mode
file_object = open("file.txt", "r+")

# Move the file pointer to the word "World"
file_object.seek(6)

# Read the file
data = file_object.read(5)

# Print the data
print(data)

# Close the file
file_object.close()
```

Output:

```cmd title="command" showLineNumbers{1} {1}
C:\Users\username>python seek.py
World
```

In the above example, we open a file in write mode using the `open()` function. Then, we move the file pointer to the word `"World"` using the `seek()` method. Then, we read the next five characters using the `read()` method. Finally, we print the data.

Another example of using the `seek()` method is to move the file pointer to different positions in the file.

**Example: Using seek() Method**
There is a file named `file.txt` with the following content:
```txt title="file.txt" showLineNumbers{1} {1}
My Name is Ravi Kishan
I am a Software Engineer
I love to code
```

```python title="seek.py" showLineNumbers{1} {2,5,8,11,14,17,20,23,26,29}
# Open a file in write mode
file_object = open("file.txt", "r+")

# Move the file pointer to get the name "Ravi Kishan"
file_object.seek(11)

# Read the file
data = file_object.read(11)

# Print the data
print(data)

# Move the file pointer to get the name "Software Engineer"
file_object.seek(34)

# Read the file
data = file_object.read(18)

# Print the data
print(data)

# Move the file pointer to get the name "code"
file_object.seek(55)

# Read the file
data = file_object.read(4)

# Print the data
print(data)

# Close the file
file_object.close()
```

Output:

```cmd title="command" showLineNumbers{1} {1}
C:\Users\username>python seek.py
Ravi Kishan
Software Engineer
code
```

In the above example, we open a file in write mode using the `open()` function. Then, we move the file pointer to get the name `"Ravi Kishan"` using the `seek()` method. Then, we read the next eleven characters using the `read()` method. Finally, we print the data. Next, we move the file pointer to get the name `"Software Engineer"` using the `seek()` method. Then, we read the next eighteen characters using the `read()` method. Finally, we print the data. Next, we move the file pointer to get the name `"code"` using the `seek()` method. Then, we read the next four characters using the `read()` method. Finally, we print the data.

## Reading and Writing to a File Simultaneously
We can read and write to a file simultaneously using the `r+` mode. This mode opens the file for both reading and writing. It overwrites the existing file if the file exists. If the file does not exist, it creates a new file for reading and writing.

```python title="read_write.py" showLineNumbers{1} {2,5,8,11,14,17,20,23,26,29}
# Open a file in write mode
file_object = open("file.txt", "r+")

# Write to the file
file_object.write("Hello World")

# Move the file pointer to the beginning of the file
file_object.seek(0)

# Read the file
data = file_object.read()

# Print the data
print(data)

# Close the file
file_object.close()
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python read_write.py
Hello World
```

In the above example, we open a file in write mode using the `open()` function. Then, we write the string `"Hello World"` to the file using the `write()` method. Next, we move the file pointer to the beginning of the file using the `seek()` method. Then, we read the file using the `read()` method. Finally, we print the data.

## Reading and Writing to a File Using the with Statement
We can also read and write to a file using the `with` statement. This statement creates a temporary variable (`file_object` in the example below) that we can use to access the file inside the indented block of the `with` statement. When we exit the `with` statement, the file is automatically closed.

**Example: Reading and Writing to a File Using the with Statement**

```python title="with.py" showLineNumbers{1} {2-13}
# Open a file in read mode
with open("file.txt", "r+") as file_object:
    # Write to the file
    file_object.write("Hello World")

    # Move the file pointer to the beginning of the file
    file_object.seek(0)

    # Read the file
    data = file_object.read()

    # Print the data
    print(data)

# The file is automatically closed
```

Output:

```cmd title="command" showLineNumbers{1} {2-6}
C:\Users\username>python with.py
Hello World
```

In the above example, we open a file in read mode using the `with` statement. Then, we write the string `"Hello World"` to the file using the `write()` method. Next, we move the file pointer to the beginning of the file using the `seek()` method. Then, we read the file using the `read()` method. Finally, we print the data. Next, we exit the `with` statement, and the file is automatically closed.

:::tip
You can also use `w+`, `rb+`, and `r+b` modes to read and write to a file. These modes open the file for both reading and writing. They overwrite the existing file if the file exists. If the file does not exist, they create a new file for reading and writing.
:::

## Conclusion
In python, we can read and write to a file using the `open()` function. This function accepts two arguments, the name of the file and the mode in which we want to open the file. The mode can be read mode, write mode, append mode, etc. The default mode is read mode. We can also use the `with` statement to read and write to a file. This statement creates a temporary variable (`file_object` in the example below) that we can use to access the file inside the indented block of the `with` statement. When we exit the `with` statement, the file is automatically closed. For more information, check out the [official documentation](https://docs.python.org/3/tutorial/inputoutput.html#reading-and-writing-files). For more tutorials, check out the Python Central Hub.