# Fibonacci Sequence Generator

# The Fibonacci sequence is a series of numbers where a number is the addition of the last two numbers, starting with 0, and 1. The Fibonacci Sequence: 0, 1, 1, 2, 3, 5, 8, 13, 21, 34, ...

n = int(input("How many numbers that generates?: "))
n1 = 0
n2 = 1
count = 0

if n <= 0:
    print("Please enter a positive integer")
elif n == 1:
    print("Fibonacci sequence upto", n, ":")
    print(n1)
else:
    print("Fibonacci sequence:")
    while count < n:
        print(n1)
        nth = n1 + n2
        # update values
        n1 = n2
        n2 = nth
        count += 1