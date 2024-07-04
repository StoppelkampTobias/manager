import unittest
from unittest.mock import patch
import sys
import os

# Fügen Sie den Quellordner zum Systempfad hinzu
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../source')))

import main
from password_manager import PasswordManager

class TestMain(unittest.TestCase):

    @patch('builtins.input', side_effect=['a', 'test_user', 'test_password', 'test_url', 'test_notes', 'test_category'])
    @patch('getpass.getpass', return_value='master_password')
    @patch('password_manager.PasswordManager.save_password')
    def test_add_password(self, mock_save_password, mock_getpass, mock_input):
        main.main()
        mock_save_password.assert_called_once_with('test_user', 'test_password', 'test_url', 'test_notes', 'test_category')

    @patch('builtins.input', side_effect=['v'])
    @patch('getpass.getpass', return_value='master_password')
    @patch('password_manager.PasswordManager.view_passwords')
    def test_view_passwords(self, mock_view_passwords, mock_getpass, mock_input):
        main.main()
        mock_view_passwords.assert_called_once()

    @patch('builtins.input', side_effect=['g', '12', 'y', 'y', 'y'])
    @patch('getpass.getpass', return_value='master_password')
    @patch('password_manager.PasswordManager.generate_password', return_value='generated_password')
    def test_generate_password(self, mock_generate_password, mock_getpass, mock_input):
        with patch('builtins.print') as mock_print:
            main.main()
            mock_generate_password.assert_called_once_with(12, True, True, True)
            mock_print.assert_any_call('Generated password: generated_password')

    @patch('builtins.input', side_effect=['r', 'test_url'])
    @patch('getpass.getpass', return_value='master_password')
    @patch('password_manager.PasswordManager.retrieve_password')
    def test_retrieve_password(self, mock_retrieve_password, mock_getpass, mock_input):
        main.main()
        mock_retrieve_password.assert_called_once_with('test_url')

    @patch('builtins.input', side_effect=['e', 'test_url', 'new_user', 'new_password', 'new_notes', 'new_categories'])
    @patch('getpass.getpass', return_value='master_password')
    @patch('password_manager.PasswordManager.edit_password')
    def test_edit_password(self, mock_edit_password, mock_getpass, mock_input):
        main.main()
        mock_edit_password.assert_called_once_with('test_url')

    @patch('builtins.input', side_effect=['d', 'test_url'])
    @patch('getpass.getpass', return_value='master_password')
    @patch('password_manager.PasswordManager.delete_password')
    def test_delete_password(self, mock_delete_password, mock_getpass, mock_input):
        main.main()
        mock_delete_password.assert_called_once_with('test_url')

if __name__ == "__main__":
    unittest.main()