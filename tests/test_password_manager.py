import unittest
from source.password_manager import PasswordManager

class TestPasswordManager(unittest.TestCase):
    def setUp(self):
        self.manager = PasswordManager("masterpassword", filename='test_passwords.json')
        self.manager.data = {}  # Reset data for testing

    def test_add_and_get_entry(self):
        self.manager.add_entry("example.com", "user", "password")
        entry = self.manager.get_entry("example.com")
        self.assertIsNotNone(entry)
        self.assertEqual(entry['username'], "user")
        self.assertEqual(entry['password'], "password")

    def test_delete_entry(self):
        self.manager.add_entry("example.com", "user", "password")
        self.manager.delete_entry("example.com")
        entry = self.manager.get_entry("example.com")
        self.assertIsNone(entry)

if __name__ == '__main__':
    unittest.main()
