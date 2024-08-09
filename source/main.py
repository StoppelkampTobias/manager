"""
This module implements a Password Manager class with functionalities
such as adding, retrieving, updating, and deleting passwords, as well
as checking password strength and verifying if a password has been
compromised in a data breach.
"""

import json
import getpass
import hashlib
import base64
import string
import requests
from cryptography.fernet import Fernet
from datetime import datetime


class PasswordManager:
    """
    A class to manage passwords securely.

    Attributes:
        masterPassword (str): The master password for encrypting/decrypting data.
        key (bytes): The key generated from the master password.
        data (dict): A dictionary storing all the password data.
    """

    def __init__(self, masterPassword):
        """
        Initializes the PasswordManager with a master password.

        Args:
            masterPassword (str): The master password used for encryption.
        """
        self.masterPassword = masterPassword
        self.key = self.generateKey(masterPassword)
        self.data = {}
        self.loadData()

    def generateKey(self, password):
        """
        Generates a key based on the master password using SHA-256 hashing.

        Args:
            password (str): The master password.

        Returns:
            bytes: A base64 encoded key.
        """
        return base64.urlsafe_b64encode(hashlib.sha256(password.encode()).digest())

    def loadData(self):
        """
        Loads and decrypts password data from the passwords.json file.
        """
        try:
            with open('passwords.json', 'rb') as file:
                encryptedData = file.read()
            fernet = Fernet(self.key)
            decryptedData = fernet.decrypt(encryptedData).decode()
            self.data = json.loads(decryptedData)
        except FileNotFoundError:
            self.data = {}

    def saveData(self):
        """
        Encrypts and saves the password data to the passwords.json file.
        """
        fernet = Fernet(self.key)
        encryptedData = fernet.encrypt(json.dumps(self.data).encode())
        with open('passwords.json', 'wb') as file:
            file.write(encryptedData)

    def addPassword(self, site, username, password, notes="", category=""):
        """
        Adds a new password entry for a site.

        Args:
            site (str): The website or service name.
            username (str): The username associated with the site.
            password (str): The password associated with the site.
            notes (str, optional): Any additional notes. Defaults to "".
            category (str, optional): Category for the site. Defaults to "".
        """
        self.data[site] = {
            'username': username,
            'password': password,
            'createdAt': datetime.now().isoformat(),
            'notes': notes,
            'category': category
        }
        self.saveData()

    def getPassword(self, site):
        """
        Retrieves the password details for a given site.

        Args:
            site (str): The site name.

        Returns:
            dict: The password details if the site exists, None otherwise.
        """
        return self.data.get(site, None)

    def deletePassword(self, site):
        """
        Deletes a password entry for a given site.

        Args:
            site (str): The site name.
        """
        if site in self.data:
            del self.data[site]
            self.saveData()

    def updatePassword(self, site, username=None, password=None, notes=None, category=None):
        """
        Updates the password details for a given site.

        Args:
            site (str): The site name.
            username (str, optional): The username to update. Defaults to None.
            password (str, optional): The password to update. Defaults to None.
            notes (str, optional): The notes to update. Defaults to None.
            category (str, optional): The category to update. Defaults to None.
        """
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
        """
        Searches for passwords by a keyword in site name or username.

        Args:
            keyword (str): The search keyword.

        Returns:
            dict: A dictionary of matching site details.
        """
        results = {}
        for site, details in self.data.items():
            if keyword.lower() in site.lower() or keyword.lower() in details['username'].lower():
                results[site] = details
        return results

    def checkPasswordStrength(self, password):
        """
        Checks if a password meets basic strength criteria.

        Args:
            password (str): The password to check.

        Returns:
            bool: True if the password is strong, False otherwise.
        """
        lengthCriteria = len(password) >= 8
        digitCriteria = any(char.isdigit() for char in password)
        upperCriteria = any(char.isupper() for char in password)
        lowerCriteria = any(char.islower() for char in password)
        specialCriteria = any(char in string.punctuation for char in password)
        return all([lengthCriteria, digitCriteria, upperCriteria, lowerCriteria, specialCriteria])

    def checkReusedPassword(self, password):
        """
        Checks if the given password is reused for any site.

        Args:
            password (str): The password to check.

        Returns:
            bool: True if the password is reused, False otherwise.
        """
        for details in self.data.values():
            if details['password'] == password:
                return True
        return False

    def checkPwnedPassword(self, password):
        """
        Checks if a password has been compromised in a known data breach.

        Args:
            password (str): The password to check.

        Returns:
            bool: True if the password has been pwned, False otherwise.
        """
        hashedPassword = hashlib.sha1(password.encode()).hexdigest().upper()
        prefix, suffix = hashedPassword[:5], hashedPassword[5:]
        response = requests.get(f'https://api.pwnedpasswords.com/range/{prefix}', timeout=5)
        if response.status_code == 200:
            hashes = (line.split(':') for line in response.text.splitlines())
            return any(s == suffix for s, _ in hashes)
        return False

def main():
    """
    The main function providing a command-line interface for the Password Manager.
    """
    masterPassword = getpass.getpass('Enter your master password: ')
    pm = PasswordManager(masterPassword)

    while True:
        print("\nPassword Manager")
        print("1. Add Password")
        print("2. Get Password")
        print("3. Delete Password")
        print("4. Update Password")
        print("5. Search Password")
        print("6. Check Password Strength")
        print("7. Check Reused Password")
        print("8. Check Pwned Password")
        print("9. Exit")
        choice = input("Enter your choice: ")

        if choice == '1':
            site = input("Enter site: ")
            username = input("Enter username: ")
            password = getpass.getpass("Enter password: ")
            notes = input("Enter notes (optional): ")
            category = input("Enter category (optional): ")
            pm.addPassword(site, username, password, notes, category)
            print("Password added successfully!")

        elif choice == '2':
            site = input("Enter site: ")
            passwordDetails = pm.getPassword(site)
            if passwordDetails:
                print(f"Username: {passwordDetails['username']}")
                print(f"Password: {passwordDetails['password']}")
                print(f"Notes: {passwordDetails['notes']}")
                print(f"Category: {passwordDetails['category']}")
                print(f"Created at: {passwordDetails['createdAt']}")
            else:
                print("Password not found!")

        elif choice == '3':
            site = input("Enter site: ")
            pm.deletePassword(site)
            print("Password deleted successfully!")

        elif choice == '4':
            site = input("Enter site: ")
            username = input("Enter username (press enter to skip): ")
            password = getpass.getpass("Enter password (press enter to skip): ")
            notes = input("Enter notes (press enter to skip): ")
            category = input("Enter category (press enter to skip): ")
            pm.updatePassword(site, username or None, password or None, notes or None, category or None)
            print("Password updated successfully!")

        elif choice == '5':
            keyword = input("Enter search keyword: ")
            results = pm.searchPassword(keyword)
            if results:
                for siteName, details in results.items():
                    print(f"\nSite: {siteName}")
                    print(f"Username: {details['username']}")
                    print(f"Password: {details['password']}")
                    print(f"Notes: {details['notes']}")
                    print(f"Category: {details['category']}")
                    print(f"Created at: {details['createdAt']}")
            else:
                print("No passwords found!")

        elif choice == '6':
            password = getpass.getpass("Enter password: ")
            if pm.checkPasswordStrength(password):
                print("Password is strong!")
            else:
                print("Password is weak!")

        elif choice == '7':
            password = getpass.getpass("Enter password: ")
            if pm.checkReusedPassword(password):
                print("Password is reused!")
            else:
                print("Password is unique!")

        elif choice == '8':
            password = getpass.getpass("Enter password: ")
            if pm.checkPwnedPassword(password):
                print("Password has been pwned!")
            else:
                print("Password is safe!")

        elif choice == '9':
            break

        else:
            print("Invalid choice! Please try again.")

if __name__ == "__main__":
    main()
