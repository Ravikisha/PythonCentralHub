# Binary to Decimal Conveter


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

print("Binary to Decimal Conveter")
print("Choose one of the following options:")
print("1. Convert a binary number to a decimal number")
print("2. Convert a decimal number to a binary number")
print("3. Exit")

option = int(ask("Enter your option: ", "1"))
if option == 1:
    binary = ask("Enter a binary number: ", "1011")
    decimal = int(binary, 2)
    print("The decimal value of", binary, "is", decimal)
elif option == 2:
    decimal = int(ask("Enter a decimal number: ", "11"))
    binary = bin(decimal)
    print("The binary value of", decimal, "is", binary)
elif option == 3:
    exit()