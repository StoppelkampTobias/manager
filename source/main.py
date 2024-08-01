import json
import os
import getpass
import hashlib
import base64
from cryptography.fernet import Fernet

# Beispiel für die Implementierung einer einfachen Verschlüsselung
class PasswordManager:
    def __init__(self, master_password):
        self.master_password = master_password
        self.key = self.generate_key(master_password)
        self.fernet = Fernet(self.key)
        self.data_file = 'data.json'
        self.data = self.load_data()

    def generate_key(self, password):
        return base64.urlsafe_b64encode(hashlib.sha256(password.encode()).digest())

    def load_data(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, 'rb') as f:
                encrypted_data = f.read()
                return json.loads(self.fernet.decrypt(encrypted_data).decode())
        return {}

    def save_data(self):
        with open(self.data_file, 'wb') as f:
            encrypted_data = self.fernet.encrypt(json.dumps(self.data).encode())
            f.write(encrypted_data)

    def add_password(self, site, username, password):
        self.data[site] = {'username': username, 'password': password}
        self.save_data()

    def get_password(self, site):
        return self.data.get(site)

    def run(self):
        while True:
            choice = input("1. Add Password\n2. Get Password\n3. Exit\nChoose an option: ")
            if choice == '1':
                site = input("Enter site: ")
                username = input("Enter username: ")
                password = getpass.getpass("Enter password: ")
                self.add_password(site, username, password)
            elif choice == '2':
                site = input("Enter site: ")
                credentials = self.get_password(site)
                if credentials:
                    print(f"Username: {credentials['username']}\nPassword: {credentials['password']}")
                else:
                    print("No credentials found for this site.")
            elif choice == '3':
                break
            else:
                print("Invalid choice.")

def run_password_manager():
    master_password = getpass.getpass("Enter master password: ")
    manager = PasswordManager(master_password)
    manager.run()