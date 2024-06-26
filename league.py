import random
from databaseManager import DatabaseManager
from team import Team
from player import Player
import constants


class League:
    def __init__(self, team_data, db_manager, current_season):
        self.teams = {team_id: Team(name, market_size) for team_id, (name, market_size) in team_data.items()}
        self.db_manager = db_manager
        self.season_games = 82
        self.playoff_teams = 16  # Number of teams that make it to the playoffs
        self.playoff_format = (7, 7, 7, 7)  # Best of 7 games for each round
        self.draft_picks = {}  # Placeholder for draft picks
        self.current_season = current_season

        # Initialize teams with players and metadata
        self.initialize_teams(db_manager, current_season)

    def initialize_teams(self, dbmanager, current_season):
        for team_id, team in self.teams.items():
            team_players_data = self.db_manager.get_players_by_team(team_id,current_season)
            existing_player_ids = set()

            for player_tuple in team_players_data:
                player_id = player_tuple[0]
                if player_id in existing_player_ids:
                    continue
                player_data = {
                    'id': player_id,
                    'name': player_tuple[1],
                    'pos': player_tuple[2],
                    'hgt': player_tuple[3],
                    'weight': player_tuple[4],
                    'born_year': player_tuple[5],
                    'born_loc': player_tuple[6],
                    'imgURL': player_tuple[7],
                    'college': player_tuple[8],
                    'injury_type': player_tuple[9],
                    'injury_games_remaining': player_tuple[10],
                    'tid': player_tuple[11],
                    'ratings': self.db_manager.get_player_ratings_from_db(player_id, current_season)
                }

                player = Player.create_from_db(dbmanager, player_data, current_season)
                team.addPlayer(player)
                existing_player_ids.add(player_id)

    def simulate_season(self):
        # Simulate season games here
        pass

    def simulate_playoffs(self):
        # Playoff simulation logic here
        pass

    def conduct_draft(self):
        # Draft process logic here
        pass

    def assign_draft_picks(self):
        # Logic to assign draft picks based on team performance
        pass

    def get_playoff_bracket(self):
        # Logic to create playoff brackets
        pass

    def simulate_game(self, team1_id, team2_id):
        # Game simulation between two teams
        pass

    def update_standings(self):
        # Update standings based on game results
        pass

    # ... additional methods as needed ...

    def print_team_details(league, team_id):

        if team_id not in league.teams:
            print(f"Team with ID {team_id} not found in the league.")
            return

        team = league.teams[team_id]
        print(f"Team Name: {team.teamName}")
        print(f"Market Size: {team.marketSize}")
        print("Roster:")

        for player in team.roster:
            print(f" - {player.name}, Position: {player.pos}, Height: {player.hgt}, Ratings: {player.ratings}")