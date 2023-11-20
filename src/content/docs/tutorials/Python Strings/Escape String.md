---
title: Python Escape String
description: How to escape a string in Python. Learn how to use escape characters in Python to manipulate text, control formatting, and handle special characters. 
sidebar: 
    order: 19
---

:::danger
In python, a string is a sequence of Unicode characters. Unicode was introduced to include every character in all languages and bring uniformity in encoding. Unicode has a unique code for every character irrespective of the platform, program, or language.

You get error when you try to use a special character in a string. For example, if you use a single quote to represent a string, you will get an error.
```python title="strings.py" showLineNumbers{1} {2}
# single quote string
print('Python's string')
```

Output

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python strings.py
Traceback (most recent call last):
    File "<stdin>", line 1
    print('Python's string')
          ^^^^^^^^^
SyntaxError: invalid syntax. Perhaps you forgot a comma?
```
:::

Escape characters in Python are special characters that don't get printed as-is but instead signal some specific action. They allow you to include special characters in strings or control the formatting of text. In this comprehensive guide, we'll explore the world of escape characters in Python and how they can be used to enhance text manipulation.

## Basics of Escape Characters

Escape characters are denoted by a backslash (`\`) followed by a specific character or sequence. The backslash tells Python that the character following it has a special meaning.

#### Escape Characters in Python
|Sequence|Escape Character|Escape Character Name|Description|
|:---|:---|:---| :---|
|1|`\n`|Newline|Inserts a new line|
|2|`\t`|Tab|Inserts a tab|
|3|`\r`|Carriage Return|Inserts a carriage return|
|4|`\b`|Backspace|Inserts a backspace|
|5|`\f`|Form Feed|Inserts a form feed|
|6|`\v`|Vertical Tab|Inserts a vertical tab|
|7|`\\`|Backslash|Inserts a backslash|
|8|`\'`|Single Quote|Inserts a single quote|
|9|`\"`|Double Quote|Inserts a double quote|
|10|`\a`|Bell|Inserts a bell|
|11|`\0`|Null Byte|Inserts a null byte|
|12|`\N{name}`|Unicode Character|Inserts a Unicode character|
|13|`\xhh`|Hexadecimal Character|Inserts a hexadecimal character|
|14|`\uhhhh`|Unicode 16-bit Hexadecimal Character|Inserts a Unicode 16-bit hexadecimal character|
|15|`\Uhhhhhhhh`|Unicode 32-bit Hexadecimal Character|Inserts a Unicode 32-bit hexadecimal character|
|16|`\ooo`|Octal Character|Inserts an octal character|

## Newline Escape Character

The newline escape character (`\n`) inserts a new line into a string. It's useful for formatting text and creating line breaks. For example, you can use it to print a string on multiple lines:

```python title="strings.py" showLineNumbers{1} {2}
# print string on multiple lines
print('This is a string\non multiple lines')
```

Output

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python strings.py
This is a string
on multiple lines
```

## Tab Escape Character

The tab escape character (`\t`) inserts a tab into a string. It's useful for formatting text and creating tabbed sections. For example, you can use it to print a string with a tab:

```python title="strings.py" showLineNumbers{1} {2}
# print string with tab
print('This is a string\twith a tab')
```

Output

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python strings.py
This is a string    with a tab
```

## Carriage Return Escape Character

The carriage return escape character (`\r`) inserts a carriage return into a string. It's useful for formatting text and creating line breaks. For example, you can use it to print a string on multiple lines:

```python title="strings.py" showLineNumbers{1} {2}
# print string on multiple lines
print('This is a string\ron multiple lines')
```

Output

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python strings.py
This is a string
on multiple lines
```

## Backspace Escape Character

The backspace escape character (`\b`) inserts a backspace into a string. It's useful for formatting text and creating tabbed sections. For example, you can use it to print a string with a backspace:

```python title="strings.py" showLineNumbers{1} {2}
# print string with backspace
print('This is a string\bwith a backspace')
```

Output

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python strings.py
This is a stringwith a backspace
```

## Form Feed Escape Character

The form feed escape character (`\f`) inserts a form feed into a string. It's useful for formatting text and creating line breaks. For example, you can use it to print a string on multiple lines:

```python title="strings.py" showLineNumbers{1} {2}
# print string on multiple lines
print('This is a string\fon multiple lines')
```

Output

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python strings.py
This is a string
on multiple lines
```

## Vertical Tab Escape Character

The vertical tab escape character (`\v`) inserts a vertical tab into a string. It's useful for formatting text and creating tabbed sections. For example, you can use it to print a string with a vertical tab:

```python title="strings.py" showLineNumbers{1} {2}
# print string with vertical tab
print('This is a string\vwith a vertical tab')
```

Output

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python strings.py
This is a string
with a vertical tab
```

## Backslash Escape Character

The backslash escape character (`\\`) inserts a backslash into a string. It's useful for formatting text and creating tabbed sections. For example, you can use it to print a string with a backslash:

```python title="strings.py" showLineNumbers{1} {2}
# print string with backslash
print('This is a string\\with a backslash')
```

Output

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python strings.py
This is a string\with a backslash
```

## Single Quote Escape Character

The single quote escape character (`\'`) inserts a single quote into a string. It's useful for formatting text and creating tabbed sections. For example, you can use it to print a string with a single quote:

```python title="strings.py" showLineNumbers{1} {2}
# print string with single quote
print('This is a string\'with a single quote')
```

Output

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python strings.py
This is a string'with a single quote
```

## Double Quote Escape Character

The double quote escape character (`\"`) inserts a double quote into a string. It's useful for formatting text and creating tabbed sections. For example, you can use it to print a string with a double quote:

```python title="strings.py" showLineNumbers{1} {2}
# print string with double quote
print('This is a string\"with a double quote')
```

Output

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python strings.py
This is a string"with a double quote
```

## Bell Escape Character

The bell escape character (`\a`) inserts a bell into a string. It's useful for formatting text and creating tabbed sections. For example, you can use it to print a string with a bell:

```python title="strings.py" showLineNumbers{1} {2}
# print string with bell
print('This is a string\awith a bell')
```

Output

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python strings.py
This is a stringwith a bell 
```
:::note
In this example, after executing the print statement, the bell sound will be heard 🔔. If you don't want to hear the bell sound, you can use the following code:
```python title="strings.py" showLineNumbers{1} {2}
# print string with bell
print('This is a string\awith a bell', end='')
```

Output

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python strings.py
This is a stringwith a bell
```
:::

## Null Byte Escape Character

The null byte escape character (`\0`) inserts a null byte into a string. It's useful for formatting text and creating tabbed sections. For example, you can use it to print a string with a null byte:

```python title="strings.py" showLineNumbers{1} {2}
# print string with null byte
print('This is a string\0with a null byte')
```

Output

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python strings.py
This is a stringwith a null byte
```

## Unicode Character Escape Character

The Unicode character escape character (`\N{name}`) inserts a Unicode character into a string. It's useful for formatting text and creating tabbed sections. For example, you can use it to print a string with a Unicode character:

```python title="strings.py" showLineNumbers{1} {2}
# print string with Unicode character
print('This is a string\N{COPYRIGHT SIGN}with a Unicode character')
```

Output

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python strings.py
This is a string©with a Unicode character
```

## Hexadecimal Character Escape Character

The hexadecimal character escape character (`\xhh`) inserts a hexadecimal character into a string. It's useful for formatting text and creating tabbed sections. For example, you can use it to print a string with a hexadecimal character:

```python title="strings.py" showLineNumbers{1} {2}
# print string with hexadecimal character
print('This is a string\x24with a hexadecimal character')
```

Output

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python strings.py
This is a string$with a hexadecimal character
```

## Unicode 16-bit Hexadecimal Character Escape Character

The Unicode 16-bit hexadecimal character escape character (`\uhhhh`) inserts a Unicode 16-bit hexadecimal character into a string. It's useful for formatting text and creating tabbed sections. For example, you can use it to print a string with a Unicode 16-bit hexadecimal character:

```python title="strings.py" showLineNumbers{1} {2}
# print string with Unicode 16-bit hexadecimal character
print('This is a string\u0024with a Unicode 16-bit hexadecimal character')
```

Output

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python strings.py
This is a string$with a Unicode 16-bit hexadecimal character
```

## Unicode 32-bit Hexadecimal Character Escape Character

The Unicode 32-bit hexadecimal character escape character (`\Uhhhhhhhh`) inserts a Unicode 32-bit hexadecimal character into a string. It's useful for formatting text and creating tabbed sections. For example, you can use it to print a string with a Unicode 32-bit hexadecimal character:

```python title="strings.py" showLineNumbers{1} {2}
# print string with Unicode 32-bit hexadecimal character
print('This is a string\U00000024with a Unicode 32-bit hexadecimal character')
```

Output

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python strings.py
This is a string$with a Unicode 32-bit hexadecimal character
```

## Octal Character Escape Character

The octal character escape character (`\ooo`) inserts an octal character into a string. It's useful for formatting text and creating tabbed sections. For example, you can use it to print a string with an octal character:

```python title="strings.py" showLineNumbers{1} {2}
# print string with octal character
print('This is a string\044with an octal character')
```

Output

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python strings.py
This is a string$with an octal character
```


## Conclusion

Escape characters in Python are powerful tools for manipulating text, controlling formatting, and handling special characters. Understanding how to use escape sequences enhances your ability to work with strings and create well-formatted, readable code.

As you continue your Python journey, experiment with different escape characters, explore their applications, and incorporate them into your projects. Whether you're working with strings, handling special characters, or managing formatting, escape characters are valuable assets in your programming toolbox.

For more tips, tricks, and practical examples, check out our tutorials on Python Central Hub!