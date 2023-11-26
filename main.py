import league
from player import Player
from team import Team
from match import Match
from databaseManager import DatabaseManager
from league import League
import requests
import random

def load_players_from_url(url):
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        players_data = data['players']
        players = [Player.create_from_json(player_data) for player_data in players_data]
        return players
    else:
        raise Exception(f"Failed to retrieve data from URL. Status code: {response.status_code}")


def main():
    db_manager = DatabaseManager('basketball_game.db')

    # Check if the database already has players
    existing_players = db_manager.get_all_players()
    if not existing_players:
        # If no players in the database, fetch and insert them
        url = 'https://raw.githubusercontent.com/alexnoob/BasketBall-GM-Rosters/master/2023-24.NBA.Roster.json'
        players = load_players_from_url(url)

        for player in players:
            try:
                db_manager.insert_player(player)
            except AttributeError as e:
                print(f"Error processing player: {player.name}. Missing attribute: {e}")
                break

    player_count = db_manager.count_rows_in_table("players")
    print(f"Number of players in the database: {player_count}")

    current_season = 2023

    # Initialise the league
    nba_league = League(league.team_data, db_manager, current_season)
    nba_league.print_team_details(0)

    # Example usage (assuming team1 and team2 are already created and populated with players)
    # match = Match(team1, team2)
    # match.simulate_game()
    # match.display_match_summary()
    # team1.displayTeamInfo()
    # team2.displayTeamInfo()

if __name__ == "__main__":
    main()