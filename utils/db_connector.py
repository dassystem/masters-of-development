import sqlite3
# https://docs.python.org/3/library/sqlite3.html

class DbConnector():
    def __init__(self, path):
        self.__path = path
        self.__conn = None
        self.__cursor = None

    def connect(self):
        self.__conn = sqlite3.connect(self.__path)
        self.__cursor = self.__conn.cursor()
        self.__cursor.execute("CREATE TABLE IF NOT EXISTS leaderboard (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, score INTEGER NOT NULL)")
        self.__conn.commit()
    
    def execute(self, query):
        return self.__cursor.execute(query)

    def execute_with_parameter(self, query, parameter):
        return self.__cursor.execute(query, parameter)

    def execute_many(self, query, parameters):
        return self.__cursor.executemany(query, parameters)

    def get_cursor(self):
        return self.__cursor

    def commit(self):
        self.__conn.commit()

    def close_connection(self):
        self.__conn.close()
