import sqlite3

class DatabaseManager:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.drop_and_create_tables()

    def create_tables(self):
        """ Create tables in the database """
        commands = [
            '''CREATE TABLE IF NOT EXISTS players (
                   id INTEGER PRIMARY KEY,
                   name TEXT NOT NULL,
                   pos TEXT,
                   hgt INTEGER,
                   weight INTEGER,
                   born_year INTEGER,
                   born_loc TEXT,
                   imgURL TEXT,
                   college TEXT,
                   injury_type TEXT,
                   injury_games_remaining INTEGER,
                   tid INTEGER  
               )''',
            '''CREATE TABLE IF NOT EXISTS ratings (
                   player_id INTEGER,
                   season INTEGER,
                   hgt INTEGER,
                   stre INTEGER,
                   spd INTEGER,
                   jmp INTEGER,
                   endu INTEGER,
                   ins INTEGER,
                   dnk INTEGER,
                   ft INTEGER,
                   fg INTEGER,
                   tp INTEGER,
                   diq INTEGER,
                   oiq INTEGER,
                   drb INTEGER,
                   pss INTEGER,
                   reb INTEGER,
                   FOREIGN KEY(player_id) REFERENCES players(id)
               )''',
            '''CREATE TABLE IF NOT EXISTS contracts (
                   player_id INTEGER,
                   amount REAL,
                   exp INTEGER,
                   rookie INTEGER,
                   FOREIGN KEY(player_id) REFERENCES players(id)
               )''',
            '''CREATE TABLE IF NOT EXISTS stats (
                   player_id INTEGER,
                   season INTEGER,
                   playoffs BOOLEAN,
                   gp INTEGER,
                   gs INTEGER,
                   min INTEGER,
                   fg INTEGER,
                   fga INTEGER,
                   tp INTEGER,
                   tpa INTEGER,
                   ft INTEGER,
                   fta INTEGER,
                   orb INTEGER,
                   drb INTEGER,
                   ast INTEGER,
                   stl INTEGER,
                   blk INTEGER,
                   tov INTEGER,
                   pf INTEGER,
                   pts INTEGER,
                   pm INTEGER,
                   pm100 REAL,
                   onOff100 REAL,
                   per REAL,
                   ortg INTEGER,
                   drtg INTEGER,
                   orbp REAL,
                   drbp REAL,
                   trbp REAL,
                   astp REAL,
                   stlp REAL,
                   blkp REAL,
                   usgp REAL,
                   ows REAL,
                   dws REAL,
                   obpm REAL,
                   dbpm REAL,
                   vorp REAL,
                   ewa REAL,
                   dd INTEGER,
                   td INTEGER,
                   FOREIGN KEY(player_id) REFERENCES players(id)
               )'''
            # Additional tables for draft, transactions, awards, etc. can be added similarly
        ]
        for command in commands:
            self.conn.execute(command)

    # Insert methods for each table need to be created here
    def insert_player(self, player):
        try:
            # Check if player already exists in the database
            cursor = self.conn.cursor()
            cursor.execute("SELECT id FROM players WHERE name = ? AND born_year = ?", (player.name, player.born_year))
            existing_player = cursor.fetchone()

            if existing_player:
                # print(f"Player {player.name} (born in {player.born_year}) already exists in the database.")
                return  # Skip inserting this player as they already exist

            # Handle missing 'injury' attribute
            injury_type = player.injury['type'] if hasattr(player, 'injury') else 'Healthy'
            injury_games_remaining = player.injury['gamesRemaining'] if hasattr(player, 'injury') else 0

            # Insert into players table
            with self.conn:
                self.conn.execute('''INSERT INTO players 
                                     (name, pos, hgt, weight, born_year, born_loc, imgURL, college, injury_type, injury_games_remaining, tid)
                                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                                  (player.name, player.pos, player.hgt, player.weight, player.born_year,
                                   player.born_loc, player.imgURL, player.college, injury_type,
                                   injury_games_remaining, player.tid))

                player_id = self.conn.execute('SELECT last_insert_rowid()').fetchone()[0]

                # Handle missing 'contract' attribute for free agents or draft prospects
                if player.contract:
                    self.conn.execute('''INSERT INTO contracts 
                                         (player_id, amount, exp, rookie)
                                         VALUES (?, ?, ?, ?)''',
                                      (player_id, player.contract.get('amount'), player.contract.get('exp'),
                                       int(player.contract.get('rookie', False))))

                # Insert into ratings table
                if hasattr(player, 'ratings'):
                    for rating in player.ratings:
                        self.conn.execute('''INSERT INTO ratings
                                             (player_id, season, hgt, stre, spd, jmp, endu, ins, dnk, ft, fg, tp, diq, oiq, drb, pss, reb)
                                             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                                          (player_id, rating.get('season', 0), rating['hgt'], rating['stre'],
                                           rating['spd'],
                                           rating['jmp'], rating['endu'], rating['ins'], rating['dnk'], rating['ft'],
                                           rating['fg'], rating['tp'], rating['diq'], rating['oiq'], rating['drb'],
                                           rating['pss'], rating['reb']))

                # Insert other related data (stats, etc.) similarly
                if hasattr(player, 'stats'):
                    for stat in player.stats:
                        self.conn.execute('''INSERT INTO stats 
                                            (player_id, season, playoffs, gp, gs, min, fg, fga, tp, tpa, ft, fta, orb, drb, ast, stl, blk, tov, pf, pts, pm, pm100, onOff100, per, ortg, drtg, orbp, drbp, trbp, astp, stlp, blkp, usgp, ows, dws, obpm, dbpm, vorp, ewa, dd, td)
                                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                                            (player_id, stat['season'], stat.get('playoffs', False), stat['gp'],
                                            stat['gs'], stat['min'], stat['fg'], stat['fga'], stat['tp'],
                                            stat['tpa'], stat['ft'], stat['fta'], stat['orb'], stat['drb'],
                                            stat['ast'], stat['stl'], stat['blk'], stat['tov'], stat['pf'],
                                            stat['pts'], stat['pm'], stat['pm100'], stat['onOff100'],
                                            stat['per'], stat['ortg'], stat['drtg'], stat['orbp'], stat['drbp'],
                                            stat['trbp'], stat['astp'], stat['stlp'], stat['blkp'], stat['usgp'],
                                            stat['ows'], stat['dws'], stat['obpm'], stat['dbpm'], stat['vorp'],
                                            stat['ewa'], stat['dd'], stat['td']))
                #print(f"Inserting player: {player.name}, Position: {player.pos}, Height: {player.hgt}, ...")

        except KeyError as e:
            pass
            # print(f"Error processing player: {player.name}. Missing key: {e}")
        except sqlite3.IntegrityError as e:
            print(f"Integrity error: {e}")
        except sqlite3.Error as e:
            print(f"SQLite error: {e}")
        except Exception as e:
            pass
            # print(f"General error: {e}")

    def get_all_players(self):
        """ Retrieve all players from the database """
        with self.conn:
            cursor = self.conn.execute('''SELECT * FROM players
                                          LEFT JOIN ratings ON players.id = ratings.player_id
                                          LEFT JOIN contracts ON players.id = contracts.player_id
                                          -- Additional JOINs for other tables
                                       ''')
            return cursor.fetchall()

    def get_players_by_team(self, team_id, season_year):
        """ Retrieve players from the database based on team ID """
        with self.conn:
            cursor = self.conn.execute('''SELECT * FROM players
                                          LEFT JOIN ratings ON players.id = ratings.player_id
                                          LEFT JOIN contracts ON players.id = contracts.player_id
                                          WHERE players.tid = ?
                                          -- Additional JOINs for other tables
                                       ''', (team_id,))
            return cursor.fetchall()

    def print_table_structure(self):
        """ Prints the structure of all tables in the database """
        cursor = self.conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        for table in tables:
            table_name = table[0]
            print(f"Structure of table '{table_name}':")
            cursor = self.conn.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            for col in columns:
                print(col)
            print("\n")

    def drop_and_create_tables(self):
        """ Drop existing tables and create new ones with updated structure """
        self.drop_tables()  # Drops all existing tables
        self.create_tables()  # Creates tables with updated structure

    def drop_tables(self):
        """ Drops all tables from the database """
        commands = [
            "DROP TABLE IF EXISTS players",
            "DROP TABLE IF EXISTS ratings",
            "DROP TABLE IF EXISTS contracts",
            "DROP TABLE IF EXISTS stats",
            # Include other tables if necessary
        ]
        for command in commands:
            self.conn.execute(command)
        print("All tables dropped.")

    def count_rows_in_table(self, table_name):
        """Counts the number of rows in a specified table."""
        with self.conn:
            cursor = self.conn.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            return count

    def get_player_ratings_from_db(self, player_id, season):
        with self.conn:
            try:
                cursor = self.conn.execute(f"""
                SELECT hgt, stre, spd, jmp, endu, ins, dnk, ft, fg, tp, diq, oiq, drb, pss, reb 
                FROM ratings 
                WHERE player_id = {player_id} AND season = {season}
                """)

                # Execute the query
                result = cursor.fetchone()

                if result:
                    # Convert the result into a dictionary
                    ratings = {
                        'hgt': result[0],
                        'stre': result[1],
                        'spd': result[2],
                        'jmp': result[3],
                        'endu': result[4],
                        'ins': result[5],
                        'dnk': result[6],
                        'ft': result[7],
                        'fg': result[8],
                        'tp': result[9],
                        'diq': result[10],
                        'oiq': result[11],
                        'drb': result[12],
                        'pss': result[13],
                        'reb': result[14]
                    }
                    return ratings
                else:
                    return None  # Or some default value or behavior
            except sqlite3.Error as e:
                print(f"Database error: {e}")
            except Exception as e:
                print(f"Exception in query: {e}")

    def close(self):
        """ Close the database connection """
        self.conn.close()

    def get_player_data(self, player_id):
        cursor = self.conn.cursor()

        query = "SELECT * FROM players WHERE id = ?"
        cursor.execute(query, (player_id,))
        row = cursor.fetchone()
        if row:
            keys = ['id', 'name', 'pos', 'hgt', 'weight', 'born_year', 'born_loc', 'imgURL', 'college', 'injury_type',
                    'injury_games_remaining', 'tid']
            return dict(zip(keys, row))
        else:
            return None

    def get_all_player_ids(self):
        """ Retrieve name and born year of all players from the database """
        with self.conn:
            cursor = self.conn.execute("SELECT name, born_year FROM players")
            return cursor.fetchall()

    def get_player_contract_from_db(self, player_id):
        with self.conn:
            try:
                cursor = self.conn.execute(f"""
                SELECT amount, exp, rookie 
                FROM contracts 
                WHERE player_id = {player_id}
                """)

                result = cursor.fetchone()

                if result:
                    contract = {
                        'amount': result[0],
                        'exp': result[1],
                        'rookie': result[2] == 1  # Assuming 1 for True, 0 for False
                    }
                    return contract
                else:
                    return None  # Or some default value or behavior
            except sqlite3.Error as e:
                print(f"Database error: {e}")
            except Exception as e:
                print(f"Exception in query: {e}")

