---
title: For Loop in Python
description: Learn about for loop in Python. for loop is used to iterate over a sequence (list, tuple, string) or other iterable objects. We will learn about for loop, range() function, break, continue, and pass statement in Python. In the end, we will also learn about the else clause in for loop.
sidebar: 
    order: 36
---

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

## Structure of for Loop
- **Initialization**: In this step, we initialize the variable `val` with the first item in the sequence. This is the first item in the sequence.
    ```python title="Syntax" showLineNumbers{1}
    for val in sequence:
    ```
    Here, `val` is the variable that takes the value of the item inside the sequence on each iteration.

- **Condition**: In this step, the `val` variable is checked to be less than or equal to the last item in the sequence. If it is true, the body of the for loop is executed. Otherwise, the loop terminates.
    ```python title="Syntax" showLineNumbers{1}
    for val in sequence:
    ```
    Here, `val` is the variable that takes the value of the item inside the sequence on each iteration.

- **Body**: The body of the for loop is separated from the rest of the code using indentation.
    ```python title="Syntax" showLineNumbers{1}
    for val in sequence:
        Body of for
    ```
    Here, `Body of for` is the body of the loop. It can contain one or more statements. It is executed once for each item in the sequence.

- **Increment/Decrement**: In this step, the variable `val` is incremented or decremented. The next item in the sequence is assigned to the variable `val`. This continues until the last item in the sequence is reached.
    ```python title="Syntax" showLineNumbers{1}
    for val in sequence:
        Body of for
    ```
    Here, Loop continues until we reach the last item in the sequence. The body of for loop is separated from the rest of the code using indentation.


:::tip
A for loop is also known as an iteration or looping statement. It is called as counter-controlled loop.
:::


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

## For Loop with else
For loops also have an `else` clause which most of us are unfamiliar with. The `else` clause executes after the loop completes normally. This means that the loop did not encounter any `break` statement. The `else` clause won't execute if the loop breaks prematurely.

### Syntax of for loop with else
The syntax of the for loop with the `else` clause is:

```python title="Syntax" showLineNumbers{1}
for val in sequence:
    Body of for
else:
    Body of else
```

The `else` clause is only executed when your `for` loop ends normally. This means that the `loop` didn't encounter any `break` or `return` statement.

### Example of for loop with else
```python title="for_loop_else.py" showLineNumbers{1} {3-5}
# for loop with else
digits = [0, 1, 5]
for i in digits:
    print(i)
else:
    print("No items left.")
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\Your Name> python for_loop_else.py
0
1
5
No items left.
```

In this program, we have used the `for` loop with the `else` clause. The `else` clause executes after the completion of the `for` loop. The `else` clause will be executed even if there is a `continue` statement inside the `for` loop (but not if `break` is encountered).

:::note
The `else` block just after `for/while` is executed only when the loop is NOT terminated by a `break` statement.
:::

## Iterating by Sequence Index
In Python, we can also access the sequence items using the index. The index starts from 0 in Python. We can use the index to iterate over a sequence. Consider the following example:

```python title="for_loop_index.py" showLineNumbers{1} {3-5}
# iterating by index
genre = ['pop', 'rock', 'jazz']
for i in range(len(genre)):
    print("I like", genre[i])
```

Output:

```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\Your Name> python for_loop_index.py
I like pop
I like rock
I like jazz
```

In this program, we have used the `len()` function to get the size of the list. The `range()` function then generates a sequence of numbers which is used to iterate over the list using the `for` loop. We use the `len()` function in the `range()` function so that the `for` loop runs the same number of times as the number of items in the list. We use the `i` index to access each element in the list `genre`.

## Iterating by Range Function
We can use the Python `range()` function to iterate over a sequence of numbers. It can be combined with the `len()` function to iterate over a sequence using indexing. Here is an example:

```python title="for_loop_range.py" showLineNumbers{1} {3-5}
# iterating by range()
for i in range(0, 10):
    print(i)
```

Output:

```cmd title="command" showLineNumbers{1} {2-12}
C:\Users\Your Name> python for_loop_range.py
0
1
2
3
4
5
6
7
8
9
```

In this program, we have used the `range()` function to iterate over a sequence of numbers. We can also specify the start, stop, and step size as `range(start, stop, step size)`. We have used `0` as the start, `10` as the stop, and `1` as the step size in the `range()` function. It returns a sequence of numbers starting from `0` to `9` (10 numbers).

## For Loop Through a String
Even strings are iterable objects, they contain a sequence of characters:

```python title="for_loop_string.py" showLineNumbers{1} {3-5}
# for loop through a string
genre = 'Rock'
for i in range(len(genre)):
    print("I like", genre[i])
```

Output:

```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\Your Name> python for_loop_string.py
I like R
I like o
I like c
I like k
```

In this program, we have used the `len()` function to get the size of the string. The `range()` function then generates a sequence of numbers which is used to iterate over the string using the `for` loop. We use the `len()` function in the `range()` function so that the `for` loop runs the same number of times as the number of characters in the string. We use the `i` index to access each character in the string `genre`.

You can also iterate over a string using a for loop without the `range()` function. For example:

```python title="for_loop_string.py" showLineNumbers{1} {3-5}
# for loop through a string
genre = 'Rock'
for i in genre:
    print("I like", i)
```

Output:

```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\Your Name> python for_loop_string.py
I like R
I like o
I like c
I like k
```

In this program, we have used the `for` loop to iterate over the string `genre`. We have not used the `range()` function. We have directly accessed each character using the `i` index in the `for` loop.

You can also use the `for` loop to iterate over a sequence of lists. Consider the following example:

```python title="for_loop_list.py" showLineNumbers{1} {3-5}
# for loop with else
digits = [0, 1, 5]
for i in digits:
    print(i)
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\Your Name> python for_loop_list.py
0
1
5
```

In this program, we have used the `for` loop to iterate over a list `digits`. We have not used the `range()` function. We have directly accessed each element using the `i` index in the `for` loop.

## Nested for Loop
In Python, a nested `for` loop is a loop inside a loop. The "inner loop" will be executed one time for each iteration of the "outer loop":

#### Syntax of Nested for Loop
```python title="Syntax" showLineNumbers{1}
for [first iterating variable] in [outer loop]: # Outer loop
    [do something]  # Optional
    for [second iterating variable] in [nested loop]:   # Nested loop
        [do something] # Optional
```

### Example of Nested for Loop
```python title="nested_for_loop.py" showLineNumbers{1} {3-5}
# nested for loop
for i in range(1, 6):
    for j in range(i):
        print(i, end=' ')
    print()
```

Output:

```cmd title="command" showLineNumbers{1} {2-7}
C:\Users\Your Name> python nested_for_loop.py
1
2 2
3 3 3
4 4 4 4
5 5 5 5 5
```

In this program, we have used the nested `for` loop to iterate over a sequence of numbers. We have used the `range()` function to generate a sequence of numbers. We have used the `i` index to print the number of stars in each row. We have used the `j` index to print the stars in each row. The `j` index depends on the `i` index. The value of the `i` index is used to determine the number of stars in each row. The value of the `j` index is used to print the stars in each row. The value of the `j` index is incremented by 1 in each iteration of the inner `for` loop. The inner `for` loop is executed `i` times for each iteration of the outer `for` loop. The outer `for` loop is executed 5 times. The inner `for` loop is executed 1 time in the first iteration of the outer `for` loop. The inner `for` loop is executed 2 times in the second iteration of the outer `for` loop. The inner `for` loop is executed 3 times in the third iteration of the outer `for` loop. The inner `for` loop is executed 4 times in the fourth iteration of the outer `for` loop. The inner `for` loop is executed 5 times in the fifth iteration of the outer `for` loop. The inner `for` loop is executed 1 + 2 + 3 + 4 + 5 = 15 times.


## Reverse Iteration/Loop
In Python, we can also iterate over a sequence in reverse, i.e., from the last item to the first item. We can do this by using the negative index. Consider the following example:

```python title="for_loop_reverse.py" showLineNumbers{1} {3-5}
# reverse iteration
for val in range(10, 0, -1):
    print(val)
```

Output:

```cmd title="command" showLineNumbers{1} {2-11}
C:\Users\Your Name> python for_loop_reverse.py
10
9
8
7
6
5
4
3
2
1
```

In this program, we have used the `range()` function to generate a sequence of numbers. We have used the negative index to iterate over the sequence in reverse. We have used `-1` as the step size in the `range()` function. It returns a sequence of numbers starting from `10` to `1` (10 numbers).


## Conclusion
In this tutorial, we have learned about the for loop in Python. We have learned how to use the for loop to iterate over a sequence of elements. We have also learned how to use the range() function to iterate over a sequence of numbers. We have also learned how to use the for loop to iterate over a string and a list. We have also learned how to use the nested for loop to iterate over a sequence of numbers. We have also learned how to use the else clause with the for loop.

As you delve deeper into Python programming, experiment with different for loops, explore their applications in real-world scenarios, and use them to enhance the efficiency and clarity of your code. For more hands-on examples and in-depth tutorials, explore our resources on Python Central Hub!