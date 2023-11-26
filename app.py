from flask import Flask, render_template
from main import Game
import threading
import webbrowser
import time

app = Flask(__name__)
game = Game(2024)

@app.route('/')
def index():
    teams = game.nba_league.teams
    print(teams)
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



# Add more routes as needed for handling different data views and operations

def open_browser():
    """Function to open a browser after a short delay."""
    time.sleep(1)  # Give the server a second to ensure it starts
    webbrowser.open('http://127.0.0.1:5000/')


if __name__ == '__main__':
    threading.Thread(target=open_browser).start()  # Open the web browser
    app.run(debug=True)  # Start the Flask app