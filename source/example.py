"""
This module contains utility functions for password generation.
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
    if useUppercase:
        characters += string.ascii_uppercase
    if useNumbers:
        characters += string.digits
    if useSpecial:
        characters += string.punctuation
        
    return ''.join(random.choice(characters) for i in range(length))
