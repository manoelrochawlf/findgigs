import mysql.connector

def get_mariadb_connection():
    conn = mysql.connector.connect(
        host="147.93.32.9",   # externo
        port=3307,            # porta externa do MariaDB
        user="root",
        password="92679048#Komest",
        database="freelo_db"
    )
    return conn
