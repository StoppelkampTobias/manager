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

    @patch('source.interface.curses')
    def test_drawMenu(self, mock_curses):
        stdscr = MagicMock()
        mock_curses.color_pair.return_value = 1
        stdscr.getmaxyx.return_value = (24, 80)  # Set the return value for getmaxyx
        self.interface.drawMenu(stdscr)
        self.assertEqual(stdscr.addstr.call_count, 9)

    @patch('source.interface.curses')
    def test_getInput(self, mock_curses):
        stdscr = MagicMock()
        stdscr.getstr.return_value = b'test_input'
        result = self.interface.getInput(stdscr, "Enter something: ")
        self.assertEqual(result, 'test_input')

    @patch('source.interface.curses')
    def test_getPasswordInput(self, mock_curses):
        stdscr = MagicMock()
        stdscr.getch.side_effect = [ord('p'), ord('a'), ord('s'), ord('s'), 10]
        result = self.interface.getPasswordInput(stdscr, "Enter password: ")
        self.assertEqual(result, 'pass')

    @patch('source.interface.curses')
    def test_run(self, mock_curses):
        # Add your test implementation here
        pass

if __name__ == '__main__':
    unittest.main()