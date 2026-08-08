# Temperature Converter


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

# Function to convert Celsius to Fahrenheit
def celsius_to_fahrenheit(celsius):
    fahrenheit = (celsius * 9/5) + 32
    return fahrenheit

# Function to convert Fahrenheit to Celsius
def fahrenheit_to_celsius(fahrenheit):
    celsius = (fahrenheit - 32) * 5/9
    return celsius

# Main function
def main():
    print("Temperature Converter")
    print("1. Celsius to Fahrenheit")
    print("2. Fahrenheit to Celsius")
    choice = int(ask("Enter your choice: ", "1"))
    if choice == 1:
        celsius = float(ask("Enter temperature in Celsius: ", "100"))
        fahrenheit = celsius_to_fahrenheit(celsius)
        print("Temperature in Fahrenheit: ", fahrenheit)
    elif choice == 2:
        fahrenheit = float(ask("Enter temperature in Fahrenheit: ", "212"))
        celsius = fahrenheit_to_celsius(fahrenheit)
        print("Temperature in Celsius: ", celsius)
    else:
        print("Invalid choice!")
        
# Call main function
main()
