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

    def addPlayer(self, player):
        if len(self.roster) < 15:
            self.roster.append(player)
            self.calculateTeamHeight()
        else:
            print("Roster is full. Cannot add more players.")

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

    # def get_basketball_team_infos(url):
    #     try:
    #         response = requests.get(url)
    #         response.raise_for_status()  # Will raise an HTTPError if the HTTP request returned an unsuccessful status code
    #         data = response.json()
    #
    #         # Filter out only the basketball information
    #         basketball_team_infos = {team: info for team, info in data.items() if 'basketball' in info['jersey']}
    #         return basketball_team_infos
    #     except requests.RequestException as e:
    #         print(f"An error occurred while fetching the team information: {e}")
    #         return {}

    # Example usage:
    # team_infos_url = 'https://raw.githubusercontent.com/zengm-games/zengm/master/src/common/teamInfos.ts'
    # basketball_team_infos = get_basketball_team_infos(team_infos_url)
    # print(basketball_team_infos)