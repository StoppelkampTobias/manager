import json
import os
import getpass
import hashlib
import base64

class PasswordManager:
    def __init__(self, filename='passwords.json'):
        self.filename = filename
        self.passwords = self.load_passwords()
        self.master_password = self.get_master_password()

    def get_master_password(self):
        if os.path.exists('master.txt'):
            with open('master.txt', 'r') as file:
                return file.read()
        else:
            master_password = getpass.getpass("Setze ein Master-Passwort: ")
            hashed_password = hashlib.sha256(master_password.encode()).hexdigest()
            with open('master.txt', 'w') as file:
                file.write(hashed_password)
            return hashed_password

    def verify_master_password(self):
        input_password = getpass.getpass("Gib dein Master-Passwort ein: ")
        hashed_input_password = hashlib.sha256(input_password.encode()).hexdigest()
        return hashed_input_password == self.master_password

    def load_passwords(self):
        if os.path.exists(self.filename):
            with open(self.filename, 'r') as file:
                return json.load(file)
        else:
            return {}

    def save_passwords(self):
        with open(self.filename, 'w') as file:
            json.dump(self.passwords, file)

    def save_password(self, website, username, password):
        if self.verify_master_password():
            encrypted_password = base64.b64encode(password.encode()).decode()
            self.passwords[website] = {'username': username, 'password': encrypted_password}
            self.save_passwords()
            print(f"Passwort für {website} gespeichert.")
        else:
            print("Falsches Master-Passwort.")

    def get_password(self, website):
        if self.verify_master_password():
            if website in self.passwords:
                encrypted_password = self.passwords[website]['password']
                decrypted_password = base64.b64decode(encrypted_password.encode()).decode()
                return {'username': self.passwords[website]['username'], 'password': decrypted_password}
            else:
                return "Kein Passwort für diese Website gefunden."
        else:
            return "Falsches Master-Passwort."