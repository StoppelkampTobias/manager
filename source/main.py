import json
import getpass
import hashlib
import base64
import string
from datetime import datetime
import curses
import requests
from cryptography.fernet import Fernet

class PasswordManager:
    """
    A class to manage passwords securely.
    """

    def __init__(self, masterPassword):
        self.masterPassword = masterPassword
        self.key = self.generateKey(masterPassword)
        self.data = {}
        self.loadData()

    def generateKey(self, password):
        return base64.urlsafe_b64encode(hashlib.sha256(password.encode()).digest())

    def loadData(self):
        try:
            with open('passwords.json', 'rb') as file:
                encryptedData = file.read()
            fernet = Fernet(self.key)
            decryptedData = fernet.decrypt(encryptedData).decode()
            self.data = json.loads(decryptedData)
        except FileNotFoundError:
            self.data = {}

    def saveData(self):
        fernet = Fernet(self.key)
        encryptedData = fernet.encrypt(json.dumps(self.data).encode())
        with open('passwords.json', 'wb') as file:
            file.write(encryptedData)

    def addPassword(self, site, username, password, notes="", category=""):
        self.data[site] = {
            'username': username,
            'password': password,
            'createdAt': datetime.now().isoformat(),
            'notes': notes,
            'category': category
        }
        self.saveData()

    def getPassword(self, site):
        return self.data.get(site, None)

    def deletePassword(self, site):
        if site in self.data:
            del self.data[site]
            self.saveData()

    def updatePassword(self, site, username=None, password=None, notes=None, category=None):
        if site in self.data:
            if username:
                self.data[site]['username'] = username
            if password:
                self.data[site]['password'] = password
            if notes:
                self.data[site]['notes'] = notes
            if category:
                self.data[site]['category'] = category
            self.saveData()

    def searchPassword(self, keyword):
        results = {}
        for site, details in self.data.items():
            if keyword.lower() in site.lower() or keyword.lower() in details['username'].lower():
                results[site] = details
        return results

    def checkPasswordStrength(self, password):
        lengthCriteria = len(password) >= 8
        digitCriteria = any(char.isdigit() for char in password)
        upperCriteria = any(char.isupper() for char in password)
        lowerCriteria = any(char.islower() for char in password)
        specialCriteria = any(char in string.punctuation for char in password)
        return all([lengthCriteria, digitCriteria, upperCriteria, lowerCriteria, specialCriteria])

    def checkReusedPassword(self, password):
        for details in self.data.values():
            if details['password'] == password:
                return True
        return False

    def checkPwnedPassword(self, password):
        hashedPassword = hashlib.sha1(password.encode()).hexdigest().upper()
        prefix, suffix = hashedPassword[:5], hashedPassword[5:]
        response = requests.get(f'https://api.pwnedpasswords.com/range/{prefix}', timeout=5)
        if response.status_code == 200:
            hashes = (line.split(':') for line in response.text.splitlines())
            return any(s == suffix for s, _ in hashes)
        return False


def draw_menu(stdscr, selected_row_idx):
    stdscr.clear()
    menu = ["Add Password", "Get Password", "Delete Password", "Update Password", "Search Password",
            "Check Password Strength", "Check Reused Password", "Check Pwned Password", "Exit"]

    h, w = stdscr.getmaxyx()

    for idx, row in enumerate(menu):
        x = w // 2 - len(row) // 2
        y = h // 2 - len(menu) // 2 + idx
        if idx == selected_row_idx:
            stdscr.attron(curses.color_pair(1))
            stdscr.addstr(y, x, row)
            stdscr.attroff(curses.color_pair(1))
        else:
            stdscr.addstr(y, x, row)

    stdscr.refresh()


def get_input(stdscr, prompt):
    """
    Helper function to get user input using curses.
    """
    curses.echo()  # Enable echoing of user input
    stdscr.clear()
    stdscr.addstr(0, 0, prompt)
    stdscr.refresh()
    input_str = stdscr.getstr().decode()
    curses.noecho()  # Disable echoing after input
    return input_str


def get_password_input(stdscr, prompt):
    """
    Helper function to get password input using curses.
    """
    curses.noecho()  # Disable echoing for password input
    stdscr.clear()
    stdscr.addstr(0, 0, prompt)
    stdscr.refresh()
    password_str = stdscr.getstr().decode()
    curses.echo()  # Re-enable echoing after password input
    return password_str



def add_password(stdscr, pm):
    site = get_input(stdscr, "Enter site: ")
    username = get_input(stdscr, "Enter username: ")
    password = get_input(stdscr, "Enter password: ")
    notes = get_input(stdscr, "Enter notes (optional): ")
    category = get_input(stdscr, "Enter category (optional): ")
    pm.addPassword(site, username, password, notes, category)
    stdscr.addstr(6, 0, "Password added successfully!")
    stdscr.refresh()
    stdscr.getch()


def get_password(stdscr, pm):
    site = get_input(stdscr, "Enter site: ")
    passwordDetails = pm.getPassword(site)
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


def delete_password(stdscr, pm):
    site = get_input(stdscr, "Enter site: ")
    pm.deletePassword(site)
    stdscr.addstr(2, 0, "Password deleted successfully!")
    stdscr.refresh()
    stdscr.getch()


def update_password(stdscr, pm):
    site = get_input(stdscr, "Enter site: ")
    username = get_input(stdscr, "Enter username (press enter to skip): ")
    password = get_input(stdscr, "Enter password (press enter to skip): ")
    notes = get_input(stdscr, "Enter notes (press enter to skip): ")
    category = get_input(stdscr, "Enter category (press enter to skip): ")
    pm.updatePassword(site, username or None, password or None, notes or None, category or None)
    stdscr.addstr(6, 0, "Password updated successfully!")
    stdscr.refresh()
    stdscr.getch()


def search_password(stdscr, pm):
    keyword = get_input(stdscr, "Enter search keyword: ")
    results = pm.searchPassword(keyword)
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


def check_password_strength(stdscr, pm):
    password = get_input(stdscr, "Enter password: ")
    stdscr.clear()
    if pm.checkPasswordStrength(password):
        stdscr.addstr(0, 0, "Password is strong!")
    else:
        stdscr.addstr(0, 0, "Password is weak!")
    stdscr.refresh()
    stdscr.getch()


def check_reused_password(stdscr, pm):
    password = get_input(stdscr, "Enter password: ")
    stdscr.clear()
    if pm.checkReusedPassword(password):
        stdscr.addstr(0, 0, "Password is reused!")
    else:
        stdscr.addstr(0, 0, "Password is unique!")
    stdscr.refresh()
    stdscr.getch()


def check_pwned_password(stdscr, pm):
    password = get_input(stdscr, "Enter password: ")
    stdscr.clear()
    if pm.checkPwnedPassword(password):
        stdscr.addstr(0, 0, "Password has been pwned!")
    else:
        stdscr.addstr(0, 0, "Password is safe!")
    stdscr.refresh()
    stdscr.getch()


def get_password_input_with_enter(stdscr, prompt):
    """
    Function to get password input and confirm it with Enter.
    """
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
        elif key == curses.KEY_BACKSPACE or key == 127:  # Handle backspace
            if password:
                password.pop()
                stdscr.delch(stdscr.getyx()[0], stdscr.getyx()[1] - 1)
        else:
            password.append(chr(key))
            stdscr.addch('*')  # Show '*' for each character typed
            
    return ''.join(password)

def get_master_password(stdscr):
    """
    Function to get and confirm the master password using curses with Enter confirmation.
    """
    while True:
        password = get_password_input_with_enter(stdscr, "Enter your master password: ")
        if password:
            confirm_password = get_password_input_with_enter(stdscr, "Confirm your master password: ")
            if password == confirm_password:
                return password
            else:
                stdscr.clear()
                stdscr.addstr(0, 0, "Passwords do not match. Please try again.")
                stdscr.refresh()
                stdscr.getch()

def main(stdscr):
    curses.curs_set(0)
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)

    masterPassword = get_master_password(stdscr)
    pm = PasswordManager(masterPassword)

    current_row = 0

    while True:
        draw_menu(stdscr, current_row)
        key = stdscr.getch()

        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < 8:
            current_row += 1
        elif key == curses.KEY_ENTER or key in [10, 13]:
            if current_row == 0:  # Add Password
                add_password(stdscr, pm)
            elif current_row == 1:  # Get Password
                get_password(stdscr, pm)
            elif current_row == 2:  # Delete Password
                delete_password(stdscr, pm)
            elif current_row == 3:  # Update Password
                update_password(stdscr, pm)
            elif current_row == 4:  # Search Password
                search_password(stdscr, pm)
            elif current_row == 5:  # Check Password Strength
                check_password_strength(stdscr, pm)
            elif current_row == 6:  # Check Reused Password
                check_reused_password(stdscr, pm)
            elif current_row == 7:  # Check Pwned Password
                check_pwned_password(stdscr, pm)
            elif current_row == 8:  # Exit
                break
        elif key == 27:  # ESC key
            break

if __name__ == "__main__":
    curses.wrapper(main)