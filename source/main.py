import json
import getpass
import hashlib
import base64
from cryptography.fernet import Fernet
from datetime import datetime
import secrets
import requests  #hinzugefügt
import string  #hinzugefügt

class PasswordManager:
    def __init__(self, master_password):
        self.master_password = master_password
        self.key = self.generate_key(master_password)
        self.data = {}
        self.load_data()

    def generate_key(self, password):
        return base64.urlsafe_b64encode(hashlib.sha256(password.encode()).digest())

    def load_data(self):
        try:
            with open('passwords.json', 'rb') as file:
                encrypted_data = file.read()
            f = Fernet(self.key)
            decrypted_data = f.decrypt(encrypted_data).decode()
            self.data = json.loads(decrypted_data)
        except FileNotFoundError:
            self.data = {}

    def save_data(self):
        f = Fernet(self.key)
        encrypted_data = f.encrypt(json.dumps(self.data).encode())
        with open('passwords.json', 'wb') as file:
            file.write(encrypted_data)

    def add_password(self, site, username, password, notes="", category=""):
        self.data[site] = {
            'username': username,
            'password': password,
            'created_at': datetime.now().isoformat(),
            'notes': notes,
            'category': category
        }
        self.save_data()

    def get_password(self, site):
        return self.data.get(site, None)

    def delete_password(self, site):
        if site in self.data:
            del self.data[site]
            self.save_data()

    def update_password(self, site, username=None, password=None, notes=None, category=None):
        if site in self.data:
            if username:
                self.data[site]['username'] = username
            if password:
                self.data[site]['password'] = password
            if notes:
                self.data[site]['notes'] = notes
            if category:
                self.data[site]['category'] = category
            self.save_data()

    def search_password(self, keyword):
        results = {}
        for site, details in self.data.items():
            if keyword.lower() in site.lower() or keyword.lower() in details['username'].lower():
                results[site] = details
        return results

    def check_password_strength(self, password):
        length_criteria = len(password) >= 8
        digit_criteria = any(char.isdigit() for char in password)
        upper_criteria = any(char.isupper() for char in password)
        lower_criteria = any(char.islower() for char in password)
        special_criteria = any(char in string.punctuation for char in password)
        return all([length_criteria, digit_criteria, upper_criteria, lower_criteria, special_criteria])

    def check_reused_password(self, password):
        for site, details in self.data.items():
            if details['password'] == password:
                return True
        return False

    def check_pwned_password(self, password):
        hashed_password = hashlib.sha1(password.encode()).hexdigest().upper()
        prefix, suffix = hashed_password[:5], hashed_password[5:]
        response = requests.get(f'https://api.pwnedpasswords.com/range/{prefix}')
        if response.status_code == 200:
            hashes = (line.split(':') for line in response.text.splitlines())
            return any(s == suffix for s, count in hashes)
        return False

def main():
    master_password = getpass.getpass('Enter your master password: ')
    pm = PasswordManager(master_password)
    
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
            pm.add_password(site, username, password, notes, category)
            print("Password added successfully!")

        elif choice == '2':
            site = input("Enter site: ")
            password = pm.get_password(site)
            if password:
                print(f"Username: {password['username']}")
                print(f"Password: {password['password']}")
                print(f"Notes: {password['notes']}")
                print(f"Category: {password['category']}")
                print(f"Created at: {password['created_at']}")
            else:
                print("Password not found!")

        elif choice == '3':
            site = input("Enter site: ")
            pm.delete_password(site)
            print("Password deleted successfully!")

        elif choice == '4':
            site = input("Enter site: ")
            username = input("Enter username (press enter to skip): ")
            password = getpass.getpass("Enter password (press enter to skip): ")
            notes = input("Enter notes (press enter to skip): ")
            category = input("Enter category (press enter to skip): ")
            pm.update_password(site, username or None, password or None, notes or None, category or None)
            print("Password updated successfully!")

        elif choice == '5':
            keyword = input("Enter search keyword: ")
            results = pm.search_password(keyword)
            if results:
                for site, details in results.items():
                    print(f"\nSite: {site}")
                    print(f"Username: {details['username']}")
                    print(f"Password: {details['password']}")
                    print(f"Notes: {details['notes']}")
                    print(f"Category: {details['category']}")
                    print(f"Created at: {details['created_at']}")
            else:
                print("No passwords found!")

        elif choice == '6':
            password = getpass.getpass("Enter password: ")
            if pm.check_password_strength(password):
                print("Password is strong!")
            else:
                print("Password is weak!")

        elif choice == '7':
            password = getpass.getpass("Enter password: ")
            if pm.check_reused_password(password):
                print("Password is reused!")
            else:
                print("Password is unique!")

        elif choice == '8':
            password = getpass.getpass("Enter password: ")
            if pm.check_pwned_password(password):
                print("Password has been pwned!")
            else:
                print("Password is safe!")

        elif choice == '9':
            break

        else:
            print("Invalid choice! Please try again.")

if __name__ == "__main__":
    main()