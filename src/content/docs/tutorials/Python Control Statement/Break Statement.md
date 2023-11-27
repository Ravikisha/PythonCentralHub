---
title: Break Statement in Loop in Python
description: Learn to use break statement to exit loop in Python. Also learn to use break with while and for loop. In this tutorial, we will learn to use break statement with the help of examples.
sidebar: 
    order: 38
---

## Breaking Free: Understanding the break Statement in Python Loops
In Python, the break statement is a powerful tool that allows you to prematurely exit from a loop. Whether you are iterating over a sequence, waiting for a condition to be met, or handling user input, the break statement provides a means to escape the loop's execution. In this comprehensive guide, we will explore the syntax, functionality, and best practices associated with the break statement in Python loops.

### What Is the break Statement?
The break statement is a control flow statement that allows you to terminate the execution of a loop prematurely. When a break statement is encountered inside a loop, the loop is immediately terminated and the program control resumes at the next statement following the loop.

:::note
The break statement can be used in both while and for loops.
:::

## Syntax of break
The syntax of a break statement in Python:

### Break Statement in while Loop
```python title="break_while_loop.py" {1-5}
while test_expression:
    Body of while
    if test_expression:
        break
```

### Break Statement in for Loop
```python title="break_for_loop.py" {1-5}
for val in sequence:
    Body of for
    if test_expression:
        break
```

Here, `val` is the variable that takes the value of the item inside the sequence on each iteration.

We generally use break statement inside the loop when we want to exit it immediately, for example, when some condition is met.

## Example of break Statement in Python
Here is an example of a break statement in python:

### break Statement in while Loop
```python title="break_while_loop.py" showLineNumbers{1} {2-10}
# break in while loop
i = 0
while i < 10:
    print(i)
    i += 1
    if i == 5:
        break
```

Output:

```cmd title="command" showLineNumbers{1} {2-7}
C:\Users\Your Name> python break_while_loop.py
0
1
2
3
4
```

In this program, we iterate through the `i` variable. We increment the `i` variable by 1 on each iteration. We check if the value of the `i` variable is 5. If it is, we break from the loop. Hence, we see in our output that only the values till 4 are printed.

### break Statement in for Loop
```python title="break_for_loop.py" showLineNumbers{1} {2-7}
# break in for loop
for val in "string":
    if val == "i":
        break
    print(val)
print("The end")
```

Output:

```cmd title="command" showLineNumbers{1} {2-5}
C:\Users\Your Name> python break_for_loop.py
s
t
r
The end
```

In this program, we iterate through the `"string"` sequence. We check if the letter is `i`, upon which we break from the loop. Hence, we see in our output that only the letters till `r` are printed.


## Use Cases for the `break` Statement

### 1. **Searching for a Specific Element:**

The `break` statement is commonly used when searching for a specific element in a sequence. Once the target element is found, there is no need to continue the loop.

```python title="break_search.py" showLineNumbers{1} {2-6}
numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9]
for number in numbers:
    if number == 5:
        print("Number found!")
        break
```

### 2. **Terminating Infinite Loops:**

In scenarios where a loop should continue indefinitely until a certain condition is met, the `break` statement can be employed to terminate the loop.

```python title="break_infinite.py" showLineNumbers{1} {2-6}
while True:
    user_input = input("Enter a number: ")
    if user_input.isdigit():
        break
    else:
        print("Invalid input. Please enter a number.")
```

In this example, the loop continues to prompt the user for input until a valid number is entered.

### 3. **Handling User Interruption:**

The `break` statement is useful for handling user interruptions, such as keyboard interrupts (`Ctrl+C`), allowing graceful termination of the loop.

```python title="break_interrupt.py" showLineNumbers{1} {2-6}
try:
    while True:
        print("Looping...")
except KeyboardInterrupt:
    print("\nLoop interrupted by user.")
```

## Best Practices for Using the `break` Statement

### 1. **Use `break` Sparingly:**

While the `break` statement provides a convenient way to exit a loop prematurely, it should be used sparingly. Overreliance on `break` statements can lead to code that is challenging to understand and maintain.

### 2. **Clearly Document Break Conditions:**

When using `break`, it's essential to provide clear comments or documentation explaining the conditions under which the loop will be terminated. This enhances code readability and helps future developers understand the logic.

```python
# Terminate the loop when the target element is found
for item in my_list:
    if item == target:
        break
```

### 3. **Consider Alternative Control Flow:**

In some cases, restructuring the loop or using other control flow mechanisms might provide a more readable and maintainable solution than relying on `break`.

### 4. **Avoid Breaking Out of Nested Loops:**

While it is possible to use `break` to exit from nested loops, it can lead to less readable code. Consider using a flag variable or restructuring the code to avoid this scenario.

## Conclusion

The `break` statement in Python loops offers a powerful mechanism for controlling the flow of a program. When used judiciously, it provides a concise way to exit a loop based on a specific condition. However, care should be taken to ensure that its usage enhances code clarity and readability rather than complicating it.

As you explore the world of Python programming, experiment with the `break` statement in various scenarios. Gain a deeper understanding of when and how to use it effectively to enhance the efficiency of your code. For more insights and practical examples, check out our tutorials on Python Central Hub!