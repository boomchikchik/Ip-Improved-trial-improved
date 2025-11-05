import time
from core.admins import admin_login
from core.user_func import user_registration, user_login
from core.mechanic_func import mechanic_login
from db.tables_create import create_tables
from db.queries_sql import sql_connect
from styles import *
from core.utils_cli import pause, menu_box
import logging

def main_func():
    while True:
        logging.basicConfig(level=logging.CRITICAL)
        options = {
            "1": "🆕 New User",
            "2": "👤 Existing User",
            "3": "🧑‍💼 Admin Login",
            "4": "🛠️ Mechanic Login",
            "0": "🚪 Exit"
        }
        choice = menu_box("🚘 VEHICLE MANAGEMENT SYSTEM", options, "Enter choice: ")
        if choice == "1": 
            user_registration()
        elif choice == "2": 
            user_login()
        elif choice == "3": 
            admin_login()
        elif choice == "4": 
            mechanic_login()
        elif choice == "0":
            print(f"{BRIGHT_CYAN}👋 Thank you for using the system!")
            break
        else:
            print(f"{BRIGHT_RED}❌ Invalid choice.")
            pause()
if __name__ == '__main__':
    print(f"{BRIGHT_CYAN}Initializing system...")
    time.sleep(2)
    sql_connect()
    time.sleep(2)
    create_tables()
    time.sleep(1.5)
    main_func()
    print(f"{BRIGHT_CYAN}System shutdown. Goodbye!")