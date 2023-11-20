---
title: Python String Concatenation
description: Learn how to concatenate strings in Python. We have also learned how to concatenate strings of different data types in Python. Now you can solve problems that require string concatenation in Python.
sidebar: 
    order: 19
---

In Python, we can concatenate strings using the `+` operator. The `+` operator allows us to add two or more strings together. Let's look at some examples.

```python title="strings.py" showLineNumbers{1} {5}
# define strings
string1 = "Hello"
string2 = "World"
# concatenate strings
string3 = string1 + string2
print(string3)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python strings.py
HelloWorld
```

In the above example, we have concatenated two strings using the `+` operator. The `+` operator concatenates the second string to the end of the first string.

## Adding a Space

We can add a space between two strings by adding an empty string (`""` or `''`) to the first string. Let's look at an example.

```python title="strings.py" showLineNumbers{1} {5}
# define strings
string1 = "Hello"
string2 = "World"
# concatenate strings
string3 = string1 + " " + string2
print(string3)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python strings.py
Hello World
```

In the above example, we have concatenated two strings with a space in between. We have added an empty string (`""`) with a space in between to the first string.

## Concatenate Strings of Different Data Types

We can concatenate strings of different data types in Python. But we need to convert the non-string data types to strings before concatenating them. We can use the `str()` function to convert non-string data types to strings. Let's look at an example.

```python title="strings.py" showLineNumbers{1} {5}
# define strings
string1 = "Hello"
number = 5
# concatenate strings
string2 = string1 + str(number)
print(string2)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python strings.py
Hello5
```

In the above example, we have concatenated a string and an integer. We have converted the integer to a string using the `str()` function before concatenating it with the string.

## Concatenate Strings Using join()

We can also concatenate strings using the `join()` method. The `join()` method takes an iterable as an argument and concatenates the elements of the iterable to the string. Let's look at an example.

```python title="strings.py" showLineNumbers{1} {5}
# define strings
string1 = "Hello"
string2 = "World"
# concatenate strings
string3 = "".join([string1, string2])
print(string3)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python strings.py
HelloWorld
```

In the above example, we have concatenated two strings using the `join()` method. We have passed a list of strings to the `join()` method. The `join()` method has concatenated the strings in the list and returned the concatenated string.

## Concatenate Strings Using f-strings

We can also concatenate strings using f-strings. f-strings are string literals that have an `f` at the beginning and curly braces (`{}`) containing expressions that will be replaced with their values. Let's look at an example.

```python title="strings.py" showLineNumbers{1} {5}
# define strings
string1 = "Hello"
string2 = "World"
# concatenate strings
string3 = f"{string1} {string2}"
print(string3)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python strings.py
Hello World
```

In the above example, we have concatenated two strings using f-strings. We have used curly braces (`{}`) to insert the values of the variables into the string.

:::note

f-strings are faster than other string concatenation methods. So, it is recommended to use f-strings for string concatenation. f-string is the most preferred way of string concatenation in Python. We can use f-strings to concatenate strings of different data types as well. Let's look at an example. f-string uses `f{expression}` to insert the value of an expression into a string. We use f-string to print and insert variables into a string. Let's look at an example.

```python title="strings.py" showLineNumbers{1} {5}
# define strings
string1 = "Hello"
number = 5
# concatenate strings
string2 = f"{string1} {number}" # variables are also expressions
print(string2)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python strings.py
Hello 5
```

In the above example, we have concatenated a string and an integer using f-strings. We have inserted the value of the variable `string1` and `number` into the string using f-strings.
:::

:::tip
f-strings are available in Python 3.6 and above. If you are using an older version of Python, you can use the `format()` method to concatenate strings. Let's look at an example.

```python title="strings.py" showLineNumbers{1} {5}
# define strings
string1 = "Hello"
string2 = "World"
# concatenate strings
string3 = "{} {}".format(string1, string2)
print(string3)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python strings.py
Hello World
```

In the above example, we have concatenated two strings using the `format()` method. We have used curly braces (`{}`) to insert the values of the variables into the string.
:::

## Concatenate Strings Using % Operator

We can also concatenate strings using the `%` operator. The `%` operator is also known as the string formatting operator. Let's look at an example.

```python title="strings.py" showLineNumbers{1} {5}
# define strings
string1 = "Hello"
string2 = "World"
# concatenate strings
string3 = "%s %s" % (string1, string2)
print(string3)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python strings.py
Hello World
```

In the above example, we have concatenated two strings using the `%` operator. We have used `%s` to insert the values of the variables into the string.

:::tip
The `%` operator is available in Python 2 and Python 3. But it is recommended to use f-strings for string concatenation in Python 3.6 and above.
:::

## Concatenate Strings Using String Slicing

We can also concatenate strings using string slicing. Let's look at an example.

```python title="strings.py" showLineNumbers{1} {5}
# define strings
string1 = "Hello"
string2 = "World"
# concatenate strings
string3 = string1[:2] + string2[2:]
print(string3)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python strings.py
HeloWorld
```

## String Concatenation in a Loop

We can also concatenate strings in a loop. Let's look at an example.

```python title="strings.py" showLineNumbers{1} {5-7}
# define strings
string1 = "Hello"
string2 = "World"
# concatenate strings
string3 = ""
for i in range(5):
    string3 += string1 + string2
print(string3)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python strings.py
HelloWorldHelloWorldHelloWorldHelloWorldHelloWorld
```

In the above example, we have concatenated two strings in a loop. We have used the `+=` operator to concatenate the strings in the loop.

## Multiline String Concatenation

We can also concatenate multiline strings in Python. Let's look at an example.

```python title="strings.py" showLineNumbers{1} {7}
# define strings
string1 = """Hello
World"""
string2 = """Hello
World"""
# concatenate strings
string3 = string1 + string2
print(string3)
```

Output:

```cmd title="command" showLineNumbers{1} {2-4}
C:\Users\Your Name> python strings.py
Hello
WorldHello
World
```

## Multiple String Concatenation

We can also concatenate multiple strings in Python. Let's look at an example.

```python title="strings.py" showLineNumbers{1} {5}
# define strings
string1 = "Hello"
string2 = "World"
# concatenate strings
string3 = string1 * 3 + string2 * 2
print(string3)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python strings.py
HelloHelloHelloWorldWorld
```

In the above example, we have concatenated multiple strings. We have used the `*` operator to concatenate the strings.

## Conclusion

In this tutorial, we have learned how to concatenate strings in Python. We have also learned how to concatenate strings of different data types in Python. Now you can solve problems that require string concatenation in Python. 🎉