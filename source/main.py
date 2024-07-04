from getpass import getpass
from password_manager import PasswordManager

def main():
    master_password = getpass("Enter master password: ")
    pm = PasswordManager(master_password)

    action = input("Do you want to (a)dd a new password, (v)iew passwords, (g)enerate a password, (r)etrieve a password, (e)dit a password, or (d)elete a password? ")

    if action == 'a':
        username = input("Enter username: ")
        password = getpass("Enter password: ")
        url = input("Enter URL: ")
        notes = input("Enter notes: ")
        categories = input("Enter categories: ")

        pm.save_password(username, password, url, notes, categories)
        print("Password saved successfully!")
    
    elif action == 'v':
        pm.view_passwords()

    elif action == 'g':
        length = int(input("Enter the desired password length: "))
        use_uppercase = input("Include uppercase letters? (y/n): ").lower() == 'y'
        use_numbers = input("Include numbers? (y/n): ").lower() == 'y'
        use_special_chars = input("Include special characters? (y/n): ").lower() == 'y'
        
        generated_password = pm.generate_password(length, use_uppercase, use_numbers, use_special_chars)
        print(f"Generated password: {generated_password}")

    elif action == 'r':
        search_term = input("Enter the URL or username to search for: ")
        pm.retrieve_password(search_term)

    elif action == 'e':
        search_term = input("Enter the URL or username to search for: ")
        pm.edit_password(search_term)

    elif action == 'd':
        search_term = input("Enter the URL or username to search for: ")
        pm.delete_password(search_term)
    
    else:
        print("Invalid action!")

if __name__ == "__main__":
    main()