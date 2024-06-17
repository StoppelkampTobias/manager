import os
import json
from datetime import datetime
from .encryption import Encryption

class PasswordManager:
    def __init__(self, master_password: str, filename='data/passwords.json'):
        self.encryption = Encryption(master_password)
        self.filename = filename
        self.ensure_data_directory_exists()
        self.data = self.load_data()

    def ensure_data_directory_exists(self):
        os.makedirs(os.path.dirname(self.filename), exist_ok=True)

    def load_data(self):
        try:
            with open(self.filename, 'r') as file:
                encrypted_data = file.read()
                if encrypted_data:
                    decrypted_data = self.encryption.decrypt(encrypted_data)
                    return json.loads(decrypted_data)
                return {}
        except FileNotFoundError:
            return {}

    def save_data(self):
        encrypted_data = self.encryption.encrypt(json.dumps(self.data))
        with open(self.filename, 'w') as file:
            file.write(encrypted_data)

    def add_entry(self, website, username, password, notes='', category=''):
        if website in self.data:
            self.data[website]['old_passwords'].append(self.data[website]['password'])
        else:
            self.data[website] = {'old_passwords': []}
        self.data[website].update({
            'username': username,
            'password': password,
            'notes': notes,
            'category': category,
            'created_at': datetime.now().isoformat()
        })
        self.save_data()

    def get_entry(self, website):
        return self.data.get(website)

    def delete_entry(self, website):
        if website in self.data:
            del self.data[website]
            self.save_data()
