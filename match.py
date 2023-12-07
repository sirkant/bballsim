import random
from player import Player


class Match:
    def __init__(self, teams):
        self.teams = teams
        self.statistics = {
            teams[0].teamName: {'FGA': 0, 'FGM': 0, 'Rebounds': 0, 'Steals': 0,
                                'Blocks': 0, 'Assists': 0, 'TOs': 0, 'Points': 0},
            teams[1].teamName: {'FGA': 0, 'FGM': 0, 'Rebounds': 0, 'Steals': 0,
                                'Blocks': 0, 'Assists': 0, 'TOs': 0, 'Points': 0}
        }
        self.current_possession_team = 0  # Decide which team starts
        self.game_clock = 48 * 60  # Total game time in seconds
        self.scores = [0, 0]
        print(f"Match initialized with teams: {self.teams[0].teamName} and {self.teams[1].teamName}")

    def game_clock_run_time(self):
        # Write a function that picks a value for possession random
        # between the total 24 seconds that it could last and 4 seconds which is the minimum that could be played
        possession_clock = random.randint(10, 24)
        return possession_clock

    def run(self):
        print("Match.run starting")
        # print(f"{self.teams} to debug later when I use the key")
        for team in self.teams:
            self.set_starting_lineup()
        # print("This match would've played and ended with a score here with a more basic function")
        while self.game_clock > 0:
            minutes = self.game_clock // 60
            seconds = self.game_clock % 60
            print(f"Current game clock: {minutes}:{seconds}")
            offense_team = self.teams[self.current_possession_team]
            defense_team = self.teams[1 - self.current_possession_team]
            print(f"Possession: {offense_team.teamName} (offense) vs {defense_team.teamName} (defense)")
            self.sim_possession(offense_team, defense_team)
            self.game_clock -= self.game_clock_run_time()  # Each possession takes 24 seconds
            self.current_possession_team = 1 - self.current_possession_team  # Switch possession
            self.update_fatigue_for_all_players()  # If fatigue is a factor

        print("Match run complete")
        return self.finalize_game()

    def set_starting_lineup(self):
        """
        Sets the starting lineup for each team based on player ratings.
        Flexible for players with general positions like 'G', 'F', 'FC', 'GF'.
        """
        position_mappings = {
            'PG': ['PG', 'G'],
            'SG': ['SG', 'G', 'GF'],
            'SF': ['SF', 'F', 'GF'],
            'PF': ['PF', 'F', 'FC'],
            'C': ['C', 'FC']
        }

        for team in self.teams:
            # print(f"Picking starting line-up for {team.teamName}")
            team.starting_lineup = {pos: None for pos in position_mappings}
            available_players = team.roster[:]

            for position, eligible_positions in position_mappings.items():
                # Filter players by eligible positions for the specific role
                # print(f"Picking players for position: {position}")
                players_at_position = [player for player in available_players if player.pos in eligible_positions]
                # print(f"Players at position: {players_at_position}")

                # Sort players by overall rating
                players_at_position.sort(key=lambda x: x.ovr, reverse=True)
                # print(f"Sorting players at position: {players_at_position}")

                # Select the top player for this position
                if players_at_position:
                    selected_player = players_at_position[0]
                    team.starting_lineup[position] = selected_player
                    available_players.remove(selected_player)
                    # print(f"Selected player: {selected_player.name} for position: {position}")

            # If there are still positions without players, fill them with the highest-rated players regardless of position
            empty_positions = [pos for pos, player in team.starting_lineup.items() if player is None]
            if empty_positions:
                empty_positions.sort()  # Sort empty positions alphabetically
                for position in empty_positions:
                    for player in available_players:
                        if player not in team.starting_lineup.values():
                            team.starting_lineup[position] = player
                            available_players.remove(player)
                            break

    def select_shot_type(self, player):
        abilities_shot_type = {
            'dnk': player.ratings['dnk'],
            'ins': player.ratings['ins'],
            'fg': player.ratings['fg'],
            'tp': player.ratings['tp']
        }

        return max(abilities_shot_type, key=abilities_shot_type.get)

    def shot_outcome(self, shot_type, shooter, defender):
        shooting_ability = shooter.ratings[shot_type] / 100  # Normalize to 0-1 scale
        defense = defender.calculate_defense_rating() / 100  # Normalize to 0-1 scale

        base_probability = {"dnk": 0.55, "ins": 0.45, "fg": 0.4, "tp": 0.30}

        # Difficulty factor based on defense and shot type
        difficulty_factor = 1 - (shooting_ability - defense) * 0.1
        difficulty_factor = max(0.5, min(difficulty_factor, 1))  # Clamp between 0.5 and 1

        shot_probability = base_probability[shot_type] * shooting_ability * difficulty_factor
        shot_probability = min(shot_probability, 0.75)  # Cap maximum probability at 75%

        return random.random() < shot_probability

    def sim_possession(self, offense_team, defense_team, offensive_rebounds=0):

        # Start the possession
        team_key = offense_team.teamName
        points = 0
        # Determine which team is attacking and update the relevant index of the scores list
        attacking_team_index = 0 if offense_team.teamName == self.teams[0].teamName else 1

        print(
            f"{offense_team.teamName} on the attack, {defense_team.teamName} defending")  # Print offense_team object for debugging

        # Turnover block of code
        if random.random() < 1 / 15:  # Approximately 1 in 15 chance
            # Turnover occurs
            print(f"Turnover by {offense_team.teamName}")
            self.statistics[team_key]['TOs'] += 1

            # Credit a random defensive player with a steal
            defender = random.choice(list(defense_team.starting_lineup.values()))
            defender.match_stats['Steals'] += 1
            print(f"Steal by {defender.name} of {defense_team.teamName}")

            # Switch possession
            self.current_possession_team = 1 - self.current_possession_team
            return  # End the possession early due to the turnover

        # Select shooter and defender
        shooter = self.select_player(offense_team, 'shooting')
        defender = self.select_player(defense_team, 'defense')
        shot_type = self.select_shot_type(shooter)
        print(f"{shooter.name} is going to shoot a {shot_type} against {defender.name}")

        # Determine if shot is made based on shot probability
        if self.shot_outcome(shot_type, shooter, defender):
            print(f"{shooter.name} made the shot")
            # Successful shot
            points = 3 if shot_type == 'tp' else 2
            print(f"+ {points} for {team_key}")
            self.statistics[team_key]['FGM'] += 1
            self.statistics[team_key]['Points'] += points
            self.scores[attacking_team_index] += points
            shooter.match_stats['FGM'] += 1  # Update player's made shot
            shooter.match_stats['Points'] += points  # Update player's points
        else:
            # Missed shot, consider rebound
            print(f"Missed shot by {shooter.name}, fight for the rebound")
            rebounding_player_and_team = self.handle_rebound(offense_team, defense_team)

            if offensive_rebounds < 3 and rebounding_player_and_team[1] == offense_team:
                self.sim_possession(offense_team, defense_team, offensive_rebounds + 1)
            else:
                self.current_possession_team = 1 - self.current_possession_team
                self.statistics[team_key]['Rebounds'] += 1
                rebounding_player_and_team[0].match_stats['Rebounds'] += 1

        # Update statistics for the possession
        self.statistics[team_key]['FGA'] += 1
        shooter.match_stats['FGA'] += 1
        self.statistics[team_key][
            'Assists'] += 1 if points > 0 and random.random() < 0.5 else 0  # Simplified assist logic
        print(f"{team_key} statistics: {self.statistics[team_key]}")

    def update_fatigue_for_all_players(self):
        # Update player fatigue, if implemented
        pass

    def select_player(self, team, attribute):
        """Selects a player from the team based on a weighted probability related to the specified attribute.
        Args:
            team (Team): The team from which to select the player.
            attribute (str): The attribute to base the selection on.
        Returns:
            Player: The selected player.
        """
        # print(f"Select player function called with {team.teamName} and {attribute}")
        if attribute == 'shooting':
            shooting = ['ins', 'dnk', 'fg', 'tp', 'oiq']
            attribute = random.choice(shooting)
        else:
            defense = ['drb', 'diq']
            attribute = random.choice(defense)

        # print(f"About to pick a player from {team.starting_lineup.values()}")
        player_values = list(team.starting_lineup.values())
        # print(player_values)
        weights = [player.ratings[attribute] for player in player_values if
                   player and player.ratings and attribute in player.ratings]

        total_weight = sum(weights)
        probabilities = [weight / total_weight for weight in weights]
        selected_player = random.choices(player_values, weights=probabilities, k=1)[0]
        # print(f"Selected player: {selected_player.name} for attribute: {attribute}")

        return selected_player

    def handle_rebound(self, offensive_team, defensive_team):

        # print(f"Called handle_rebound function with {offensive_team.teamName} and {defensive_team.teamName} as input")
        # Calculate rebounding strengths
        off_rebound_strength = offensive_team.calculate_rebound_rating(offensive_team)
        def_rebound_strength = defensive_team.calculate_rebound_rating(defensive_team)
        # print(f"Strong battle to get the rebound")

        # Determine who gets the rebound
        total_strength = off_rebound_strength + def_rebound_strength
        if random.random() < (off_rebound_strength / total_strength):
            # Offensive team gets the rebound
            rebounding_team = offensive_team
        else:
            # Defensive team gets the rebound
            rebounding_team = defensive_team

        # Select the player who gets the rebound
        rebounding_player = random.choice(rebounding_team.roster)
        print(f"Rebounded by {rebounding_player.name}")
        return rebounding_player, rebounding_team

    def finalize_game(self):
        print("Finalizing game")
        for team in self.teams:
            for player in team.roster:
                print(f"{player.name} stats: {player.match_stats}")
            stats = self.statistics[team.teamName]
            print(f"Team: {team.teamName}")
            for stat, value in stats.items():
                print(f"  {stat}: {value}")

        return self.statistics

    def test_matchup(self):
        for team in self.teams:
            print(f"Team: {team.teamName}")
            for player in team.players:
                print(f"  {player.name}: {player.rating}")
