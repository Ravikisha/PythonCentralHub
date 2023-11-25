---
title: If-else Statement in Python
description: Learn about if-else statement in Python. The if-else statement is used to execute a block of code based on a condition. We will learn about the syntax of the if-else statement in Python. We will also learn about the ternary operator in Python.
sidebar: 
    order: 33
---

## Mastering If-else Statement in Python: A Comprehensive Guide
The if-else statement in Python is used to execute a block of code based on a condition. Understanding the if-else statement is fundamental to writing flexible and dynamic Python programs. In this comprehensive guide, we'll explore the syntax and usage of the if-else statement in Python.

## What is the If-else Statement in Python?
The if-else statement in Python is used to execute a block of code based on a condition. The if-else statement is also known as the if-then-else statement. The if-else statement is a selection statement, which is a type of control statement in Python.


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

## Syntax of the If-else Statement in Python
The syntax of the if-else statement in Python is as follows:

```python title="Syntax" showLineNumbers{1} {1,3}
if condition:
    # code to execute if condition is True
else:
    # code to execute if condition is False
```

The if-else statement begins with the `if` keyword, followed by a condition. The condition is followed by a colon (`:`). The code to execute if the condition is `True` is written on the next line, indented by four spaces. The code to execute if the condition is `False` is written after the `else` keyword, on the next line, indented by four spaces.

## Rules for Writing the If-else Statement in Python
The following are the rules for writing the if-else statement in Python:
- The `if` keyword must be followed by a condition.
- The condition must be followed by a colon (`:`).
- The code to execute if the condition is `True` must be indented by four spaces.
- The `else` keyword must be followed by a colon (`:`).
- The code to execute if the condition is `False` must be indented by four spaces.
- The `else` clause is optional.
- The `else` clause must be written after the `if` clause.
- The `else` clause must be written before the `elif` clause.
- The `else` clause must be written after the `elif` clause.
- The `elif` clause is optional.
- The `elif` clause must be written after the `if` clause.
- The `elif` clause must be written before the `else` clause.
- The `elif` clause must be written after the `elif` clause.
- The `elif` keyword must be followed by a condition.

:::tip
The `else` clause is optional. If the `else` clause is not present, the code to execute if the condition is `False` is not executed.
:::

There are five ways to write the if-else statement in Python:
- `if` statement
- `if-else` statement
- `if-elif-else` statement
- `nested if-else` statement
- `ternary operator` statement


## If Statement
#### `if` Statement
The `if` statement in Python is used to execute a block of code if a condition is `True`. The `if` statement is also known as the `if-then` statement. The `if` statement is a selection statement, which is a type of control statement in Python.

The syntax of the `if` statement in Python is as follows:

```python title="Syntax" showLineNumbers{1} {1}
if condition:
    # code to execute if condition is True
```

The `if` statement begins with the `if` keyword, followed by a condition. The condition is followed by a colon (`:`). The code to execute if the condition is `True` is written on the next line, indented by four spaces.

:::tip
The `if` statement does not have an `else` clause. If you want to execute a block of code if the condition is `False`, you should use the `if-else` statement.
:::

The following example demonstrates how to use the `if` statement in Python:

```python title="if.py" showLineNumbers{1} {3}
# if statement
x = 10
if x > 5:
    print("x is greater than 5")
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python if.py
x is greater than 5
```

In the above example, we have used the `if` statement to check if the value of the variable `x` is greater than `5`. Since the value of `x` is `10`, the condition is `True`, and the code inside the `if` statement is executed. The string `"x is greater than 5"` is printed to the console.

## If-else Statement
#### `if-else` Statement
The `if-else` statement in Python is used to execute a block of code if a condition is `True`. If the condition is `False`, a different block of code is executed. The `if-else` statement is also known as the `if-then-else` statement. The `if-else` statement is a selection statement, which is a type of control statement in Python.

The syntax of the `if-else` statement in Python is as follows:

```python title="Syntax" showLineNumbers{1} {1,3}
if condition:
    # code to execute if condition is True
else:
    # code to execute if condition is False
```

The `if-else` statement begins with the `if` keyword, followed by a condition. The condition is followed by a colon (`:`). The code to execute if the condition is `True` is written on the next line, indented by four spaces. The code to execute if the condition is `False` is written after the `else` keyword, on the next line, indented by four spaces.

:::tip
The `else` clause is optional. If the `else` clause is not present, the code to execute if the condition is `False` is not executed.
:::

The following example demonstrates how to use the `if-else` statement in Python:

```python title="if-else.py" showLineNumbers{1} {3-5}
# if-else statement
x = 10
if x > 5:
    print("x is greater than 5")
else:
    print("x is less than or equal to 5")
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python if-else.py
x is greater than 5
```

In the above example, we have used the `if-else` statement to check if the value of the variable `x` is greater than `5`. Since the value of `x` is `10`, the condition is `True`, and the code inside the `if` statement is executed. The string `"x is greater than 5"` is printed to the console.

## If-elif-else Statement
#### `if-elif-else` Statement
The `if-elif-else` statement in Python is used to execute a block of code if a condition is `True`. If the condition is `False`, a different block of code is executed. The `if-elif-else` statement is also known as the `if-then-else` statement. The `if-elif-else` statement is a selection statement, which is a type of control statement in Python.

The syntax of the `if-elif-else` statement in Python is as follows:

```python title="Syntax" showLineNumbers{1} {1,3,5}
if condition1:
    # code to execute if condition1 is True
elif condition2:
    # code to execute if condition2 is True
else:
    # code to execute if condition1 and condition2 are False
```

The `if-elif-else` statement begins with the `if` keyword, followed by a condition. The condition is followed by a colon (`:`). The code to execute if the condition is `True` is written on the next line, indented by four spaces. The `elif` keyword is followed by a condition. The condition is followed by a colon (`:`). The code to execute if the condition is `True` is written on the next line, indented by four spaces. The code to execute if the condition is `False` is written after the `else` keyword, on the next line, indented by four spaces.

:::tip
The `elif` clause is optional. If the `elif` clause is not present, the code to execute if the condition is `False` is not executed.
:::

The following example demonstrates how to use the `if-elif-else` statement in Python:

```python title="if-elif-else.py" showLineNumbers{1} {3-7}
# if-elif-else statement
x = 10
if x > 5:
    print("x is greater than 5")
elif x < 5:
    print("x is less than 5")
else:
    print("x is equal to 5")
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python if-elif-else.py
x is greater than 5
```

In the above example, we have used the `if-elif-else` statement to check if the value of the variable `x` is greater than `5`. Since the value of `x` is `10`, the condition is `True`, and the code inside the `if` statement is executed. The string `"x is greater than 5"` is printed to the console.

Another example of the `if-elif-else` statement in Python:

```python title="if-elif-else.py" showLineNumbers{1} {3-7}
# if-elif-else multiple statements
x = 10
if x > 5:
    print("x is greater than 5")
elif x < 5:
    print("x is less than 5")
elif x > 10:
    print("x is greater than 10")
else:
    print("x is equal to 5")
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python if-elif-else.py
x is greater than 5
```

In the above example, we have used the `if-elif-else` statement to check if the value of the variable `x` is greater than `5`. Since the value of `x` is `10`, the condition is `True`, and the code inside the `if` statement is executed. The string `"x is greater than 5"` is printed to the console.

## Nested If-else Statement
#### `nested if-else` Statement
The `nested if-else` statement in Python is used to execute a block of code if a condition is `True`. If the condition is `False`, a different block of code is executed. The `nested if-else` statement is also known as the `nested if-then-else` statement. The `nested if-else` statement is a selection statement, which is a type of control statement in Python.

The syntax of the `nested if-else` statement in Python is as follows:

```python title="Syntax" showLineNumbers{1} {1,3}
if condition1:
    # code to execute if condition1 is True
    if condition2:
        # code to execute if condition2 is True
    else:
        # code to execute if condition2 is False
else:
    # code to execute if condition1 is False
```

The `nested if-else` statement begins with the `if` keyword, followed by a condition. The condition is followed by a colon (`:`). The code to execute if the condition is `True` is written on the next line, indented by four spaces. The `if` keyword is followed by a condition. The condition is followed by a colon (`:`). The code to execute if the condition is `True` is written on the next line, indented by four spaces. The code to execute if the condition is `False` is written after the `else` keyword, on the next line, indented by four spaces. The code to execute if the condition is `False` is written after the `else` keyword, on the next line, indented by four spaces.

:::tip
Nested if-else statements can be nested to any level.
:::

The following example demonstrates how to use the `nested if-else` statement in Python:

```python title="nested-if-else.py" showLineNumbers{1} {3-9}
# nested if-else statement
x = 10
if x > 5:
    print("x is greater than 5")
    if x > 10:
        print("x is greater than 10")
    else:
        print("x is less than or equal to 10")
else:
    print("x is less than or equal to 5")
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\Your Name> python nested-if-else.py
x is greater than 5
x is less than or equal to 10
```

## Ternary Operator
#### `ternary operator` Statement
The `ternary operator` statement in Python is used to execute a block of code if a condition is `True`. If the condition is `False`, a different block of code is executed. The `ternary operator` statement is also known as the `conditional operator` statement. The `ternary operator` statement is a selection statement, which is a type of control statement in Python.

The syntax of the `ternary operator` statement in Python is as follows:

```python title="Syntax" showLineNumbers{1} {1}
condition1 if condition2 else condition3
```

The `ternary operator` statement begins with a condition, followed by the `if` keyword. The `if` keyword is followed by a condition. The condition is followed by the `else` keyword. The `else` keyword is followed by a condition.

:::tip
The `ternary operator` statement is a one-line shorthand for the `if-else` statement.
:::

The following example demonstrates how to use the `ternary operator` statement in Python:

```python title="ternary-operator.py" showLineNumbers{1} {3}
# ternary operator statement
x = 10
print("x is greater than 5") if x > 5 else print("x is less than or equal to 5")
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python ternary-operator.py
x is greater than 5
```

In the above example, we have used the `ternary operator` statement to check if the value of the variable `x` is greater than `5`. Since the value of `x` is `10`, the condition is `True`, and the code inside the `if` statement is executed. The string `"x is greater than 5"` is printed to the console.

Another example of the `ternary operator` statement in Python:

```python title="ternary-operator.py" showLineNumbers{1} {3}
# ternary operator multiple statements
x = 10
print("x is greater than 5") if x > 5 else print("x is less than or equal to 5") if x < 5 else print("x is equal to 5")
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python ternary-operator.py
x is greater than 5
```

In the above example, we have used the `ternary operator` statement to check if the value of the variable `x` is greater than `5`. Since the value of `x` is `10`, the condition is `True`, and the code inside the `if` statement is executed. The string `"x is greater than 5"` is printed to the console.

:::tip
For more information on the ternary operator, see the [Python documentation](https://docs.python.org/3/reference/expressions.html#conditional-expressions). Or see the [Python Ternary Operator](https://www.python-central-hub.vercel.app/tutorials/ternary-operator) tutorial on Python Central Hub.


## Conclusion
In this guide, we explored the syntax and usage of the if-else statement in Python. We also explored the ternary operator, which is a one-line shorthand for the if-else statement. Now that you have a solid understanding of the if-else statement in Python, you can use it to write flexible and dynamic Python programs. In this guide, we explored the syntax and usage of the if-else statement in Python. We also explored the ternary operator, which is a one-line shorthand for the if-else statement. Now that you have a solid understanding of the if-else statement in Python, you can use it to write flexible and dynamic Python programs.