"""
This module contains an example function that generates a random password.
"""

import random
import string

def generatePassword(length=12, useUppercase=True, useNumbers=True, useSpecial=True):
    """
    Generate a random password with the given parameters.

    :param length: The length of the password to generate (default is 12).
    :param useUppercase: Include uppercase letters if True (default is True).
    :param useNumbers: Include digits if True (default is True).
    :param useSpecial: Include special characters if True (default is True).
    :return: A randomly generated password as a string.
    """
    characters = string.ascii_lowercase
    password = []

    if useUppercase:
        characters += string.ascii_uppercase
        password.append(random.choice(string.ascii_uppercase))

    if useNumbers:
        characters += string.digits
        password.append(random.choice(string.digits))

    if useSpecial:
        characters += string.punctuation
        password.append(random.choice(string.punctuation))

    # Fill the rest of the password length with random choices from all allowed characters
    password += [random.choice(characters) for _ in range(length - len(password))]

    # Shuffle the resulting list to ensure random distribution of required characters
    random.shuffle(password)

    return ''.join(password)
