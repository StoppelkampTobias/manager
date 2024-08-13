# Password Manager

A simple, secure password manager in Python that provides a text-based user interface (TUI) for managing passwords.

## Prerequisites

- Python 3.11.5

## Installation

Install dependencies with:

```bash
pip install -r requirements.txt
```

## Usage

Start the program by executing the following command:

```bash
python3.11 main.py
```

After starting, you will be prompted to enter your master password. This password is used to encrypt and decrypt your stored passwords. After successfully entering the master password, you will be taken to the main menu, where you can perform various actions such as adding, retrieving, updating, and deleting passwords.

## Analysis Tools

The code of the password manager can be analyzed and reviewed with various tools:

### Mypy - Static Type Checking

Check the code for type errors with mypy:

```bash
mypy source | tee mypy_output.txt
mypy main.py
```

This runs mypy for the entire `source` folder and the `main.py` file. The results are saved in the `mypy_output.txt` file.

### Pylint - Code Analysis

Run pylint to check the code for style issues and potential errors:

```bash
pylint source main.py
```

### Coverage - Code Coverage

To check the test coverage, you can use coverage. Make sure you have written tests for your project and run the tests with coverage:

```bash
coverage run -m unittest discover
coverage report
coverage html  # Generates an HTML report of the test coverage
```

## Tests

To check the test coverage and test the functionality of the password manager, ensure that your tests are organized in the `tests` folder and run them using unittest:

```bash
python -m unittest discover
```

When you have any questions you can contact: Tobias Stoppelkamp: stoppelkamp055@gmail.com or David Prinz: david.prinz1123@gmail.com