from database import get_db_connection
from typing import Optional, Dict, Any, List

class DocumentRepository:
    @staticmethod
    def open_db():
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        return cursor, conn
    
    @staticmethod
    def close_db(conn, cursor):
        cursor.close()
        conn.close()

    