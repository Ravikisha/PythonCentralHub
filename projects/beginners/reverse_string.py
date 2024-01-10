# Reverse a String

# Reverse a string using a for loop
def reverse_string_for_loop(string):
    string_reverse = ''
    for i in string:
        string_reverse = i + string_reverse
    return string_reverse

# Reverse a string using a while loop
def reverse_string_while_loop(string):
    string_reverse = ''
    index = len(string)
    while index > 0:
        string_reverse += string[ index - 1 ]
        index = index - 1
    return string_reverse

# Reverse a string using recursion
def reverse_string_recursion(string):
    if len(string) == 0:
        return string
    else:
        return reverse_string_recursion(string[1:]) + string[0]
    
# Reverse a string using extended slice syntax
def reverse_string_extended_slice(string):
    return string[::-1]

# Reverse a string using a stack
def reverse_string_stack(string):
    stack = []
    for i in string:
        stack.append(i)
    string_reverse = ''
    while len(stack) > 0:
        string_reverse += stack.pop()
    return string_reverse

# Reverse a string using a list comprehension
def reverse_string_list_comprehension(string):
    return ''.join([string[i] for i in range(len(string) - 1, -1, -1)])

# Reverse a string using a generator expression
def reverse_string_generator_expression(string):
    return ''.join(i for i in reversed(string))


