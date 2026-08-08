# Fabonacci Sequence Generator (Dynamic Programming)


def ask(prompt, default):
    """Read a line, or fall back to `default` when nobody is there to type.

    Without this the script raises EOFError as soon as it runs unattended --
    in a test, a scheduled job, or the documentation build that captures this
    output. The default is what the demo uses.
    """
    try:
        answer = input(prompt)
    except EOFError:
        print(f"{default}   (no input available, using the default)")
        return default
    return answer.strip() or default

n = int(ask("How many numbers that generates?: ", "12"))
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