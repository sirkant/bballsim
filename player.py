import random
import requests
import json
from constants import team_data


class Player:
    def __init__(self, player_data):
        if 'name' in player_data:
            self.name = player_data.get('name', 'Unknown Player')
        else:
            first_name = player_data.get('firstName', '')
            last_name = player_data.get('lastName', '')
            self.name = f"{first_name} {last_name}".strip()

        # Initialize ratings as a dictionary
        self.ratings = player_data.get('ratings', {})
        self.stats = player_data.get('stats', {})
        self.contract = player_data.get('contract', {})
        self.match_stats = {'FGM': 0, 'FGA': 0, 'Points': 0,
                            'Rebounds': 0, 'Assists': 0, 'Steals': 0, 'Blocks': 0}
        

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
        self.fatigue = 0  # New attribute
        self.ovr = self.calculate_ovr_rating()
        #self.teamName = team_data[self.tid][0]


    def init_ratings_from_db(self, ratings_data):
        for key in ['hgt', 'stre', 'spd', 'jmp', 'endu', 'ins', 'dnk', 'ft', 'fg', 'tp', 'diq', 'oiq', 'drb', 'pss',
                    'reb']:
            self.ratings[key] = ratings_data.get(key, None)


    def init_stats_from_db(self, stats_data):
        for key in ['fg', 'fga', 'fgp', 'tp', 'tpa', 'tpp', 'ft', 'fta', 'ftp', 'orb', 'drb', 'trb', 'ast', 'tov', 'stl',
                    'blk', 'blkp', 'pf', 'pfd', 'pts']:
            self.stats[key] = stats_data.get(key, None)

    def calculate_ovr_rating(self):
        """Calculates the overall rating based on the individual ratings of various attributes.
        Returns: ovr (float): The overall rating calculated from the sum of individual ratings divided by the number of ratings.
        """
        num_ratings = len(self.ratings)
        if num_ratings == 0:
            return 0

        total_rating = 0
        for key in ['hgt', 'stre', 'spd', 'jmp', 'endu', 'ins', 'dnk', 'ft', 'fg', 'tp', 'diq', 'oiq', 'drb', 'pss',
                    'reb']:
            if key in self.ratings:
                total_rating += self.ratings[key]

        ovr_rating = total_rating / num_ratings
        self.ovr = ovr_rating
        return ovr_rating

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

    def update_fatigue(self, change):
        self.fatigue += change
        self.fatigue = max(0, min(self.fatigue, 100))  # Keep within bounds

    def adjust_ratings_for_fatigue(self):
        if self.fatigue > 0:
            fatigue_factor = 1 - (self.fatigue / 100)

    def update_match_stats(self, stat, value):
        if stat in self.match_stats:
            self.match_stats[stat] += value

    def update_overall_stats(self):
        for stat, value in self.match_stats.items():
            if stat in self.stats:
                self.stats[stat] += value
        self.reset_match_stats()

    def reset_match_stats(self):
        for stat in self.match_stats:
            self.match_stats[stat] = 0

    def calculate_defense_rating(self):
        """
        Calculate the defense rating of the player based on the average of the 'diq', 'drb', 'spd', 'hgt' ratings.
        """
        def_rating = (self.ratings['diq'] + self.ratings['drb'] + self.ratings['spd'] + self.ratings['hgt']) / 4
        return def_rating

def test_calculate_ovr_rating():
    # Create a player instance with sample ratings
    player_data = {
        'ratings': {
            'hgt': 80,
            'stre': 70,
            'spd': 90,
            'jmp': 80,
            'endu': 85,
            'ins': 75,
            'dnk': 90,
            'ft': 80,
            'fg': 85,
            'tp': 75,
            'diq': 70,
            'oiq': 80,
            'drb': 85,
            'pss': 90,
            'reb': 80
        }
    }
    player = Player(player_data)

    # Calculate the overall rating
    ovr_rating = player.calculate_ovr_rating()
    def_rating = player.calculate_defense_rating()

    # Compare the calculated rating with the expected value
    print(team_data)
    print(ovr_rating)
    print(f"Player plays for {team_data[0][0]}")

test_calculate_ovr_rating()


