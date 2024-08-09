#pylint: disable=C)
import unittest
import hashlib
import json
from unittest.mock import patch, mock_open, MagicMock
from datetime import datetime
from source.main import PasswordManager  

# pylint: disable=missing-docstring

class TestPasswordManager(unittest.TestCase):

    @patch('source.main.Fernet')
    @patch('builtins.open', new_callable=mock_open, read_data=b'{}')
    def test_load_data_empty_file(self, mock_file, mock_fernet):
        mock_fernet_instance = mock_fernet.return_value
        mock_fernet_instance.decrypt.return_value = b'{}'

        pm = PasswordManager('masterpassword')
        mock_file.assert_called_once_with('passwords.json', 'rb')
        mock_fernet_instance.decrypt.assert_called_once()
        self.assertEqual(pm.data, {})

    @patch('source.main.Fernet')
    @patch('builtins.open', new_callable=mock_open)
    def test_save_data(self, mock_file, mock_fernet):
        mock_fernet_instance = mock_fernet.return_value
        mock_fernet_instance.encrypt.return_value = b'encrypted_data'
        mock_fernet_instance.decrypt.return_value = b'{}'  # Return a valid empty JSON object

        pm = PasswordManager('masterpassword')
        pm.data = {'example.com': {'username': 'user', 'password': 'pass', 'createdAt': '2024-01-01T00:00:00'}}
        
        pm.saveData()

        # Verify that open was called twice, first for reading and then for writing
        self.assertEqual(mock_file.call_count, 2)

        # Check that the first call was for reading
        mock_file.assert_any_call('passwords.json', 'rb')

        # Check that the second call was for writing
        mock_file.assert_any_call('passwords.json', 'wb')

        # Check that the write method was called with the expected encrypted data
        handle = mock_file()
        handle.write.assert_called_once_with(b'encrypted_data')



    @patch('source.main.Fernet')
    def test_add_password(self, mock_fernet):
        mock_fernet_instance = mock_fernet.return_value
        mock_fernet_instance.decrypt.return_value = b'{}'
        mock_fernet_instance.encrypt.return_value = b'encrypted_data'

        pm = PasswordManager('masterpassword')
        pm.addPassword('example.com', 'user', 'pass', 'notes', 'category')

        self.assertIn('example.com', pm.data)
        self.assertEqual(pm.data['example.com']['username'], 'user')
        self.assertEqual(pm.data['example.com']['password'], 'pass')
        self.assertEqual(pm.data['example.com']['notes'], 'notes')
        self.assertEqual(pm.data['example.com']['category'], 'category')

    @patch('source.main.Fernet')
    def test_get_password(self, mock_fernet):
        mock_fernet_instance = mock_fernet.return_value
        mock_fernet_instance.decrypt.return_value = b'{}'
        
        pm = PasswordManager('masterpassword')
        pm.data = {'example.com': {'username': 'user', 'password': 'pass'}}
        
        result = pm.getPassword('example.com')
        self.assertEqual(result['username'], 'user')
        self.assertEqual(result['password'], 'pass')

    @patch('source.main.Fernet')
    def test_delete_password(self, mock_fernet):
        mock_fernet_instance = mock_fernet.return_value
        mock_fernet_instance.decrypt.return_value = b'{}'
        mock_fernet_instance.encrypt.return_value = b'encrypted_data'
        
        pm = PasswordManager('masterpassword')
        pm.data = {'example.com': {'username': 'user', 'password': 'pass'}}
        
        pm.deletePassword('example.com')
        self.assertNotIn('example.com', pm.data)

    @patch('source.main.Fernet')
    def test_update_password(self, mock_fernet):
        mock_fernet_instance = mock_fernet.return_value
        mock_fernet_instance.decrypt.return_value = b'{}'
        mock_fernet_instance.encrypt.return_value = b'encrypted_data'
        
        pm = PasswordManager('masterpassword')
        pm.data = {'example.com': {'username': 'user', 'password': 'pass'}}
        
        pm.updatePassword('example.com', username='new_user', password='new_pass')
        self.assertEqual(pm.data['example.com']['username'], 'new_user')
        self.assertEqual(pm.data['example.com']['password'], 'new_pass')

    @patch('source.main.Fernet')
    def test_search_password(self, mock_fernet):
        mock_fernet_instance = mock_fernet.return_value
        mock_fernet_instance.decrypt.return_value = b'{}'
        
        pm = PasswordManager('masterpassword')
        pm.data = {
            'example.com': {'username': 'user', 'password': 'pass'},
            'testsite.com': {'username': 'tester', 'password': 'testpass'}
        }
        
        results = pm.searchPassword('example')
        self.assertIn('example.com', results)
        self.assertNotIn('testsite.com', results)

    @patch('source.main.Fernet')
    def test_check_password_strength(self, mock_fernet):
        mock_fernet_instance = mock_fernet.return_value
        mock_fernet_instance.decrypt.return_value = b'{}'
        
        pm = PasswordManager('masterpassword')
        strong_password = 'StrongPass123!'
        weak_password = 'weak'
        
        self.assertTrue(pm.checkPasswordStrength(strong_password))
        self.assertFalse(pm.checkPasswordStrength(weak_password))

    @patch('source.main.Fernet')
    def test_check_reused_password(self, mock_fernet):
        mock_fernet_instance = mock_fernet.return_value
        mock_fernet_instance.decrypt.return_value = b'{}'
        
        pm = PasswordManager('masterpassword')
        pm.data = {'example.com': {'username': 'user', 'password': 'pass'}}
        
        self.assertTrue(pm.checkReusedPassword('pass'))
        self.assertFalse(pm.checkReusedPassword('differentpass'))

    @patch('source.main.requests.get')
    @patch('source.main.Fernet')
    def test_check_pwned_password(self, mock_fernet, mock_requests_get):
        mock_fernet_instance = mock_fernet.return_value
        mock_fernet_instance.decrypt.return_value = b'{}'
        
        pm = PasswordManager('masterpassword')
        
        response_data = '5BAA6:003A68...'
        mock_requests_get.return_value.status_code = 200
        mock_requests_get.return_value.text = response_data

        pwned_password = 'password'
        hashed_pwned = hashlib.sha1(pwned_password.encode()).hexdigest().upper()
        prefix = hashed_pwned[:5]  # The first 5 characters sent to the API
        suffix = hashed_pwned[5:]  # The remaining characters compared to the API response

        # Adjust the mocked response to include the hashed suffix
        mock_requests_get.return_value.text = f'{suffix}:3\n'

        self.assertTrue(pm.checkPwnedPassword(pwned_password))
