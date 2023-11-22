---
title: Python String Methods
description: Learn about the various methods available for Python strings. Learn about more than 70 methods available for Python strings.
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
|61|`bin()`|Converts an integer to a binary string|
|62|`chr()`|Converts an integer to a character|
|63|`len()`|Returns the length of the string|
|64|`repr()`|Returns a readable version of the string|
|65|`ascii()`|Returns a readable version of the string|
|66|`max()`|Returns the largest character in the string|
|67|`min()`|Returns the smallest character in the string|
|68|`str()`|Returns a string object|
|69|`type()`|Returns the type of the specified object|
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

## 16. isidentifier()
The `isidentifier()` method returns `True` if the string is a valid identifier, otherwise `False`.

**Syntax**:
#### `string.isidentifier()`
- **Returns** - `True` if the string is a valid identifier, otherwise `False`

**Example**:
```python title="strings.py" showLineNumbers{1} {3-6}
# isidentifier() method
string = 'PythonStrings'
print(string.isidentifier())
print('Python Strings'.isidentifier())
print('Python-Strings'.isidentifier())
print('Python_Strings'.isidentifier())
```

Output

```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\Your Name> python strings.py
True
False
False
True
```

## 17. islower()
The `islower()` method returns `True` if all the characters are in lower case, otherwise `False`.

**Syntax**:
#### `string.islower()`
- **Returns** - `True` if all characters in the string are lower case

**Example**:
```python title="strings.py" showLineNumbers{1} {3-4}
# islower() method
string = 'python strings'
print(string.islower())
print('Python Strings'.islower())
```

Output

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\Your Name> python strings.py
True
False
```
:::caution
The `islower()` method will return `False` if the string contains any uppercase characters. It also returns `False` if the string contains any special characters, like `!`, `@`, `#`, `$`, etc. It also returns `False` if the string contains any whitespace characters.
:::

## 18. isnumeric()
The `isnumeric()` method returns `True` if all the characters are numeric (0-9), otherwise `False`.

**Syntax**:
#### `string.isnumeric()`
- **Returns** - `True` if all characters in the string are numeric

**Example**:
```python title="strings.py" showLineNumbers{1} {3-4}
# isnumeric() method
string = '123456'
print(string.isnumeric())
print('123 456'.isnumeric())
```

Output

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\Your Name> python strings.py
True
False
```

:::caution
The `isnumeric()` method will return `False` if the string contains any other character than numeric characters, such as `a`, `b`, `c`, `!`, `@`, `#`, `$`, etc. It also returns `False` if the string contains any whitespace characters.
:::

## 19. isprintable()
The `isprintable()` method returns `True` if all the characters are printable, otherwise `False`.

**Syntax**:
#### `string.isprintable()`
- **Returns** - `True` if all characters in the string are printable

**Example**:
```python title="strings.py" showLineNumbers{1} {3-4}
# isprintable() method
string = 'Python Strings'
print(string.isprintable())
print('Python\nStrings'.isprintable())
```

Output

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\Your Name> python strings.py
True
False
```

## 20. isspace()
The `isspace()` method returns `True` if all the characters in a string are whitespaces, otherwise `False`.

**Syntax**:
#### `string.isspace()`
- **Returns** - `True` if all characters in the string are whitespaces

**Example**:
```python title="strings.py" showLineNumbers{1} {3-4}
# isspace() method
string = '   '
print(string.isspace())
print('Python Strings'.isspace())
```

Output

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\Your Name> python strings.py
True
False
```

## 21. istitle()
The `istitle()` method returns `True` if all words in a text start with a upper case letter, AND the rest of the word are lower case letters, otherwise `False`.

**Syntax**:
#### `string.istitle()`
- **Returns** - `True` if all words in a text start with a upper case letter, AND the rest of the word are lower case letters

**Example**:
```python title="strings.py" showLineNumbers{1} {3-4}
# istitle() method
string = 'Python Strings'
print(string.istitle())
print('Python strings'.istitle())
```

Output

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\Your Name> python strings.py
True
False
```

## 22. isupper()
The `isupper()` method returns `True` if all the characters are in upper case, otherwise `False`.

**Syntax**:
#### `string.isupper()`
- **Returns** - `True` if all characters in the string are upper case

**Example**:
```python title="strings.py" showLineNumbers{1} {3-4}
# isupper() method
string = 'PYTHON STRINGS'
print(string.isupper())
print('Python Strings'.isupper())
```

Output

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\Your Name> python strings.py
True
False
```

:::caution
The `isupper()` method will return `False` if the string contains any lowercase characters. It also returns `False` if the string contains any special characters, like `!`, `@`, `#`, `$`, etc. It also returns `False` if the string contains any whitespace characters.
:::

## 23. join()
The `join()` method takes all items in an iterable and joins them into one string.

**Syntax**:
#### `string.join(iterable)`
- **iterable** - Required. Any iterable object where all the returned values are strings

**Example**:
```python title="strings.py" showLineNumbers{1} {3-4}
# join() method
string = 'Python Strings'
print(' '.join(string))
print(''.join(string))
```

Output

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\Your Name> python strings.py
P y t h o n   S t r i n g s
Python Strings
```

## 24. ljust()
The `ljust()` method will left align the string, using a specified character (space is default) as the fill character.

**Syntax**:
#### `string.ljust(length, character)`
- **length** - The length of the returned string
- **character** (optional) - The character to fill the missing space on the right side. Default is `" "`
- **Returns** - A left aligned string

**Example**:
```python title="strings.py" showLineNumbers{1} {3-4}
# ljust() method
string = 'Python Strings'
print(string.ljust(20))
print(string.ljust(20, '*'))
```

Output

```cmd title="command" showLineNumbers{1} {3-4}
C:\Users\Your Name> python strings.py
Python Strings
Python Strings*******
```

## 25. lower()
The `lower()` method returns a string where all characters are lower case.

**Syntax**:
#### `string.lower()`
- **Returns** - A lower case string

**Example**:
```python title="strings.py" showLineNumbers{1} {3}
# lower() method
string = 'Python Strings'
print(string.lower())
```

Output

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python strings.py
python strings
```

## 26. lstrip()
The `lstrip()` method removes any leading characters (space is the default leading character to remove)

**Syntax**:
#### `string.lstrip(characters)`
- **characters** (optional) - A set of characters to remove as leading characters
- **Returns** - A left trim version of the string

**Example**:
```python title="strings.py" showLineNumbers{1} {3-4}
# lstrip() method
string = '   Python Strings'
print(string.lstrip())
print(string.lstrip('   '))
```

Output

```cmd title="command" showLineNumbers{1} {2-4}
C:\Users\Your Name> python strings.py
Python Strings
Python Strings
```


## 27. maketrans()
The `maketrans()` method generates a translation table that can be used for replacing specified characters. This method is often used in conjunction with the `translate()` method to perform character substitutions in a string.

**Syntax**:
#### `str.maketrans(x[, y[, z]])`
- **x** - If only one argument is provided, it should be a dictionary mapping Unicode ordinals to translation strings. If two arguments are provided, they must be of equal length, and each character in x will be mapped to the character at the same position in y. If three arguments are provided, each charac ter in x will be mapped to the character at the same position in y and z.
- **y** - Mapping table, where each character in x will be mapped to the character at the same position in y. This argument is optional.
- **z** - If present, it specifies a string to be used for deleting characters.

**Returns**:
- A translation table.

**Example**:
```python title="strings.py" showLineNumbers{1} {4,6-7}
# maketrans() method
intab = "aeiou"
outtab = "12345"
trans_table = str.maketrans(intab, outtab)

string = "Hello, World!"
translated_string = string.translate(trans_table)

print("Original String:", string)
print("Translated String:", translated_string)
```

Output

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\Your Name> python strings.py
Original String: Hello, World!
Translated String: H2ll4, W4rld!
```
:::note
In this example, the `maketrans()` method is used to create a translation table (`trans_table`) that maps vowels to corresponding digits. The `translate()` method then applies this table to replace vowels in the original string.
:::

## 28. partition()
The `partition()` method divides a string into three parts based on the specified separator. It searches for the separator in the string, and once found, it returns a tuple containing the part before the separator, the separator itself, and the part after the separator.

**Syntax**:
#### `string.partition(separator)`
- **separator** - The string to search for within the given string.

**Returns**:
- A tuple containing three elements: the part before the separator, the separator itself, and the part after the separator.

**Example**:
```python title="strings.py" showLineNumbers{1} {3}
# partition() method
string = "Python is fun"
partitioned = string.partition("is")

print("Original String:", string)
print("Partitioned Result:", partitioned)
```

Output

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\Your Name> python strings.py
Original String: Python is fun
Partitioned Result: ('Python ', 'is', ' fun')
```
:::note
In this example, the `partition()` method is used to split the string into three parts based on the separator "is". The result is a tuple with the part before "is", "is" itself, and the part after "is".
:::

## 29. replace()
The `replace()` method returns a copy of the string where all occurrences of a substring is replaced with another substring.

**Syntax**:
#### `string.replace(old, new, count)`
- **old** - The substring to be replaced.
- **new** - The string which would replace the substring passed.
- **count** (optional) - The number of times old substring needs to be replaced with new substring. Default is `-1` which means replace all occurrences.
- **Returns** - A copy of the string where all occurrences of a substring is replaced with another substring.

**Example**:
```python title="strings.py" showLineNumbers{1} {3}
# replace() method
string = "Python is fun"
replaced = string.replace("is", "was")
print("Original String:", string)
print("Replaced String:", replaced)
```

Output

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\Your Name> python strings.py
Original String: Python is fun
Replaced String: Python was fun
```

## 30. rfind()
The `rfind()` method finds the last occurrence of the specified value. The `rfind()` method returns `-1` if the value is not found.

**Syntax**:
#### `string.rfind(value, start, end)`
- **value** - Required. The value to search for
- **start** (optional) - Optional. Where to start the search. Default is `0`
- **end** (optional) - Optional. Where to end the search. Default is `len(string)`
- **Returns** - The index of the last occurrence of the specified value

**Example**:
```python title="strings.py" showLineNumbers{1} {3-4}
# rfind() method
string = 'Python Strings'
print(string.rfind('s'))
print(string.rfind('s', 7, 14))
```

Output

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\Your Name> python strings.py
13
-1
```

## 31. rindex()
The `rindex()` method finds the last occurrence of the specified value. The `rindex()` method raises an exception if the value is not found.

**Syntax**:
#### `string.rindex(value, start, end)`
- **value** - Required. The value to search for
- **start** (optional) - Optional. Where to start the search. Default is `0`
- **end** (optional) - Optional. Where to end the search. Default is `len(string)`
- **Returns** - The index of the last occurrence of the specified value

**Example**:
```python title="strings.py" showLineNumbers{1} {3-4}
# rindex() method
string = 'Python Strings'
print(string.rindex('s'))
print(string.rindex('s', 7, 14))
```

Output

```cmd title="command" showLineNumbers{1} {2-6}
C:\Users\Your Name> python strings.py
13
Traceback (most recent call last):
  File "strings.py", line 4, in <module>
    print(string.rindex('s', 7, 14))
ValueError: substring not found
```

## 32. rjust()
The `rjust()` method will right align the string, using a specified character (space is default) as the fill character.

**Syntax**:
#### `string.rjust(length, character)`
- **length** - The length of the returned string
- **character** (optional) - The character to fill the missing space on the left side. Default is `" "`
- **Returns** - A right aligned string

**Example**:
```python title="strings.py" showLineNumbers{1} {3-4}
# rjust() method
string = 'Python Strings'
print(string.rjust(20))
print(string.rjust(20, '*'))
```

Output

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\Your Name> python strings.py
      Python Strings
*******Python Strings
```

## 33. rpartition()
The `rpartition()` method divides a string into three parts based on the specified separator. It searches for the separator in the string, moving from right to left, and once found, it returns a tuple containing the part before the separator, the separator itself, and the part after the separator.

**Syntax**:
#### `string.rpartition(separator)`
- **separator** - The string to search for within the given string.
- **Returns** - A tuple containing three elements: the part before the separator, the separator itself, and the part after the separator.

**Example**:
```python title="strings.py" showLineNumbers{1} {3}
# rpartition() method
string = "Python is fun"
partitioned = string.rpartition("is")
print("Original String:", string)
print("Partitioned Result:", partitioned)
```

Output

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\Your Name> python strings.py
Original String: Python is fun
Partitioned Result: ('Python ', 'is', ' fun')
```

## 34. rsplit()
The `rsplit()` method splits a string into a list, starting from the right. If no "max" is specified, this method will return the same as the `split()` method.

**Syntax**:
#### `string.rsplit(separator, maxsplit)`
- **separator** (optional) - Specifies the separator to use when splitting the string. By default any whitespace is a separator
- **maxsplit** (optional) - Specifies how many splits to do. Default value is `-1`, which is "all occurrences"
- **Returns** - A list of strings split at each separator

**Example**:
```python title="strings.py" showLineNumbers{1} {3-4}
# rsplit() method
string = 'Python Strings'
print(string.rsplit())
print(string.rsplit(' ', 1))
```

Output

```cmd title="command" showLineNumbers{1} {2-4}
C:\Users\Your Name> python strings.py
['Python', 'Strings']
['Python', 'Strings']
```

## 35. rstrip()
The `rstrip()` method removes any trailing characters (characters at the end a string), space is the default trailing character to remove.

**Syntax**:
#### `string.rstrip(characters)`
- **characters** (optional) - A set of characters to remove as trailing characters
- **Returns** - A right trim version of the string
  
**Example**:
```python title="strings.py" showLineNumbers{1} {3-4}
# rstrip() method
string = 'Python Strings   '
print(string.rstrip())
print(string.rstrip('   '))
```

Output

```cmd title="command" showLineNumbers{1} {2-4}
C:\Users\Your Name> python strings.py
Python Strings
Python Strings
```

## 36. split()
The `split()` method splits a string into a list.

**Syntax**:
#### `string.split(separator, maxsplit)`
- **separator** (optional) - Specifies the separator to use when splitting the string. By default any whitespace is a separator
- **maxsplit** (optional) - Specifies how many splits to do. Default value is `-1`, which is "all occurrences"
- **Returns** - A list of strings split at each separator

**Example**:
```python title="strings.py" showLineNumbers{1} {3-4}
# split() method
string = 'Python Strings'
print(string.split())
print(string.split(' ', 1))
```

Output

```cmd title="command" showLineNumbers{1} {2-4}
C:\Users\Your Name> python strings.py
['Python', 'Strings']
['Python', 'Strings']
```

## 37. splitlines()
The `splitlines()` method splits a string into a list. The splitting is done at line breaks.

**Syntax**:
#### `string.splitlines(keepends)`
- **keepends** (optional) - Specifies if the line breaks should be included (True), or not (False). Default value is `False`
- **Returns** - A list of lines in the string

**Example**:
```python title="strings.py" showLineNumbers{1} {3-4}
# splitlines() method
string = 'Python\nStrings'
print(string.splitlines())
print(string.splitlines(True))
```

Output

```cmd title="command" showLineNumbers{1} {2-4}
C:\Users\Your Name> python strings.py
['Python', 'Strings']
['Python\n', 'Strings']
```

## 38. startswith()
The `startswith()` method returns `True` if the string starts with the specified value, otherwise `False`.

**Syntax**:
#### `string.startswith(value, start, end)`
- **value** - Required. The value to check if the string starts with
- **start** (optional) - Optional. An Integer specifying at which position to start the search
- **end** (optional) - Optional. An Integer specifying at which position to end the search
- **Returns** - `True` if the string starts with the specified value, otherwise `False`

**Example**:
```python title="strings.py" showLineNumbers{1} {3-4}
# startswith() method
string = 'Python Strings'
print(string.startswith('P'))
print(string.startswith('p', 7, 14))
```

Output

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\Your Name> python strings.py
True
False
```

## 39. strip()
The `strip()` method removes any leading (spaces at the beginning) and trailing (spaces at the end) characters (space is the default leading character to remove)

**Syntax**:
#### `string.strip(characters)`
- **characters** (optional) - A set of characters to remove as leading/trailing characters
- **Returns** - A trimmed version of the string

**Example**:
```python title="strings.py" showLineNumbers{1} {3-4}
# strip() method
string = '   Python Strings   '
print(string.strip())
print(string.strip('   '))
```

Output

```cmd title="command" showLineNumbers{1} {2-4}
C:\Users\Your Name> python strings.py
Python Strings
Python Strings
```

## 40. swapcase()
The `swapcase()` method returns a string where all the upper case letters are lower case and vice versa.

**Syntax**:
#### `string.swapcase()`
- **Returns** - A string where all the upper case letters are lower case and vice versa

**Example**:
```python title="strings.py" showLineNumbers{1} {3}
# swapcase() method
string = 'Python Strings'
print(string.swapcase())
```

Output

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python strings.py
pYTHON sTRINGS
```

## 41. title()
The `title()` method returns a string where the first character in every word is upper case. Like a header, or a title.

**Syntax**:
#### `string.title()`
- **Returns** - A string where the first character in every word is upper case

**Example**:
```python title="strings.py" showLineNumbers{1} {3}
# title() method
string = 'Python Strings'
print(string.title())
```

Output

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python strings.py
Python Strings
```

## 42. translate()
The `translate()` method returns a string where some specified characters are replaced with the character described in a dictionary, or in a mapping table.

**Syntax**:
#### `string.translate(table)`
- **table** - A mapping table, where each character in the intab parameter will be mapped to the character at the same position in the outtab parameter.
- **Returns** - A string where specified characters are replaced with specified characters

**Example**:
```python title="strings.py" showLineNumbers{1} {3-4}
# translate() method
string = 'Python Strings'
print(string.translate({ord('P'): 'J'}))
print(string.translate({ord('P'): 'J', ord('S'): 'L'}))
```

Output

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\Your Name> python strings.py
Jython Strings
Jython Ltrings
```

## 43. upper()
The `upper()` method returns a string where all characters are in upper case.

**Syntax**:
#### `string.upper()`
- **Returns** - A string where all characters are in upper case
- **Example**:
```python title="strings.py" showLineNumbers{1} {3}
# upper() method
string = 'Python Strings'
print(string.upper())
```

Output

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python strings.py
PYTHON STRINGS
```

## 44. zfill()
The `zfill()` method adds zeros (0) at the beginning of the string, until it reaches the specified length.

**Syntax**:
#### `string.zfill(length)`
- **length** - The length of the returned string, with `0` digits filled to the left
- **Returns** - A copy of the string with `0` digits to the left of the specified length

**Example**:
```python title="strings.py" showLineNumbers{1} {3-4}
# zfill() method
string = 'Python Strings'
print(string.zfill(20))
print(string.zfill(20).upper())
```

Output

```cmd title="command" showLineNumbers{1} {2-4}
C:\Users\Your Name> python strings.py
000000Python Strings
000000PYTHON STRINGS
```

## 45. +
The `+` operator is used to concatenate two strings.

**Syntax**:
#### `string1 + string2`
- **string1** - Required. First string to be concatenated
- **string2** - Required. Second string to be concatenated
- **Returns** - A concatenated string

**Example**:
```python title="strings.py" showLineNumbers{1} {4}
# + operator
string1 = 'Python'
string2 = 'Strings'
print(string1 + string2)
```

Output

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python strings.py
PythonStrings
```

## 46. *
The `*` operator is used to repeat a string for a given number of times.

**Syntax**:
#### `string * number`
- **string** - Required. The string to be repeated
- **number** - Required. A number specifying how many times the string should be repeated
- **Returns** - A string repeated the specified number of times

**Example**:
```python title="strings.py" showLineNumbers{1} {3-4}
# * operator
string = 'Python Strings'
print(string * 2)
print(string * 3)
```

Output

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\Your Name> python strings.py
Python StringsPython Strings
Python StringsPython StringsPython Strings
```

## 47. []
The `[]` operator is used to slice a string.

**Syntax**:
#### `string[index]`
- **index** - Required. An integer specifying at which position to start the slicing. The indexing starts from `0`
- **Returns** - A sliced string

**Example**:
```python title="strings.py" showLineNumbers{1} {3-4}
# [] operator
string = 'Python Strings'
print(string[0])
print(string[7])
```

Output

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\Your Name> python strings.py
P
S
```

## 48. [:]
The `[:]` operator is used to slice a string.

**Syntax**:
#### `string[start:end:step]`
- **start** (optional) - Optional. An integer specifying at which position to start the slicing. The indexing starts from `0`
- **end** (optional) - Optional. An integer specifying at which position to end the slicing
- **step** (optional) - Optional. An integer specifying the step of the slicing. Default is `1`
- **Returns** - A sliced string

**Example**:
```python title="strings.py" showLineNumbers{1} {3-4}
# [:] operator
string = 'Python Strings'
print(string[:6])
print(string[7:])
```

Output

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\Your Name> python strings.py
Python
Strings
```

:::tip
For more details about slicing, please refer to the [Python Slicing](/tutorial/string-slicing/)
:::

## 49. in
The `in` operator returns `True` if a specified character is present in the string.

**Syntax**:
#### `character in string`
- **character** - Required. A character to be searched for
- **string** - Required. The string to search in
- **Returns** - `True` if the specified character is present in the string

**Example**:
```python title="strings.py" showLineNumbers{1} {3-4}
# in operator
string = 'Python Strings'
print('P' in string)
print('p' in string)
```

Output

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\Your Name> python strings.py
True
False
```

## 50. not in
The `not in` operator returns `True` if a specified character is not present in the string.

**Syntax**:
#### `character not in string`
- **character** - Required. A character to be searched for
- **string** - Required. The string to search in
- **Returns** - `True` if the specified character is not present in the string

**Example**:
```python title="strings.py" showLineNumbers{1} {3-4}
# not in operator
string = 'Python Strings'
print('P' not in string)
print('p' not in string)
```

Output

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\Your Name> python strings.py
False
True
```

## 51. %
The `%` operator is used to format a set of variables enclosed in a "tuple" (a fixed size list), together with a format string, which contains normal text together with "argument specifiers", special symbols like `%s` and `%d`.

**Syntax**:
#### `string % values`
- **string** - Required. A string containing the format string and argument specifiers
- **values** - Required. A tuple containing the values to be formatted
- **Returns** - A formatted string

**Example**:
```python title="strings.py" showLineNumbers{1} {3-4}
# % operator
string = 'Python %s'
print(string % 'Strings')
print(string % 3.6)
```

Output

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\Your Name> python strings.py
Python Strings
Python 3.6
```

## 52. <
The `<` operator is used to compare two strings, to determine if the left string is less than the right string.

**Syntax**:
#### `string1 < string2`
- **string1** - Required. The first string to be compared
- **string2** - Required. The second string to be compared
- **Returns** - `True` if the left string is less than the right string

**Example**:
```python title="strings.py" showLineNumbers{1} {4-5}
# < operator
string1 = 'Python'
string2 = 'Strings'
print(string1 < string2)
print(string1 < 'Python')
```

Output

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\Your Name> python strings.py
True
False
```

## 53. <=
The `<=` operator is used to compare two strings, to determine if the left string is less than or equal to the right string.

**Syntax**:
#### `string1 <= string2`
- **string1** - Required. The first string to be compared
- **string2** - Required. The second string to be compared
- **Returns** - `True` if the left string is less than or equal to the right string

**Example**:
```python title="strings.py" showLineNumbers{1} {4-5}
# <= operator
string1 = 'Python'
string2 = 'Strings'
print(string1 <= string2)
print(string1 <= 'Python')
```

Output

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\Your Name> python strings.py
True
True
```

## 54. >
The `>` operator is used to compare two strings, to determine if the left string is greater than the right string.

**Syntax**:
#### `string1 > string2`
- **string1** - Required. The first string to be compared
- **string2** - Required. The second string to be compared
- **Returns** - `True` if the left string is greater than the right string

**Example**:
```python title="strings.py" showLineNumbers{1} {4-5}
# > operator
string1 = 'Python'
string2 = 'Strings'
print(string1 > string2)
print(string1 > 'Python')
```

Output

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\Your Name> python strings.py
False
False
```

## 55. >=
The `>=` operator is used to compare two strings, to determine if the left string is greater than or equal to the right string.

**Syntax**:
#### `string1 >= string2`
- **string1** - Required. The first string to be compared
- **string2** - Required. The second string to be compared
- **Returns** - `True` if the left string is greater than or equal to the right string

**Example**:
```python title="strings.py" showLineNumbers{1} {4-5}
# >= operator
string1 = 'Python'
string2 = 'Strings'
print(string1 >= string2)
print(string1 >= 'Python')
```

Output

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\Your Name> python strings.py
False
True
```


## 56. ==
The `==` operator is used to compare two strings, to determine if the left string is equal to the right string.

**Syntax**:
#### `string1 == string2`
- **string1** - Required. The first string to be compared
- **string2** - Required. The second string to be compared
- **Returns** - `True` if the left string is equal to the right string

**Example**:
```python title="strings.py" showLineNumbers{1} {4-5}
# == operator
string1 = 'Python'
string2 = 'Strings'
print(string1 == string2)
print(string1 == 'Python')
```

Output

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\Your Name> python strings.py
False
True
```

## 57. !=
The `!=` operator is used to compare two strings, to determine if the left string is not equal to the right string.

**Syntax**:
#### `string1 != string2`
- **string1** - Required. The first string to be compared
- **string2** - Required. The second string to be compared
- **Returns** - `True` if the left string is not equal to the right string

**Example**:
```python title="strings.py" showLineNumbers{1} {4-5}
# != operator
string1 = 'Python'
string2 = 'Strings'
print(string1 != string2)
print(string1 != 'Python')
```

Output

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\Your Name> python strings.py
True
False
```

## 58. ord()
The `ord()` function returns an integer representing the Unicode character.

**Syntax**:
#### `ord(character)`
- **character** - Required. A character
- **Returns** - An integer representing the Unicode character

**Example**:
```python title="strings.py" showLineNumbers{1} {2-3}
# ord() function
print(ord('A'))
print(ord('a'))
```

Output

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\Your Name> python strings.py
65
97
```

## 59. hex()
The `hex()` function converts an integer number to the corresponding hexadecimal string.

**Syntax**:
#### `hex(number)`
- **number** - Required. An integer number (int object)
- **Returns** - A hexadecimal string

**Example**:
```python title="strings.py" showLineNumbers{1} {2-3}
# hex() function
print(hex(255))
print(hex(-42))
```

Output

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\Your Name> python strings.py
0xff
-0x2a
```

## 60. oct()
The `oct()` function converts an integer number to the corresponding octal string.

**Syntax**:
#### `oct(number)`
- **number** - Required. An integer number (int object)
- **Returns** - An octal string

**Example**:
```python title="strings.py" showLineNumbers{1} {2-3}
# oct() function
print(oct(255))
print(oct(-42))
```

Output

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\Your Name> python strings.py
0o377
-0o52
```

## 61. bin()
The `bin()` function converts an integer number to the corresponding binary string.

**Syntax**:
#### `bin(number)`
- **number** - Required. An integer number (int object)
- **Returns** - A binary string

**Example**:
```python title="strings.py" showLineNumbers{1} {2-3}
# bin() function
print(bin(255))
print(bin(-42))
```

Output

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\Your Name> python strings.py
0b11111111
-0b101010
```

## 62. chr()
The `chr()` function returns a character (a string) from an integer (represents unicode code point of the character).

**Syntax**:
#### `chr(number)`
- **number** - Required. An integer representing the Unicode code point of the character
- **Returns** - A character (a string) from an integer (represents unicode code point of the character)

**Example**:
```python title="strings.py" showLineNumbers{1} {2-3}
# chr() function
print(chr(65))
print(chr(97))
```

Output

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\Your Name> python strings.py
A
a
```

## 63. len()
The `len()` function returns the number of items (length) in an object.

**Syntax**:
#### `len(object)`
- **object** - Required. An object (string, bytes or array etc.)
- **Returns** - The number of items in an object

**Example**:
```python title="strings.py" showLineNumbers{1} {2-3}
# len() function
print(len('Python'))
print(len('Python Strings'))
```

Output

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\Your Name> python strings.py
6
14
```

## 64. repr()
The `repr()` function returns a printable representation of the given object.

**Syntax**:
#### `repr(object)`
- **object** - Required. Any object, like lists, tuples, strings etc.
- **Returns** - A printable representation of the given object

**Example**:
```python title="strings.py" showLineNumbers{1} {2-3}
# repr() function
print(repr('Python'))
print(repr('Python Strings'))
```

Output

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\Your Name> python strings.py
'Python'
'Python Strings'
```

## 65. ascii()
The `ascii()` function returns a readable version of any object (Strings, Tuples, Lists, etc).

**Syntax**:
#### `ascii(object)`
- **object** - Required. Any object, like lists, tuples, strings etc.
- **Returns** - A readable version of any object (Strings, Tuples, Lists, etc)

**Example**:
```python title="strings.py" showLineNumbers{1} {2-3}
# ascii() function
print(ascii('Python'))
print(ascii('Python Strings'))
```

Output

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\Your Name> python strings.py
'Python'
'Python Strings'
```

## 66. max()
The `max()` function returns the largest item in an iterable.

**Syntax**:
#### `max(iterable)`
- **iterable** - Required. An iterable object (list, tuple, string etc.)
- **Returns** - The largest item in the given iterable

**Example**:
```python title="strings.py" showLineNumbers{1} {2-3}
# max() function
print(max('Python'))
print(max('Python Strings'))
```

Output

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\Your Name> python strings.py
y
y
```

## 67. min()
The `min()` function returns the smallest item in an iterable.

**Syntax**:
#### `min(iterable)`
- **iterable** - Required. An iterable object (list, tuple, string etc.)
- **Returns** - The smallest item in the given iterable

**Example**:
```python title="strings.py" showLineNumbers{1} {2-3}
# min() function
print(min('Python'))
print(min('Python Strings'))
```

Output

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\Your Name> python strings.py
P
P
```

## 68. str()
The `str()` function returns the string version of the given object.

**Syntax**:
#### `str(object)`
- **object** - Required. An object to be converted to string
- **Returns** - The string version of the given object

**Example**:
```python title="strings.py" showLineNumbers{1} {2-3}
# str() function
print(str(3.6))
print(str(3.6) + ' is a float number')
```

Output

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\Your Name> python strings.py
3.6
3.6 is a float number
```

## 69. type()
The `type()` function returns the type of the specified object.

**Syntax**:
#### `type(object)`
- **object** - Required. An object whose type needs to be returned
- **Returns** - The type of the specified object

**Example**:
```python title="strings.py" showLineNumbers{1} {2-3}
# type() function
print(type('Python'))
print(type(3.6))
```

Output

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\Your Name> python strings.py
<class 'str'>
<class 'float'>
```

## 70. help()
The `help()` function is used to display the documentation of modules, functions, classes, keywords etc.

**Syntax**:
#### `help(object)`
- **object** - Required. The object to be described
- **Returns** - The documentation of the specified object

**Example**:
```python title="strings.py" showLineNumbers{1} {2}
# help() function
print(help(str.upper))
```

Output

```cmd title="command" showLineNumbers{1} {2-7}
C:\Users\Your Name> python strings.py
Help on method_descriptor:

upper(self, /)
    Return a copy of the string converted to uppercase.

None
```

## Conclusion
In this tutorial, we have learned about the Python string methods and operators with the help of examples. We have also learned about the built-in functions that can be used with strings. Now you can use these methods and operators to manipulate strings in your Python programs. 

:::tip
For more details about Python strings methods and operators, please refer to [Python String Methods](https://docs.python.org/2/library/string.html) and [Python String Operators](https://docs.python.org/2/library/stdtypes.html#string-methods) documentation.
:::