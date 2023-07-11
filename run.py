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

# Color constants
BLUE = Fore.BLUE
RED = Fore.RED
YELLOW = Fore.YELLOW
GREEN = Fore.GREEN
RESET_ALL = Style.RESET_ALL


def print_menu():
    print(f"{BLUE}\nWelcome to the {RED}WORD TRIAD GAME{BLUE} menu!\n{RESET_ALL}")
    print(f"{BLUE}Please, choose a game by typing the corresponding number:{RESET_ALL}")
    print("1. Scramble Game")
    print("2. Hangman Game")
    print("3. Guessing Game")
    print("4. Exit\n")


# Credits: https://rb.gy/w1qy2
def load_words_from_google_sheets(sheet_name):
    worksheet = SHEET.worksheet(sheet_name)
    data = worksheet.get_all_records()
    words_df = pd.DataFrame(data)
    return words_df


# Choose the difficulty level for scramble and hangman games
def choose_difficulty(difficulties):
    print("Categories:")
    for i, difficulty in enumerate(difficulties):
        print(f"{i+1}. {difficulty}")

    while True:
        difficulty_choice = input(f"\nChoose a difficulty level (1-{len(difficulties)}):")

        if difficulty_choice == "quit":
            return None

        # Check if the difficulty choise is a valid input
        if difficulty_choice.isdigit() and int(difficulty_choice) in range(1, len(difficulties) + 1):
            return difficulties[int(difficulty_choice) - 1]

        print(
            f"{YELLOW}Invalid difficulty choice! "
            f"Please choose a number between 1 and {len(difficulties)}{RESET_ALL}"
        )


# Shuffle the words
def scramble_word(word):
    scrambled = list(word)
    random.shuffle(scrambled)
    return ''.join(scrambled)


# Scramble Game
def play_scramble_game():
    words_df = load_words_from_google_sheets("scramble")
    difficulties = words_df["difficulty"].unique()

    print(f"{BLUE}\nWelcome to {RED}Scramble Game!{RESET_ALL}")
    print(f"{BLUE}Unscramble the word to earn points.\n{RESET_ALL}")

    selected_difficulty = choose_difficulty(difficulties)

    def play_game():
        # Filter the words from google sheet
        # based on the selected difficulty level
        difficulty_words = words_df[words_df["difficulty"] == selected_difficulty]

        # Retrieve data from the 'words' column from the google sheet
        # and store the words as a list
        words = difficulty_words["words"].tolist()

        # Track the words that have already been used in the game,
        # for unique gameplay experience.
        used_words = set()
        score = 0

        while True:
            if len(used_words) == len(words):
                print(f"{GREEN}\nYou have unscrambled all the words!{RESET_ALL}")
                break

            word = random.choice(words)
            while word in used_words:
                word = random.choice(words)

            used_words.add(word)
            scrambled_word = scramble_word(word)

            print(f"\nScrambled word: {YELLOW}{scrambled_word}{RESET_ALL}")
            guess = input("Enter your guess: ").lower()

            if guess == "quit":
                return

            if guess == word:
                score += 1
                print(f"{GREEN}Correct! Your score is {score}{RESET_ALL}")
            else:
                print(f"{RED}Incorrect! The correct word is {word}{RESET_ALL}")

        print(f"{GREEN}Thanks for playing! Your final score is {score}{RESET_ALL}\n")

        while True:
            next_action = input("Enter 'play' to play again or 'menu' to go back to the menu: ")
            if next_action == "play":
                play_game()  # Restart the game
            elif next_action == "menu":
                return main_fcn()  # Go back to the menu
            else:
                print(f"{YELLOW}\nInvalid input! Please enter 'play' or 'menu'.{RESET_ALL}")

    play_game()


# Display the hangman word with guessed letters
def display_word(word, guessed_letters):
    display = ""
    for char in word:
        if char in guessed_letters:
            display += char + " "
        else:
            display += "_ "
    return display


# Hangman game
def play_hangman_game():
    words_df = load_words_from_google_sheets("hangman")
    difficulties = words_df["difficulty"].unique()

    print(f"{BLUE}\nWelcome to {RED}Hangman Game!{RESET_ALL}")
    print(f"{BLUE}Guess the word to win!{RESET_ALL}")

    selected_difficulty = choose_difficulty(difficulties)

    def play_game():
        difficulty_words = words_df[words_df["difficulty"] == selected_difficulty]
        words = difficulty_words["words"].tolist()

        used_words = set()
        score = 0

        while True:
            if len(used_words) == len(words):
                print(f"{GREEN}\nYou have guessed all the words!{RESET_ALL}")
                break

            word = random.choice(words)
            while word in used_words:
                word = random.choice(words)

            used_words.add(word)
            hidden_word = "_" * len(word)
            guessed_letters = set()
            attempts = len(word)

            print(f"{BLUE}Enter 'quit' to exit the game.{RESET_ALL}")
            print(f"{BLUE}Total attempts: {len(word)}\n{RESET_ALL}")

            while attempts > 0:
                print(f"Attempts remaining: {RED}{attempts}{RESET_ALL}")
                print(f"Guessed letters: {RED}{', '.join(guessed_letters)}{RESET_ALL}")
                print(f"Word to guess: {YELLOW}{hidden_word}{RESET_ALL}")
                guess = input("Enter your guess: ").lower()

                if guess == "quit":
                    return

                if guess in guessed_letters:
                    print(f"\n{YELLOW}You already guessed that letter!\n{RESET_ALL}")

                # Check 'guess' to be a single alphabetic letter
                elif guess.isalpha() and len(guess) == 1:
                    guessed_letters.add(guess)

                    if guess in word:
                        hidden_word = display_word(word, guessed_letters)
                        print(f"\n{GREEN}Correct guess! Word: {YELLOW}{hidden_word}\n{RESET_ALL}")

                        if "_" not in hidden_word:
                            score += 1
                            print(
                                f"{GREEN}You've guessed the word correctly! "
                                f"Your score is {score}{RESET_ALL}"
                            )
                            break
                    else:
                        attempts -= 1
                        print(f"\n{RED}Incorrect guess! Word: {YELLOW}{hidden_word}\n{RESET_ALL}")
                else:
                    print(f"\n{YELLOW}Invalid input! Please enter a single letter.\n{RESET_ALL}")

            if attempts == 0:
                print(f"{RED}You've run out of attempts. The word was {word}{RESET_ALL}")

        print(f"{GREEN}Thanks for playing! Your final score is {score}{RESET_ALL}\n")

        while True:
            next_action = input(f"Enter 'play' to play again or 'menu' to go back to the menu: ")
            if next_action == "play":
                play_game()  # Restart the game
            elif next_action == "menu":
                return main_fcn()  # Go back to the menu
            else:
                print(f"{YELLOW}\nInvalid input! Please enter 'play' or 'menu'.{RESET_ALL}")

    play_game()


# Generate random number for Guessing Game
def generate_number():
    return random.randint(1, 10)


# Guessing Game
def play_guessing_game():
    while True:
        number = generate_number()
        attempts = 3

        print(f"{BLUE}\nWelcome to {RED}Guessing Game!{RESET_ALL}")
        print(f"{BLUE}Guess the number between 1 and 10 to win!{RESET_ALL}")
        print(f"{BLUE}Enter 'quit' to exit the game.\n{RESET_ALL}")
        while True:
            try:
                if attempts == 0:
                    print(f"{RED}Game Over! You ran out of attempts.{RESET_ALL}")
                    print(f"The number was: {number}\n")
                    break

                guess = input("Enter your guess: ")

                if guess == "quit":
                    break

                if guess.isdigit():
                    guess = int(guess)
                    if guess == number:
                        print(
                            f"\n{GREEN}Congratulations! "
                            f"You guessed the correct number: {number}{RESET_ALL}"
                        )
                        break
                    elif guess < number:
                        print(f"{YELLOW}Too low!\n{RESET_ALL}")
                    else:
                        print(f"{YELLOW}Too high!\n{RESET_ALL}")
                    attempts -= 1
                else:
                    raise ValueError("Invalid input! Please enter a number.")

            except ValueError as e:
                print(f"\n{YELLOW}{str(e)}{RESET_ALL}")
                continue

        while True:
            try:
                play_again = input("Enter 'play' to play again or 'menu' to go back to the menu: ")
                if play_again == "play":
                    break
                elif play_again == "menu":
                    return
                else:
                    raise ValueError("Invalid input! Please enter 'play' or 'menu'.")

            except ValueError as e:
                print(f"\n{YELLOW}{str(e)}{RESET_ALL}")

    print(f"{GREEN}Thanks for playing!{RESET_ALL}")


def main_fcn():
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
            print(f"{BLUE}Goodbye!{RESET_ALL}")
            break
        else:
            print(f"{YELLOW}\nInvalid choice! Please enter a number between 1 and 4.{RESET_ALL}")


main_fcn()
