import random
import requests
import json


class Player:
    def __init__(self, player_data):
        if 'name' in player_data:
            self.name = player_data.get('name', 'Unknown Player')
        else:
            first_name = player_data.get('firstName', '')
            last_name = player_data.get('lastName', '')
            self.name = f"{first_name} {last_name}".strip()

        # Initialize ratings as a dictionary
        self.ratings = player_data.get('ratings', [])
        self.stats = player_data.get('stats', [])
        self.contract = player_data.get('contract', {})

        # Set attributes directly from player_data
        for key in ['id', 'pos', 'hgt', 'weight', 'imgURL', 'college', 'tid']:
            setattr(self, key, player_data.get(key, None))

        # Handle the nested 'born' structure
        self.born_year = None
        self.born_loc = None
        if 'born' in player_data:
            self.born_year = player_data['born'].get('year', None)
            self.born_loc = player_data['born'].get('loc', None)

        # Handle 'injury' structure, if exists
        self.injury_type = player_data.get('injury', {}).get('type', 'Healthy')
        self.injury_games_remaining = player_data.get('injury', {}).get('gamesRemaining', 0)

    def init_ratings_from_db(self, ratings_data):
        for key in ['hgt', 'stre', 'spd', 'jmp', 'endu', 'ins', 'dnk', 'ft', 'fg', 'tp', 'diq', 'oiq', 'drb', 'pss',
                    'reb']:
            self.ratings[key] = ratings_data.get(key, None)

    def init_contract_from_db(self, ratings_data):
        for key in ['amount', 'exp', 'rookie']:
            self.contract[key] = ratings_data.get(key, None)

    def print_attributes(self):
        for key, value in self.__dict__.items():
            print(f"{key}: {value}")

    def age_and_develop(self):
        """ Simulate player aging and development over a year """
        self.age += 1

        # Development logic based on age and potential
        if self.age < 24:
            growth_rate = 1.05  # Young players grow faster
        elif 24 <= self.age <= 30:
            growth_rate = 1.02  # Prime age, moderate growth
        else:
            growth_rate = 0.98  # Older players may start to decline

        # Update current rating based on potential and growth rate
        self.current_rating = min(self.current_rating * growth_rate, self.potential)

        # Adjust potential - players may not always reach their full potential
        self.potential -= 0.5  # Potential decreases slightly each year

        # Ensure ratings stay within bounds
        self.current_rating = min(max(self.current_rating, 0), 100)
        self.potential = min(max(self.potential, 0), 100)

    def update_stats(self, points, rebounds, assists):
        """ Update player's game statistics """
        self.stats['points'] = points
        self.stats['rebounds'] = rebounds
        self.stats['assists'] = assists

    def display_player_info(self):
        """ Display player information """
        print(f"Name: {self.name}")
        print(f"Position: {self.position}")
        print(f"Ratings: {self.ratings}")
        print(f"Potential: {self.potential}")
        print(f"Age: {self.age}")
        print(
            f"Stats: Points: {self.stats['points']}, Rebounds: {self.stats['rebounds']}, Assists: {self.stats['assists']}")

    @classmethod
    def create_from_json(cls, player_data):
        return cls(player_data)

    @classmethod
    def create_from_db(cls, db_manager, player_data, current_season):
        player_id = player_data['id']
        player_data = db_manager.get_player_data(player_id)
        player = cls(player_data)
        ratings_data = db_manager.get_player_ratings_from_db(player_id, current_season)
        player.ratings = ratings_data
        contract_data = db_manager.get_player_contract_from_db(player_id)
        player.contract = contract_data
        return player
