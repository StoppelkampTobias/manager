import unittest
import string
from source.example import generate_password

class TestUtils(unittest.TestCase):

    def test_generate_password_length(self):
        password = generate_password(16)
        self.assertEqual(len(password), 16)

    def test_generate_password_uppercase(self):
        password = generate_password(use_uppercase=True)
        self.assertTrue(any(char.isupper() for char in password))

    def test_generate_password_numbers(self):
        password = generate_password(use_numbers=True)
        self.assertTrue(any(char.isdigit() for char in password))

    def test_generate_password_special(self):
        password = generate_password(use_special=True)
        self.assertTrue(any(char in string.punctuation for char in password))

if __name__ == '__main__':
    unittest.main()