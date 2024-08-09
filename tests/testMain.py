#pylint: disable=C)
#pylint: disable=W)
import unittest
from unittest.mock import patch, MagicMock
import curses
import cryptography.fernet
from main import getHiddenPassword, main

class TestPasswordManagerInterface(unittest.TestCase):

    @patch('main.curses')
    def testGetHiddenPassword(self, mockCurses):
        stdscr = MagicMock()
        stdscr.getch.side_effect = [ord('p'), ord('a'), ord('s'), ord('s'), 10]  # Simulate user input 'pass' + Enter
        mockCurses.KEY_BACKSPACE = 127

        result = getHiddenPassword(stdscr, "Enter your password: ")
        self.assertEqual(result, 'pass')
        stdscr.addstr.assert_called_with(0, 0, "Enter your password: ")  # Updated expected string
        self.assertEqual(stdscr.addch.call_count, 4)  # Four characters entered

    @patch('main.PasswordManager')
    @patch('main.CursesInterface')
    @patch('main.getHiddenPassword')
    @patch('main.curses')
    def testMainCorrectPassword(self, mockCurses, mockGetHiddenPassword, mockCursesInterface, mockPasswordManager):
        stdscr = MagicMock()
        mockGetHiddenPassword.return_value = 'correct_password'
        mockPm = MagicMock()
        mockPasswordManager.return_value = mockPm
        mockInterface = MagicMock()
        mockCursesInterface.return_value = mockInterface

        with patch('main.curses.wrapper', lambda f: f(stdscr)):
            main(stdscr)

        mockGetHiddenPassword.assert_called_once_with(stdscr, "Enter your master password: ")
        mockPasswordManager.assert_called_once_with('correct_password')
        mockPm.loadData.assert_called_once()
        mockCursesInterface.assert_called_once_with(mockPm)
        mockInterface.run.assert_called_once_with(stdscr)

    @patch('main.PasswordManager')
    @patch('main.getHiddenPassword')
    @patch('main.curses')
    def testMainIncorrectPassword(self, mockCurses, mockGetHiddenPassword, mockPasswordManager):
        stdscr = MagicMock()
        mockGetHiddenPassword.return_value = 'incorrect_password'
        mockPm = MagicMock()
        mockPasswordManager.return_value = mockPm
        mockPm.loadData.side_effect = cryptography.fernet.InvalidToken

        with patch('main.curses.wrapper', lambda f: f(stdscr)):
            main(stdscr)

        self.assertEqual(mockGetHiddenPassword.call_count, 3)  # Three attempts should be made
        self.assertEqual(mockPasswordManager.call_count, 3)
        self.assertEqual(mockPm.loadData.call_count, 3)
        stdscr.addstr.assert_any_call(0, 0, "Incorrect master password. Please try again.")
        stdscr.addstr.assert_any_call(1, 0, "Press any key to continue...")
        stdscr.addstr.assert_any_call(0, 0, "Maximum attempts reached. Exiting...")
        self.assertEqual(stdscr.getch.call_count, 3)  # One key press per attempt

if __name__ == '__main__':
    unittest.main()