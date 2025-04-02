import mysql.connector

def get_db_connection():
    conn = mysql.connector.connect(
        host="mysql_db", 
        user="root", 
        password="root", 
        database="mydb"
    )
    return conn