Passwort-Manager

Dies ist ein einfacher Passwort-Manager, der in Python implementiert ist.

## Installation

Benötigte Bibliotheken installieren:



Der abschnitt ab hier ist für euch, um zu verstehen wie man das Programm ausführt. 
Alle befehle müsst ihr hier im Terminal ausführen, oder in WSL in diese Verzeichniss navigieren, un sie dann von da aus ausführen.
1. pip install -r requirements.txt
2. python3 main.py

So wird das Programm gestartet. 

wenn ihr:
python3 -m unittest discover tests 

eingebt, werden Drei "_pycache_" ordner, (einer als unterordner im "source" Ordner, einer als Unterordner im "tests" Ordner und eienr als Normaler Ordner) erstellt. Zudem wird eine "master.txt" 
erstellt, in welche das "Masterpasswort" gespeichert wird. Zu guter letzt wird eine "test_passwords.json" erstellt. Diese 3 Ornder, die "master.txt" und die "test_passwords.json" bitte vor 
jedem Push wieder löschen. 
