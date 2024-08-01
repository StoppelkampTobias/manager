import unittest
from unittest.mock import patch, mock_open
import os
import sys
import json

# Add source directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'source')))

from password_manager import PasswordManager, generate_key, encrypt_data, decrypt_data, hash_password, generate_password

class TestPasswordManager(unittest.TestCase):

    def setUp(self):
        self.master_password = "testpassword"
        self.manager = PasswordManager(self.master_password)
        self.key = self.manager.key
        self.hashed_master_password = hash_password(self.master_password)
        self.data = {
            self.hashed_master_password: [
                {
                    "username": "user1",
                    "password": encrypt_data("pass1", self.key).decode(),
                    "url": "example.com",
                    "notes": encrypt_data("notes1", self.key).decode(),
                    "categories": encrypt_data("category1", self.key).decode(),
                    "creation_date": encrypt_data("2023-01-01T00:00:00", self.key).decode(),
                    "password_history": []
                }
            ]
        }

    def tearDown(self):
        if os.path.exists("passwords.json"):
            os.remove("passwords.json")
        if os.path.exists("key.key"):
            os.remove("key.key")

    @patch("builtins.open", new_callable=mock_open, read_data=json.dumps({}))
    @patch("os.path.exists", return_value=True)
    def test_load_data(self, mock_exists, mock_open):
        self.manager.data = self.data
        self.manager.save_password("user2", "pass2", "example2.com", "notes2", "category2")
        self.manager.data = {}  # Clear the current data
        self.assertEqual(self.manager.load_data(), self.data)

    @patch("builtins.open", new_callable=mock_open)
    def test_save_password(self, mock_open):
        self.manager.data = self.data
        self.manager.save_password("user2", "pass2", "example2.com", "notes2", "category2")
        mock_open.assert_called_with("passwords.json", "w")

    def test_view_passwords(self):
        self.manager.data = self.data
        with patch("builtins.print") as mock_print:
            self.manager.view_passwords()
            mock_print.assert_any_call("Username: user1")
            mock_print.assert_any_call("Password: pass1")

    def test_generate_key(self):
        key = generate_key()
        self.assertEqual(len(key), 44)

    def test_encrypt_decrypt_data(self):
        data = "testdata"
        encrypted_data = encrypt_data(data, self.key)
        decrypted_data = decrypt_data(encrypted_data, self.key)
        self.assertEqual(data, decrypted_data)

    def test_hash_password(self):
        hashed_password = hash_password(self.master_password)
        self.assertEqual(len(hashed_password), 64)  # Length of SHA-256 hash

    def test_generate_password(self):
        password = generate_password()
        self.assertEqual(len(password), 12)  # Default length

if __name__ == "__main__":
    unittest.main()
