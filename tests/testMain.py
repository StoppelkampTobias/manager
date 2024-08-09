import unittest
from unittest.mock import patch, MagicMock
import curses
import cryptography.fernet
from main import getHiddenPassword, main

class TestPasswordManagerInterface(unittest.TestCase):

    @patch('main.curses')
    def test_getHiddenPassword(self, mock_curses):
        stdscr = MagicMock()
        stdscr.getch.side_effect = [ord('p'), ord('a'), ord('s'), ord('s'), 10]  # Simulate user input 'pass' + Enter
        mock_curses.KEY_BACKSPACE = 127

        result = getHiddenPassword(stdscr, "Enter your password: ")
        self.assertEqual(result, 'pass')
        stdscr.addstr.assert_called_with(0, 0, "Enter your password: ")  # Updated expected string
        self.assertEqual(stdscr.addch.call_count, 4)  # Four characters entered

    @patch('main.PasswordManager')
    @patch('main.CursesInterface')
    @patch('main.getHiddenPassword')
    @patch('main.curses')
    def test_main_correct_password(self, mock_curses, mock_getHiddenPassword, mock_CursesInterface, mock_PasswordManager):
        stdscr = MagicMock()
        mock_getHiddenPassword.return_value = 'correct_password'
        mock_pm = MagicMock()
        mock_PasswordManager.return_value = mock_pm
        mock_interface = MagicMock()
        mock_CursesInterface.return_value = mock_interface

        with patch('main.curses.wrapper', lambda f: f(stdscr)):
            main(stdscr)

        mock_getHiddenPassword.assert_called_once_with(stdscr, "Enter your master password: ")
        mock_PasswordManager.assert_called_once_with('correct_password')
        mock_pm.loadData.assert_called_once()
        mock_CursesInterface.assert_called_once_with(mock_pm)
        mock_interface.run.assert_called_once_with(stdscr)

    @patch('main.PasswordManager')
    @patch('main.getHiddenPassword')
    @patch('main.curses')
    def test_main_incorrect_password(self, mock_curses, mock_getHiddenPassword, mock_PasswordManager):
        stdscr = MagicMock()
        mock_getHiddenPassword.return_value = 'incorrect_password'
        mock_pm = MagicMock()
        mock_PasswordManager.return_value = mock_pm
        mock_pm.loadData.side_effect = cryptography.fernet.InvalidToken

        with patch('main.curses.wrapper', lambda f: f(stdscr)):
            main(stdscr)

        self.assertEqual(mock_getHiddenPassword.call_count, 3)
        self.assertEqual(mock_PasswordManager.call_count, 3)
        self.assertEqual(mock_pm.loadData.call_count, 3)
        stdscr.addstr.assert_any_call(0, 0, "Incorrect master password. Please try again.")
        stdscr.addstr.assert_any_call(1, 0, "Press any key to continue...")
        self.assertEqual(stdscr.getch.call_count, 4)  # Updated expected call count
        stdscr.addstr.assert_any_call(0, 0, "Maximum attempts reached. Exiting...")

if __name__ == '__main__':
    unittest.main()