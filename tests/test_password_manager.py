import unittest
from source.password_manager import PasswordManager
from unittest.mock import patch

class TestPasswordManager(unittest.TestCase):
    @patch('getpass.getpass', return_value='masterpassword')
    def setUp(self, mock_getpass):
        self.manager = PasswordManager(filename='test_passwords.json')

    @patch('getpass.getpass', return_value='masterpassword')
    def test_save_password(self, mock_getpass):
        self.manager.save_password('example.com', 'user', 'pass')
        self.assertIn('example.com', self.manager.passwords)

    @patch('getpass.getpass', return_value='masterpassword')
    def test_get_password(self, mock_getpass):
        self.manager.save_password('example.com', 'user', 'pass')
        password = self.manager.get_password('example.com')
        self.assertEqual(password['password'], 'pass')

    def tearDown(self):
        os.remove('test_passwords.json')
        if os.path.exists('master.txt'):
            os.remove('master.txt')

if __name__ == "__main__":
    unittest.main()
