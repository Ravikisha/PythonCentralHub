# Password Strength Checker

import re

def password_strength_checker(password):
    if len(password) < 8:
        print("Password must be at least 8 characters long.")
    elif not re.search("[a-z]", password):
        print("Password must contain at least one lowercase letter.")
    elif not re.search("[A-Z]", password):
        print("Password must contain at least one uppercase letter.")
    elif not re.search("[0-9]", password):
        print("Password must contain at least one number.")
    elif not re.search("[_@$]", password):
        print("Password must contain at least one special character.")
    else:
        print("Password is strong.")
        
password_strength_checker("Password123")
password_strength_checker("Password")
password_strength_checker("password123")
password_strength_checker("PASSWORD123")
password_strength_checker("Password@")
password_strength_checker("Password123@")
password_strength_checker("Password123@!")
