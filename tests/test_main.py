import unittest
from unittest.mock import patch, mock_open
from source.main import PasswordManager
import json

class TestPasswordManager(unittest.TestCase):

    def setUp(self):
        self.manager = PasswordManager('master_password')

    def test_add_password(self):
        self.manager.add_password('example.com', 'user', 'pass')
        self.assertIn('example.com', self.manager.data)

    def test_add_password_missing_fields(self):
        with self.assertRaises(ValueError):
            self.manager.add_password('example.com', '', 'pass')
        with self.assertRaises(ValueError):
            self.manager.add_password('example.com', 'user', '')

    def test_get_password(self):
        self.manager.add_password('example.com', 'user', 'pass')
        password = self.manager.get_password('example.com')
        self.assertEqual(password['username'], 'user')
        self.assertEqual(password['password'], 'pass')

    def test_get_nonexistent_password(self):
        password = self.manager.get_password('nonexistent.com')
        self.assertIsNone(password)

    def test_delete_password(self):
        self.manager.add_password('example.com', 'user', 'pass')
        self.manager.delete_password('example.com')
        self.assertNotIn('example.com', self.manager.data)

    def test_delete_nonexistent_password(self):
        with self.assertRaises(ValueError):
            self.manager.delete_password('nonexistent.com')

    def test_update_password(self):
        self.manager.add_password('example.com', 'user', 'pass')
        self.manager.update_password('example.com', password='newpass')
        password = self.manager.get_password('example.com')
        self.assertEqual(password['password'], 'newpass')

    def test_update_nonexistent_password(self):
        with self.assertRaises(ValueError):
            self.manager.update_password('nonexistent.com', password='newpass')

    def test_search_password(self):
        self.manager.add_password('example.com', 'user', 'pass')
        results = self.manager.search_password('example')
        self.assertIn('example.com', results)

    def test_check_password_strength(self):
        strong_password = 'Str0ngP@ssw0rd!'
        weak_password = 'weak'
        self.assertTrue(self.manager.check_password_strength(strong_password))
        self.assertFalse(self.manager.check_password_strength(weak_password))

    def test_check_reused_password(self):
        self.manager.add_password('example.com', 'user', 'pass')
        self.assertTrue(self.manager.check_reused_password('pass'))
        self.assertFalse(self.manager.check_reused_password('newpass'))

    @patch('source.main.requests.get')
    def test_check_pwned_password(self, mock_get):
        mock_response = unittest.mock.Mock()
        mock_response.status_code = 200
        mock_response.text = '00000A6D7:1\n00000E8F2:1'
        mock_get.return_value = mock_response

        pwned_password = 'password'
        self.assertTrue(self.manager.check_pwned_password(pwned_password))

        safe_password = 'safe_password'
        self.assertFalse(self.manager.check_pwned_password(safe_password))

    @patch('source.main.requests.get')
    def test_check_pwned_password_no_response(self, mock_get):
        mock_response = unittest.mock.Mock()
        mock_response.status_code = 503
        mock_get.return_value = mock_response

        password = 'password'
        self.assertFalse(self.manager.check_pwned_password(password))

    def test_add_password_with_notes_and_category(self):
        self.manager.add_password('example.com', 'user', 'pass', 'important note', 'work')
        password = self.manager.get_password('example.com')
        self.assertEqual(password['notes'], 'important note')
        self.assertEqual(password['category'], 'work')

    def test_update_password_username_and_notes(self):
        self.manager.add_password('example.com', 'user', 'pass')
        self.manager.update_password('example.com', username='newuser', notes='new note')
        password = self.manager.get_password('example.com')
        self.assertEqual(password['username'], 'newuser')
        self.assertEqual(password['notes'], 'new note')

    @patch('builtins.open', new_callable=mock_open)
    def test_save_data(self, mock_file):
        self.manager.add_password('example.com', 'user', 'pass')
        self.manager.save_data()
        mock_file.assert_called_with('passwords.json', 'wb')

    @patch('builtins.open', new_callable=mock_open, read_data=json.dumps({'example.com': {'username': 'user', 'password': 'pass'}}).encode())
    @patch('source.main.Fernet.decrypt', return_value=json.dumps({'example.com': {'username': 'user', 'password': 'pass'}}).encode())
    def test_load_data(self, mock_decrypt, mock_file):
        manager = PasswordManager('master_password')
        self.assertIn('example.com', manager.data)

    @patch('builtins.open', new_callable=mock_open)
    @patch('source.main.Fernet.decrypt')
    def test_load_data_file_not_found(self, mock_decrypt, mock_file):
        mock_file.side_effect = FileNotFoundError
        manager = PasswordManager('master_password')
        self.assertEqual(manager.data, {})

    @patch('builtins.open', new_callable=mock_open)
    @patch('source.main.Fernet.decrypt', side_effect=Exception('Decryption failed'))
    def test_load_data_decryption_failed(self, mock_decrypt, mock_file):
        mock_file.return_value.read.return_value = b'some_data'
        manager = PasswordManager('master_password')
        self.assertEqual(manager.data, {})

    def test_load_data_empty_file(self):
        with patch('builtins.open', mock_open(read_data=b'')):
            self.manager.load_data()
            self.assertEqual(self.manager.data, {})

    def test_generate_key(self):
        key = self.manager.generate_key('test_password')
        self.assertIsNotNone(key)
        self.assertEqual(len(key), 44)

    def test_save_data_io_error(self):
        with patch('builtins.open', mock_open()), \
             patch('source.main.Fernet.encrypt', side_effect=IOError('Failed to write')):
            manager = PasswordManager('master_password')
            manager.data = {'example.com': {'username': 'user', 'password': 'pass'}}
            with self.assertRaises(IOError):
                manager.save_data()

    def test_load_data_general_exception(self):
        with patch('builtins.open', mock_open(read_data=b'some_data')), \
             patch('source.main.Fernet.decrypt', side_effect=Exception('Decryption failed')):
            manager = PasswordManager('master_password')
            self.assertEqual(manager.data, {})

    @patch('builtins.open', new_callable=mock_open, read_data=b'some_data')
    @patch('source.main.Fernet.decrypt', return_value=b'invalid_json')
    def test_load_data_invalid_json(self, mock_decrypt, mock_file):
        manager = PasswordManager('master_password')
        self.assertEqual(manager.data, {})

if __name__ == '__main__':
    unittest.main()