Passwort-Manager

Dies ist ein einfacher Passwort-Manager, der in Python implementiert ist.

## Installation

Benötigte Bibliotheken installieren:



Der abschnitt ab hier ist für euch, um zu verstehen wie man das Programm ausführt. 
Alle befehle müsst ihr hier im Terminal ausführen, oder in WSL in diese Verzeichniss navigieren, un sie dann von da aus ausführen.
1. pip install -r requirements.txt
2. python3 main.py 
Dann startet das Programm und ihr werdet aufgefordert ein Master Passwort zu 
erstellen. Nach dem erstellen wird die Textdatei mit dem Namen: "master.txt" erstellt, in welche das 
"Masterpasswort" gespeichert wird. Sobald ihr dann Passwörter speichert (also Option "1" wählt) wird eine Jsondatei mit dem Namen: "passwords.json" erstellt, in welche alle Passwörter mit der dazugehörigen Website und Benutzernamen gespeichert werden. Zudem wird ein "_pycache_"Ordner, im Source Ordner erstellt.

wenn ihr:
python3 -m unittest discover tests 

eingebt, werden zwei "_pycache_" Ordner, ( einer als Unterordner im "tests" Ordner und eienr als Normaler Ordner) 
erstellt. 

Die 3 Order, also der Unterordner im soureordner, der Unterordner im testordner, sowie der normale Order, die "master.txt" und falls vorhanden die "passwords.json" bitte vor jedem Push wieder 
löschen, sodass wir noch folgende Struktur 
haben: 
.
├── main.py
├── mypy.ini
├── pylintrc
├── README.md
├── requirements.txt
├── documentation
│   └── Bewertung.xlsx
├── source
│   ├── main.py
│   └── password_manager.py
└── tests
    ├── test_main.py
    └── test_password_manager.py
