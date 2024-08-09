import curses
from source.main import PasswordManager
from source.interface import CursesInterface
import cryptography.fernet

def get_hidden_password(stdscr, prompt):
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
    curses.curs_set(0)
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)

    while True:
        try:
            masterPassword = get_hidden_password(stdscr, "Enter your master password: ")
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

        except Exception as e:
            stdscr.clear()
            stdscr.addstr(0, 0, f"An unexpected error occurred: {str(e)}")
            stdscr.addstr(1, 0, "Press any key to exit...")
            stdscr.refresh()
            stdscr.getch()
            break

if __name__ == "__main__":
    curses.wrapper(main)
