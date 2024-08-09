# pylint: disable=C)
"""
disables pylint warning for invalid constant name
"""

import unittest
import string
from source.example import generatePassword


class TestPasswordGenerator(unittest.TestCase):

    def test_default_password_length(self):
        password = generatePassword()
        self.assertEqual(len(password), 12, "Default password length should be 12")

    def test_custom_password_length(self):
        password = generatePassword(length=16)
        self.assertEqual(len(password), 16, "Custom password length should be 16")

    def test_password_with_uppercase(self):
        password = generatePassword(useUppercase=True)
        self.assertTrue(any(c.isupper() for c in password), "Password should contain uppercase letters")

    def test_password_without_uppercase(self):
        password = generatePassword(useUppercase=False)
        self.assertFalse(any(c.isupper() for c in password), "Password should not contain uppercase letters")

    def test_password_with_numbers(self):
        password = generatePassword(useNumbers=True)
        self.assertTrue(any(c.isdigit() for c in password), "Password should contain numbers")

    def test_password_without_numbers(self):
        password = generatePassword(useNumbers=False)
        self.assertFalse(any(c.isdigit() for c in password), "Password should not contain numbers")

    def test_password_with_special_characters(self):
        password = generatePassword(useSpecial=True)
        self.assertTrue(any(c in string.punctuation for c in password), "Password should contain special characters")

    def test_password_without_special_characters(self):
        password = generatePassword(useSpecial=False)
        self.assertFalse(any(c in string.punctuation for c in password), "Password should not contain special characters")

    def test_password_with_all_disabled(self):
        password = generatePassword(useUppercase=False, useNumbers=False, useSpecial=False)
        self.assertTrue(all(c.islower() for c in password), "Password should contain only lowercase letters")

if __name__ == "__main__":
    unittest.main()
