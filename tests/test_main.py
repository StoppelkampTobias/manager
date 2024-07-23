import unittest
from source.main import PasswordManager

class TestPasswordManager(unittest.TestCase):
    def setUp(self):
        self.manager = PasswordManager("test_master_password")

    def test_add_and_get_password(self):
        self.manager.add_password("test_site", "test_user", "test_password")
        credentials = self.manager.get_password("test_site")
        self.assertEqual(credentials['username'], "test_user")
        self.assertEqual(credentials['password'], "test_password")

    def tearDown(self):
        if os.path.exists(self.manager.data_file):
            os.remove(self.manager.data_file)

if __name__ == '__main__':
    unittest.main()