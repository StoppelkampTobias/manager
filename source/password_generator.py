import random
import string

class PasswordGenerator:
    @staticmethod
    def generate(length=12, use_upper=True, use_lower=True, use_digits=True, use_special=True):
        char_pool = ''
        if use_upper:
            char_pool += string.ascii_uppercase
        if use_lower:
            char_pool += string.ascii_lowercase
        if use_digits:
            char_pool += string.digits
        if use_special:
            char_pool += string.punctuation
        if not char_pool:
            raise ValueError("At least one character set must be selected")

        return ''.join(random.choice(char_pool) for _ in range(length))
