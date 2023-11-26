import random

class Match:
    def __init__(self, team1, team2):
        self.team1 = team1
        self.team2 = team2
        self.statistics = {
            'team1': {'FGA': 0, 'FGM': 0, 'Rebounds': 0, 'Steals': 0, 'Blocks': 0, 'Assists': 0, 'TOs': 0, 'Points': 0},
            'team2': {'FGA': 0, 'FGM': 0, 'Rebounds': 0, 'Steals': 0, 'Blocks': 0, 'Assists': 0, 'TOs': 0, 'Points': 0}
        }

    def simulate_possession(self, offense_team, defense_team):
        team_key = 'team1' if offense_team == self.team1 else 'team2'
        points = 0

        # Select shooter and defender
        shooter = self.select_player(offense_team, 'shooting')
        defender = self.select_player(defense_team, 'defense')

        # Determine if shot is made based on shot probability
        if random.random() < self.calculate_shot_probability(shooter, defender):
            # Successful shot
            points = 3 if self.is_three_pointer(shooter) else 2
            self.statistics[team_key]['FGM'] += 1
            self.statistics[team_key]['Points'] += points
        else:
            # Missed shot, consider rebound
            if random.random() < 0.3:  # Chance of offensive rebound
                rebounder = self.select_player(offense_team, 'rebounding')
                if random.random() < self.calculate_rebound_probability(rebounder, defense_team):
                    self.simulate_possession(offense_team, defense_team)  # Offensive rebound, new possession
                else:
                    self.statistics[team_key]['Rebounds'] += 1  # Defensive rebound, possession changes

        # Update statistics for the possession
        self.statistics[team_key]['FGA'] += 1
        self.statistics[team_key][
            'Assists'] += 1 if points > 0 and random.random() < 0.5 else 0  # Simplified assist logic
        self.statistics[team_key]['TOs'] += 1 if random.random() < 0.15 else 0  # Simplified turnover logic

    def simulate_game(self):
        for _ in range(100):  # Simulate 100 possessions per team
            self.simulate_possession(self.team1, self.team2)
            self.simulate_possession(self.team2, self.team1)

    def select_player(self, team, skill):
        # Select a player based on the specified skill
        # For simplicity, this is a random choice, but it can be based on player stats
        return random.choice(team.roster)

    def calculate_shot_probability(self, shooter, defender):
        # Calculate the probability of a successful shot
        # Simplified logic: based on shooter's rating and defender's rating
        return (shooter.current_rating - defender.current_rating) / 200 + 0.5

    def is_three_pointer(self, player):
        # Determine if the shot is a three-pointer
        # For simplicity, this is random, but can be based on player's position and skills
        return random.random() < 0.3

    def calculate_rebound_probability(self, rebounder, defense_team):
        # Calculate the probability of securing an offensive rebound
        # Simplified logic: based on rebounder's skill vs. defense team's overall rebounding skill
        defense_rebounding = sum([player.current_rating for player in defense_team.roster]) / len(defense_team.roster)
        return (rebounder.current_rating - defense_rebounding) / 200 + 0.5

    def display_match_summary(self):
        print(f"Match Summary: {self.team1.teamName} vs {self.team2.teamName}")
        for team_key, team_name in zip(['team1', 'team2'], [self.team1.teamName, self.team2.teamName]):
            stats = self.statistics[team_key]
            print(f"Team: {team_name}")
            print(f"  Points: {stats['Points']}, FGA: {stats['FGA']}, FGM: {stats['FGM']}")
            print(f"  Rebounds: {stats['Rebounds']}, Assists: {stats['Assists']}, TOs: {stats['TOs']}")