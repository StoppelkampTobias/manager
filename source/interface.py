import curses
import string
from source.main import PasswordManager  

class CursesInterface:
    def __init__(self, pm):
        self.pm = pm
        self.current_row = 0

    def draw_menu(self, stdscr):
        stdscr.clear()
        menu = ["Add Password", "Get Password", "Delete Password", "Update Password", "Search Password",
                "Check Password Strength", "Check Reused Password", "Check Pwned Password", "Exit"]

        h, w = stdscr.getmaxyx()

        for idx, row in enumerate(menu):
            x = w // 2 - len(row) // 2
            y = h // 2 - len(menu) // 2 + idx
            if idx == self.current_row:
                stdscr.attron(curses.color_pair(1))
                stdscr.addstr(y, x, row)
                stdscr.attroff(curses.color_pair(1))
            else:
                stdscr.addstr(y, x, row)

        stdscr.refresh()

    def get_input(self, stdscr, prompt):
        curses.echo()  # Enable echoing of user input
        stdscr.clear()
        stdscr.addstr(0, 0, prompt)
        stdscr.refresh()
        input_str = stdscr.getstr().decode()
        curses.noecho()  # Disable echoing after input
        return input_str

    def get_password_input(self, stdscr, prompt, check_strength=False):
        stdscr.clear()
        stdscr.addstr(0, 0, prompt)
        stdscr.refresh()

        password = []
        while True:
            key = stdscr.getch()
            if key in (10, 13):  # Enter key
                break
            elif key == 27:  # ESC key to cancel
                return None
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

        password_str = ''.join(password)

        if check_strength:
            # Check password strength after the entire password is entered
            is_strong, reasons = self.pm.checkPasswordStrength(password_str)

            stdscr.move(2, 0)
            stdscr.clrtoeol()
            if is_strong:
                stdscr.addstr(2, 0, "Password strength: Strong")
            else:
                stdscr.addstr(2, 0, "Password strength: Weak")
                stdscr.addstr(3, 0, f"Weaknesses: {', '.join(reasons)}")
                stdscr.addstr(4, 0, "Press Enter to continue...")

            stdscr.refresh()
            stdscr.getch()  # Wait for the user to press a key to continue

        return password_str



    def run(self, stdscr):
        curses.curs_set(0)
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)

        while True:
            self.draw_menu(stdscr)
            key = stdscr.getch()

            if key == curses.KEY_UP and self.current_row > 0:
                self.current_row -= 1
            elif key == curses.KEY_DOWN and self.current_row < 8:
                self.current_row += 1
            elif key == curses.KEY_ENTER or key in [10, 13]:
                if self.current_row == 0:  # Add Password
                    self.add_password(stdscr)
                elif self.current_row == 1:  # Get Password
                    self.get_password(stdscr)
                elif self.current_row == 2:  # Delete Password
                    self.delete_password(stdscr)
                elif self.current_row == 3:  # Update Password
                    self.update_password(stdscr)
                elif self.current_row == 4:  # Search Password
                    self.search_password(stdscr)
                elif self.current_row == 5:  # Check Password Strength
                    self.check_password_strength(stdscr)
                elif self.current_row == 6:  # Check Reused Password
                    self.check_reused_password(stdscr)
                elif self.current_row == 7:  # Check Pwned Password
                    self.check_pwned_password(stdscr)
                elif self.current_row == 8:  # Exit
                    break
            elif key == 27:  # ESC key
                break

    def add_password(self, stdscr):
        site = self.get_input(stdscr, "Enter site: ")
        username = self.get_input(stdscr, "Enter username: ")
        password = self.get_password_input(stdscr, "Enter password: ", check_strength=True)

        is_strong, reasons = self.pm.checkPasswordStrength(password)
        if not is_strong:
            stdscr.addstr(5, 0, "Password is weak. Would you like to:")
            stdscr.addstr(6, 0, "1. Use the weak password")
            stdscr.addstr(7, 0, "2. Re-enter the password")
            stdscr.addstr(8, 0, "3. Generate a strong password")
            stdscr.refresh()

            choice = stdscr.getch()

            if choice == ord('1'):
                pass  # Continue with the weak password
            elif choice == ord('2'):
                return self.add_password(stdscr)  # Re-enter the password
            elif choice == ord('3'):
                password = self.pm.generateStrongPassword()
                stdscr.addstr(9, 0, f"Generated strong password: {password}")
                stdscr.refresh()
                stdscr.getch()

        notes = self.get_input(stdscr, "Enter notes (optional): ")
        category = self.get_input(stdscr, "Enter category (optional): ")
        self.pm.addPassword(site, username, password, notes, category)
        stdscr.addstr(10, 0, "Password added successfully!")
        stdscr.refresh()
        stdscr.getch()

    def get_password(self, stdscr):
        site = self.get_input(stdscr, "Enter site: ")
        passwordDetails = self.pm.getPassword(site)
        stdscr.clear()
        if passwordDetails:
            stdscr.addstr(0, 0, f"Username: {passwordDetails['username']}")
            stdscr.addstr(1, 0, f"Password: {passwordDetails['password']}")
            stdscr.addstr(2, 0, f"Notes: {passwordDetails['notes']}")
            stdscr.addstr(3, 0, f"Category: {passwordDetails['category']}")
            stdscr.addstr(4, 0, f"Created At: {passwordDetails['createdAt']}")
        else:
            stdscr.addstr(0, 0, "Password not found!")
        stdscr.refresh()
        stdscr.getch()

    def delete_password(self, stdscr):
        site = self.get_input(stdscr, "Enter site: ")
        self.pm.deletePassword(site)
        stdscr.addstr(2, 0, "Password deleted successfully!")
        stdscr.refresh()
        stdscr.getch()

    def update_password(self, stdscr):
        site = self.get_input(stdscr, "Enter site: ")
        username = self.get_input(stdscr, "Enter username (press enter to skip): ")
        password = self.get_password_input(stdscr, "Enter password (press enter to skip): ", check_strength=True)
        notes = self.get_input(stdscr, "Enter notes (press enter to skip): ")
        category = self.get_input(stdscr, "Enter category (press enter to skip): ")
        self.pm.updatePassword(site, username or None, password or None, notes or None, category or None)
        stdscr.addstr(6, 0, "Password updated successfully!")
        stdscr.refresh()
        stdscr.getch()

    def search_password(self, stdscr):
        keyword = self.get_input(stdscr, "Enter search keyword: ")
        results = self.pm.searchPassword(keyword)
        stdscr.clear()
        if results:
            row = 0
            for siteName, details in results.items():
                stdscr.addstr(row, 0, f"Site: {siteName}")
                stdscr.addstr(row + 1, 0, f"Username: {details['username']}")
                stdscr.addstr(row + 2, 0, f"Password: {details['password']}")
                stdscr.addstr(row + 3, 0, f"Notes: {details['notes']}")
                stdscr.addstr(row + 4, 0, f"Category: {details['category']}")
                stdscr.addstr(row + 5, 0, f"Created At: {details['createdAt']}")
                row += 7
        else:
            stdscr.addstr(0, 0, "No passwords found!")
        stdscr.refresh()
        stdscr.getch()

    def check_password_strength(self, stdscr):
        password = self.get_password_input(stdscr, "Enter password: ", check_strength=True)
        stdscr.clear()
        if self.pm.checkPasswordStrength(password)[0]:
            stdscr.addstr(0, 0, "Password is strong!")
        else:
            stdscr.addstr(0, 0, "Password is weak!")
        stdscr.refresh()
        stdscr.getch()

    def check_reused_password(self, stdscr):
        stdscr.clear()
        reused_passwords = {}
        for site, details in self.pm.data.items():
            if self.pm.checkReusedPassword(details['password']):
                reused_passwords[site] = details['password']
        
        if reused_passwords:
            row = 0
            for site, password in reused_passwords.items():
                stdscr.addstr(row, 0, f"Reused password found at site: {site}")
                stdscr.addstr(row + 1, 0, f"Password: {password}")
                row += 3
        else:
            stdscr.addstr(0, 0, "No reused passwords found!")
        
        stdscr.refresh()
        stdscr.getch()

    def check_pwned_password(self, stdscr):
        stdscr.clear()
        pwned_passwords = {}
        for site, details in self.pm.data.items():
            if self.pm.checkPwnedPassword(details['password']):
                pwned_passwords[site] = details['password']
        
        if pwned_passwords:
            row = 0
            for site, password in pwned_passwords.items():
                stdscr.addstr(row, 0, f"Pwned password found at site: {site}")
                stdscr.addstr(row + 1, 0, f"Password: {password}")
                row += 3
        else:
            stdscr.addstr(0, 0, "No pwned passwords found!")
        
        stdscr.refresh()
        stdscr.getch()
