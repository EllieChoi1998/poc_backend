import time
import mysql.connector
from mysql.connector import Error

def get_db_connection(retries=10, delay=3):
    for attempt in range(retries):
        try:
            conn = mysql.connector.connect(
                host="mysql_db",
                user="root",
                password="root",
                database="mydb"
            )
            return conn
        except Error as e:
            print(f"[DB 연결 재시도 중] 시도 {attempt + 1}/{retries} - {e}")
            time.sleep(delay)
    raise Exception("MySQL 서버에 연결할 수 없습니다.")
