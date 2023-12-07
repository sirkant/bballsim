import league
from player import Player
from team import Team
from match import Match
from databaseManager import DatabaseManager
from league import League
import requests
import constants


class Game:
    def __init__(self, current_season):
        self.db_manager = DatabaseManager('basketball_game.db')
        self.current_season = current_season
        self.nba_league = None
        self.load_players_and_initialize_league()

    def load_players_and_initialize_league(self):
        existing_players = self.db_manager.get_all_player_ids()  # Fetch only name and born year
        existing_player_ids = set(existing_players)

        url = 'https://raw.githubusercontent.com/alexnoob/BasketBall-GM-Rosters/master/2023-24.NBA.Roster.json'
        players = self.load_players_from_url(url)

        for player in players:
            player_id = (player.name, player.born_year)
            if player_id not in existing_player_ids:
                try:
                    self.db_manager.insert_player(player)
                    existing_player_ids.add(player_id)  # Update the set after inserting
                except AttributeError as e:
                    print(f"Error processing player: {player.name}. Missing attribute: {e}")

        self.nba_league = League(constants.team_data, self.db_manager, self.current_season)
        player_count = self.get_player_count()
        print(f"Number of players in the database: {player_count}")

    def load_players_from_url(self, url):  # Added 'self' parameter
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            players_data = data['players']
            players = [Player.create_from_json(player_data) for player_data in players_data]
            for player in players:
                try:
                    self.db_manager.insert_player(player)  # Changed line
                except AttributeError as e:
                    print(f"Error processing player: {player.name}. Missing attribute: {e}")
            return players
        else:
            pass
        raise Exception(f"Failed to retrieve data from URL. Status code: {response.status_code}")

    def get_player_count(self):
        return self.db_manager.count_rows_in_table("players")

    def get_team_details(self, team_id):
        team = self.nba_league.teams[team_id]
        players = self.db_manager.get_players_by_team(team_id, self.current_season)
        return team, players

    def get_player_details(self, player_id):
        # Iterate through all teams in the league
        for team in self.nba_league.teams.values():
            # Iterate through each player in the team's roster
            for player in team.roster:
                # Check if the player's ID matches the given player_id
                if player.id == player_id:
                    # Return the Player object
                    return player
        # Return None or raise an exception if player is not found
        return None

    def play_match(self, teams):
        print(teams)
        print("Teams Type:", type(teams))
        print(f"Starting function match between: {teams[0].teamName}, {teams[1].teamName}")
        match = Match(teams)
        print(match.teams)
        print(f"Initiating match between: {match.teams[0].teamName}, {match.teams[1].teamName}")
        match.run()
        return match
