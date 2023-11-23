---
title: Python Tenary Operator
description: Learn how to use the Python ternary operator. The ternary operator is a conditional operator that returns a value based on the result of a condition.  
sidebar: 
    order: 30
---

## Mastering the Ternary Operator in Python
The ternary operator, also known as the conditional expression, provides a concise and expressive way to write conditional statements in a single line. It's a powerful tool for simplifying code and making it more readable. In this comprehensive guide, we'll explore the ternary operator in Python, its syntax, use cases, and best practices.

### What is the Ternary Operator?
The ternary operator is a conditional operator that returns a value based on the result of a condition. It's a shorthand for the `if-else` statement. The ternary operator is also known as the conditional expression.

:::tip
We are going to more study about the `if-else` statement in the next tutorial. You can check it out [here](/tutorials/Python%20Conditional/).
:::

The ternary operator is a powerful tool for simplifying code and making it more readable. It's a concise way to write conditional statements in a single line.

### Syntax
The ternary operator has the following syntax:

```python title="Syntax" showLineNumbers{1}
<value_if_true> if <condition> else <value_if_false>
```

The ternary operator consists of three operands separated by the `if` and `else` keywords. The first operand is the condition, the second operand is the value to return if the condition is true, and the third operand is the value to return if the condition is false.

### Example
Let's take a look at a simple example of the ternary operator in Python:

```python title="ternary_operator.py" showLineNumbers{1} {4}
# Ternary operator
x = 10
y = 5
z = x if x > y else y
print(z)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python ternary_operator.py
10
```

In the above example, we have used the ternary operator to assign the value of `x` to the variable `z` if the condition `x > y` is true. Otherwise, the value of `y` is assigned to the variable `z`.

## Nested Ternary Operator
The ternary operator can be nested to create more complex conditional statements. The following example demonstrates how to use the nested ternary operator in Python:

```python title="nested_ternary_operator.py" showLineNumbers{1} {5}
# Nested ternary operator
x = 10
y = 5
z = 2
a = x if x > y else y if y > z else z
print(a)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python nested_ternary_operator.py
10
```

In the above example, we have used the nested ternary operator to assign the value of `x` to the variable `a` if the condition `x > y` is true. Otherwise, the value of `y` is assigned to the variable `a` if the condition `y > z` is true. Otherwise, the value of `z` is assigned to the variable `a`.

## Ternary Operator vs. if-else Statement
The ternary operator is a shorthand for the `if-else` statement. It's a concise way to write conditional statements in a single line. The ternary operator is a powerful tool for simplifying code and making it more readable.

Consider the following example:

```python title="if_else_statement.py" showLineNumbers{1} {4-7}
# if-else statement
x = 10
y = 5
if x > y:
    z = x
else:
    z = y
print(z)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python if_else_statement.py
10
```

The above example can be rewritten using the ternary operator as follows:

```python title="ternary_operator.py" showLineNumbers{1} {4}
# Ternary operator
x = 10
y = 5
z = x if x > y else y
print(z)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\Your Name> python ternary_operator.py
10
```

As you can see, the ternary operator is a concise way to write conditional statements in a single line.

## Benefits and Best Practices
### Readability and Conciseness
The ternary operator enhances code readability by succinctly expressing conditional statements in a single line. It's especially useful for simple conditions.

### Avoiding Redundant Code
The ternary operator helps avoid redundancy when assigning values based on conditions, eliminating the need for repetitive if-else blocks.

### Caution with Complexity
While the ternary operator is powerful for simple conditions, it's essential to use it judiciously. For complex conditions, especially those involving multiple operations, an if-else block might be more readable.

### PEP 8 Guidelines
The Python Enhancement Proposal (PEP) 8, the style guide for Python code, recommends using the ternary operator sparingly, especially when it makes the code less readable. Clarity should be prioritized over brevity.
:::tip
We are going to more study about the PEP 8 guidelines in the next tutorial. You can check it out [here](https://peps.python.org/pep-0008/).
:::

## Conclusion
The ternary operator in Python is a valuable tool for writing concise and readable code, especially in cases where simple conditional assignments are needed. As you incorporate the ternary operator into your code, keep in mind the balance between brevity and readability. Use it for straightforward conditions to enhance the clarity of your code, and be mindful of PEP 8 guidelines for maintaining a consistent and readable coding style.

For more insights and practical examples, check out our tutorials on Python Central Hub!