# Calculator Program

# Importing Modules
import math

# Defining Functions
def add(x, y):
    return x + y

def sub(x, y):
    return x - y

def mul(x, y):
    return  x * y

def div(x, y):
    return x / y

def sqrt(x):
    return math.sqrt(x)

def power(x, y):
    return math.pow(x, y)


# Main Program
print("Select Operation.")
print("1. Addition")
print("2. Subtraction")
print("3. Multiplication")
print("4. Division")
print("5. Square Root")
print("6. Power")
print("E. Exit")
print("R. Restart")

while True:
    choice = input("Enter Choice (1/2/3/4/5/6/E/R): ")

    if choice in ('1', '2', '3', '4', '5', '6'):
        num1 = float(input("Enter First Number: "))
        num2 = float(input("Enter Second Number: "))

        if choice == '1':
            print(num1, "+", num2, "=", add(num1, num2))

        elif choice == '2':
            print(num1, "-", num2, "=", sub(num1, num2))

        elif choice == '3':
            print(num1, "*", num2, "=", mul(num1, num2))

        elif choice == '4':
            print(num1, "/", num2, "=", div(num1, num2))

        elif choice == '5':
            print("Square Root of", num1, "=", sqrt(num1))
            print("Square Root of", num2, "=", sqrt(num2))

        elif choice == '6':
            print(num1, "to the power of", num2, "=", power(num1, num2))

    elif choice.upper() == 'E':
        confirm = input("Are you sure you want to exit? (Y/N): ")
        if confirm.upper() == 'Y':
            print("Exiting...")
            break
        elif confirm.upper() == 'N':
            print("Select Operation.")
            print("1. Addition")
            print("2. Subtraction")
            print("3. Multiplication")
            print("4. Division")
            print("5. Square Root")
            print("6. Power")
            print("7. Exit")
            print("R. Restart")
        else:
            print("Invalid Input")

    elif choice.upper() == 'R':
        print("Restarting...")
        print("Select Operation.")
        print("1. Addition")
        print("2. Subtraction")
        print("3. Multiplication")
        print("4. Division")
        print("5. Square Root")
        print("6. Power")
        print("7. Exit")
        print("R. Restart")

    else:
        print("Invalid Input")