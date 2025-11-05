import mysql.connector as sql
from sqlalchemy import create_engine
import pymysql
import time
from styles import BRIGHT_GREEN as BG, BRIGHT_RED as BR

# Creating a database
def create_database(mycon):
    cursor = mycon.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS vehiclemanagement")
    print(f"{BG}Database 'vehiclemanagement' ensured.")
    mycon.close()

def sql_connect():
    try:
        print(f"{BG}Trying initial connection...")
        mycon = sql.connect(host="localhost", user="root", password="123456")
        create_database(mycon)
    except sql.Error as e:
        print(f"{BR}🔥 SQL Error during initial connection: {e}")
        raise

    print(f"{BG}Connecting to DB vehiclemanagement...")
    mycon = sql.connect(host="localhost", user="root", password="123456", database="vehiclemanagement")
    print(f"{BG}DB PERMANENT connection established.")
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

# Remove this call from global scope and call in your main script instead:
# mycon, cursor, engine, engcon = sql_connect()
try:
    mycon, cursor, engine, engcon = sql_connect()
    print(f"{BG}Database connection ready....")
    time.sleep(3)
except Exception as e:
    print(f"{BR}Failed to connect to database: {e}")
    exit(1)