"""
Main file to run the password manager interface.
"""
import curses
from typing import Any
import cryptography.fernet
from source.passwordManager import PasswordManager
from source.interface import CursesInterface



def getHiddenPassword(stdscr: Any, prompt: str) -> str:
    """
    Get a hidden password input from the user.
    """
    stdscr.clear()
    stdscr.addstr(0, 0, prompt)
    stdscr.refresh()

    password: list[str] = []
    while True:
        key = stdscr.getch()
        if key in (10, 13):  # Enter key
            break
        elif key in (curses.KEY_BACKSPACE, 127):  # Handle backspace
            if password:
                password.pop()
                y, x = stdscr.getyx()
                if x > 0:
                    stdscr.move(y, x - 1)
                    stdscr.delch()
        else:
            password.append(chr(key))
            stdscr.addch('*')
        stdscr.refresh()

    return ''.join(password)

def main(stdscr: Any) -> None:
    """
    Main function to run the password manager interface.
    """
    curses.curs_set(0)
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
    maxAttempts = 3
    attempts = 0

    while attempts < maxAttempts:
        try:
            masterPassword = getHiddenPassword(stdscr, "Enter your master password: ")
            pm = PasswordManager(masterPassword)
            pm.loadData()  # Try to load the data to validate the password
            interface = CursesInterface(pm)
            interface.run(stdscr)
            break  # If the password is correct, proceed to the interface

        except cryptography.fernet.InvalidToken:
            attempts += 1
            stdscr.clear()
            stdscr.addstr(0, 0, "Incorrect master password. Please try again.")
            stdscr.addstr(1, 0, "Press any key to continue...")
            stdscr.refresh()
            stdscr.getch()

    if attempts == maxAttempts:
        stdscr.clear()
        stdscr.addstr(0, 0, "Maximum attempts reached. Exiting...")
        stdscr.refresh()
        stdscr.getch()

if __name__ == "__main__":
    curses.wrapper(main)
