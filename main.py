from source.password_manager import PasswordManager

def main():
    manager = PasswordManager()
    while True:
        print("Willkommen zum Passwort-Manager")
        print("1. Passwort speichern")
        print("2. Passwort anzeigen")
        print("3. Beenden")

        choice = input("Wähle eine Option: ")

        if choice == '1':
            website = input("Website: ")
            username = input("Benutzername: ")
            password = input("Passwort: ")
            manager.save_password(website, username, password)
        elif choice == '2':
            website = input("Website: ")
            print(manager.get_password(website))
        elif choice == '3':
            break
        else:
            print("Ungültige Wahl, bitte versuche es erneut.")

if __name__ == "__main__":
    main()
