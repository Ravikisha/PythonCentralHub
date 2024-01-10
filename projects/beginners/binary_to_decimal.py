# Binary to Decimal Conveter

print("Binary to Decimal Conveter")
print("Choose one of the following options:")
print("1. Convert a binary number to a decimal number")
print("2. Convert a decimal number to a binary number")
print("3. Exit")

option = int(input("Enter your option: "))
if option == 1:
    binary = input("Enter a binary number: ")
    decimal = int(binary, 2)
    print("The decimal value of", binary, "is", decimal)
elif option == 2:
    decimal = int(input("Enter a decimal number: "))
    binary = bin(decimal)
    print("The binary value of", decimal, "is", binary)
elif option == 3:
    exit()