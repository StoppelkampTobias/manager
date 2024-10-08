#pylint: disable=C)
#pylint: disable=W)
import unittest
from unittest.mock import MagicMock, patch
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from source.interface import CursesInterface

class TestCursesInterface(unittest.TestCase):

    def setUp(self):
        self.pm = MagicMock()
        self.interface = CursesInterface(self.pm)

    def testInitialization(self):
        self.assertIsInstance(self.interface, CursesInterface)
        self.assertEqual(self.interface.pm, self.pm)

    @patch('source.interface.curses')
    def testDrawMenu(self, mockCurses):
        stdscr = MagicMock()
        mockCurses.color_pair.return_value = 1
        stdscr.getmaxyx.return_value = (24, 80)
        self.interface.drawMenu(stdscr)
        self.assertEqual(stdscr.addstr.call_count, 9)

    @patch('source.interface.curses')
    def testDrawMenuDifferentSize(self, mockCurses):
        stdscr = MagicMock()
        mockCurses.color_pair.return_value = 1
        stdscr.getmaxyx.return_value = (30, 100)
        self.interface.drawMenu(stdscr)
        self.assertEqual(stdscr.addstr.call_count, 9)

    @patch('source.interface.curses')
    def testGetInput(self, mockCurses):
        stdscr = MagicMock()
        stdscr.getstr.return_value = b'test_input'
        result = self.interface.getInput(stdscr, "Enter something: ")
        self.assertEqual(result, 'test_input')

    @patch('source.interface.curses')
    def testGetInputEmpty(self, mockCurses):
        stdscr = MagicMock()
        stdscr.getstr.return_value = b''
        result = self.interface.getInput(stdscr, "Enter something: ")
        self.assertEqual(result, '')

    @patch('source.interface.curses')
    def testGetPasswordInput(self, mockCurses):
        stdscr = MagicMock()
        stdscr.getch.side_effect = [ord('p'), ord('a'), ord('s'), ord('s'), 10]
        result = self.interface.getPasswordInput(stdscr, "Enter password: ")
        self.assertEqual(result, 'pass')

    @patch('source.interface.curses')
    def testGetPasswordInputEmpty(self, mockCurses):
        stdscr = MagicMock()
        stdscr.getch.side_effect = [10]
        result = self.interface.getPasswordInput(stdscr, "Enter password: ")
        self.assertEqual(result, '')

    @patch('source.interface.curses')
    def testRun(self, mockCurses):
        stdscr = MagicMock()
        mockCurses.KEY_DOWN = 258
        mockCurses.KEY_UP = 259
        mockCurses.KEY_ENTER = 10
        stdscr.getmaxyx.return_value = (24, 80)  # Mock the terminal size

        stdscr.getch.side_effect = [
            mockCurses.KEY_DOWN,  # Move to 'Get Password'
            mockCurses.KEY_ENTER,  # Select 'Get Password'
            27  # Exit
        ]

        with patch.object(self.interface, 'getPassword') as mockGetPassword:
            self.interface.run(stdscr)
            mockGetPassword.assert_called_once()

    @patch('source.interface.curses')
    def testAddPasswordStrong(self, mockCurses):
        stdscr = MagicMock()
        self.pm.checkPasswordStrength.return_value = (True, [])

        with patch.object(self.interface, 'getInput', side_effect=["example.com", "user", "", ""]), \
            patch.object(self.interface, 'getPasswordInput', return_value="StrongPass123"):
            self.interface.addPassword(stdscr)
            self.pm.addPassword.assert_called_once_with("example.com", "user", "StrongPass123", "", "")

    @patch('source.interface.curses')
    def testAddPasswordGenerateStrong(self, mockCurses):
        stdscr = MagicMock()
        self.pm.checkPasswordStrength.return_value = (False, ["too short"])
        self.pm.generateStrongPassword.return_value = "StrongPass123"
        stdscr.getch.return_value = ord('3')  # Simulate choosing to generate a strong password

        with patch.object(self.interface, 'getInput', side_effect=["example.com", "user", "", ""]), \
            patch.object(self.interface, 'getPasswordInput', return_value="weakpass"):
            self.interface.addPassword(stdscr)
            self.pm.addPassword.assert_called_once_with("example.com", "user", "StrongPass123", "", "")

    @patch('source.interface.curses')
    def testGetPassword(self, mockCurses):
        stdscr = MagicMock()
        self.pm.getPassword.return_value = {
            'username': 'user',
            'password': 'pass',
            'notes': 'some notes',
            'category': 'general',
            'createdAt': '2024-01-01'
        }

        with patch.object(self.interface, 'getInput', return_value="example.com"):
            self.interface.getPassword(stdscr)
            self.pm.getPassword.assert_called_once_with("example.com")
            stdscr.addstr.assert_any_call(0, 0, "Username: user")

    @patch('source.interface.curses')
    def testDeletePassword(self, mockCurses):
        stdscr = MagicMock()

        with patch.object(self.interface, 'getInput', return_value="example.com"):
            self.interface.deletePassword(stdscr)
            self.pm.deletePassword.assert_called_once_with("example.com")
            stdscr.addstr.assert_called_with(2, 0, "Password deleted successfully!")

    @patch('source.interface.curses')
    def testUpdatePassword(self, mockCurses):
        stdscr = MagicMock()

        with patch.object(self.interface, 'getInput', return_value="example.com"), \
             patch.object(self.interface, 'getPasswordInput', return_value="newpass"):
            self.interface.updatePassword(stdscr)
            self.pm.updatePassword.assert_called_once_with("example.com", "example.com", "newpass", "example.com", "example.com")

    @patch('source.interface.curses')
    def testSearchPassword(self, mockCurses):
        stdscr = MagicMock()
        self.pm.searchPassword.return_value = {
            'example.com': {
                'username': 'user',
                'password': 'pass',
                'notes': 'some notes',
                'category': 'general',
                'createdAt': '2024-01-01'
            }
        }

        with patch.object(self.interface, 'getInput', return_value="example"):
            self.interface.searchPassword(stdscr)
            self.pm.searchPassword.assert_called_once_with("example")
            stdscr.addstr.assert_any_call(0, 0, "Site: example.com")

    @patch('source.interface.curses')
    def testCheckPwnedPasswordWithPwnedPasswords(self, mockCurses):
        stdscr = MagicMock()
        # Mock the pm data and checkPwnedPassword method
        self.pm.data = {
            'example.com': {'password': '123456'},
            'another.com': {'password': 'password'}
        }
        self.pm.checkPwnedPassword.side_effect = lambda password: password in ['123456']

        self.interface.checkPwnedPassword(stdscr)

        stdscr.clear.assert_called_once()
        stdscr.addstr.assert_any_call(0, 0, "Pwned password found at site: example.com")
        stdscr.addstr.assert_any_call(1, 0, "Password: 123456")
        stdscr.refresh.assert_called_once()
        stdscr.getch.assert_called_once()

    @patch('source.interface.curses')
    def testCheckPwnedPasswordNoPwnedPasswords(self, mockCurses):
        stdscr = MagicMock()
        # Mock the pm data and checkPwnedPassword method
        self.pm.data = {
            'example.com': {'password': 'securepassword'},
            'another.com': {'password': 'anothersecurepassword'}
        }
        self.pm.checkPwnedPassword.side_effect = lambda password: False

        self.interface.checkPwnedPassword(stdscr)

        stdscr.clear.assert_called_once()
        stdscr.addstr.assert_called_once_with(0, 0, "No pwned passwords found!")
        stdscr.refresh.assert_called_once()
        stdscr.getch.assert_called_once()

    @patch('source.interface.curses')
    def testCheckReusedPasswordWithReusedPasswords(self, mockCurses):
        stdscr = MagicMock()
        # Mock the pm data and checkReusedPassword method
        self.pm.data = {
            'example.com': {'password': 'reusedpassword'},
            'another.com': {'password': 'reusedpassword'},
            'unique.com': {'password': 'uniquepassword'}
        }
        self.pm.checkReusedPassword.side_effect = lambda password: password == 'reusedpassword'

        self.interface.checkReusedPassword(stdscr)

        stdscr.clear.assert_called_once()
        stdscr.addstr.assert_any_call(0, 0, "Reused password found at site: example.com")
        stdscr.addstr.assert_any_call(1, 0, "Password: reusedpassword")
        stdscr.addstr.assert_any_call(3, 0, "Reused password found at site: another.com")
        stdscr.addstr.assert_any_call(4, 0, "Password: reusedpassword")
        stdscr.refresh.assert_called_once()
        stdscr.getch.assert_called_once()

    @patch('source.interface.curses')
    def testCheckReusedPasswordNoReusedPasswords(self, mockCurses):
        stdscr = MagicMock()
        # Mock the pm data and checkReusedPassword method
        self.pm.data = {
            'example.com': {'password': 'uniquepassword1'},
            'another.com': {'password': 'uniquepassword2'}
        }
        self.pm.checkReusedPassword.side_effect = lambda password: False

        self.interface.checkReusedPassword(stdscr)

        stdscr.clear.assert_called_once()
        stdscr.addstr.assert_called_once_with(0, 0, "No reused passwords found!")
        stdscr.refresh.assert_called_once()
        stdscr.getch.assert_called_once()

if __name__ == '__main__':
    unittest.main()