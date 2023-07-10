# Your code goes here.
# You can delete these comments, but do not change the name of this file
# Write your code to expect a terminal of 80 characters wide and 24 rows high

import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from colorama import Fore, Style
import random

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
    ]

CREDS = Credentials.from_service_account_file('creds.json')
SCOPED_CREDS = CREDS.with_scopes(SCOPE)
GSPREAD_CLIENT = gspread.authorize(SCOPED_CREDS)
SHEET = GSPREAD_CLIENT.open('word_triad')


def print_menu():
    print(Fore.BLUE + "\nWelcome to the " + Fore.RED + "WORD TRIAD GAME" + Fore.BLUE + " menu!\n" + Style.RESET_ALL)
    print(Fore.BLUE + "Please, choose a game by typing the corresponding number:" + Style.RESET_ALL)
    print("1. Scramble Game")
    print("2. Hangman Game")
    print("3. Guessing Game")
    print("4. Exit\n")


#https://rb.gy/w1qy2
def load_words_from_google_sheets(sheet_name):
    worksheet = SHEET.worksheet(sheet_name)
    data = worksheet.get_all_records()
    words_df = pd.DataFrame(data)
    return words_df


def choose_difficulty(difficulties):
    print("Categories:")
    for i, difficulty in enumerate(difficulties):
        print(f"{i+1}. {difficulty}")

    while True:
        difficulty_choice = input("\nChoose a difficulty level (1-{}):".format(len(difficulties)))

        if difficulty_choice == "quit":
            return None

        #check if the difficulty choise is a valid input
        if difficulty_choice.isdigit() and int(difficulty_choice) in range(1, len(difficulties) + 1):
            return difficulties[int(difficulty_choice) - 1]

        print(Fore.YELLOW + "Invalid difficulty choice! Please choose a number between 1 and {}.".format(len(difficulties)) + Style.RESET_ALL)


def scramble_word(word):
    scrambled = list(word)
    random.shuffle(scrambled)
    return ''.join(scrambled)


def play_scramble_game():
    words_df = load_words_from_google_sheets("scramble")
    difficulties = words_df["difficulty"].unique()

    print(Fore.BLUE + "\nWelcome to " + Fore.RED + "Scramble Game!" + Style.RESET_ALL)
    print(Fore.BLUE + "Unscramble the word to earn points." + Style.RESET_ALL)
    print(Fore.BLUE + "Enter 'quit' to exit the game.\n" + Style.RESET_ALL)

    selected_difficulty = choose_difficulty(difficulties)

    #Filter the words from google sheet based on the selected difficulty level
    difficulty_words = words_df[words_df["difficulty"] == selected_difficulty]

    #Retrive data from the 'words' column from the google sheet and stores the words as a list
    words = difficulty_words["words"].tolist()

    #Track the words that have already been used in the game, for unique gameplay experience.
    used_words = set()
    score = 0

    while True:
        if len(used_words) == len(words):
            print(Fore.GREEN + "\nYou have unscrambled all the words!" + Style.RESET_ALL)
            break

        word = random.choice(words)
        while word in used_words:
            word = random.choice(words)

        used_words.add(word)
        scrambled_word = scramble_word(word)

        print("\nScrambled word:", Fore.YELLOW + scrambled_word + Style.RESET_ALL)
        guess = input("Enter your guess: ").lower()

        if guess == "quit":
            break

        if guess == word:
            score += 1
            print(Fore.GREEN + "Correct! Your score is", score, Style.RESET_ALL)
        else:
            print(Fore.RED + "Incorrect! The correct word is", word, Style.RESET_ALL)

    print(f"{Fore.GREEN}Thanks for playing! Your final score is {score}{Style.RESET_ALL}\n")

    while True:
        next_action = input("Enter 'play' to play again or 'menu' to go back to the menu: ")
        if next_action == "play":
            # Reset the game and continue playing
            used_words = set()
            score = 0
            break
        elif next_action == "menu":
            # Go back to the menu
            return
        else:
            print(Fore.YELLOW + "\nInvalid input! Please enter 'play' or 'menu'." + Style.RESET_ALL)


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
        print(Fore.YELLOW + "\nInvalid choice! Please enter a number between 1 and 4." + Style.RESET_ALL)