"""
Main file to run the password manager interface.
"""
import curses
import cryptography.fernet
from source.passwordManager import PasswordManager
from source.interface import CursesInterface


def getHiddenPassword(stdscr, prompt):
    """
    Get a hidden password input from the user.
    """
    stdscr.clear()
    stdscr.addstr(0, 0, prompt)
    stdscr.refresh()

    password = []
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

def main(stdscr):
    """
    Main function to run the password manager interface.
    """
    curses.curs_set(0)
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)

    while True:
        try:
            masterPassword = getHiddenPassword(stdscr, "Enter your master password: ")
            pm = PasswordManager(masterPassword)
            pm.loadData()  # Try to load the data to validate the password
            interface = CursesInterface(pm)
            interface.run(stdscr)
            break  # If the password is correct, proceed to the interface

        except cryptography.fernet.InvalidToken:
            stdscr.clear()
            stdscr.addstr(0, 0, "Incorrect master password. Please try again.")
            stdscr.addstr(1, 0, "Press any key to continue...")
            stdscr.refresh()
            stdscr.getch()


if __name__ == "__main__":
    curses.wrapper(main)
