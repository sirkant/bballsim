import random
from player import Player


# TODO -1 - Fix breaking bug untraced yet
# TODO 0 - Fix weights issue

# TODO 1 - Make the number of FG more reasonable
# TODO 2 - Track 3pts -->
# TODO 3 - Add FG% -->
# TODO 4 - Add FT and fouls -->
# TODO 5 - Add +/- -->

class Match:
    def __init__(self, teams):
        self.teams = teams
        self.statistics = {
            teams[0].teamName: {'FGA': 0, 'FGM': 0, 'Rebounds': 0, 'Steals': 0,
                                'Blocks': 0, 'Assists': 0, 'TOs': 0, 'Points': 0, 'Minutes': 0},
            teams[1].teamName: {'FGA': 0, 'FGM': 0, 'Rebounds': 0, 'Steals': 0,
                                'Blocks': 0, 'Assists': 0, 'TOs': 0, 'Points': 0, 'Minutes': 0}
        }
        self.current_possession_team = 0  # Decide which team starts
        self.game_clock = 48 * 60  # Total game time in seconds
        self.scores = [0, 0]
        self.play_by_play = []
        self.play_by_play.append(
            f"Today we'll see a game between the {self.teams[0].teamName} and the {self.teams[1].teamName}")
        self.player_time_tracker = {team.teamName: {player.name: 0 for player in team.roster} for team in teams}

    def game_clock_run_time(self):
        # Write a function that picks a value for possession random
        # between the total 24 seconds that it could last and 4 seconds which is the minimum that could be played
        possession_clock = random.randint(12, 24)
        return possession_clock

    def run(self):
        self.play_by_play.append("Match starting")
        print(f"{self.teams} to debug later when I use the key")
        self.set_starting_lineup()
        # print("This match would've played and ended with a score here with a more basic function")

        while self.game_clock > 0:
            print(self.play_by_play[-1])
            # Time management
            possession_duration = self.game_clock_run_time()
            if self.game_clock - possession_duration < 0:  # Adjust the last possession time
                possession_duration = self.game_clock

            minutes = self.game_clock // 60
            seconds = self.game_clock % 60
            self.play_by_play.append(f"Current game clock: {minutes}:{seconds}")

            # Determine teams
            offense_team = self.teams[self.current_possession_team]
            defense_team = self.teams[1 - self.current_possession_team]
            self.play_by_play.append(
                f"Possession: {offense_team.teamName} (offense) vs {defense_team.teamName} (defense)")

            # Run possession
            self.sim_possession(offense_team, defense_team)

            # Update time tracker for players
            for team in self.teams:
                for player in team.starting_lineup.values():
                    if player:  # Check if player is not None
                        self.player_time_tracker[team.teamName][player.name] += possession_duration

            # Decrease time played by possession
            self.game_clock -= possession_duration  # Each possession takes 24 seconds
            self.current_possession_team = 1 - self.current_possession_team  # Switch possession

            # Implement fatigue
            # self.update_fatigue_for_all_players()  # If fatigue is a factor

        # Game ends
        self.play_by_play.append(
            "Game ends. Final scores: " + self.teams[0].teamName + " " + str(self.scores[0]) + " - " + self.teams[
                1].teamName + " " + str(self.scores[1]))
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
            print(f"Picking starting line-up for {team.teamName}")
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
                    print(f"Selected player: {selected_player.name} for position: {position}")

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
        print(team_key)
        points = 0
        # Determine which team is attacking and update the relevant index of the scores list
        attacking_team_index = 0 if offense_team.teamName == self.teams[0].teamName else 1

        self.play_by_play.append(
            f"{offense_team.teamName} on the attack, {defense_team.teamName} defending")  # Print offense_team object for debugging

        # Turnover block of code
        if random.random() < 1 / 15:  # Approximately 1 in 15 chance
            # Turnover occurs
            self.play_by_play.append(f"Turnover by {offense_team.teamName}")
            player = self.select_player(offense_team, 'TOs')
            player.match_stats['TOs'] += 1
            self.statistics[team_key]['TOs'] += 1

            # Credit a random defensive player with a steal
            defender = random.choice(list(defense_team.starting_lineup.values()))
            defender.match_stats['Steals'] += 1
            self.play_by_play.append(f"Steal by {defender.name} of {defense_team.teamName}")

            # Switch possession
            self.current_possession_team = 1 - self.current_possession_team
            return  # End the possession early due to the turnover

        # Select shooter and defender
        shooter = self.select_player(offense_team, 'shooting')
        defender = self.select_player(defense_team, 'defense')
        shot_type = self.select_shot_type(shooter)
        self.play_by_play.append(f"{shooter.name} is going to shoot a {shot_type} against {defender.name}")

        # Determine if shot is made based on shot probability
        if self.shot_outcome(shot_type, shooter, defender):
            self.play_by_play.append(f"{shooter.name} made the shot")
            # Successful shot
            points = 3 if shot_type == 'tp' else 2
            self.play_by_play.append(f"+ {points} for {team_key}")
            self.statistics[team_key]['FGM'] += 1
            self.statistics[team_key]['Points'] += points
            self.scores[attacking_team_index] += points
            shooter.match_stats['FGM'] += 1  # Update player's made shot
            shooter.match_stats['Points'] += points  # Update player's points
        else:
            # Missed shot, consider rebound
            self.play_by_play.append(f"Missed shot by {shooter.name}, fight for the rebound")
            print(f"Missed shot by {shooter.name}, fight for the rebound")
            rebounding_player_and_team = self.handle_rebound(offense_team, defense_team)
            print(f"Rebound by {rebounding_player_and_team[0].name} of {rebounding_player_and_team[1].teamName}")

            if offensive_rebounds < 3 and rebounding_player_and_team[1] == offense_team:
                self.sim_possession(offense_team, defense_team, offensive_rebounds + 1)
            else:
                self.current_possession_team = 1 - self.current_possession_team
                self.statistics[team_key]['Rebounds'] += 1
                rebounding_player_and_team[0].match_stats['Rebounds'] += 1

        # Update statistics for the possession
        self.statistics[team_key]['FGA'] += 1
        shooter.match_stats['FGA'] += 1
        print("Possession ended")

        if random.random() < 0.25:
            print("Assist to be added")
            # Increment team assist
            self.statistics[team_key]['Assists'] += 1
            print(f"Assist added to team {offense_team.teamName}, to determine who")
            # Weighted selection of assisting player based on passing rating
            assisting_player = self.determine_assisting_player(shooter=shooter, offense_team=offense_team)
            print(f"assist player is {assisting_player.name}")
            # Increment the assisting player's assist count
            assisting_player.match_stats['Assists'] += 1

        self.play_by_play.append(f"{team_key} statistics: {self.statistics[team_key]}")

    def update_fatigue_for_all_players(self):
        for team in self.teams:
            for player in team.roster:
                if player in team.starting_lineup.values():  # Player is on the court
                    player.adjust_ratings_for_fatigue(-0.005)  # Decrease by 0.5%
                else:
                    player.adjust_ratings_for_fatigue(0.002)  # Restore by 0.2% when benched
                # player.ensure_minimum_ratings()

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
        # weights = [player.ratings[attribute] for player in player_values if
        #            player and player.ratings and attribute in player.ratings]
        #
        # total_weight = sum(weights)
        # probabilities = [weight / total_weight for weight in weights]
        # selected_player = random.choices(player_values, weights=probabilities, k=1)[0]
        player_values = [player for player in team.starting_lineup.values()
                         if player and player.ratings and attribute in player.ratings]

        weights = [player.ratings[attribute] for player in player_values]

        selected_player = random.choices(player_values, weights=weights, k=1)[0]
        # print(f"Selected player: {selected_player.name} for attribute: {attribute}")

        return selected_player

    def handle_rebound(self, offensive_team, defensive_team):

        print(f"Called handle_rebound function with {offensive_team.teamName} and {defensive_team.teamName} as input")
        # Calculate rebounding strengths
        off_rebound_strength = offensive_team.calculate_rebound_rating(offensive_team)
        def_rebound_strength = defensive_team.calculate_rebound_rating(defensive_team)
        self.play_by_play.append(f"Strong battle to get the rebound")

        # Determine who gets the rebound
        total_strength = off_rebound_strength + def_rebound_strength
        if random.random() < (off_rebound_strength / total_strength):
            # Offensive team gets the rebound
            rebounding_team = offensive_team
        else:
            # Defensive team gets the rebound
            rebounding_team = defensive_team

        # Select the player who gets the rebound
        rebounding_player = random.choice(list(rebounding_team.starting_lineup.values()))
        self.play_by_play.append(f"Rebounded by {rebounding_player.name}")
        print(f"Rebounded by {rebounding_player.name}")
        return rebounding_player, rebounding_team

    def determine_assisting_player(self, offense_team, shooter):
        print("Running determine_assisting_player")
        print(f"About to pick an assist player from {offense_team.starting_lineup.values()}")

        candidates = [player for player in offense_team.starting_lineup.values() if
                      player is not None and player != shooter]
        weights = []

        for player in candidates:
            if player.ratings is not None:
                pss_rating = player.ratings.get('pss', 30)  # Use dict.get() to handle missing keys
                weights.append(pss_rating)
                if pss_rating == 30:
                    print(f"Player {player.name} does not have a 'pss' rating. Using default value.")
            else:
                print(f"Player {player.name} has no ratings data. Using default value.")
                weights.append(30)

        assisting_player = random.choices(candidates, weights=weights, k=1)[0]
        print(f"Successfully picked {assisting_player.name} as the assisting player")
        return assisting_player

    def finalize_game(self):
        print("Finalizing game")
        for team in self.teams:
            for player in team.roster:
                minutes, seconds = divmod(self.player_time_tracker[team.teamName][player.name], 60)
                player.match_stats['Minutes'] = f"{minutes}:{seconds:02d}"
                # self.play_by_play.append(f"{player.name} played {player.match_stats}")
                print(f"{player.name} stats: {player.match_stats}")
            stats = self.statistics[team.teamName]
            print(f"Team: {team.teamName}")
            for stat, value in stats.items():
                # self.play_by_play.append(f"{stat}: {value}")
                print(f"  {stat}: {value}")

        return self.statistics

    def test_matchup(self):
        for team in self.teams:
            print(f"Team: {team.teamName}")
            for player in team.players:
                print(f"  {player.name}: {player.rating}")
