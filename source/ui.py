import curses
from .password_manager import PasswordManager
from .password_generator import PasswordGenerator
import getpass

class UI:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        curses.curs_set(0)
        self.password_manager = None

    def start(self):
        self.stdscr.clear()
        self.stdscr.addstr(0, 0, "Welcome to the Password Manager")
        self.stdscr.addstr(1, 0, "Please enter your master password: ")
        curses.echo()
        master_password = self.stdscr.getstr(2, 0).decode('utf-8')
        curses.noecho()
        self.password_manager = PasswordManager(master_password)
        self.main_menu()

    def main_menu(self):
        while True:
            self.stdscr.clear()
            self.stdscr.addstr(0, 0, "Password Manager - Main Menu")
            self.stdscr.addstr(1, 0, "1. Add Entry")
            self.stdscr.addstr(2, 0, "2. View Entry")
            self.stdscr.addstr(3, 0, "3. Delete Entry")
            self.stdscr.addstr(4, 0, "4. Generate Password")
            self.stdscr.addstr(5, 0, "5. Exit")
            choice = self.stdscr.getch()

            if choice == ord('1'):
                self.add_entry()
            elif choice == ord('2'):
                self.view_entry()
            elif choice == ord('3'):
                self.delete_entry()
            elif choice == ord('4'):
                self.generate_password()
            elif choice == ord('5'):
                break

    def add_entry(self):
        self.stdscr.clear()
        self.stdscr.addstr(0, 0, "Add Entry")
        self.stdscr.addstr(1, 0, "Website: ")
        website = self.stdscr.getstr(2, 0).decode('utf-8')
        self.stdscr.addstr(3, 0, "Username: ")
        username = self.stdscr.getstr(4, 0).decode('utf-8')
        self.stdscr.addstr(5, 0, "Password: ")
        password = getpass.getpass()
        self.stdscr.addstr(6, 0, "Notes: ")
        notes = self.stdscr.getstr(7, 0).decode('utf-8')
        self.stdscr.addstr(8, 0, "Category: ")
        category = self.stdscr.getstr(9, 0).decode('utf-8')
        self.password_manager.add_entry(website, username, password, notes, category)
        self.stdscr.addstr(10, 0, "Entry added successfully! Press any key to return to the main menu.")
        self.stdscr.getch()

    def view_entry(self):
        self.stdscr.clear()
        self.stdscr.addstr(0, 0, "View Entry")
        self.stdscr.addstr(1, 0, "Website: ")
        website = self.stdscr.getstr(2, 0).decode('utf-8')
        entry = self.password_manager.get_entry(website)
        if entry:
            self.stdscr.addstr(3, 0, f"Username: {entry['username']}")
            self.stdscr.addstr(4, 0, f"Password: {entry['password']}")
            self.stdscr.addstr(5, 0, f"Notes: {entry['notes']}")
            self.stdscr.addstr(6, 0, f"Category: {entry['category']}")
            self.stdscr.addstr(7, 0, f"Created At: {entry['created_at']}")
        else:
            self.stdscr.addstr(3, 0, "Entry not found!")
        self.stdscr.addstr(8, 0, "Press any key to return to the main menu.")
        self.stdscr.getch()

    def delete_entry(self):
        self.stdscr.clear()
        self.stdscr.addstr(0, 0, "Delete Entry")
        self.stdscr.addstr(1, 0, "Website: ")
        website = self.stdscr.getstr(2, 0).decode('utf-8')
        self.password_manager.delete_entry(website)
        self.stdscr.addstr(3, 0, "Entry deleted successfully! Press any key to return to the main menu.")
        self.stdscr.getch()

    def generate_password(self):
        self.stdscr.clear()
        self.stdscr.addstr(0, 0, "Generate Password")
        self.stdscr.addstr(1, 0, "Length: ")
        length = int(self.stdscr.getstr(2, 0).decode('utf-8'))
        password = PasswordGenerator.generate(length)
        self.stdscr.addstr(3, 0, f"Generated Password: {password}")
        self.stdscr.addstr(4, 0, "Press any key to return to the main menu.")
        self.stdscr.getch()
