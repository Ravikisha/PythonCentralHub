---
title: For Loop in Python
description: Learn about for loop in Python. for loop is used to iterate over a sequence (list, tuple, string) or other iterable objects. We will learn about for loop, range() function, break, continue, and pass statement in Python. In the end, we will also learn about the else clause in for loop.
sidebar: 
    order: 36
---


<!-- ## and Operator
#### `and` Operator
The `and` operator returns `True` if both operands are `True`. Otherwise, it returns `False`. The following example demonstrates how to use the `and` operator in Python:

```python title="operators.py" showLineNumbers{1} {4-5}
# and operator
x = 10
y = 5
z = x < 10 and y > 1
t = x < 10 and y < 1
print(z)
print(t)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\Your Name> python operators.py
True
False
```

In the above example, we have used the `and` operator to combine two conditions. Since both conditions are `True`, the result of the `and` operator is `True`. The result of the `and` operator is then assigned to the variable `z`. The value of `z` is then printed to the console. -->

## Unveiling the Power of for Loops in Python
In Python, the for loop is a versatile and fundamental construct that facilitates the iteration over a sequence of elements. Whether you're working with lists, strings, or other iterable objects, the for loop simplifies the process of executing a set of statements for each item in the sequence. In this comprehensive guide, we'll explore the syntax, functionality, and best practices associated with for loops in Python.

### What Is a for Loop?
A for loop is a Python statement which repeats a group of statements a specified number of times. You can iterate over any object that is iterable, such as a list, tuple, string, and so on. 

In Python, you can use the for loop in two ways:
- **Iterating over a sequence**: We can use a for loop to iterate over a sequence. The sequence can be a list, tuple, string, or any other iterable object.
- **Iterating over a range**: In Python, we can also use a for loop to iterate over a range. Using a for loop with a range() function, we can execute a set of statements for each item in a range.

### Syntax of for Loop
The syntax of the for loop in Python is:

```python title="Syntax" showLineNumbers{1}
for val in sequence:
    Body of for
```

Here, `val` is the variable that takes the value of the item inside the sequence on each iteration.

Loop continues until we reach the last item in the sequence. The body of for loop is separated from the rest of the code using indentation.

## Example: Python for Loop
```python title="for_loop.py" showLineNumbers{1} {3-5}
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

In this program, we have used the for loop to iterate over a list and calculate the sum of numbers. We initialize the `sum` variable to zero and iterate over each element of the list using a for loop and add it to the `sum` variable. Finally, we print the `sum` variable which contains the sum of numbers in the given list.

## range function
#### `range()` function
The `range()` function is used to generate a sequence of numbers. It returns an object that produces a sequence of integers from start (inclusive) to stop (exclusive) by step. `range(i, j)` produces `i, i+1, i+2, ..., j-1`. Start defaults to 0, and stop is omitted! `range(4)` produces `0, 1, 2, 3`. These are exactly the valid indices for a list of 4 elements. When step is given, it specifies the increment (or decrement). For example, `range(1, 5)` produces `1, 2, 3, 4`. `range(6, 1, -1)` produces `6, 5, 4, 3, 2`.

### Syntax of range()
The syntax of the range() function is:

```python title="Syntax" showLineNumbers{1}
range(start, stop[, step])
```
- `range()` takes three arguments.
- `start` is the starting number of the sequence. It defaults to 0 if not specified.
- `stop` is the last number of the sequence. It does not include this number. The `range()` function goes up to `stop - 1`.
- `step` is the difference between each number in the sequence. It defaults to 1 if not specified.
- The `range()` function only works with the integers. Float is not allowed. If you need a range of floats, you can use the `numpy` library.
- It returns a range object. You need to convert it to a list to see the sequence of numbers.

### Example: range() function
```python title="range_function.py" showLineNumbers{1} {2-5}
# range() function
print(range(10))
print(list(range(10)))
print(list(range(2, 8)))
print(list(range(2, 20, 3)))
```

Output:

```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\Your Name> python range_function.py
range(0, 10)
[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
[2, 3, 4, 5, 6, 7]
[2, 5, 8, 11, 14, 17]
```

In this program, we have used the `range()` function to generate a sequence of numbers. We have passed one, two, and three arguments to the `range()` function. When we pass only one argument, it starts generating numbers from 0 and stops before the specified number. When we pass two arguments, it starts from the first argument and stops before the second argument. The third argument is the step size. The `range()` function increments the number by the step size until it reaches the second argument. The third argument is optional. If we do not specify the step size, it increments the number by 1. 

In the above example, we have converted the range object to a list using the `list()` function. The `list()` function converts the range object to a list.

## for loop with else
