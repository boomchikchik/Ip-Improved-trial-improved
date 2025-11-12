import mysql.connector as sql
from sqlalchemy import create_engine
import pymysql
import time
from styles import B_G, B_R

# Creating a database
def create_database(mycon):
    cursor = mycon.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS vehiclemanagement")
    print(f"{B_G}Database 'vehiclemanagement' ensured.")
    mycon.close()

def sql_connect():
    try:
        print(f"{B_G}Trying initial connection...")
        mycon = sql.connect(host="localhost", user="root", password="123456")
        create_database(mycon)
    except sql.Error as e:
        print(f"{B_R}🔥 SQL Error during initial connection: {e}")
        raise

    print(f"{B_G}Connecting to DB vehiclemanagement...")
    mycon = sql.connect(host="localhost", user="root", password="123456", database="vehiclemanagement")
    print(f"{B_G}DB PERMANENT connection established.")
    cursor = mycon.cursor()
    mycon.autocommit = False  # You must commit/rollback manually
    mycon.start_transaction(isolation_level='READ COMMITTED')  # Prevents dirty reads

    engine = create_engine(
        "mysql+pymysql://root:123456@localhost/vehiclemanagement",
        isolation_level="AUTOCOMMIT",  # Needed for to_sql commits
        # echo=True  # Uncomment for debug logging SQL queries
    )
    engcon = engine.connect()
    return mycon, cursor, engine, engcon

try:
    mycon, cursor, engine, engcon = sql_connect()
    print(f"{B_G}Database connection ready....")
    time.sleep(3)
except Exception as e:
    print(f"{B_R}Failed to connect to database: {e}")
    exit(1)