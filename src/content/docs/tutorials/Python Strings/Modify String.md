---
title: Python Modify Strings
description: Learn how to modify strings in Python. Strings are immutable in Python. This means that once a string is created, we cannot change it. We can only create a new string.
sidebar: 
    order: 17
---

In the python, strings are immutable. This means that once a string is created, we cannot change it. We can only create a new string.
But we can modify the existing string by reassigning a variable to another string. The new string can be a substring of the original string or a concatenation of two or more strings. Let's look at some examples.

#### Example 1: Modify a String

```python title="strings.py" showLineNumbers{1} {3}
# define a string
string = "Hello World"
string = string[:6] + "Python"
print(string)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python strings.py
Hello Python
```

In the above example, we have modified the string by assigning a new string to the variable `string`. The new string is a concatenation of the first six characters of the original string and the string `"Python"`.

## Convert String to List

In Python, a string can't be updated but we can convert a string to a list and modify the list. After making the required changes, we can convert the list back to a string. We can use the `list()` function to convert a string to a list, and the `str()` function to convert a list back to a string.


```python title="strings.py" showLineNumbers{1} {4,6,8}
# define a string
string = "Hello World"
# convert the string to a list
string = list(string)
# change the 7th character of the list
string[6] = 'P'
# convert the list back to a string
string = ''.join(string)
print(string)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python strings.py
Hello Porld
```

In the above example, we have converted the string to a list, changed the 7th character of the list, and converted the list back to a string.

## append() and insert() Methods

We can also use the `append()` and `insert()` methods to modify strings in Python. The `append()` method adds a single character to the end of the string, and the `insert()` method adds a single character at the specified index.


```python title="strings.py" showLineNumbers{1} {4,6,8,10}
# define a string
string = "Hello World"
# convert the string to a list
string = list(string)
# append the letter 'P' to the list
string.append('P')
# insert the letter 'y' at index 6
string.insert(6, 'y')
# convert the list back to a string
string = ''.join(string)
print(string)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python strings.py
Hello PyWorld
```

In the above example, we have converted the string to a list, appended the letter `'P'` to the list, inserted the letter `'y'` at index 6, and converted the list back to a string.

## Delete a String

We can delete a string by using the `del` keyword. The `del` keyword can delete a single character, a range of characters, or an entire string.

```python title="strings.py" showLineNumbers{1} {4, 7, 10}
# define a string
string = "Hello World"
# delete the letter 'H'
del string[0]
print(string)
# delete the letters 'el' from index 1 to index 3
del string[1:4]
print(string)
# delete the entire string
del string
print(string)
```

Output:

```cmd title="command" showLineNumbers{1} {2-7}
C:\Users\Your Name> python strings.py
ello World
eo World
Traceback (most recent call last):
  File "strings.py", line 10, in <module>
    print(string)
NameError: name 'string' is not defined
```