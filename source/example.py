import random
import string

def generate_password(length=12, use_uppercase=True, use_numbers=True, use_special=True):
    characters = string.ascii_lowercase
    if use_uppercase:
        characters += string.ascii_uppercase
    if use_numbers:
        characters += string.digits
    if use_special:
        characters += string.punctuation
    
    return ''.join(random.choice(characters) for i in range(length))