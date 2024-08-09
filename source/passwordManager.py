"""
In this file, we will implement the PasswordManager class that will be used to manage passwords securely.
"""
import json
import random
import hashlib
import base64
import string
from typing import Dict, Any, Optional, Tuple, List
from datetime import datetime
import requests
from cryptography.fernet import Fernet
import cryptography.fernet



class PasswordManager:
    """
    A class to manage passwords securely.
    """

    def __init__(self, masterPassword: str) -> None:
        self.masterPassword: str = masterPassword
        self.key: bytes = self.generateKey(masterPassword)
        self.data: Dict[str, Dict[str, Any]] = {}

    def generateKey(self, password: str) -> bytes:
        """
        Generate an encryption key based on the master password.
        """
        return base64.urlsafe_b64encode(hashlib.sha256(password.encode()).digest())

    def loadData(self) -> None:
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

    def saveData(self) -> None:
        """
        Encrypt and save the password data to the file.
        """
        fernet = Fernet(self.key)
        encryptedData = fernet.encrypt(json.dumps(self.data).encode())
        with open('passwords.json', 'wb') as file:
            file.write(encryptedData)

    def addPassword(self, site: str, username: Optional[str] = None, password: Optional[str] = None, notes: Optional[str] = None, category: Optional[str] = None) -> None:
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

    def getPassword(self, site: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a password entry by site name.
        """
        return self.data.get(site, None)

    def deletePassword(self, site: str) -> None:
        """
        Delete a password entry by site name.
        """
        if site in self.data:
            del self.data[site]
            self.saveData()

    def updatePassword(self, site: str, username: Optional[str] = None, password: Optional[str] = None, notes: Optional[str] = None, category: Optional[str] = None) -> None:
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

    def searchPassword(self, keyword: str) -> Dict[str, Dict[str, Any]]:
        """
        Search for password entries by a keyword.
        """
        results = {}
        for site, details in self.data.items():
            if keyword.lower() in site.lower() or keyword.lower() in details['username'].lower():
                results[site] = details
        return results

    def checkPasswordStrength(self, password: str) -> Tuple[bool, List[str]]:
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

    def generateStrongPassword(self, length: int = 12) -> str:
        """
        Generate a strong random password.
        """
        if length < 8:
            length = 8  # Ensure the password is at least 8 characters long
        allChars = string.ascii_letters + string.digits + string.punctuation
        password = ''.join(random.choice(allChars) for _ in range(length))
        return password

    def checkReusedPassword(self, password: str) -> bool:
        """
        Check if the given password is reused in any existing entries.
        """
        for details in self.data.values():
            if details['password'] == password:
                return True
        return False

    def checkPwnedPassword(self, password: str) -> bool:
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
