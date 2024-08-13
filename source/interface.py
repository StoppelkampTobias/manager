"""
Interface module for the Password Manager application using Curses
"""
import curses
from typing import Any, Optional

class CursesInterface:
    """
    Interface class for the Password Manager application using Curses
    """
    def __init__(self, pm: Any) -> None:
        self.pm = pm
        self.currentRow: int = 0

    def drawMenu(self, stdscr: Any) -> None:
        """
        drawMenu method to draw the main menu
        """
        stdscr.clear()
        menu = ["Add Password", "Get Password", "Delete Password", "Update Password", "Search Password",
                "Check Password Strength", "Check Reused Password", "Check Pwned Password", "Exit"]

        h, w = stdscr.getmaxyx()

        for idx, row in enumerate(menu):
            x = w // 2 - len(row) // 2
            y = h // 2 - len(menu) // 2 + idx
            if idx == self.currentRow:
                stdscr.attron(curses.color_pair(1))
                stdscr.addstr(y, x, row)
                stdscr.attroff(curses.color_pair(1))
            else:
                stdscr.addstr(y, x, row)

        stdscr.refresh()

    def getInput(self, stdscr: Any, prompt: str) -> str:
        """
        getInput method to get user input
        """
        curses.echo()  # Enable echoing of user input
        stdscr.clear()
        stdscr.addstr(0, 0, prompt)
        stdscr.refresh()
        inputStr = stdscr.getstr().decode()
        curses.noecho()  # Disable echoing after input
        return str(inputStr)

    def getPasswordInput(self, stdscr: Any, prompt: str, checkStrength: bool = False) -> Optional[str]:
        """
        getPasswordInput method to get hidden password input
        """
        stdscr.clear()
        stdscr.addstr(0, 0, prompt)
        stdscr.refresh()

        password: list[str] = []
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

        passwordStr = ''.join(password)

        if checkStrength:
            # Check password strength after the entire password is entered
            isStrong, reasons = self.pm.checkPasswordStrength(passwordStr)

            stdscr.move(2, 0)
            stdscr.clrtoeol()
            if isStrong:
                stdscr.addstr(2, 0, "Password strength: Strong")
            else:
                stdscr.addstr(2, 0, "Password strength: Weak")
                stdscr.addstr(3, 0, f"Weaknesses: {', '.join(reasons)}")
                stdscr.addstr(4, 0, "Press Enter to continue...")

            stdscr.refresh()
            stdscr.getch()  # Wait for the user to press a key to continue

        return passwordStr

    def run(self, stdscr: Any) -> None:
        """
        run method to start the interface
        """
        curses.curs_set(0)
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)

        while True:
            self.drawMenu(stdscr)
            key = stdscr.getch()

            if key == curses.KEY_UP and self.currentRow > 0:
                self.currentRow -= 1
            elif key == curses.KEY_DOWN and self.currentRow < 8:
                self.currentRow += 1
            elif key == curses.KEY_ENTER or key in [10, 13]:
                if self.currentRow == 0:  # Add Password
                    self.addPassword(stdscr)
                elif self.currentRow == 1:  # Get Password
                    self.getPassword(stdscr)
                elif self.currentRow == 2:  # Delete Password
                    self.deletePassword(stdscr)
                elif self.currentRow == 3:  # Update Password
                    self.updatePassword(stdscr)
                elif self.currentRow == 4:  # Search Password
                    self.searchPassword(stdscr)
                elif self.currentRow == 5:  # Check Password Strength
                    self.checkPasswordStrength(stdscr)
                elif self.currentRow == 6:  # Check Reused Password
                    self.checkReusedPassword(stdscr)
                elif self.currentRow == 7:  # Check Pwned Password
                    self.checkPwnedPassword(stdscr)
                elif self.currentRow == 8:  # Exit
                    break
            elif key == 27:  # ESC key
                break

    def addPassword(self, stdscr: Any) -> None:
        """
        addPassword method to add a new password
        """
        site: str = self.getInput(stdscr, "Enter site: ")
        username: str = self.getInput(stdscr, "Enter username: ")
        password: Optional[str] = self.getPasswordInput(stdscr, "Enter password: ", checkStrength=True)

        isStrong, _ = self.pm.checkPasswordStrength(password)
        if not isStrong:
            stdscr.clear()  # Clear the screen before displaying the new content
            stdscr.addstr(5, 0, "Password is weak. Would you like to:")
            stdscr.addstr(6, 0, "1. Use the weak password")
            stdscr.addstr(7, 0, "2. Re-enter the password")
            stdscr.addstr(8, 0, "3. Generate a strong password")
            stdscr.refresh()

            choice = stdscr.getch()

            if choice == ord('1'):
                pass  # Continue with the weak password
            elif choice == ord('2'):
                return self.addPassword(stdscr)  # Re-enter the password
            elif choice == ord('3'):
                password = self.pm.generateStrongPassword()
                stdscr.addstr(9, 0, f"Generated strong password: {password}")
                stdscr.refresh()
                stdscr.getch()

        notes: str = self.getInput(stdscr, "Enter notes (optional): ")
        category: str = self.getInput(stdscr, "Enter category (optional): ")
        self.pm.addPassword(site, username, password, notes, category)

        # Get the maximum dimensions of the screen
        h, w = stdscr.getmaxyx()

        # Ensure the coordinates are within bounds

        if 10 < h and 0 < w:
            stdscr.addstr(10, 0, "Password added successfully!")
        else:
            stdscr.addstr(0, 0, "Screen size too small to display message")

        stdscr.refresh()
        stdscr.getch()

    def getPassword(self, stdscr: Any) -> None:
        """
        getPassword method to get an existing password
        """
        site: str = self.getInput(stdscr, "Enter site: ")
        passwordDetails: Optional[dict[str, Any]] = self.pm.getPassword(site)
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

    def deletePassword(self, stdscr: Any) -> None:
        """
        deletePassword method to delete an existing password
        """
        site: str = self.getInput(stdscr, "Enter site: ")
        self.pm.deletePassword(site)
        stdscr.addstr(2, 0, "Password deleted successfully!")
        stdscr.refresh()
        stdscr.getch()

    def updatePassword(self, stdscr: Any) -> None:
        """
        updatePassword method to update an existing password
        """
        site: str = self.getInput(stdscr, "Enter site: ")
        username: Optional[str] = self.getInput(stdscr, "Enter username (press enter to skip): ")
        password: Optional[str] = self.getPasswordInput(stdscr, "Enter password (press enter to skip): ", checkStrength=True)
        notes: Optional[str] = self.getInput(stdscr, "Enter notes (press enter to skip): ")
        category: Optional[str] = self.getInput(stdscr, "Enter category (press enter to skip): ")
        self.pm.updatePassword(site, username or None, password or None, notes or None, category or None)
        stdscr.addstr(6, 0, "Password updated successfully!")
        stdscr.refresh()
        stdscr.getch()


    def searchPassword(self, stdscr: Any) -> None:
        """
        searchPassword method to search for a password
        """
        keyword: str = self.getInput(stdscr, "Enter search keyword: ")
        results: dict[str, dict[str, Any]] = self.pm.searchPassword(keyword)
        stdscr.clear()
        if results:
            row: int = 0
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

    def checkPasswordStrength(self, stdscr: Any) -> None:
        """
        checkPasswordStrength method to check the strength of a password
        """
        password: Optional[str] = self.getPasswordInput(stdscr, "Enter password: ", checkStrength=True)
        stdscr.clear()
        if self.pm.checkPasswordStrength(password)[0]:
            stdscr.addstr(0, 0, "Password is strong!")
        else:
            stdscr.addstr(0, 0, "Password is weak!")
        stdscr.refresh()
        stdscr.getch()

    def checkReusedPassword(self, stdscr: Any) -> None:
        """
        checkReusedPassword method to check for reused passwords
        """
        stdscr.clear()
        reusedPasswords: dict[str, str] = {}
        for site, details in self.pm.data.items():
            if self.pm.checkReusedPassword(details['password']):
                reusedPasswords[site] = details['password']

        if reusedPasswords:
            row: int = 0
            for site, password in reusedPasswords.items():
                stdscr.addstr(row, 0, f"Reused password found at site: {site}")
                stdscr.addstr(row + 1, 0, f"Password: {password}")
                row += 3
        else:
            stdscr.addstr(0, 0, "No reused passwords found!")

        stdscr.refresh()
        stdscr.getch()

    def checkPwnedPassword(self, stdscr: Any) -> None:
        """
        checkPwnedPassword method to check for pwned passwords
        """
        stdscr.clear()
        pwnedPasswords: dict[str, str] = {}
        try:
            for site, details in self.pm.data.items():
                if self.pm.checkPwnedPassword(details['password']):
                    pwnedPasswords[site] = details['password']

            if pwnedPasswords:
                row: int = 0
                for site, password in pwnedPasswords.items():
                    stdscr.addstr(row, 0, f"Pwned password found at site: {site}")
                    stdscr.addstr(row + 1, 0, f"Password: {password}")
                    row += 3
            else:
                stdscr.addstr(0, 0, "No pwned passwords found!")

        except ValueError as e:
            stdscr.addstr(0, 0, f"An error occurred: {str(e)}")

        stdscr.refresh()
        stdscr.getch()
