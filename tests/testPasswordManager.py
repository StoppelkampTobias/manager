#pylint: disable=C)
import unittest
from unittest.mock import patch, mock_open
from cryptography.fernet import InvalidToken
import json
from source.passwordManager import PasswordManager


class TestPasswordManager(unittest.TestCase):

    def setUp(self):
        self.masterPassword = "SuperSecretMasterPassword"
        self.passwordManager = PasswordManager(self.masterPassword)

    def testGenerateKey(self):
        key = self.passwordManager.generateKey(self.masterPassword)
        self.assertEqual(len(key), 44)  # Base64 URL safe encoded SHA-256 hash should be 44 bytes long

    @patch('builtins.open', new_callable=mock_open, read_data=b'')
    @patch('cryptography.fernet.Fernet.decrypt')
    def testLoadDataEmptyFile(self, _mockDecrypt, _mockFile):
        _mockDecrypt.return_value = json.dumps({}).encode()
        self.passwordManager.loadData()
        self.assertEqual(self.passwordManager.data, {})

    @patch('builtins.open', new_callable=mock_open, read_data=b'encrypted_data')
    @patch('cryptography.fernet.Fernet.decrypt', side_effect=InvalidToken)
    def testLoadDataInvalidToken(self, _mockDecrypt, _mockFile):
        with self.assertRaises(InvalidToken):
            self.passwordManager.loadData()

    @patch('builtins.open', new_callable=mock_open)
    @patch('cryptography.fernet.Fernet.encrypt')
    def testSaveData(self, _mockEncrypt, _mockFile):
        self.passwordManager.data = {'example.com': {'username': 'user', 'password': 'pass'}}
        _mockEncrypt.return_value = b'encrypted_data'
        self.passwordManager.saveData()
        _mockFile().write.assert_called_once_with(b'encrypted_data')

    def testAddPassword(self):
        self.passwordManager.addPassword('example.com', 'user', 'pass')
        self.assertIn('example.com', self.passwordManager.data)
        self.assertEqual(self.passwordManager.data['example.com']['username'], 'user')

    def testGetPassword(self):
        self.passwordManager.data = {'example.com': {'username': 'user', 'password': 'pass'}}
        passwordEntry = self.passwordManager.getPassword('example.com')
        self.assertIsNotNone(passwordEntry)
        self.assertEqual(passwordEntry['username'], 'user')

    def testDeletePassword(self):
        self.passwordManager.data = {'example.com': {'username': 'user', 'password': 'pass'}}
        self.passwordManager.deletePassword('example.com')
        self.assertNotIn('example.com', self.passwordManager.data)

    def testUpdatePassword(self):
        self.passwordManager.data = {'example.com': {'username': 'user', 'password': 'pass'}}
        self.passwordManager.updatePassword('example.com', username='new_user', password='new_pass')
        self.assertEqual(self.passwordManager.data['example.com']['username'], 'new_user')
        self.assertEqual(self.passwordManager.data['example.com']['password'], 'new_pass')

    def testSearchPassword(self):
        self.passwordManager.data = {
            'example.com': {'username': 'user', 'password': 'pass'},
            'testsite.com': {'username': 'test', 'password': 'pass123'}
        }
        results = self.passwordManager.searchPassword('test')
        self.assertIn('testsite.com', results)
        self.assertNotIn('example.com', results)

    def testCheckPasswordStrength(self):
        weakPassword = 'weak'
        strongPassword = 'Str0ngPass!'
        isStrong, reasons = self.passwordManager.checkPasswordStrength(weakPassword)
        self.assertFalse(isStrong)
        self.assertGreater(len(reasons), 0)

        isStrong, reasons = self.passwordManager.checkPasswordStrength(strongPassword)
        self.assertTrue(isStrong)
        self.assertEqual(len(reasons), 0)

    def testGenerateStrongPassword(self):
        password = self.passwordManager.generateStrongPassword(12)
        isStrong, reasons = self.passwordManager.checkPasswordStrength(password)
        print(f"Generated password: {password}")
        if not isStrong:
            print(f"Reasons for weakness: {reasons}")
        self.assertTrue(isStrong)
        self.assertEqual(len(password), 12)


    def testCheckReusedPassword(self):
        self.passwordManager.data = {'example.com': {'username': 'user', 'password': 'pass'}}
        self.assertTrue(self.passwordManager.checkReusedPassword('pass'))
        self.assertFalse(self.passwordManager.checkReusedPassword('different_pass'))

    @patch('requests.get')
    def testCheckPwnedPassword(self, _mockGet):
        # 'password' SHA-1 hash is '5BAA61E4C9B93F3F0682250B6CF8331B7EE68FD8'
        # Prefix: '5BAA6', Suffix: '1E4C9B93F3F0682250B6CF8331B7EE68FD8'
        _mockGet.return_value.status_code = 200
        _mockGet.return_value.text = '1E4C9B93F3F0682250B6CF8331B7EE68FD8:5\nABCDE:2\n'

        # Now the suffix should match, and the test should pass
        self.assertTrue(self.passwordManager.checkPwnedPassword('password'))

        # Test a password that has not been pwned
        _mockGet.return_value.text = '00000:1\n'
        self.assertFalse(self.passwordManager.checkPwnedPassword('notcompromisedpassword'))


if __name__ == '__main__':
    unittest.main()
