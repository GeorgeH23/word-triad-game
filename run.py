import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from colorama import Fore, Style
import random


class WordTriadGame:
    def __init__(self):
        # Define the Google Sheets API scope
        self.SCOPE = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive.file",
            "https://www.googleapis.com/auth/drive"
        ]
        self.CREDS = Credentials.from_service_account_file('creds.json')
        self.SCOPED_CREDS = self.CREDS.with_scopes(self.SCOPE)
        self.GSPREAD_CLIENT = gspread.authorize(self.SCOPED_CREDS)
        self.SHEET = self.GSPREAD_CLIENT.open('word_triad')

        # Track if a game has been played
        self.game_played = False

        # Color constants for formatting text
        self.BLUE = Fore.BLUE
        self.RED = Fore.RED
        self.YELLOW = Fore.YELLOW
        self.GREEN = Fore.GREEN
        self.RESET_ALL = Style.RESET_ALL

    def print_menu(self):
        print(
            f"{self.BLUE}\nWelcome to the "
            f"{self.RED}WORD TRIAD GAME"
            f"{self.BLUE} menu!\n{self.RESET_ALL}"
        )
        print(
            f"{self.BLUE}"
            f"Please, choose a game by typing the corresponding number: "
            f"{self.RESET_ALL}"
        )
        print("1. Scramble Game")
        print("2. Hangman Game")
        print("3. Guessing Game")
        print("4. Exit\n")

    # Credits: https://rb.gy/w1qy2
    def load_words_from_google_sheets(self, sheet_name):
        worksheet = self.SHEET.worksheet(sheet_name)
        data = worksheet.get_all_records()
        words_df = pd.DataFrame(data)
        return words_df

    # Choose the difficulty level for scramble and hangman games
    def choose_difficulty(self, difficulties):
        print("Categories:")
        for i, difficulty in enumerate(difficulties):
            print(f"{i+1}. {difficulty}")

        while True:
            difficulty_choice = input(f"\nChoose a difficulty level (1-{len(difficulties)}):")

            if difficulty_choice.lower() == "quit":
                self.main_fcn()
                break

            # Check if the difficulty choise is a valid input
            if (
                difficulty_choice.isdigit() and
                int(difficulty_choice) in range(1, len(difficulties) + 1)
            ):
                return difficulties[int(difficulty_choice) - 1]

            print(
                f"{self.YELLOW}Invalid difficulty choice! "
                f"Please choose a number between 1 and {len(difficulties)}"
                f"{self.RESET_ALL}"
            )

    # Shuffle the words
    def scramble_word(self, word):
        scrambled = list(word)
        random.shuffle(scrambled)
        return ''.join(scrambled)

    # Scramble Game
    def play_scramble_game(self):
        words_df = self.load_words_from_google_sheets("scramble")
        difficulties = words_df["difficulty"].unique()

        print(f"{self.BLUE}\nWelcome to {self.RED}Scramble Game!{self.RESET_ALL}")
        print(f"{self.BLUE}Unscramble the word to earn points.\n{self.RESET_ALL}")

        selected_difficulty = self.choose_difficulty(difficulties)

        def play_game():
            # Filter the words from google sheet based on difficulty
            difficulty_words = words_df[words_df["difficulty"] == selected_difficulty]

            # Retrieve data from the 'words' column from the google sheet
            words = difficulty_words["words"].tolist()

            # Track the words that have already been used in the game
            used_words = set()
            score = 0

            while True:
                # Check if all words have been unscrabled.
                if len(used_words) == len(words):
                    print(f"{self.GREEN}\nYou have unscrambled all the words!{self.RESET_ALL}")
                    break

                word = random.choice(words)
                while word in used_words:
                    word = random.choice(words)

                used_words.add(word)
                scrambled_word = self.scramble_word(word)

                # Display the scrambled word and prompt for a guess.
                print(f"\nScrambled word: {self.YELLOW}{scrambled_word}{self.RESET_ALL}")
                guess = input("Enter your guess: ").lower()

                if guess == "quit":
                    return

                # Check if the guess is correct and update the score.
                if guess == word:
                    score += 1
                    print(f"{self.GREEN}Correct! Your score is {score}{self.RESET_ALL}")
                else:
                    print(f"{self.RED}Incorrect! The correct word is {word}{self.RESET_ALL}")

            # Display the final score.
            print(f"{self.GREEN}Thanks for playing! Your final score is {score}{self.RESET_ALL}\n")

            # After completing a game round, prompt for the next action.
            while True:
                try:
                    next_action = input("Enter 'play' to play again or 'menu' to go back to the menu: ")
                    if next_action == "play":
                        play_game()  # Restart the game
                    elif next_action == "menu":
                        return  # Go back to the menu
                    else:
                        raise ValueError("Invalid input! Please enter 'play' or 'menu'.")

                except ValueError as e:
                    print(f"\n{self.YELLOW}{str(e)}{self.RESET_ALL}")
                    break  # Exit the loop after display the error message.

        play_game()

    # Display the hangman word with guessed letters filled in.
    def display_word(self, word, guessed_letters):
        display = ""
        for char in word:
            if char in guessed_letters:
                display += char + " "
            else:
                display += "_ "
        return display

    # Hangman game
    def play_hangman_game(self):
        words_df = self.load_words_from_google_sheets("hangman")
        difficulties = words_df["difficulty"].unique()

        print(f"{self.BLUE}\nWelcome to {self.RED}Hangman Game!{self.RESET_ALL}")
        print(f"{self.BLUE}Guess the word to win!{self.RESET_ALL}")

        selected_difficulty = self.choose_difficulty(difficulties)

        def play_game():
            difficulty_words = words_df[words_df["difficulty"] == selected_difficulty]
            words = difficulty_words["words"].tolist()

            used_words = set()
            score = 0

            while True:
                if len(used_words) == len(words):
                    print(f"{self.GREEN}\nYou have guessed all the words!{self.RESET_ALL}")
                    break

                word = random.choice(words)
                while word in used_words:
                    word = random.choice(words)

                used_words.add(word)
                hidden_word = "_" * len(word)
                guessed_letters = set()
                attempts = len(word)

                print(f"{self.BLUE}Enter 'quit' to exit the game.{self.RESET_ALL}")
                print(f"{self.BLUE}Total attempts: {len(word)}\n{self.RESET_ALL}")

                while attempts > 0:
                    print(f"Attempts remaining: {self.RED}{attempts}{self.RESET_ALL}")
                    print(f"Guessed letters: {self.RED}{', '.join(guessed_letters)}{self.RESET_ALL}")
                    print(f"Word to guess: {self.YELLOW}{hidden_word}{self.RESET_ALL}")

                    try:
                        guess = input("Enter your guess: ").lower()

                        if guess == "quit":
                            return

                        if guess in guessed_letters:
                            print(f"\n{self.YELLOW}You already guessed that letter!\n{self.RESET_ALL}")

                        # Check 'guess' to be a single alphabetic letter
                        elif guess.isalpha() and len(guess) == 1:
                            guessed_letters.add(guess)

                            if guess in word:
                                # Update the hidden_word with the correctly guessed letter.
                                hidden_word = self.display_word(word, guessed_letters)
                                print(
                                    f"\n{self.GREEN}Correct guess! Word: "
                                    f"{self.YELLOW}{hidden_word}\n"
                                    f"{self.RESET_ALL}"
                                )

                                if "_" not in hidden_word:
                                    # All letters have been guessed correctly.
                                    score += 1
                                    print(
                                        f"{self.GREEN}You've guessed the word correctly! "
                                        f"Your score is {score}"
                                        f"{self.RESET_ALL}"
                                    )
                                    break
                            else:
                                # Incorrect guess.
                                attempts -= 1
                                print(
                                    f"\n{self.RED}Incorrect guess! Word: "
                                    f"{self.YELLOW}{hidden_word}\n"
                                    f"{self.RESET_ALL}"
                                )
                        else:
                            raise ValueError("Invalid input! Please enter a single letter.")

                    except ValueError as e:
                        print(f"\n{self.YELLOW}{str(e)}\n{self.RESET_ALL}")

                if attempts == 0:
                    print(f"{self.RED}You've run out of attempts. The word was {word}{self.RESET_ALL}")

            # Display the final score.
            print(f"{self.GREEN}Thanks for playing! Your final score is {score}{self.RESET_ALL}\n")

            # After completing a game round, prompt for the next action.
            while True:
                try:
                    next_action = input(f"Enter 'play' to play again or 'menu' to go back to the menu: ")
                    if next_action == "play":
                        play_game()  # Restart the game
                    elif next_action == "menu":
                        return  # Go back to the menu
                    else:
                        raise ValueError("Invalid input! Please enter 'play' or 'menu'.")

                except ValueError as e:
                    print(f"\n{self.YELLOW}{str(e)}{self.RESET_ALL}")
                    break  # Exit the loop after display the error message.

        play_game()

    # Generate random number for Guessing Game
    def generate_number(self):
        return random.randint(1, 10)

    # Guessing Game
    def play_guessing_game(self):
        restart_game = True

        while restart_game:
            number = self.generate_number()
            attempts = 3

            print(f"{self.BLUE}\nWelcome to {self.RED}Guessing Game!{self.RESET_ALL}")
            print(f"{self.BLUE}Guess the number between 1 and 10 to win!{self.RESET_ALL}")
            print(f"{self.BLUE}Enter 'quit' to exit the game.\n{self.RESET_ALL}")
            while True:
                try:
                    # Check if the player has run out of attempts.
                    if attempts == 0:
                        print(f"{self.RED}Game Over! You ran out of attempts.{self.RESET_ALL}")
                        print(f"The number was: {number}\n")
                        break

                    guess = input("Enter your guess: ")

                    if guess == "quit":
                        print(f"{self.GREEN}Thanks for playing!\n{self.RESET_ALL}")
                        return

                    # Check if the 'guess' is a valid number.
                    if guess.isdigit():
                        guess = int(guess)
                        if guess == number:
                            print(
                                f"\n{self.GREEN}Congratulations! "
                                f"You guessed the correct number: "
                                f"{number}{self.RESET_ALL}"
                            )
                            break
                        elif guess < number:
                            print(f"{self.YELLOW}Too low!\n{self.RESET_ALL}")
                        else:
                            print(f"{self.YELLOW}Too high!\n{self.RESET_ALL}")
                        attempts -= 1
                    else:
                        raise ValueError("Invalid input! Please enter a number.")

                except ValueError as e:
                    # Handle the ValueError and display an error message.
                    print(f"\n{self.YELLOW}{str(e)}{self.RESET_ALL}")
                    continue

            print(f"{self.GREEN}Thanks for playing!{self.RESET_ALL}")

            if restart_game:
                # After completing a game round, prompt for the next action.
                while True:
                    try:
                        next_action = input("Enter 'play' to play again or 'menu' to go back to the menu: ")
                        if next_action == "play":
                            break  # Exit the loop and restart the game.
                        elif next_action == "menu":
                            return  # Exit the function and go back to the menu.
                        else:
                            raise ValueError("Invalid input! Please enter 'play' or 'menu'.")

                    except ValueError as e:
                        print(f"\n{self.YELLOW}{str(e)}{self.RESET_ALL}")
                        break  # Exit the loop after display the error message.

    def main_fcn(self):
        while True:
            self.print_menu()
            choice = input("Enter your choice (1-4): ")

            if choice == "1":
                self.play_scramble_game()
                self.game_played = True
            elif choice == "2":
                self.play_hangman_game()
                self.game_played = True
            elif choice == "3":
                self.play_guessing_game()
                self.game_played = True
            elif choice == "4":
                if self.game_played:
                    # If any game has been played, display a thanks message.
                    print(f"\n{self.GREEN}Thanks for playing!{self.RESET_ALL}")
                print(f"{self.BLUE}Goodbye!{self.RESET_ALL}")
                break  # Exit the loop and end the program
            else:
                # If the user enters an invalid choice, display an error message
                print(
                    f"{self.YELLOW}\nInvalid choice! "
                    f"Please enter a number between 1 and 4."
                    f"{self.RESET_ALL}"
                )

    # Start the program by calling the main function
    def run(self):
        self.main_fcn()


game = WordTriadGame()
game.run()
