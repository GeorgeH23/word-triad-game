# Your code goes here.
# You can delete these comments, but do not change the name of this file
# Write your code to expect a terminal of 80 characters wide and 24 rows high

import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from colorama import Fore, Style

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
    ]

CREDS = Credentials.from_service_account_file('creds.json')
SCOPED_CREDS = CREDS.with_scopes(SCOPE)
GSPREAD_CLIENT = gspread.authorize(SCOPED_CREDS)
SHEET = GSPREAD_CLIENT.open('word_triad')

scramble = SHEET.worksheet('scramble')

data = scramble.get_all_values()

print(data)


def print_menu():
    print(Fore.BLUE + "Welcome to the " + Fore.RED + "WORD TRIAD GAME" + Fore.BLUE + " menu!\n" + Style.RESET_ALL)
    print(Fore.BLUE + "Please, choose a game by typing the corresponding number:" + Style.RESET_ALL)
    print("1. Scramble Game")
    print("2. Hangman Game")
    print("3. Guessing Game")
    print("4. Exit\n")


while True:
    print_menu()
    choice = input("Enter your choice (1-4): ")

    if choice == "1":
        play_scramble_game()
    elif choice == "2":
        play_hangman_game()
    elif choice == "3":
        play_guessing_game()
    elif choice == "4":
        print(Fore.BLUE + "Goodbye!" + Style.RESET_ALL)
        break
    else:
        print("Invalid choice! Please enter a number between 1 and 4.")