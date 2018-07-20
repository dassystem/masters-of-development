import sqlite3
# https://docs.python.org/3/library/sqlite3.html


class DbConnector:
    def __init__(self, path: str):
        self.__path: str = path
        self.__conn = None
        self.__cursor: sqlite3.Cursor = None

    def connect(self) -> None:
        self.__conn = sqlite3.connect(self.__path)
        self.__cursor = self.__conn.cursor()
        self.__cursor.execute(
            "CREATE TABLE IF NOT EXISTS leaderboard (" +
            "  id INTEGER PRIMARY KEY AUTOINCREMENT," +
            "  name TEXT NOT NULL," +
            "  score INTEGER NOT NULL" +
            ")"
        )
        self.__conn.commit()

    def execute(self, query: str) -> sqlite3.Cursor:
        return self.__cursor.execute(query)

    def execute_with_parameter(self, query: str, parameter: tuple) -> sqlite3.Cursor:
        return self.__cursor.execute(query, parameter)

    def execute_many(self, query: str, parameters: tuple) -> sqlite3.Cursor:
        return self.__cursor.executemany(query, parameters)

    def get_cursor(self) -> sqlite3.Cursor:
        return self.__cursor

    def commit(self) -> None:
        self.__conn.commit()

    def close_connection(self) -> None:
        self.__conn.close()
