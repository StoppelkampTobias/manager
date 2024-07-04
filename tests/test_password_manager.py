import unittest
from unittest.mock import patch, mock_open
import sys
import os

# Fügen Sie den Quellordner zum Systempfad hinzu
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../source')))

from password_manager import PasswordManager

class TestPasswordManager(unittest.TestCase):

    def setUp(self):
        self.pm = PasswordManager("master_password")

    @patch('builtins.open', new_callable=mock_open, read_data='{}')
    @patch('os.path.exists', return_value=True)
    def test_save_password(self, mock_exists, mock_open):
        self.pm.save_password('test_user', 'test_password', 'test_url', 'test_notes', 'test_category')
        mock_open.assert_called_with('passwords.json', 'w')

    @patch('builtins.open', new_callable=mock_open, read_data='{"hashed_master_password": []}')
    @patch('os.path.exists', return_value=True)
    def test_view_passwords(self, mock_exists, mock_open):
        with patch('json.load', return_value={'hashed_master_password': [{'username': 'test_user', 'password': 'test_password'}]}):
            with patch('password_manager.decrypt_data', return_value='test_password'):
                with patch('builtins.print') as mock_print:
                    self.pm.view_passwords()
                    mock_print.assert_any_call(f'Username: test_user')

    def test_generate_password(self):
        password = self.pm.generate_password(12)
        self.assertEqual(len(password), 12)

    @patch('builtins.open', new_callable=mock_open, read_data='{"hashed_master_password": []}')
    @patch('os.path.exists', return_value=True)
    def test_retrieve_password(self, mock_exists, mock_open):
        with patch('json.load', return_value={'hashed_master_password': [{'url': 'test_url', 'username': 'test_user', 'password': 'test_password'}]}):
            with patch('password_manager.decrypt_data', return_value='test_password'):
                with patch('builtins.print') as mock_print:
                    self.pm.retrieve_password('test_url')
                    mock_print.assert_any_call(f'URL: test_url')

    @patch('builtins.open', new_callable=mock_open, read_data='{"hashed_master_password": []}')
    @patch('os.path.exists', return_value=True)
    def test_edit_password(self, mock_exists, mock_open):
        with patch('json.load', return_value={'hashed_master_password': [{'url': 'test_url', 'username': 'test_user', 'password': 'test_password'}]}):
            with patch('password_manager.decrypt_data', return_value='test_password'):
                with patch('password_manager.encrypt_data', return_value='encrypted_data'):
                    self.pm.edit_password('test_url')
                    self.assertTrue(mock_open.called)

    @patch('builtins.open', new_callable=mock_open, read_data='{"hashed_master_password": []}')
    @patch('os.path.exists', return_value=True)
    def test_delete_password(self, mock_exists, mock_open):
        with patch('json.load', return_value={'hashed_master_password': [{'url': 'test_url', 'username': 'test_user', 'password': 'test_password'}]}):
            self.pm.delete_password('test_url')
            self.assertTrue(mock_open.called)

if __name__ == "__main__":
    unittest.main()