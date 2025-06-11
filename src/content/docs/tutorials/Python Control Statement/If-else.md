---
title: If-else Statement in Python
description: Learn about if-else statement in Python. The if-else statement is used to execute a block of code based on a condition. We will learn about the syntax of the if-else statement in Python. We will also learn about the ternary operator in Python.
sidebar: 
    order: 34
---

## Mastering If-else Statement in Python: A Comprehensive Guide
The if-else statement in Python is used to execute a block of code based on a condition. Understanding the if-else statement is fundamental to writing flexible and dynamic Python programs. In this comprehensive guide, we'll explore the syntax and usage of the if-else statement in Python.

## What is the If-else Statement in Python?
The if-else statement in Python is used to execute a block of code based on a condition. The if-else statement is also known as the if-then-else statement. The if-else statement is a selection statement, which is a type of control statement in Python.

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

```python title="Syntax" showLineNumbers{1} {1-2}
if condition:
    # code to execute if condition is True
```

**Diagram**:
```mermaid title="if statement" desc="Diagram of the if statement in Python"
graph TD
    A[Start] --> B{Condition}
    B -->|True| C[Execute Code]
    C --> D[End]
    B ---->|False| E[End]
```

The `if` statement begins with the `if` keyword, followed by a condition. The condition is followed by a colon (`:`). The code to execute if the condition is `True` is written on the next line, indented by four spaces.

:::tip
The `if` statement does not have an `else` clause. If you want to execute a block of code if the condition is `False`, you should use the `if-else` statement.
:::

The following example demonstrates how to use the `if` statement in Python:

```python title="if.py" showLineNumbers{1} {3-4}
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

```python title="Syntax" showLineNumbers{1} {1-4}
if condition:
    # code to execute if condition is True
else:
    # code to execute if condition is False
```

The `if-else` statement begins with the `if` keyword, followed by a condition. The condition is followed by a colon (`:`). The code to execute if the condition is `True` is written on the next line, indented by four spaces. The code to execute if the condition is `False` is written after the `else` keyword, on the next line, indented by four spaces.

**Diagram**:
```mermaid title="if-else statement" desc="Diagram of the if-else statement in Python"
graph TD
    A[Start] --> B{Condition}
    B -->|True| C[Execute Code]
    C --> D[End]
    B ---->|False| E[Execute Code]
    E --> F[End]
```


:::tip
The `else` clause is optional. If the `else` clause is not present, the code to execute if the condition is `False` is not executed.
:::

The following example demonstrates how to use the `if-else` statement in Python:

```python title="if-else.py" showLineNumbers{1} {3-6}
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

```python title="Syntax" showLineNumbers{1} {1-6}
if condition1:
    # code to execute if condition1 is True
elif condition2:
    # code to execute if condition2 is True
else:
    # code to execute if condition1 and condition2 are False
```

The `if-elif-else` statement begins with the `if` keyword, followed by a condition. The condition is followed by a colon (`:`). The code to execute if the condition is `True` is written on the next line, indented by four spaces. The `elif` keyword is followed by a condition. The condition is followed by a colon (`:`). The code to execute if the condition is `True` is written on the next line, indented by four spaces. The code to execute if the condition is `False` is written after the `else` keyword, on the next line, indented by four spaces.

**Diagram**:
```mermaid title="if-elif-else statement" desc="Diagram of the if-elif-else statement in Python"
graph TD
    A[Start] --> B{Condition1}
    B -->|True| C[Execute Code]
    C --> D[End]
    B ---->|False| E{Condition2}
    E -->|True| F[Execute Code]
    F --> G[End]
    E ---->|False| H[Execute Code]
    H --> I[End]
```

:::tip
The `elif` clause is optional. If the `elif` clause is not present, the code to execute if the condition is `False` is not executed.
:::

The following example demonstrates how to use the `if-elif-else` statement in Python:

```python title="if-elif-else.py" showLineNumbers{1} {3-8}
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

```python title="if-elif-else.py" showLineNumbers{1} {3-10}
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

```python title="Syntax" showLineNumbers{1} {1-10}
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

**Diagram**:
```mermaid title="nested if-else statement" desc="Diagram of the nested if-else statement in Python"
graph TD
    A[Start] --> B{Condition1}
    B -->|True| C[Execute Code]
    C --> D{Condition2}
    D -->|True| E[Execute Code]
    E --> F[End]
    D ---->|False| G[Execute Code]
    G --> H[End]
    B ---->|False| I[Execute Code]
    I --> J[End]
```

:::tip
Nested if-else statements can be nested to any level.
:::

The following example demonstrates how to use the `nested if-else` statement in Python:

```python title="nested-if-else.py" showLineNumbers{1} {3-10}
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

**Diagram**:
```mermaid title="ternary operator statement" desc="Diagram of the ternary operator statement in Python"
graph TD
    A[Start] --> B{Condition2}
    B -->|True| C[Execute Code]
    C --> D[End]
    B ---->|False| E[Execute Code]
    E --> F[End]
```

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
For more information on the ternary operator, see the [Python documentation](https://docs.python.org/3/reference/expressions.html#conditional-expressions). Or see the [Python Ternary Operator](https://www.pythoncentralhub.live/tutorials/ternary-operator) tutorial on Python Central Hub.
:::

## Conclusion
In this guide, we explored the syntax and usage of the if-else statement in Python. We also explored the ternary operator, which is a one-line shorthand for the if-else statement. Now that you have a solid understanding of the if-else statement in Python, you can use it to write flexible and dynamic Python programs. In this guide, we explored the syntax and usage of the if-else statement in Python. We also explored the ternary operator, which is a one-line shorthand for the if-else statement. Now that you have a solid understanding of the if-else statement in Python, you can use it to write flexible and dynamic Python programs.

As you delve deeper into Python programming, experiment with different control statements, explore their applications in real-world scenarios, and use them to enhance the efficiency and clarity of your code. For more hands-on examples and in-depth tutorials, explore our resources on Python Central Hub!