---
title: While Loop in Python
description: Learn about while loop in Python. How to use while loop in Python. How to use break and continue statement in while loop. How to use else statement with while loop. How to use nested while loop in Python. How to use while loop with list and dictionary in Python. How to use while loop with range() function in Python. How to use while loop with enumerate() function in Python.
sidebar: 
    order: 37
---

## Unveiling the Power of for Loops in Python
In Python, the for loop is a versatile and fundamental construct that facilitates the iteration over a sequence of elements. Whether you're working with lists, strings, or other iterable objects, the for loop simplifies the process of executing a set of statements for each item in the sequence. In this comprehensive guide, we'll explore the syntax, functionality, and best practices associated with for loops in Python.

### What Is a While Loop?
A while loop is a control flow statement that allows code to be executed repeatedly based on a given Boolean condition. The while loop can be thought of as a repeating if statement.

The while loop is used extensively in Python and alone with for and if-else loops, forms the basis of manipulating data in the language.

### Syntax of while Loop in Python
The syntax of a while loop in Python programming language is −

```python
while expression:
   statement(s)
```

Here, statement(s) may be a single statement or a block of statements. The condition may be any expression, and true is any non-zero value. The loop iterates while the condition is true.

When the condition becomes false, program control passes to the line immediately following the loop.

:::note
In Python, all the statements indented by the same number of character spaces after a programming construct are considered to be part of a single block of code. Python uses indentation as its method of grouping statements.
:::

:::tip
A while loop is also known as condition-controlled loop.
:::

<!-- ```python title="for_loop.py" showLineNumbers{1} {3-5}
# for loop
numbers = [6, 5, 3, 8, 4, 2, 5, 4, 11]
sum = 0
for val in numbers:
    sum = sum+val
print("The sum is", sum)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\Your Name> python for_loop.py
The sum is 48
```

In this program, we have used the for loop to iterate over a list and calculate the sum of numbers. We initialize the `sum` variable to zero and iterate over each element of the list using a for loop and add it to the `sum` variable. Finally, we print the `sum` variable which contains the sum of numbers in the given list. -->

## Example of while Loop in Python
Here is an example of while loop in Python:

```python title="while_loop.py" showLineNumbers{1} {2-6}
# while loop
numbers = [6, 5, 3, 8, 4, 2, 5, 4, 11]
sum = 0
i = 0
while i < len(numbers):
    sum = sum + numbers[i]
    i = i+1
print("The sum is", sum)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\Your Name> python while_loop.py
The sum is 48
```
