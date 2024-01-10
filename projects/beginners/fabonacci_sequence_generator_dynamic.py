# Fabonacci Sequence Generator (Dynamic Programming)

n = int(input("How many numbers that generates?: "))
dp = [0, 1]

if n <= 0:
    print("Please enter a positive integer")
elif n == 1:
    print("Fibonacci sequence upto", n, ":")
    print(dp[0])
else:
    print("Fibonacci sequence:")
    for i in range(2, n):
        dp.append(dp[i-1] + dp[i-2])
    print(dp)