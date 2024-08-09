#pylint: disable=C)
import unittest
from unittest.mock import patch, MagicMock
import cryptography.fernet  # Import cryptography for InvalidToken exception
from main import main

class TestMain(unittest.TestCase):

    @patch('curses.initscr', return_value=MagicMock())
    @patch('curses.curs_set')
    @patch('curses.init_pair')
    @patch('curses.wrapper')
    def test_main_correct_password(self, _mock_wrapper, _mock_init_pair, _mock_curs_set, _mock_initscr):
        stdscr = MagicMock()
        _mock_wrapper.side_effect = lambda func: func(stdscr)

        with patch('main.getHiddenPassword', return_value='correct_password'):
            with patch('source.passwordManager.PasswordManager.loadData', return_value=None):
                with patch('source.interface.CursesInterface.run', return_value=None):
                    main(stdscr)
                    self.assertTrue(_mock_curs_set.called)  # Assert that curses.curs_set was called

    @patch('curses.initscr', return_value=MagicMock())
    @patch('curses.curs_set')
    @patch('curses.init_pair')
    @patch('curses.wrapper')
    def test_main_incorrect_password(self, _mock_wrapper, _mock_init_pair, _mock_curs_set, _mock_initscr):
        stdscr = MagicMock()
        _mock_wrapper.side_effect = lambda func: func(stdscr)

        with patch('main.getHiddenPassword', return_value='wrong_password'):
            with patch('source.passwordManager.PasswordManager.loadData', side_effect=cryptography.fernet.InvalidToken):
                with patch('source.interface.CursesInterface.run', return_value=None):
                    main(stdscr)
                    stdscr.addstr.assert_any_call(0, 0, "Incorrect master password. Please try again.")  # Check if the error message was displayed

if __name__ == '__main__':
    unittest.main()
