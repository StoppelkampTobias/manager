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
        except cryptography.fernet.InvalidToken:
            raise cryptography.fernet.InvalidToken("The master password is incorrect or the data is corrupted.")
        except Exception as e:
            raise Exception(f"An unexpected error occurred: {e}")

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
        if length < 8:
            length = 8  # Ensure the password is at least 8 characters long
        all_chars = string.ascii_letters + string.digits + string.punctuation
        password = ''.join(random.choice(all_chars) for _ in range(length))
        return password

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
