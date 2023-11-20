---
title: Python String Methods
description: Learn about the various methods available for Python strings.
sidebar: 
    order: 20
---

Python's built-in str class defines different methods. These methods can be used to manipulate strings. In this tutorial, we will learn about the different methods available for Python strings. 

#### These are some of the most commonly used string methods:
|Sequence|<div style="width:100px">Function Name</div>|Description|
|:---|:-------|:---|
|1|`capitalize()`|Converts the first character to upper case|
|2|`casefold()`|Converts string into lower case|
|3|`center()`|Returns a centered string|
|4|`count()`|Returns the number of times a specified value occurs in a string|
|5|`encode()`|Returns an encoded version of the string|
|6|`endswith()`|Returns true if the string ends with the specified value|
|7|`expandtabs()`|Sets the tab size of the string|
|8|`find()`|Searches the string for a specified value and returns the position of where it was found|
|9|`format()`|Formats specified values in a string|
|10|`format_map()`|Formats specified values in a string|
|11|`index()`|Searches the string for a specified value and returns the position of where it was found|
|12|`isalnum()`|Returns True if all characters in the string are alphanumeric|
|13|`isalpha()`|Returns True if all characters in the string are in the alphabet|
|14|`isdecimal()`|Returns True if all characters in the string are decimals|
|15|`isdigit()`|Returns True if all characters in the string are digits|
|16|`isidentifier()`|Returns True if the string is an identifier|
|17|`islower()`|Returns True if all characters in the string are lower case|
|18|`isnumeric()`|Returns True if all characters in the string are numeric|
|19|`isprintable()`|Returns True if all characters in the string are printable|
|20|`isspace()`|Returns True if all characters in the string are whitespaces|
|21|`istitle()`|Returns True if the string follows the rules of a title|
|22|`isupper()`|Returns True if all characters in the string are upper case|
|23|`join()`|Joins the elements of an iterable to the end of the string|
|24|`ljust()`|Returns a left justified version of the string|
|25|`lower()`|Converts a string into lower case|
|26|`lstrip()`|Returns a left trim version of the string|
|27|`maketrans()`|Returns a translation table to be used in translations|
|28|`partition()`|Returns a tuple where the string is parted into three parts|
|29|`replace()`|Returns a string where a specified value is replaced with a specified value|
|30|`rfind()`|Searches the string for a specified value and returns the last position of where it was found|
|31|`rindex()`|Searches the string for a specified value and returns the last position of where it was found|
|32|`rjust()`|Returns a right justified version of the string|
|33|`rpartition()`|Returns a tuple where the string is parted into three parts|
|34|`rsplit()`|Splits the string at the specified separator, and returns a list|
|35|`rstrip()`|Returns a right trim version of the string|
|36|`split()`|Splits the string at the specified separator, and returns a list|
|37|`splitlines()`|Splits the string at line breaks and returns a list|
|38|`startswith()`|Returns true if the string starts with the specified value|
|39|`strip()`|Returns a trimmed version of the string|
|40|`swapcase()`|Swaps cases, lower case becomes upper case and vice versa|
|41|`title()`|Converts the first character of each word to upper case|
|42|`translate()`|Returns a translated string|
|43|`upper()`|Converts a string into upper case|
|44|`zfill()`|Fills the string with a specified number of 0 values at the beginning|
|45|`+`|Concatenates two strings|
|46|`*`|Returns a string repeated the specified number of times|
|47|`[]`|Returns the character at the specified index|
|48|`[:]`|Returns the slice from the specified index to the specified index|
|49|`in`|Returns True if a sequence with the specified value is present in the object|
|50|`not in`|Returns True if a sequence with the specified value is not present in the object|
|51|`%`|Formats specified values in a string|
|52|`<`|Returns True if the first string is lower than the second string|
|53|`<=`|Returns True if the first string is lower than or equal to the second string|
|54|`>`|Returns True if the first string is greater than the second string|
|55|`>=`|Returns True if the first string is greater than or equal to the second string|
|56|`==`|Returns True if the first string is equal to the second string|
|57|`!=`|Returns True if the first string is not equal to the second string|
|58|`ord()`|Converts a character into Unicode|
|59|`hex()`|Converts an integer to a hexadecimal string|
|60|`oct()`|Converts an integer to an octal string|
|61|`chr()`|Converts an integer to a character|
|62|`len()`|Returns the length of the string|
|63|`repr()`|Returns a readable version of the string|
|64|`ascii()`|Returns a readable version of the string|
|65|`max()`|Returns the largest character in the string|
|66|`min()`|Returns the smallest character in the string|
|67|`str()`|Returns a string object|
|68|`type()`|Returns the type of the specified object|
|69|`vars()`|Returns the `__dict__` property of an object|
|70|`help()`|Executes the built-in help system|

## 1. capitalize()
The `capitalize()` method returns a string where the first character is upper case.

**Syntax**:
#### `string.capitalize()`
- **Returns** - A capitalized string

**Example**:
```python title="strings.py" showLineNumbers{1} {3}
# capitalize() method
string = 'python strings'
print(string.capitalize())
```

Output

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python strings.py
Python strings
```

## 2. casefold()
The `casefold()` method returns a string where all the characters are lower case.

**Syntax**:
#### `string.casefold()`
- **Returns** - A lower case string

**Example**:
```python title="strings.py" showLineNumbers{1} {3}
# casefold() method
string = 'Python Strings'
print(string.casefold())
```

Output

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python strings.py
python strings
```

## 3. center()
The `center()` method will center align the string, using a specified character (space is default) as the fill character.

**Syntax**:
#### `string.center(length, character)`
- **length** - The length of the returned string
- **character** (optional) - The character to fill the missing space on each side. Default is `" "`
- **Returns** - A centered string

**Example**:
```python title="strings.py" showLineNumbers{1} {3}
# center() method
string = 'Python Strings'
print(string.center(20))
print(string.center(20, '*'))
```

Output

```cmd title="command" showLineNumbers{1} {3}
C:\Users\Your Name> python strings.py
   Python Strings
***Python Strings***
```

## 4. count()
The `count()` method returns the number of times a specified value appears in the string.

**Syntax**:
#### `string.count(value, start, end)`
- **value** - The value to search for
- **start** (optional) - The position to start the search. Default is `0`
- **end** (optional) - The position to end the search. Default is `len(string)`
- **Returns** - The number of times the value appears in the string

**Example**:
```python title="strings.py" showLineNumbers{1} {3}
# count() method
string = 'Python Strings'
print(string.count('s'))
print(string.count('s', 7, 14))
```

Output

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\Your Name> python strings.py
2
1
```

## 5. encode()
The `encode()` method encodes the string, using the specified encoding. If no encoding is specified, UTF-8 will be used.

**Syntax**:
#### `string.encode(encoding, errors)`
- **encoding** (optional) - A String specifying the encoding to use. Default is `UTF-8`
- **errors** (optional) - A String specifying the error method. Legal values are:
    - `backslashreplace` - uses a backslash instead of the character that could not be encoded
    - `ignore` - ignores the characters that cannot be encoded
    - `namereplace` - replaces the character with a text explaining the character
    - `strict` - Default, raises an error on failure
    - `replace` - replaces the character with a questionmark
    - `xmlcharrefreplace` - replaces the character with an xml character

**Example**:
```python title="strings.py" showLineNumbers{1} {3}
# encode() method
string = 'Python Strings'
print(string.encode())
print(string.encode(encoding='ascii', errors='ignore'))
```

Output

```cmd title="command" showLineNumbers{1} {3}
C:\Users\Your Name> python strings.py
b'Python Strings'
b'Python Strings'
```

## 6. endswith()
The `endswith()` method returns `True` if the string ends with the specified value, otherwise `False`.

**Syntax**:
#### `string.endswith(value, start, end)`
- **value** - Required. The value to check if the string ends with
- **start** (optional) - Optional. An Integer specifying at which position to start the search
- **end** (optional) - Optional. An Integer specifying at which position to end the search
- **Returns** - `True` if the string ends with the specified value, otherwise `False`

**Example**:
```python title="strings.py" showLineNumbers{1} {3-4}
# endswith() method
string = 'Python Strings'
print(string.endswith('s'))
print(string.endswith('s', 7, 14))
```

Output

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\Your Name> python strings.py
True
False
```

## 7. expandtabs()
The `expandtabs()` method sets the tab size to the specified number of whitespaces.

**Syntax**:
#### `string.expandtabs(tabsize)`
- **tabsize** (optional) - A number specifying the tabsize. Default tabsize is `8`
- **Returns** - A string where all `\t` characters are replaced with whitespaces using the specified tabsize

**Example**:
```python title="strings.py" showLineNumbers{1} {3-5}
# expandtabs() method
string = 'Python\tStrings'
print(string.expandtabs())
print(string.expandtabs(2))
print(string.expandtabs(4))
```

Output

```cmd title="command" showLineNumbers{1} {2-4}
C:\Users\Your Name> python strings.py
Python  Strings
Python  Strings
Python    Strings
```

## 8. find()
The `find()` method finds the first occurrence of the specified value. The `find()` method returns `-1` if the value is not found.

**Syntax**:
#### `string.find(value, start, end)`
- **value** - Required. The value to search for
- **start** (optional) - Optional. Where to start the search. Default is `0`
- **end** (optional) - Optional. Where to end the search. Default is `len(string)`
- **Returns** - The index of the first occurrence of the specified value

**Example**:
```python title="strings.py" showLineNumbers{1} {3-4}
# find() method
string = 'Python Strings'
print(string.find('s'))
print(string.find('s', 7, 14))
```

Output

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\Your Name> python strings.py
7
-1
```

## 9. format()
The `format()` method formats the specified value(s) and insert them inside the string's placeholder.

**Syntax**:
#### `string.format(value1, value2...)`
- **value1, value2...** - Optional. A value to be formatted and inserted into the string's placeholder
- **Returns** - A formatted string

**Example**:
```python title="strings.py" showLineNumbers{1} {3-4}
# format() method
string = 'Python Strings'
print('I love {}'.format(string))
print('I love {0}'.format(string))
```

Output

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\Your Name> python strings.py
I love Python Strings
I love Python Strings
```

## 10. format_map()
The `format_map()` method formats the specified value(s) and insert them inside the string's placeholder.

**Syntax**:
#### `string.format_map(map)`
- **map** - Required. A dictionary containing the variables to insert into the string's placeholder
- **Returns** - A formatted string

**Example**:
```python title="strings.py" showLineNumbers{1} {3-4}
# format_map() method
string = 'Python Strings'
print('I love {name}'.format_map({'name': string}))
print('I love {name}'.format_map({'name': 'Python'}))
```

Output

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\Your Name> python strings.py
I love Python Strings
I love Python
```

## 11. index()
The `index()` method finds the first occurrence of the specified value. The `index()` method raises an exception if the value is not found.

**Syntax**:
#### `string.index(value, start, end)`
- **value** - Required. The value to search for
- **start** (optional) - Optional. Where to start the search. Default is `0`
- **end** (optional) - Optional. Where to end the search. Default is `len(string)`
- **Returns** - The index of the first occurrence of the specified value

**Example**:
```python title="strings.py" showLineNumbers{1} {3-4}
# index() method
string = 'Python Strings'
print(string.index('s'))
print(string.index('s', 7, 14))
```

Output

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\Your Name> python strings.py
7
Traceback (most recent call last):
  File "strings.py", line 4, in <module>
    print(string.index('s', 7, 14))
ValueError: substring not found
```

## 12. isalnum()
The `isalnum()` method returns `True` if all the characters are alphanumeric, meaning alphabet letter (a-z) and numbers (0-9).

**Syntax**:
#### `string.isalnum()`
- **Returns** - `True` if all characters in the string are alphanumeric

**Example**:
```python title="strings.py" showLineNumbers{1} {3-4}
# isalnum() method
string = 'PythonStrings'
print(string.isalnum())
print('Python Strings'.isalnum())
```

Output

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\Your Name> python strings.py
True
False
```
:::caution
The `isalnum()` method will return `False` if the string contains any special characters, like `!`, `@`, `#`, `$`, etc. It also returns `False` if the string contains any whitespace characters.
:::

## 13. isalpha()
The `isalpha()` method returns `True` if all the characters are alphabet letters (a-z).

**Syntax**:
#### `string.isalpha()`
- **Returns** - `True` if all characters in the string are alphabet letters

**Example**:
```python title="strings.py" showLineNumbers{1} {3-4}
# isalpha() method
string = 'PythonStrings'
print(string.isalpha())
print('Python Strings'.isalpha())
```

Output

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\Your Name> python strings.py
True
False
```

:::caution
The `isalpha()` method will return `False` if the string contains any special characters, like `!`, `@`, `#`, `$`, etc. It also returns `False` if the string contains any whitespace characters.
:::

## 14. isdecimal()
The `isdecimal()` method returns `True` if all the characters are decimals (0-9).

**Syntax**:
#### `string.isdecimal()`
- **Returns** - `True` if all characters in the string are decimals

**Example**:
```python title="strings.py" showLineNumbers{1} {3-4}
# isdecimal() method
string = '123456'
print(string.isdecimal())
print('123 456'.isdecimal())
```

Output

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\Your Name> python strings.py
True
False
```

:::caution
The `isdecimal()` method will return `False` if the string contains any other character than decimal characters, such as `a`, `b`, `c`, `!`, `@`, `#`, `$`, etc. It also returns `False` if the string contains any whitespace characters.
:::

## 15. isdigit()
The `isdigit()` method returns `True` if all the characters are digits, otherwise `False`.

**Syntax**:
#### `string.isdigit()`
- **Returns** - `True` if all characters in the string are digits

**Example**:
```python title="strings.py" showLineNumbers{1} {3-4}
# isdigit() method
string = '123456'
print(string.isdigit())
print('123 456'.isdigit())
```

Output

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\Your Name> python strings.py
True
False
```

:::caution
The `isdigit()` method will return `False` if the string contains any other character than digits, such as `a`, `b`, `c`, `!`, `@`, `#`, `$`, etc. It also returns `False` if the string contains any whitespace characters.
:::
