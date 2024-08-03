import unittest
from unittest.mock import patch
from source.main import PasswordManager
import string

class TestPasswordManager(unittest.TestCase):

    def setUp(self):
        self.manager = PasswordManager('master_password')

    def test_add_password(self):
        self.manager.add_password('example.com', 'user', 'pass')
        self.assertIn('example.com', self.manager.data)

    def test_get_password(self):
        self.manager.add_password('example.com', 'user', 'pass')
        password = self.manager.get_password('example.com')
        self.assertEqual(password['username'], 'user')
        self.assertEqual(password['password'], 'pass')

    def test_delete_password(self):
        self.manager.add_password('example.com', 'user', 'pass')
        self.manager.delete_password('example.com')
        self.assertNotIn('example.com', self.manager.data)

    def test_update_password(self):
        self.manager.add_password('example.com', 'user', 'pass')
        self.manager.update_password('example.com', password='newpass')
        password = self.manager.get_password('example.com')
        self.assertEqual(password['password'], 'newpass')

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

if __name__ == '__main__':
    unittest.main()