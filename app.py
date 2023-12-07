from flask import Flask, render_template
from main import Game
import threading
import webbrowser
import time
import random
import constants
from match import Match

app = Flask(__name__)
game = Game(2024)

@app.route('/')
def index():
    teams = game.nba_league.teams
    return render_template('index.html', teams=teams)

@app.route('/players/count')
def player_count():
    count = game.get_player_count()
    return render_template('players.html', count=count)  # Pass the count to the players.html template

@app.route('/team/<int:team_id>')
def team_details(team_id):
    team_info = game.get_team_details(team_id)
    if isinstance(team_info, tuple):
        # Assuming the first element of the tuple is the team object
        team = team_info[0]
    else:
        team = team_info

    if team:
        # Assuming team is an object with attributes like 'teamName' and 'players'
        print("Team Name:", team.teamName)  # Debug print
        print("Team Players", team.roster)
        return render_template('team_detail.html', team=team)
    else:
        # Handle the error or redirect
        return "Team not found", 404

@app.route('/player/<int:player_id>')
def player_details(player_id):
    player_info = game.get_player_details(player_id)
    if player_info:
        return render_template('player_detail.html', player=player_info)
    else:
        return "Player not found", 404

@app.route('/play_match')
def play_match():
    teams_list = list(game.nba_league.teams.values())
    try:
        teams = random.sample(teams_list, 2)  # Randomly select two teams
        match = Match(teams)
        match_result = match.run()  # Assuming run method returns final stats

        # Create a dictionary to map team names to their stats
        stats_dict = {
            teams[0].teamName: match_result[teams[0].teamName],
            teams[1].teamName: match_result[teams[1].teamName]
        }

        return render_template('match_result.html', team_stats=stats_dict)
    except TypeError as e:
        print("Error selecting teams:", e)
        return "An error occurred in team selection", 500

@app.route('/play_match_denver')
def play_match_denver():
    teams_list = list(game.nba_league.teams.values())
    try:
        teams = teams_list[7], teams_list[19]  # Randomly select two teams
        match = Match(teams)
        match_result = match.run()  # Assuming run method returns final stats

        # Create a dictionary to map team names to their stats
        stats_dict = {
            teams[0].teamName: match_result[teams[0].teamName],
            teams[1].teamName: match_result[teams[1].teamName]
        }

        return render_template('match_result.html', team_stats=stats_dict)
    except TypeError as e:
        print("Error selecting teams:", e)
        return "An error occurred in team selection", 500







# Add more routes as needed for handling different data views and operations

def open_browser():
    """Function to open a browser after a short delay."""
    time.sleep(1)  # Give the server a second to ensure it starts
    webbrowser.open('http://127.0.0.1:5000/')


if __name__ == '__main__':
    threading.Thread(target=open_browser).start()  # Open the web browser
    app.run(debug=True)  # Start the Flask app