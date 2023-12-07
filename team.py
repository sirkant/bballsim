import random

class Team:
    def __init__(self, teamName, marketSize):
        self.teamName = teamName
        self.roster = []
        self.marketSize = marketSize
        self.teamHeight = 0
        self.scouting = 0
        self.coaching = 0
        self.medical = 0
        self.facilities = 0
        self.record = 0
        self.starting_lineup = []

    def addPlayer(self, player):
        if len(self.roster) < 15:
            self.roster.append(player)
            self.calculateTeamHeight()
        # else:
            # print("Roster is full. Cannot add more players.")

    def add_players_to_roster(self, players):
        for player in players:
            if player.tid == self.team_id:
                self.roster.append(player)

    def removePlayer(self, player):
        if player in self.roster:
            self.roster.remove(player)
            self.calculateTeamHeight()
        else:
            print("Player not found in roster.")

    def calculateTeamHeight(self):
        if not self.roster:
            self.teamHeight = 0
        else:
            total_height = sum(player.hgt for player in self.roster)
            self.teamHeight = total_height / len(self.roster)

    def updateMarketSize(self, newSize):
        self.marketSize = newSize

    def investInScouting(self, amount):
        self.scouting += amount

    def investInCoaching(self, amount):
        self.coaching += amount

    def investInMedical(self, amount):
        self.medical += amount

    def investInFacilities(self, amount):
        self.facilities += amount

    def displayTeamInfo(self):
        print(f"Team Name: {self.teamName}")
        print(f"Team Avg Height: {self.teamHeight}")
        print(f"Market Size: {self.marketSize}")
        print("Roster:")
        for player in self.roster:
            print(f" - {player.name}: {player.pos}")  # Use current_rating instead of rating
        print(f"Scouting: {self.scouting}, Coaching: {self.coaching}, Medical: {self.medical}, Facilities: {self.facilities}")

    def rebound_rating(self):
        rebound_rating = sum([player.current_rating for player in self.starting_lineup.values()]) / len(self.starting_lineup)
        return rebound_rating
    
    def calculate_defense_rating(self):
        """
        Calculate the defense rating of the team based on the average of the 'diq', 'drb', 'spd', 'hgt' ratings of the players.
        """
        total_rating = 0
        for player in self.starting_lineup.values():
            total_rating += (player.ratings['diq'] + player.ratings['drb'] + player.ratings['spd'] + player.ratings['hgt']) / 4
        return total_rating / len(self.roster)
    
    def calculate_rebound_rating(self, team):
        """
        Calculate the rebound rating of the team based on the average of the 'drb' and 'orb' ratings of the players.
        Add a bit of randomness to the rating.
        """
        total_rating = 0
        if team.starting_lineup is None:
            print(f"No starting lineup found for team {team.teamName}")
            return 0
        else:
            for player in team.starting_lineup.values():
                total_rating += (player.ratings['reb'] + player.ratings['hgt']) / 2
            total_rating /= len(team.starting_lineup)
            print(f"Team Rebounding Rating (drb): {total_rating}")

        # Add a random factor to the total rating
        random_factor = random.uniform(0.8, 1.2)  # Adjust the range as needed
        total_rating *= random_factor
        print(f"Rebound Rating for team {team.teamName}: {total_rating}")
        return total_rating
