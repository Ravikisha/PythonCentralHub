---
title: Python String Formatting
description: Learn how to format strings in Python. Learn how to use the `%` operator, the `format()` method, and f-strings. Learn how to use placeholders to format strings.
sidebar: 
    order: 18
---
:::danger
In python, we cannot combine strings and numbers like this:

```python title="strings.py" showLineNumbers{1} {3}
# define variables
name = "John"
age = 23
# print string
print(name + " is " + age + " years old.")
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python strings.py
Traceback (most recent call last):
  File "strings.py", line 5, in <module>
    print(name + " is " + age + " years old.")
TypeError: can only concatenate str (not "int") to str
```

The above example will throw an error because we cannot combine strings and numbers like this, using the `+` operator. We can only combine strings with other strings.
:::

String formatting is the process of building a string representation dynamically by inserting the value of numeric expressions in an already existing string. Python's string concatenation operator doesn't accept a non-string operand. Hence, Python offers following string formatting techniques −

- The `%` operator
- The `format()` method
- f-strings
- Template Strings

## The `%` Operator

The `%` operator is also known as the string formatting operator. It accepts a string on the left side and a tuple of values on the right side. The string contains one or more placeholders (`%s`, `%d`, `%f`, `%c`) that are replaced with the values from the tuple. Let's look at an example.

```python title="strings.py" showLineNumbers{1} {5}
# define variables
name = "John"
age = 23
# print string
print("%s is %d years old." % (name, age))
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python strings.py
John is 23 years old.
```

In the above example, we have used `%s` and `%d` placeholders to insert the values of the variables into the string.

Here is a list of placeholders that can be used in the string −
| Sequence | Placeholder | Meaning                                           |
| :------- | :---------- | :------------------------------------------------ |
| 1        | `%c`        | Character                                         |
| 2        | `%s`        | String conversion via `str()` prior to formatting |
| 3        | `%i`        | Signed decimal integer                            |
| 4        | `%d`        | Signed decimal integer                            |
| 5        | `%u`        | Unsigned decimal integer                          |
| 6        | `%o`        | Octal integer                                     |
| 7        | `%x`        | Hexadecimal integer (lowercase letters)           |
| 8        | `%X`        | Hexadecimal integer (UPPERcase letters)           |
| 9        | `%e`        | Exponential notation (with lowercase 'e')         |
| 10       | `%E`        | Exponential notation (with UPPERcase 'E')         |
| 11       | `%f`        | Floating-point real number                        |
| 12       | `%g`        | The shorter of `%f` and `%e`                      |
| 13       | `%G`        | The shorter of `%f` and `%E`                      |

Examples of using the `%` operator −

```python title="strings.py" showLineNumbers{1} {5}
# define variables
a = 5
b = 3.14
# print string
print("a is %d and b is %f" % (a, b))
```
Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python strings.py
a is 5 and b is 3.140000
```

Another example:
> `%d` and `%s` placeholders to insert the values of the variables into the string.
    
```python title="strings.py" showLineNumbers{1} {5}
# define variables
name = "Ravi"
age = 19
# print string
print("%s is %d years old." % (name, age))
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python strings.py
Ravi is 19 years old.
```

In the above example, we have used `%s` and `%d` placeholders to insert the values of the variables into the string.

Other supported symbols and functionality are listed in the following table −
| Sequence | Symbol  | Functionality                                                                                                      |
| :------- | :------ | :----------------------------------------------------------------------------------------------------------------- |
| 1        | `*`     | Width or precision                                                                                                 |
| 2        | `-`     | Left justification                                                                                                 |
| 3        | `+`     | Display the sign                                                                                                   |
| 4        | `<sp>`  | Leave a blank space before a positive number                                                                       |
| 5        | `#`     | Add the octal leading zero ( '0' ) or hexadecimal leading '0x' or '0X', depending on whether 'x' or 'X' were used. |
| 6        | `0`     | Pad from left with zeros (instead of spaces)                                                                       |
| 7        | `%`     | '%%' leaves you with a single literal '%'                                                                          |
| 8        | `(var)` | Mapping variable (dictionary arguments)                                                                            |
| 9        | `m.n.`  | m is the minimum total width and n is the number of digits to display after the decimal point (if appl.)           |

Examples of using the `%` operator −
> `%5d` is used to specify the width of the field. The field will be filled with spaces if the value doesn't use up the entire width. 

```python title="strings.py" showLineNumbers{1} {5}
# define variables
a = 5
b = "Ravi"
# print string
print("a is %5d and b is %5s" % (a, b))
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python strings.py
a is     5 and b is Ravi
```

In the above example, we have used `%5d` and `%5s` placeholders to insert the values of the variables into the string. The number `5` is used to specify the width of the field. The field will be filled with spaces if the value doesn't use up the entire width.

Another example:
> `%05d` is used to specify the width of the field. The field will be filled with `0` if the value doesn't use up the entire width. 

```python title="strings.py" showLineNumbers{1} {5}
# define variables
a = 5
b = "Ravi"
# print string
print("a is %05d and b is %5s" % (a, b))
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python strings.py
a is 00005 and b is Ravi
```

In the above example, we have used `%05d` and `%5s` placeholders to insert the values of the variables into the string. The number `5` is used to specify the width of the field. The field will be filled with `0` if the value doesn't use up the entire width.

Another example:
> `%1.2f` is used to specify the minimum total width of the field. The number `1` is used to specify the minimum total width of the field. The number `2` is used to specify the number of digits to display after the decimal point.

```python title="strings.py" showLineNumbers{1} {4}
# define variables
pi = 3.141592653589793
# print string
print("The value of pi is %1.2f" % pi)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python strings.py
The value of pi is 3.14
```

In this example, we have used `%1.2f` placeholder to insert the value of the variable into the string. The number `1` is used to specify the minimum total width of the field. The number `2` is used to specify the number of digits to display after the decimal point.

Another example:
> `%20s` is used to specify the width of the field. The field will be filled with spaces if the value doesn't use up the entire width.

```python title="strings.py" showLineNumbers{1} {3-4}
# define variables
name = "Ravi Kishan"
print("Hello, %20s." % name)
print("Hello, %-20s." % name)
```

Output:

```cmd title="command" showLineNumbers{1} {3}
C:\Users\Your Name> python strings.py
Hello,          Ravi Kishan.
Hello, Ravi Kishan         .
```

In this example, we have used `%20s` and `%-20s` placeholders to insert the values of the variables into the string. The number `20` is used to specify the width of the field. The field will be filled with spaces if the value doesn't use up the entire width. The `-` sign is used to left-justify the value.

Another example:
> `%5.7s` is used to specify the minimum total width of the field. The number `5` is used to specify the minimum total width of the field. The number `7` is used to specify the maximum total width of the field. The field will be filled with spaces if the value doesn't use up the entire width.

```python title="strings.py" showLineNumbers{1} {4-5}
# define variables
name = "Ravi Kishan"
print("Welcome, %.5s." % name)
print("Welcome, %5.7s." % name)
```

Output:

```cmd title="command" showLineNumbers{1} {3}
C:\Users\Your Name> python strings.py
Welcome, Ravi.
Welcome, Ravi Ki.
```

In this example, we have used `%.5s` and `%5.7s` placeholders to insert the values of the variables into the string. The number `5` is used to specify the minimum total width of the field. The number `7` is used to specify the maximum total width of the field. The field will be filled with spaces if the value doesn't use up the entire width.

Another example:
> `%*.*s` is used to specify the minimum total width of the field.

```python title="strings.py" showLineNumbers{1} {3-4}
# define variables
name = "Ravi Kishan"
print("Welcome, %*.*s." % (5, 7, name))
print("Welcome, %*.*s." % (-5, 7, name))
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\Your Name> python strings.py
Welcome,   Ravi Ki.
Welcome, Ravi Ki.
```

In this example, we have used `%*.*s` placeholder to insert the values of the variables into the string. The first number `5` is used to specify the minimum total width of the field. The second number `7` is used to specify the maximum total width of the field. The field will be filled with spaces if the value doesn't use up the entire width. The `-` sign is used to left-justify the value.

Another example:

:::tip
The `%` operator is deprecated as of Python 3.1 and will be removed in Python 4.0. Use one of the other methods described in this tutorial.
For more information, see [PEP 3101](https://www.python.org/dev/peps/pep-3101/).
:::

## The format() Method

#### `format()`

The `format()` method is used to perform string formatting. It takes the passed arguments, formats them, and places them in the string where the placeholders (`{}`) are. 

`format()` is a method of the `str` class. Hence, it can be used with any string object. This is a built-in method in Python. Hence, it doesn't require any import statement.
:::tip
For more information about `import` statement, see [Python Modules](/docs/tutorials/Python%20Modules/).

:::

#### `str.format()`

The `str.format()` method is used to perform string formatting. It takes the passed arguments, formats them, and places them in the string where the placeholders (`{}`) are. this returns a new string object. 

Let's look at an example.

```python title="strings.py" showLineNumbers{1} {5}
# define variables
name = "Ravi"
age = 23
# print string
print("{} is {} years old.".format(name, age))
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python strings.py
Ravi is 23 years old.
```

In the above example, we have used `{}` placeholders to insert the values of the variables into the string.

Here is a list of placeholders that can be used in the string −
| Sequence | Placeholder | Meaning|
| :------- | :---------- | :-----|
| 1        | `{}`        | Insert the value in the placeholder|
| 2        | `{0}`       | Insert the value of the first argument in the placeholder|
| 3        | `{1}`       | Insert the value of the second argument in the placeholder|
| 4        | `{2}`       | Insert the value of the third argument in the placeholder|
| 5        | `{n}`       | Insert the value of the nth argument in the placeholder|
| 6        | `{m:n}`     | Insert the value of the nth argument in the placeholder with the minimum total width of m and n digits after the decimal point (if appl.)|
| 7        | `{m:n.m}`   | Insert the value of the nth argument in the placeholder with the minimum total width of m and n digits after the decimal point (if appl.)|
| 8        | `{m:n.mf}`  | Insert the value of the nth argument in the placeholder with the minimum total width of m and n digits after the decimal point (if appl.) and the sign|
| 9        | `{m:n.m%}`  | Insert the value of the nth argument in the placeholder with the minimum total width of m and n digits after the decimal point (if appl.) and the sign|
| 10       | `{m:n.mg}`  | Insert the value of the nth argument in the placeholder with the minimum total width of m and n digits after the decimal point (if appl.) and the sign|
| 11       | `{var}`     | Insert the value of the mapping variable (dictionary arguments) in the placeholder|
| 12       | `{var:n}`   | Insert the value of the mapping variable (dictionary arguments) in the placeholder with the minimum total width of n digits after the decimal point (if appl.)|
| 13       | `{var:n.m}` | Insert the value of the mapping variable (dictionary arguments) in the placeholder with the minimum total width of m and n digits after the decimal point (if appl.)|
| 14       | `{var:n.mf}`| Insert the value of the mapping variable (dictionary arguments) in the placeholder with the minimum total width of m and n digits after the decimal point (if appl.) and the sign|

Examples of using the `format()` method −

```python title="strings.py" showLineNumbers{1} {5}
# define variables
a = 5
b = 3.14
# print string
print("a is {} and b is {}".format(a, b))
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python strings.py
a is 5 and b is 3.14
```

Another example:
> `{0}` and `{1}` placeholders to insert the values of the variables into the string.

```python title="strings.py" showLineNumbers{1} {5}
# define variables
name = "Ravi"
age = 23
# print string
print("{1} is {0} years old.".format(name, age))
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python strings.py
23 is Ravi years old.
```

In the above example, we have used `{1}` and `{0}` placeholders to insert the values of the variables into the string. The number `1` is used to specify the position of the second argument in the placeholder. The number `0` is used to specify the position of the first argument in the placeholder. The first argument is `name` and the second argument is `age`. Hence, the value of `age` is inserted in the first placeholder and the value of `name` is inserted in the second placeholder.

Another example:
> `{0:5d}` is used to specify the minimum total width of the field. The number `0` is used to specify the position of the first argument in the placeholder. The number `5` is used to specify the minimum total width of the field. The field will be filled with spaces if the value doesn't use up the entire width.

```python title="strings.py" showLineNumbers{1} {5}
# define variables
a = 5
b = "Ravi"
# print string
print("a is {0:5d} and b is {1:5s}".format(a, b))
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python strings.py
a is     5 and b is Ravi
```

In the above example, we have used `{0:5d}` and `{1:5s}` placeholders to insert the values of the variables into the string. The number `0` is used to specify the position of the first argument in the placeholder. The number `5` is used to specify the minimum total width of the field. The field will be filled with spaces if the value doesn't use up the entire width.

Another example:
> `{0:05d}` is used to specify the minimum total width of the field. The number `0` is used to specify the position of the first argument in the placeholder. The number `5` is used to specify the minimum total width of the field. The field will be filled with `0` if the value doesn't use up the entire width.

```python title="strings.py" showLineNumbers{1} {5}
# define variables
a = 5
b = "Ravi"
# print string
print("a is {0:05d} and b is {1:5s}".format(a, b))
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python strings.py
a is 00005 and b is Ravi
```

In the above example, we have used `{0:05d}` and `{1:5s}` placeholders to insert the values of the variables into the string. The number `0` is used to specify the position of the first argument in the placeholder. The number `5` is used to specify the minimum total width of the field. The field will be filled with `0` if the value doesn't use up the entire width.

Another example:
> `{0:1.2f}` is used to specify the minimum total width of the field. The number `0` is used to specify the position of the first argument in the placeholder. The number `1` is used to specify the minimum total width of the field. The number `2` is used to specify the number of digits to display after the decimal point.

```python title="strings.py" showLineNumbers{1} {4}
# define variables
pi = 3.141592653589793
# print string
print("The value of pi is {0:1.2f}".format(pi))
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python strings.py
The value of pi is 3.14
```

In this example, we have used `{0:1.2f}` placeholder to insert the value of the variable into the string. The number `0` is used to specify the position of the first argument in the placeholder. The number `1` is used to specify the minimum total width of the field. The number `2` is used to specify the number of digits to display after the decimal point.

Another example:
> `{0:20s}` is used to specify the minimum total width of the field. The number `0` is used to specify the position of the first argument in the placeholder. The number `20` is used to specify the minimum total width of the field. The field will be filled with spaces if the value doesn't use up the entire width.

```python title="strings.py" showLineNumbers{1} {3-4}
# define variables
name = "Ravi Kishan"
print("Hello, {0:20s}.".format(name))
print("Hello, {0:<20s}.".format(name))
```

Output:

```cmd title="command" showLineNumbers{1} {3}
C:\Users\Your Name> python strings.py
Hello, Ravi Kishan       .
Hello, Ravi Kishan       .
```

In this example, we have used `{0:20s}` and `{0:<20s}` placeholders to insert the values of the variables into the string. The number `0` is used to specify the position of the first argument in the placeholder. The number `20` is used to specify the minimum total width of the field. The field will be filled with spaces if the value doesn't use up the entire width. The `<` sign is used to left-justify the value.

Another example:
> `{0:5.7s}` is used to specify the minimum total width of the field. The number `0` is used to specify the position of the first argument in the placeholder. The number `5` is used to specify the minimum total width of the field. The number `7` is used to specify the maximum total width of the field. The field will be filled with spaces if the value doesn't use up the entire width.

```python title="strings.py" showLineNumbers{1} {4-5}
# define variables
name = "Ravi Kishan"
print("Welcome, {0:.5s}.".format(name))
print("Welcome, {0:5.7s}.".format(name))
```

Output:

```cmd title="command" showLineNumbers{1} {3}
C:\Users\Your Name> python strings.py
Welcome, Ravi.
Welcome, Ravi Ki.
```

In this example, we have used `{0:.5s}` and `{0:5.7s}` placeholders to insert the values of the variables into the string. The number `0` is used to specify the position of the first argument in the placeholder. The number `5` is used to specify the minimum total width of the field. The number `7` is used to specify the maximum total width of the field. The field will be filled with spaces if the value doesn't use up the entire width.

Another example:
> `{0:*<5.7s}` is used to specify the minimum total width of the field. The number `0` is used to specify the position of the first argument in the placeholder. The number `5` is used to specify the minimum total width of the field. The number `7` is used to specify the maximum total width of the field. The field will be filled with `*` if the value doesn't use up the entire width. The `<` sign is used to left-justify the value.

```python title="strings.py" showLineNumbers{1} {4-5}
# define variables
name = "Ravi Kishan"
print("Welcome, {0:*<5.7s}.".format(name))
print("Welcome, {0:*>5.7s}.".format(name))
```

Output:

```cmd title="command" showLineNumbers{1} {3}
C:\Users\Your Name> python strings.py
Welcome, Ravi Ki.
Welcome, **Ravi Ki.
```

In this example, we have used `{0:*<5.7s}` and `{0:*>5.7s}` placeholders to insert the values of the variables into the string. The number `0` is used to specify the position of the first argument in the placeholder. The number `5` is used to specify the minimum total width of the field. The number `7` is used to specify the maximum total width of the field. The field will be filled with `*` if the value doesn't use up the entire width. The `<` sign is used to left-justify the value.

Another example:
> `{var}` is used to specify the mapping variable (dictionary arguments) in the placeholder.

```python title="strings.py" showLineNumbers{1} {3-4}
# define variables
name = "Ravi Kishan"
age = 23
print("{name} is {age} years old.".format(name=name, age=age))
print("{name} is {age} years old.".format(**locals()))
```

Output:

```cmd title="command" showLineNumbers{1} {3}
C:\Users\Your Name> python strings.py
Ravi Kishan is 23 years old.
Ravi Kishan is 23 years old.
```

In this example, we have used `{name}` and `{age}` placeholders to insert the values of the variables into the string. The `name` and `age` are the mapping variables (dictionary arguments) in the placeholder. `name` and `age` are the keys of the dictionary. `name=name` and `age=age` are the values of the dictionary. Hence, the value of `name` is inserted in the first placeholder and the value of `age` is inserted in the second placeholder. The `**locals()` is used to unpack the dictionary. 

Another example:
> `{name:5s}` is used to specify the mapping variable (dictionary arguments) in the placeholder with the minimum total width of the field. The number `5` is used to specify the minimum total width of the field. The field will be filled with spaces if the value doesn't use up the entire width.

```python title="strings.py" showLineNumbers{1} {3-4}
# define variables
name = "Ravi Kishan"
age = 23
print("{name:5s} is {age} years old.".format(name=name, age=age))
print("{name:5s} is {age} years old.".format(**locals()))
```

Output:

```cmd title="command" showLineNumbers{1} {3}
C:\Users\Your Name> python strings.py
Ravi Kishan is 23 years old.
Ravi Kishan is 23 years old.
```

In this example, we have used `{name:5s}` and `{age}` placeholders to insert the values of the variables into the string. The number `5` is used to specify the minimum total width of the field. The field will be filled with spaces if the value doesn't use up the entire width. The `name` and `age` are the mapping variables (dictionary arguments) in the placeholder. `name` and `age` are the keys of the dictionary. `name=name` and `age=age` are the values of the dictionary. Hence, the value of `name` is inserted in the first placeholder and the value of `age` is inserted in the second placeholder. The `**locals()` is used to unpack the dictionary.

Another example:
> You can use `format()` to do formatting of a string to store it in a variable.

```python title="strings.py" showLineNumbers{1} {4-5}
# define variables
name = "Ravi Kishan"
age = 23
holders = "{name} is {age} years old."
intro = holders.format(name=name, age=age)
print(intro)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python strings.py
Ravi Kishan is 23 years old.
```

## F-Strings

F-strings provide a concise and convenient way to embed python expressions inside string literals for formatting. F-strings are prefixed with `f` or `F`. The string literals can contain replacement fields surrounded by curly braces `{}`. Anything inside the curly braces is considered as an expression that will be evaluated at runtime. The result of the evaluated expression will be converted into a string and inserted into the string literal. Let's look at an example.

```python title="strings.py" showLineNumbers{1} {5}
# define variables
name = "Ravi"
age = 23
# print string
print(f"{name} is {age} years old.")
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python strings.py
Ravi is 23 years old.
```

In the above example, we have used `{}` placeholders to insert the values of the variables into the string.

Here is a list of placeholders that can be used in the string −
| Sequence | Placeholder | Meaning|
| :------- | :---------- | :-----|
| 1        | `{}`        | Insert the value in the placeholder|
| 2        | `{var}`     | Insert the value of the mapping variable (dictionary arguments) in the placeholder|
| 3        | `{var:n}`   | Insert the value of the mapping variable (dictionary arguments) in the placeholder with the minimum total width of n digits after the decimal point (if appl.)|
| 4        | `{var:n.m}` | Insert the value of the mapping variable (dictionary arguments) in the placeholder with the minimum total width of m and n digits after the decimal point (if appl.)|
| 5        | `{var:n.mf}`| Insert the value of the mapping variable (dictionary arguments) in the placeholder with the minimum total width of m and n digits after the decimal point (if appl.) and the sign|
| 6        | `{var:n.m%}`| Insert the value of the mapping variable (dictionary arguments) in the placeholder with the minimum total width of m and n digits after the decimal point (if appl.) and the sign|
| 7        | `{var:n.mg}`| Insert the value of the mapping variable (dictionary arguments) in the placeholder with the minimum total width of m and n digits after the decimal point (if appl.) and the sign|

Examples of using the f-strings −

```python title="strings.py" showLineNumbers{1} {5}
# define variables
a = 5
b = 3.14
# print string
print(f"a is {a} and b is {b}")
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python strings.py
a is 5 and b is 3.14
```

Another example:
> `{a}` and `{b}` placeholders to insert the values of the variables into the string.

```python title="strings.py" showLineNumbers{1} {5}
# define variables
name = "Ravi"
age = 23
# print string
print(f"{age} is {name} years old.")
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python strings.py
23 is Ravi years old.
```

In the above example, we have used `{age}` and `{name}` placeholders to insert the values of the variables into the string. The `age` and `name` are the mapping variables (dictionary arguments) in the placeholder. `age` and `name` are the keys of the dictionary. `age=age` and `name=name` are the values of the dictionary. Hence, the value of `age` is inserted in the first placeholder and the value of `name` is inserted in the second placeholder.

Another example:
> `{a:5d}` is used to specify the minimum total width of the field. The number `5` is used to specify the minimum total width of the field. The field will be filled with spaces if the value doesn't use up the entire width.

```python title="strings.py" showLineNumbers{1} {5}
# define variables
a = 5
b = "Ravi"
# print string
print(f"a is {a:5d} and b is {b:5s}")
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python strings.py
a is     5 and b is Ravi
```

In the above example, we have used `{a:5d}` and `{b:5s}` placeholders to insert the values of the variables into the string. The number `5` is used to specify the minimum total width of the field. The field will be filled with spaces if the value doesn't use up the entire width.

Another example:
> `{a:05d}` is used to specify the minimum total width of the field. The number `5` is used to specify the minimum total width of the field. The field will be filled with `0` if the value doesn't use up the entire width.

```python title="strings.py" showLineNumbers{1} {5}

# define variables
a = 5
b = "Ravi"
# print string
print(f"a is {a:05d} and b is {b:5s}")
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python strings.py
a is 00005 and b is Ravi
```

In the above example, we have used `{a:05d}` and `{b:5s}` placeholders to insert the values of the variables into the string. The number `5` is used to specify the minimum total width of the field. The field will be filled with `0` if the value doesn't use up the entire width.

Another example:
> `{a:1.2f}` is used to specify the minimum total width of the field. The number `1` is used to specify the minimum total width of the field. The number `2` is used to specify the number of digits to display after the decimal point.

```python title="strings.py" showLineNumbers{1} {4}
# define variables
pi = 3.141592653589793
# print string
print(f"The value of pi is {pi:1.2f}")
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python strings.py
The value of pi is 3.14
```

In this example, we have used `{pi:1.2f}` placeholder to insert the value of the variable into the string. The number `1` is used to specify the minimum total width of the field. The number `2` is used to specify the number of digits to display after the decimal point.

Another example:
> `{a:20s}` is used to specify the minimum total width of the field. The number `20` is used to specify the minimum total width of the field. The field will be filled with spaces if the value doesn't use up the entire width.

```python title="strings.py" showLineNumbers{1} {3-4}
# define variables
name = "Ravi Kishan"
print(f"Hello, {name:20s}.")
print(f"Hello, {name:<20s}.")
```

Output:

```cmd title="command" showLineNumbers{1} {3}
C:\Users\Your Name> python strings.py
Hello, Ravi Kishan       .
Hello, Ravi Kishan       .
```

In this example, we have used `{name:20s}` and `{name:<20s}` placeholders to insert the values of the variables into the string. The number `20` is used to specify the minimum total width of the field. The field will be filled with spaces if the value doesn't use up the entire width. The `<` sign is used to left-justify the value.

Another example:
> `{a:5.7s}` is used to specify the minimum total width of the field. The number `5` is used to specify the minimum total width of the field. The number `7` is used to specify the maximum total width of the field. The field will be filled with spaces if the value doesn't use up the entire width.

```python title="strings.py" showLineNumbers{1} {4-5}
# define variables
name = "Ravi Kishan"
print(f"Welcome, {name:.5s}.")
print(f"Welcome, {name:5.7s}.")
```

Output:

```cmd title="command" showLineNumbers{1} {3}
C:\Users\Your Name> python strings.py
Welcome, Ravi.
Welcome, Ravi Ki.
```

In this example, we have used `{name:.5s}` and `{name:5.7s}` placeholders to insert the values of the variables into the string. The number `5` is used to specify the minimum total width of the field. The number `7` is used to specify the maximum total width of the field. The field will be filled with spaces if the value doesn't use up the entire width.

Another example:
`x`, `o`, `X`, `b`, `n`, `e`, `E`, `f`, `F`, `g`, `G`, `%` can be used to format the numbers.

```python title="strings.py" showLineNumbers{1} {4-5}
# define variables
a = 5
b = 3.14
print(f"a is {a:x} and b is {b:o}")
print(f"a is {a:X} and b is {b:b}")
print(f"a is {a:n} and b is {b:e}")
print(f"a is {a:N} and b is {b:E}")
print(f"a is {a:f} and b is {b:F}")
print(f"a is {a:g} and b is {b:G}")
print(f"a is {a:%} and b is {b:%}")
```

Output:

```cmd title="command" showLineNumbers{1} {3}
C:\Users\Your Name> python strings.py
a is 5 and b is 5
a is 5 and b is 11
a is 5 and b is 3.140000e+00
a is 5 and b is 3.140000E+00
a is 5.000000 and b is 3.140000
a is 5 and b is 3.14
a is 500.000000% and b is 314.000000%
```

In this example, we have used `{a:x}`, `{b:o}`, `{a:X}`, `{b:b}`, `{a:n}`, `{b:e}`, `{a:N}`, `{b:E}`, `{a:f}`, `{b:F}`, `{a:g}`, `{b:G}`, `{a:%}`, and `{b:%}` placeholders to insert the values of the variables into the string. `x`, `o`, `X`, `b`, `n`, `e`, `E`, `f`, `F`, `g`, `G`, `%` are used to format the numbers.

This table is the representation of the above example −
| Sequence | Placeholder | Meaning|
| :------- | :---------- | :-----|
| 1        | `{a:x}`     | Convert the value of `a` to hexadecimal format|
| 2        | `{b:o}`     | Convert the value of `b` to octal format|
| 3        | `{a:X}`     | Convert the value of `a` to hexadecimal format|
| 4        | `{b:b}`     | Convert the value of `b` to binary format|
| 5        | `{a:n}`     | Convert the value of `a` to number format|
| 6        | `{b:e}`     | Convert the value of `b` to exponential format|
| 7        | `{a:N}`     | Convert the value of `a` to number format|
| 8        | `{b:E}`     | Convert the value of `b` to exponential format|
| 9        | `{a:f}`     | Convert the value of `a` to float format|
| 10       | `{b:F}`     | Convert the value of `b` to float format|
| 11       | `{a:g}`     | Convert the value of `a` to general format|
| 12       | `{b:G}`     | Convert the value of `b` to general format|
| 13       | `{a:%}`    | Convert the value of `a` to percentage format|
| 14       | `{b:%}`    | Convert the value of `b` to percentage format|
| 15       | `{a:,.2f}`  | Convert the value of `a` to float format with comma as a thousand separator and 2 digits after the decimal point|
| 16      | `{a:,.2%}`  | Convert the value of `a` to percentage format with comma as a thousand separator and 2 digits after the decimal point|
| 17       | `{a:,.2e}`  | Convert the value of `a` to exponential format with comma as a thousand separator and 2 digits after the decimal point|

Another example:
> You can use the expression as a placeholder.

```python title="strings.py" showLineNumbers{1} {4-5}
# define variables
a = 9
b = 3
print(f"{a} + {b} = {a+b}")
print(f"{a} - {b} = {a-b}")
```

Output:

```cmd title="command" showLineNumbers{1} {3}
C:\Users\Your Name> python strings.py
9 + 3 = 12
9 - 3 = 6
```

In this example, we have used `{a} + {b} = {a+b}` and `{a} - {b} = {a-b}` placeholders to insert the values of the variables into the string. The expression `{a+b}` is used as a placeholder. The expression `{a-b}` is used as a placeholder.

Another example:
> You can use `f-strings` to do formatting of a string to store it in a variable.

```python title="strings.py" showLineNumbers{1} {4}
# define variables
name = "Ravi Kishan"
age = 23
intro = f"{name} is {age} years old."
print(intro)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python strings.py
Ravi Kishan is 23 years old.
```

## Template Strings

Template strings provide a simpler way to do string formatting. Template strings are prefixed with `$` or `${}`. The string literals can contain replacement fields surrounded by curly braces `{}`. Anything inside the curly braces is considered as an expression that will be evaluated at runtime. The result of the evaluated expression will be converted into a string and inserted into the string literal. Let's look at an example.

```python title="strings.py" showLineNumbers{1} {5}
from string import Template
# define variables
name = "Ravi"
age = 23
# print string
print(Template("$name is $age years old.").substitute(name=name, age=age))
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python strings.py
Ravi is 23 years old.
```

In the above example, we have used `${}` placeholders to insert the values of the variables into the string.

Here is a list of placeholders that can be used in the string −
| Sequence | Placeholder | Meaning|
| :------- | :---------- | :-----|
| 1        | `${}`       | Insert the value in the placeholder|
| 2        | `${var}`    | Insert the value of the mapping variable (dictionary arguments) in the placeholder|
| 3        | `${var:n}`  | Insert the value of the mapping variable (dictionary arguments) in the placeholder with the minimum total width of n digits after the decimal point (if appl.)|
| 4        | `${var:n.m}`| Insert the value of the mapping variable (dictionary arguments) in the placeholder with the minimum total width of m and n digits after the decimal point (if appl.)|
| 5        | `${var:n.mf}`| Insert the value of the mapping variable (dictionary arguments) in the placeholder with the minimum total width of m and n digits after the decimal point (if appl.) and the sign|
| 6        | `${var:n.m%}`| Insert the value of the mapping variable (dictionary arguments) in the placeholder with the minimum total width of m and n digits after the decimal point (if appl.) and the sign|
| 7        | `${var:n.mg}`| Insert the value of the mapping variable (dictionary arguments) in the placeholder with the minimum total width of m and n digits after the decimal point (if appl.) and the sign|
| 8        | `${var:5s}` | Insert the value of the mapping variable (dictionary arguments) in the placeholder with the minimum total width of the field. The number `5` is used to specify the minimum total width of the field. The field will be filled with spaces if the value doesn't use up the entire width.|
| 9        | `${var:5.7s}`| Insert the value of the mapping variable (dictionary arguments) in the placeholder with the minimum total width of the field. The number `5` is used to specify the minimum total width of the field. The number `7` is used to specify the maximum total width of the field. The field will be filled with spaces if the value doesn't use up the entire width.|

:::tip
The `Template` class is used to create a template string. The `substitute()` method is used to substitute the values of the variables into the string. you can apply all the formatting techniques that we have learned in the previous sections.
:::

:::caution
The `Template` class is not safe for untrusted input. It may lead to security issues. Hence, it is recommended to use the `format()` method or f-strings.
:::

## Conclusion

In this tutorial, we have learned about the string formatting techniques in Python. We have learned about the `%` operator, `format()` method, f-strings, and template strings. We have also learned about the placeholders that can be used in the string. We have also learned about the formatting of numbers. Now you can use any of these techniques to format the strings in Python.

:::tip
For more information about strings formatting, see [Python String Formatting](https://docs.python.org/3/library/string.html#formatstrings).
:::