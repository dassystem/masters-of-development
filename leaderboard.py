import utils.db_connector

MAX_ENTRIES = 5

class Leaderboard(object):
    def __init__(self):
        self.__db_connector = utils.db_connector.DbConnector("assets/leaderboard.db")
        self.__db_connector.connect()
        
        self.__init_board()
        
    def __init_board(self):
        c = self.__db_connector.get_cursor()
        
        self.__board = []
                
        for row in c.execute("SELECT id, name, score FROM leaderboard ORDER BY score DESC"):
            self.__board.append(LeaderboardEntry(row[0], row[1], row[2]))
    
    def get_count(self):
        return len(self.__board)
    
    def get_entries(self):
        return self.__board.copy()
    
    def add_entry(self, player_info):
        if len(self.__board) >= MAX_ENTRIES:
            last_entry = self.__board[-1]
            
            if last_entry.get_score() > player_info.get_score():
                return

            c = self.__db_connector.get_cursor()
            c.execute("DELETE FROM leaderboard WHERE id = :id", {"id": last_entry.get_id()})
            self.__db_connector.commit()
            
        self.__db_connector.execute_with_parameter("INSERT INTO leaderboard (name, score) VALUES (?,?)", player_info)
        self.__db_connector.commit()
        pk = self.__db_connector.get_cursor().lastrowid
        self.__board.append(LeaderboardEntry(pk, player_info[0], player_info[1]))
        self.__board.sort(key = lambda entry: entry.get_score(), reverse = True)
    
class LeaderboardEntry(object):
    def __init__(self, identity, name, score):
        self.__id = identity
        self.__name = name
        self.__score = score
        
    def get_id(self):
        return self.__id
    
    def get_name(self):
        return self.__name
        
    def get_score(self):
        return self.__score
