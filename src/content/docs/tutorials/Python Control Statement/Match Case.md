---
title: Match Case Statement in Python
description: Learn about match case statement in Python. Match case statement is used to control the flow of execution of the program. We will learn about match case statement in Python. Match case statement is new in Python 3.10.
sidebar: 
    order: 35
---

## Mastering Match Case Statement in Python: A Comprehensive Guide
Match case statement in Python is used to control the flow of execution of the program. It is also known as pattern matching statement. Match case statement is new in Python 3.10. In this comprehensive guide, we'll explore the syntax and usage of match case statement in Python.

## What is Match Case Statement in Python?
Match case statement in Python is used to control the flow of execution of the program. It is also known as pattern matching statement. Match case statement is new in Python 3.10. It is similar to switch case statement in other programming languages. It is used to compare the value of an expression against a list of patterns and execute the corresponding block of code if a match is found.

## Syntax of Match Case Statement in Python
The syntax of match case statement in Python is as follows:

```python title="Syntax" showLineNumbers{1}
match expression:
    case pattern1:
        # statements
    case pattern2:
        # statements
    case pattern3:
        # statements
    ...
    case patternN:
        # statements
    case _:
        # statements
```

:::tip
The `case _:` is optional. It is known as the wildcard pattern. It matches any value.
:::

:::info
This syntax is equivalent to the c++, Java, and JavaScript switch case statement.
:::

The match case statement starts with the `match` keyword followed by an expression. The expression is evaluated and compared against the patterns. If a match is found, the corresponding block of code is executed. If no match is found, the block of code under the `_` pattern is executed. The `_` pattern is known as the wildcard pattern. It matches any value.

## Example of Match Case Statement in Python
The following example demonstrates how to use the match case statement in Python:

```python title="match_case.py" showLineNumbers{1} {3-15}
# match case statement
x = 4
match x:
    case 1:
        print("x is 1")
    case 2:
        print("x is 2")
    case 3:
        print("x is 3")
    case 4:
        print("x is 4")
    case 5:
        print("x is 5")
    case _:
        print("x is not 1, 2, 3, 4, or 5")
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\Your Name> python match_case.py
x is 4
```

In the above example, we have used the match case statement to compare the value of the variable `x` against a list of patterns. Since the value of `x` is `4`, the block of code under the `case 4:` is executed.

Another example of match case statement in Python:

```python title="match_case.py" showLineNumbers{1} {3-15}
# match case statement
x = 10
match x:
    case 1:
        print("x is 1")
    case 2:
        print("x is 2")
    case 3:
        print("x is 3")
    case 4:
        print("x is 4")
    case 5:
        print("x is 5")
    case _:
        print("x is not 1, 2, 3, 4, or 5")
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\Your Name> python match_case.py
x is not 1, 2, 3, 4, or 5
```

In the above example, we have used the match case statement to compare the value of the variable `x` against a list of patterns. Since the value of `x` is not `1`, `2`, `3`, `4`, or `5`, the block of code under the `case _:` is executed.

## Combining Match Case Statement
The match case statement can be combined with other control statements such as if-else statement, for statement, while statement, etc. The following example demonstrates how to combine the match case statement with the if-else statement:

```python title="match_case.py" showLineNumbers{1} {3-15}
# match case statement
day = "Monday"
match day:
    case "Saturday" | "Sunday":
        print("It's a weekend")
    case "Monday" | "Tuesday" | "Wednesday" | "Thursday" | "Friday":
        print("It's a weekday")
    case _:
        print("Invalid day")
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\Your Name> python match_case.py
It's a weekday
```

In the above example, we have used the match case statement to compare the value of the variable `day` against a list of patterns. Since the value of `day` is `Monday`, the block of code under the `case "Monday" | "Tuesday" | "Wednesday" | "Thursday" | "Friday":` is executed.

## Match Case Statement with Conditional Statement
The match case statement can be combined with the if-else statement. The following example demonstrates how to combine the match case statement with the if-else statement:

```python title="match_case.py" showLineNumbers{1} {3-15}
# match case statement
x = 10
match x:
    case x < 10:
        print("x is less than 10")
    case x > 10:
        print("x is greater than 10")
    case x == 10:
        print("x is equal to 10")
    case _:
        print("Invalid value")
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\Your Name> python match_case.py
x is equal to 10
```

In the above example, we have used the match case statement to compare the value of the variable `x` against a list of patterns. Since the value of `x` is `10`, the block of code under the `case x == 10:` is executed.

## Match Case Statement with if-elif-else Statement
The match case statement can be combined with the if-elif-else statement. The following example demonstrates how to combine the match case statement with the if-elif-else statement:

```python title="match_case.py" showLineNumbers{1} {3-16}
# match case statement
day = "Monday"
x = 10
match day:
    case "Saturday" if x == 10:
        print("It's a weekend")
    case "Sunday" if x == 10:
        print("It's a weekend")
    case "Monday" if x > 10:
        print("It's a weekday")
    case "Monday" if x < 10:
        print("It's a not a weekday")
    case "Monday" if x == 10:
        print("It's a fun")
    case _:
        print("Invalid day")
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\Your Name> python match_case.py
It's a fun
```

In the above example, we have used the match case statement to compare the value of the variable `day` against a list of patterns. Since the value of `day` is `Monday` and the value of `x` is `10`, the block of code under the `case "Monday" if x == 10:` is executed.

## Nested Match Case Statement
The match case statement can be nested inside another match case statement. The following example demonstrates how to nest the match case statement:

```python title="match_case.py" showLineNumbers{1} {3-18}
# match case statement
day = "Monday"
x = 10
match day:
    case "Saturday" | "Sunday":
        match x:
            case 10:
                print("It's a weekend")
            case _:
                print("It's a not a weekend")
    case "Monday" | "Tuesday" | "Wednesday" | "Thursday" | "Friday":
        match x:
            case 10:
                print("It's a weekday")
            case _:
                print("It's a not a weekday")
    case _:
        print("Invalid day")
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\Your Name> python match_case.py
It's a weekday
```

In the above example, we have used the match case statement to compare the value of the variable `day` against a list of patterns. Since the value of `day` is `Monday`, the block of code under the `case "Monday" | "Tuesday" | "Wednesday" | "Thursday" | "Friday":` is executed. The match case statement is nested inside the block of code under the `case "Monday" | "Tuesday" | "Wednesday" | "Thursday" | "Friday":`. Since the value of `x` is `10`, the block of code under the `case 10:` is executed.

## Match Case Statement with list
The match case statement can be used with a list. The following example demonstrates how to use the match case statement with a list:

```python title="match_case.py" showLineNumbers{1} {3-15}
# match case statement
match [1, 2, 3]:
    case [1, 2, 3]:
        print("List is [1, 2, 3]")
    case [4, 5, 6]:
        print("List is [4, 5, 6]")
    case [7, 8, 9]:
        print("List is [7, 8, 9]")
    case _:
        print("Invalid list")
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\Your Name> python match_case.py
List is [1, 2, 3]
```

In the above example, we have used the match case statement to compare the value of the list `[1, 2, 3]` against a list of patterns. Since the value of the list `[1, 2, 3]` is `[1, 2, 3]`, the block of code under the `case [1, 2, 3]:` is executed.

## Conclusion
In this guide, we explored the syntax and usage of match case statement in Python. Now that you have a solid understanding of match case statement in Python, you can use it to write flexible and dynamic Python programs. As you delve deeper into Python programming, experiment with different match case statements, explore their applications in real-world scenarios, and use them to enhance the efficiency and clarity of your code. For more hands-on examples and in-depth tutorials, explore our resources on Python Central Hub! 