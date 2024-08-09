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

    def test_initialization(self):
        self.assertIsInstance(self.interface, CursesInterface)
        self.assertEqual(self.interface.pm, self.pm)

    @patch('source.interface.curses')
    def test_drawMenu(self, mock_curses):
        stdscr = MagicMock()
        mock_curses.color_pair.return_value = 1
        stdscr.getmaxyx.return_value = (24, 80)
        self.interface.drawMenu(stdscr)
        self.assertEqual(stdscr.addstr.call_count, 9)

    @patch('source.interface.curses')
    def test_drawMenu_different_size(self, mock_curses):
        stdscr = MagicMock()
        mock_curses.color_pair.return_value = 1
        stdscr.getmaxyx.return_value = (30, 100)
        self.interface.drawMenu(stdscr)
        self.assertEqual(stdscr.addstr.call_count, 9)

    @patch('source.interface.curses')
    def test_getInput(self, mock_curses):
        stdscr = MagicMock()
        stdscr.getstr.return_value = b'test_input'
        result = self.interface.getInput(stdscr, "Enter something: ")
        self.assertEqual(result, 'test_input')

    @patch('source.interface.curses')
    def test_getInput_empty(self, mock_curses):
        stdscr = MagicMock()
        stdscr.getstr.return_value = b''
        result = self.interface.getInput(stdscr, "Enter something: ")
        self.assertEqual(result, '')

    @patch('source.interface.curses')
    def test_getPasswordInput(self, mock_curses):
        stdscr = MagicMock()
        stdscr.getch.side_effect = [ord('p'), ord('a'), ord('s'), ord('s'), 10]
        result = self.interface.getPasswordInput(stdscr, "Enter password: ")
        self.assertEqual(result, 'pass')

    @patch('source.interface.curses')
    def test_getPasswordInput_empty(self, mock_curses):
        stdscr = MagicMock()
        stdscr.getch.side_effect = [10]
        result = self.interface.getPasswordInput(stdscr, "Enter password: ")
        self.assertEqual(result, '')

    @patch('source.interface.curses')
    def test_run(self, mock_curses):
        stdscr = MagicMock()
        mock_curses.KEY_DOWN = 258
        mock_curses.KEY_UP = 259
        mock_curses.KEY_ENTER = 10
        stdscr.getmaxyx.return_value = (24, 80)  # Mock the terminal size

        stdscr.getch.side_effect = [
            mock_curses.KEY_DOWN,  # Move to 'Get Password'
            mock_curses.KEY_ENTER,  # Select 'Get Password'
            27  # Exit
        ]

        with patch.object(self.interface, 'getPassword') as mock_getPassword:
            self.interface.run(stdscr)
            mock_getPassword.assert_called_once()


    @patch('source.interface.curses')
    def test_addPassword_strong(self, mock_curses):
        stdscr = MagicMock()
        self.pm.checkPasswordStrength.return_value = (True, [])

        with patch.object(self.interface, 'getInput', side_effect=["example.com", "user", "", ""]), \
            patch.object(self.interface, 'getPasswordInput', return_value="StrongPass123"):
            self.interface.addPassword(stdscr)
            self.pm.addPassword.assert_called_once_with("example.com", "user", "StrongPass123", "", "")

    @patch('source.interface.curses')
    def test_addPassword_generate_strong(self, mock_curses):
        stdscr = MagicMock()
        self.pm.checkPasswordStrength.return_value = (False, ["too short"])
        self.pm.generateStrongPassword.return_value = "StrongPass123"
        stdscr.getch.return_value = ord('3')  # Simulate choosing to generate a strong password

        with patch.object(self.interface, 'getInput', side_effect=["example.com", "user", "", ""]), \
            patch.object(self.interface, 'getPasswordInput', return_value="weakpass"):
            self.interface.addPassword(stdscr)
            self.pm.addPassword.assert_called_once_with("example.com", "user", "StrongPass123", "", "")


    @patch('source.interface.curses')
    def test_getPassword(self, mock_curses):
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
    def test_deletePassword(self, mock_curses):
        stdscr = MagicMock()

        with patch.object(self.interface, 'getInput', return_value="example.com"):
            self.interface.deletePassword(stdscr)
            self.pm.deletePassword.assert_called_once_with("example.com")
            stdscr.addstr.assert_called_with(2, 0, "Password deleted successfully!")

    @patch('source.interface.curses')
    def test_updatePassword(self, mock_curses):
        stdscr = MagicMock()

        with patch.object(self.interface, 'getInput', return_value="example.com"), \
             patch.object(self.interface, 'getPasswordInput', return_value="newpass"):
            self.interface.updatePassword(stdscr)
            self.pm.updatePassword.assert_called_once_with("example.com", "example.com", "newpass", "example.com", "example.com")

    @patch('source.interface.curses')
    def test_searchPassword(self, mock_curses):
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

if __name__ == '__main__':
    unittest.main()
