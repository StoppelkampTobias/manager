import unittest
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

    def test_check_pwned_password(self):
        password = 'password'
        # Assume that 'password' is a known pwned password
        self.assertTrue(self.manager.check_pwned_password(password))

if __name__ == '__main__':
    unittest.main()