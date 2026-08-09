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


import time


def benchmark_methods(string, iterations=10000):
    """Time every method on the same string, slowest last.

    Recursion is the one to watch: it builds a new string at every level, so
    its cost grows with the square of the length while the slice does not
    grow at all in Python-level work.
    """
    methods = [
        reverse_string_for_loop,
        reverse_string_while_loop,
        reverse_string_recursion,
        reverse_string_extended_slice,
        reverse_string_stack,
        reverse_string_list_comprehension,
        reverse_string_generator_expression,
    ]
    timings = []
    for method in methods:
        start_time = time.perf_counter()
        for _ in range(iterations):
            method(string)
        elapsed = time.perf_counter() - start_time
        timings.append((method.__name__, elapsed))

    fastest = min(elapsed for _, elapsed in timings)
    for name, elapsed in sorted(timings, key=lambda pair: pair[1]):
        print(f"{name:42} {elapsed:7.4f}s  {elapsed / fastest:5.1f}x")
    return timings


# Test the functions
string = 'Reverse this string'
print('Original string:', string)
print('For loop:', reverse_string_for_loop(string))
print('While loop:', reverse_string_while_loop(string))
print('Recursion:', reverse_string_recursion(string))
print('Extended slice:', reverse_string_extended_slice(string))
print('Stack:', reverse_string_stack(string))
print('List comprehension:', reverse_string_list_comprehension(string))
print('Generator expression:', reverse_string_generator_expression(string))

# Every method must agree, or the timings below compare a correct
# implementation against a broken one.
methods = [reverse_string_for_loop, reverse_string_while_loop,
           reverse_string_recursion, reverse_string_extended_slice,
           reverse_string_stack, reverse_string_list_comprehension,
           reverse_string_generator_expression]
expected = string[::-1]
assert all(method(string) == expected for method in methods)
print("\nAll seven agree. Timing them on the same string, 10,000 runs each:\n")
benchmark_methods(string)
