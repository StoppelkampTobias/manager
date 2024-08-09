# pylint: disable=C)
"""
disables pylint warning for invalid constant name
"""
# pylint: disable=unused-import,unused-variable

import unittest
import hashlib
from unittest.mock import patch, mock_open, MagicMock
from datetime import datetime
import json
from source.main import PasswordManager

# pylint: disable=missing-docstring

class TestPasswordManager(unittest.TestCase):

    @patch('builtins.open', new_callable=mock_open, read_data=b'')
    @patch('your_module_name.Fernet')
    def test_load_data_empty_file(self, mock_fernet, mock_open_file):
        mock_fernet_instance = mock_fernet.return_value
        mock_fernet_instance.decrypt.return_value = b'{}'

        pm = PasswordManager('masterpassword')
        mock_open_file.assert_called_once_with('passwords.json', 'rb')
        mock_fernet_instance.decrypt.assert_called_once()
        self.assertEqual(pm.data, {})

    @patch('builtins.open', new_callable=mock_open)
    @patch('your_module_name.Fernet')
    def test_save_data(self, mock_fernet, mock_open_file):
        mock_fernet_instance = mock_fernet.return_value
        pm = PasswordManager('masterpassword')
        pm.data = {'example.com': {'username': 'user', 'password': 'pass', 'createdAt': '2024-01-01T00:00:00'}}
        
        pm.saveData()
        
        mock_fernet_instance.encrypt.assert_called_once()
        mock_open_file.assert_called_once_with('passwords.json', 'wb')
        handle = mock_open_file()
        handle.write.assert_called_once()

    def test_add_password(self):
        pm = PasswordManager('masterpassword')
        with patch.object(pm, 'saveData', return_value=None) as mock_save_data:
            pm.addPassword('example.com', 'user', 'pass', 'notes', 'category')
            self.assertIn('example.com', pm.data)
            self.assertEqual(pm.data['example.com']['username'], 'user')
            self.assertEqual(pm.data['example.com']['password'], 'pass')
            self.assertEqual(pm.data['example.com']['notes'], 'notes')
            self.assertEqual(pm.data['example.com']['category'], 'category')
            self.assertTrue(mock_save_data.called)

    def test_get_password(self):
        pm = PasswordManager('masterpassword')
        pm.data = {'example.com': {'username': 'user', 'password': 'pass'}}
        result = pm.getPassword('example.com')
        self.assertEqual(result['username'], 'user')
        self.assertEqual(result['password'], 'pass')

    def test_delete_password(self):
        pm = PasswordManager('masterpassword')
        pm.data = {'example.com': {'username': 'user', 'password': 'pass'}}
        with patch.object(pm, 'saveData', return_value=None) as mock_save_data:
            pm.deletePassword('example.com')
            self.assertNotIn('example.com', pm.data)
            self.assertTrue(mock_save_data.called)

    def test_update_password(self):
        pm = PasswordManager('masterpassword')
        pm.data = {'example.com': {'username': 'user', 'password': 'pass'}}
        with patch.object(pm, 'saveData', return_value=None) as mock_save_data:
            pm.updatePassword('example.com', username='new_user', password='new_pass')
            self.assertEqual(pm.data['example.com']['username'], 'new_user')
            self.assertEqual(pm.data['example.com']['password'], 'new_pass')
            self.assertTrue(mock_save_data.called)

    def test_search_password(self):
        pm = PasswordManager('masterpassword')
        pm.data = {
            'example.com': {'username': 'user', 'password': 'pass'},
            'testsite.com': {'username': 'tester', 'password': 'testpass'}
        }
        results = pm.searchPassword('example')
        self.assertIn('example.com', results)
        self.assertNotIn('testsite.com', results)

    def test_check_password_strength(self):
        pm = PasswordManager('masterpassword')
        strong_password = 'StrongPass123!'
        weak_password = 'weak'
        self.assertTrue(pm.checkPasswordStrength(strong_password))
        self.assertFalse(pm.checkPasswordStrength(weak_password))

    def test_check_reused_password(self):
        pm = PasswordManager('masterpassword')
        pm.data = {'example.com': {'username': 'user', 'password': 'pass'}}
        self.assertTrue(pm.checkReusedPassword('pass'))
        self.assertFalse(pm.checkReusedPassword('differentpass'))

    @patch('your_module_name.requests.get')
    def test_check_pwned_password(self, mock_requests_get):
        pm = PasswordManager('masterpassword')
        response_data = 'ABCDEF1234567890:1\n1234567890ABCDEF:2'
        mock_requests_get.return_value.status_code = 200
        mock_requests_get.return_value.text = response_data

        pwned_password = 'password'
        not_pwned_password = 'differentpassword'

        hashed_pwned = hashlib.sha1(pwned_password.encode()).hexdigest().upper()
        hashed_not_pwned = hashlib.sha1(not_pwned_password.encode()).hexdigest().upper()

        self.assertTrue(pm.checkPwnedPassword(pwned_password))
        self.assertFalse(pm.checkPwnedPassword(not_pwned_password))

if __name__ == "__main__":
    unittest.main()
