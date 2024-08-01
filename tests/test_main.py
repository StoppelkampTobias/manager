import unittest
import json
import os
from unittest.mock import patch, mock_open
from main import PasswordManager

class TestPasswordManagerV1(unittest.TestCase):
    
    def setUp(self):
        self.master_password = "testpassword"
        self.manager = PasswordManager(self.master_password)
        self.data = {
            "example.com": {
                "username": "user1",
                "password": "pass1"
            }
        }

    def tearDown(self):
        if os.path.exists(self.manager.data_file):
            os.remove(self.manager.data_file)

    @patch("builtins.open", new_callable=mock_open, read_data=json.dumps({}))
    @patch("os.path.exists", return_value=True)
    def test_load_data(self, mock_exists, mock_open):
        self.manager.data = self.data
        self.manager.save_data()
        self.manager.data = {}  # Clear the current data
        self.assertEqual(self.manager.load_data(), self.data)

    @patch("builtins.open", new_callable=mock_open)
    def test_save_data(self, mock_open):
        self.manager.data = self.data
        self.manager.save_data()
        mock_open.assert_called_with(self.manager.data_file, "wb")

    @patch("builtins.open", new_callable=mock_open)
    def test_add_password(self, mock_open):
        site = "newsite.com"
        username = "newuser"
        password = "newpass"
        self.manager.add_password(site, username, password)
        self.assertIn(site, self.manager.data)
        self.assertEqual(self.manager.data[site]["username"], username)
        self.assertEqual(self.manager.data[site]["password"], password)

    def test_get_password(self):
        self.manager.data = self.data
        result = self.manager.get_password("example.com")
        self.assertEqual(result, self.data["example.com"])

    def test_generate_key(self):
        key = self.manager.generate_key(self.master_password)
        self.assertEqual(len(key), 44)  # Length of base64 encoded SHA-256 hash

if __name__ == "__main__":
    unittest.main()
