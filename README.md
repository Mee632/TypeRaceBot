# TypeRaceBot

TypeRaceBot is a Discord bot written in Python that allows users to play a typing speed game. The bot provides several commands for users to interact with, including starting a game, viewing user records and progress, and viewing a leaderboard of top scores.

## Features

- **TypeRace Game**: Users can start a typing speed game with the `!typerace` command. The bot will provide a sentence for the user to type as fast as they can. The bot calculates the user's words per minute (WPM) and correctness of the typed sentence.

- **Multiplayer Game**: Users can start a multiplayer typing speed game with the `!multiplayer` command. The bot will provide a sentence for all players to type as fast as they can. The bot calculates each player's WPM and correctness, and announces the winner.

- **User Records**: Users can view their own or other users' records with the `!userrecords` command. The bot will display the user's best WPM, accuracy, and the language used in their best game.

- **User Progress**: Users can view their own or other users' progress with the `!userprogress` command. The bot will display the user's WPM and accuracy for each game they've played.

- **Leaderboard**: Users can view the top 10 records with the `!leaderboard` command. The bot will display the top 10 users' WPM, accuracy, and the language used in their best game.

## Installation

1. Clone this repository.
2. Install the required Python packages by running `pip install -r requirements.txt`.
3. Set up your MongoDB database and update the connection string in `main.py`.
4. Create a `.env` file in the root directory and add your Discord bot token with the key `DISCORD_TOKEN`.
5. Run `main.py` to start the bot.

## Usage

Invite the bot to your Discord server. Use the `!help` command to view all available commands and how to use them.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
