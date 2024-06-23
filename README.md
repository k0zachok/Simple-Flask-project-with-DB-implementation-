# Blackjack Game Project

## Overview

This is a web-based Blackjack game where users can register, log in, and play Blackjack against a dealer. The game includes functionalities for placing bets, managing friends, viewing a leaderboard, and playing multiple rounds.

## Features

- **User Authentication**: Register and log in with secure password hashing.
- **Gameplay**: Play Blackjack with betting functionality.
- **Leaderboard**: View global and friends-only leaderboards with ranks based on points.
- **Friend Management**: Add and manage friends.
- **Game State Persistence**: Game state and user data are persisted across sessions.

## Technologies Used

- **Backend**: Flask
- **Frontend**: HTML, CSS, JavaScript
- **Database**: SQLite
- **Authentication**: Flask-Login

## Installation

1. **Clone the repository**:
   ```sh
   git clone https://github.com/k0zachok/prog_assignment2.git
2. **Create the virtual environment**:
   ```sh
   python3 -m venv venv
3. **Install dependencies:**:
   ```sh
   pip install -r requirements.txt
4. **Set up the database:**:
   ```sh
   flask db init
   flask db migrate
   flask db upgrade

5. **Run the application:**:
   ```sh
   flask run
   
## Usage

## Register
Go to the Register page.
Enter your username and password.
Click "Register".
## Login
Go to the Login page.
Enter your username and password.
Click "Login".
## Start a Game
After logging in, click "Start Game" on the main page.
Place your bet on the "Place Bet" screen.
Play the game by choosing to hit, stand, or double down.
## Manage Friends
Go to the Friends page.
Add friends by entering their username and sending a friend request.
View sent and received requests and manage your friends list.
## View Leaderboard
Go to the Leaderboard page.
View the global leaderboard or switch to the friends-only leaderboard.

   

