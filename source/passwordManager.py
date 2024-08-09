"""
In this file, we will implement the PasswordManager class that will be used to manage passwords securely.
"""
import json
import random
import hashlib
import base64
import string
from datetime import datetime
import requests
from cryptography.fernet import Fernet
import cryptography.fernet

class PasswordManager:
    """
    A class to manage passwords securely.
    """

    def __init__(self, masterPassword):
        self.masterPassword = masterPassword
        self.key = self.generateKey(masterPassword)
        self.data = {}

    def generateKey(self, password):
        """
        Generate an encryption key based on the master password.
        """
        return base64.urlsafe_b64encode(hashlib.sha256(password.encode()).digest())

    def loadData(self):
        """
        Load and decrypt the password data from the file.
        """
        try:
            with open('passwords.json', 'rb') as file:
                encryptedData = file.read()
            fernet = Fernet(self.key)
            decryptedData = fernet.decrypt(encryptedData).decode()
            self.data = json.loads(decryptedData)
        except FileNotFoundError:
            self.data = {}
        except cryptography.fernet.InvalidToken as exc:
            raise cryptography.fernet.InvalidToken("The master password is incorrect or the data is corrupted.") from exc

    def saveData(self):
        """
        Encrypt and save the password data to the file.
        """
        fernet = Fernet(self.key)
        encryptedData = fernet.encrypt(json.dumps(self.data).encode())
        with open('passwords.json', 'wb') as file:
            file.write(encryptedData)

    def addPassword(self, site, username, password, notes="", category=""):
        """
        Add a new password entry to the data.
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
        Retrieve a password entry by site name.
        """
        return self.data.get(site, None)

    def deletePassword(self, site):
        """
        Delete a password entry by site name.
        """
        if site in self.data:
            del self.data[site]
            self.saveData()

    def updatePassword(self, site, username=None, password=None, notes=None, category=None):
        """
        Update an existing password entry.
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
        Search for password entries by a keyword.
        """
        results = {}
        for site, details in self.data.items():
            if keyword.lower() in site.lower() or keyword.lower() in details['username'].lower():
                results[site] = details
        return results

    def checkPasswordStrength(self, password):
        """
        Check the strength of a given password.
        """
        reasons = []
        if len(password) < 8:
            reasons.append("Password is too short (minimum 8 characters).")
        if not any(char.isdigit() for char in password):
            reasons.append("Password should contain at least one digit.")
        if not any(char.isupper() for char in password):
            reasons.append("Password should contain at least one uppercase letter.")
        if not any(char.islower() for char in password):
            reasons.append("Password should contain at least one lowercase letter.")
        if not any(char in string.punctuation for char in password):
            reasons.append("Password should contain at least one special character.")

        return len(reasons) == 0, reasons

    def generateStrongPassword(self, length=12):
        """
        Generate a strong random password.
        """
        if length < 8:
            length = 8  # Ensure the password is at least 8 characters long
        allChars = string.ascii_letters + string.digits + string.punctuation
        password = random.choice(string.digits) + random.choice(string.ascii_uppercase) + random.choice(string.ascii_lowercase) + ''.join(random.choice(allChars) for _ in range(length-3))
        password = ''.join(random.sample(password, len(password)))  # Shuffle the characters
        return password

    def checkReusedPassword(self, password):
        """
        Check if the given password is reused in any existing entries.
        """
        for details in self.data.values():
            if details['password'] == password:
                return True
        return False

    def checkPwnedPassword(self, password):
        """
        Check if the given password has been compromised using the Pwned Passwords API.
        """
        hashedPassword = hashlib.sha1(password.encode()).hexdigest().upper()
        prefix, suffix = hashedPassword[:5], hashedPassword[5:]
        response = requests.get(f'https://api.pwnedpasswords.com/range/{prefix}', timeout=5)
        if response.status_code == 200:
            hashes = (line.split(':') for line in response.text.splitlines())
            return any(s == suffix for s, _ in hashes)
        return False
