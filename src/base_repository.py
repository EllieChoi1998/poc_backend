# base_repository.py
from database import get_db_connection

class BaseRepository:
    @staticmethod
    def open_db(dictionary=True):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=dictionary)
        return cursor, conn

    @staticmethod
    def close_db(conn, cursor):
        cursor.close()
        conn.close()

    class DB:
        def __init__(self, dictionary=True):
            self.dictionary = dictionary

        def __enter__(self):
            self.conn = get_db_connection()
            self.cursor = self.conn.cursor(dictionary=self.dictionary)
            return self.cursor, self.conn

        def __exit__(self, exc_type, exc_val, exc_tb):
            self.cursor.close()
            self.conn.close()
