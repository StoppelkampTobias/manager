#pylint: disable=C)
import unittest
from unittest.mock import patch, MagicMock
import cryptography.fernet  # Import cryptography for InvalidToken exception
import curses
from main import main


class TestMain(unittest.TestCase):

    @patch('main.getHiddenPassword', return_value='correct_password')
    @patch('source.passwordManager.PasswordManager.loadData', return_value=None)
    @patch('source.interface.CursesInterface.run', return_value=None)
    def test_main_correct_password(self, mock_run, mock_load_data, mock_get_hidden_password):
        # Use curses.wrapper to properly initialize curses environment
        def run_curses_app(stdscr):
            main(stdscr)

        curses.wrapper(run_curses_app)
        mock_load_data.assert_called_once()  # Ensure data was attempted to be loaded
        mock_run.assert_called_once()  # Ensure interface run was called



if __name__ == '__main__':
    unittest.main()
