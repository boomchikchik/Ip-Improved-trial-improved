# =====================================================
#  core/utils_cli.py - OPTIMIZED
# =====================================================
import pandas as pd
from tabulate import tabulate
from db.queries_sql import mycon, cursor, engcon
from styles import *

# ================== HELPERS ==================
def get_inputs(fields, prompt=":",required=False):
    """Get multiple inputs from user as a dictionary
    IT CREATES A TEMPRORARY MEMORY MAPPED DATA TO LATER INSERT INTO DB OR UPDATE
    I HAVE USED IT 10 TIMES IN PROJECT SAVING MANY LINES OF CODE """
    result = {}
    for field in fields:
        field_label = field.replace('_', ' ').title()
        user_input = input(f"{BRIGHT_YELLOW}{field_label} {prompt} ").strip()
        if user_input or not required:
            result[field] = user_input
        else:
            print(f"{BRIGHT_RED}❌ {field_label} is required./n {prompt}")
            return get_inputs(fields, prompt, required)
    return result

def pause(msg="Press Enter to continue..."):
    """Pause execution until user presses Enter"""
    try: 
        input(f"{DIM_YELLOW}{msg}")
    except EOFError: 
        pass

def fetch_df(sql, params=None):
    """Execute SQL query and return DataFrame"""
    try:
        return pd.read_sql(sql, con=engcon, params=params) if params else pd.read_sql(sql, con=engcon)
    except Exception as e:
        print(f"{BRIGHT_RED}DB Error: {e}")
        return pd.DataFrame()


def exec_sql(sql, params=None, success="✅ Done."):
    """Execute SQL command (INSERT/UPDATE/DELETE) with auto-commit"""
    try:
        cursor.execute(sql, params or ())
        mycon.commit()
        print(f"{BRIGHT_GREEN}{success}")
        return True
    except Exception as e:
        mycon.rollback()
        print(f"{BRIGHT_RED}DB Error: {e}")
        return False


def show_table(sql, params=None, title=None,hide_cols=None,df_=None):
    """Fetch and display query results in table format"""
    df = fetch_df(sql, params) if not df_ else df_
    if hide_cols:
        df = df.drop(columns=[c for c in hide_cols], errors='ignore')
    if df.empty:
        print(f"{BRIGHT_RED}No records found.")
        return False  
    else:
        if title: 
            print(f"\n{BRIGHT_CYAN}{title}")
        print(tabulate(df, headers="keys", tablefmt="fancy_grid", showindex=False))
    pause()
    return True


def menu_box(title, options, prompt="Select an option: "):
    """Display menu and get user choice"""
    print(f"\n{BRIGHT_YELLOW}{title}") if title else ""
    
    if isinstance(options, list):
        print(tabulate([[opt] for opt in options], tablefmt="fancy_grid"))
    elif isinstance(options, dict):
        print(tabulate([[f"{k}. {v}"] for k, v in options.items()], tablefmt="fancy_grid"))
    else:
        print(f"{BRIGHT_RED}Invalid options format.")
        return None
    
    return input(f"{BRIGHT_CYAN}{prompt}").strip()


def dashboard_loop(title, options):
    """Generic dashboard loop handler"""
    while True:
        choice = menu_box(title, {k: subtitle[0] for k, subtitle in options.items()})
        try: 
            func = options.get(choice)[1]
        except:
            func = False
        if func:
            func()
        elif choice == "0" or func is None:
            print(f"{BRIGHT_MAGENTA}↩ Back to previous menu.")
            break
        else:
            print(f"{BRIGHT_RED}❌ Invalid choice.")




# import bcrypt

# # Hash
# hashed = bcrypt.hashpw(b"mypassword", bcrypt.gensalt())

# # Check
# bcrypt.checkpw(b"mypassword", hashed)


# # core/utils_cli.py
# import pandas as pd
# from tabulate import tabulate
# from db.queries_sql import mycon, cursor, engcon
# from styles import *

# def pause(msg="Press Enter to continue..."):
#     try: input(f"{DIM_YELLOW}{msg}")
#     except EOFError: pass

# def fetch_df(sql, params=None):
#     try:
#         if params:
#             return pd.read_sql(sql, con=engcon, params=params)
#         else:
#             return pd.read_sql(sql, con=engcon)
#     except Exception as e:
#         print(f"{BRIGHT_RED}DB Error: {e}")
#         return pd.DataFrame()


# def exec_sql(sql, params=None, ok="✅ Done.",success=None):
#     if success is not None:
#         ok = success
#     try:
#         cursor.execute(sql, params or ())
#         mycon.commit()
#         print(f"{BRIGHT_GREEN}{ok}")
#         return True
#     except Exception as e:
#         mycon.rollback()
#         print(f"{BRIGHT_RED}DB Error: {e}")
#         return False

# def show_table(sql, params=None, title=None):
#     df = fetch_df(sql, params)
#     if df.empty:
#         print(f"{BRIGHT_RED}No records found.")
#     else:
#         if title: print(f"\n{BRIGHT_CYAN}{title}")
#         print(tabulate(df, headers="keys", tablefmt="fancy_grid", showindex=False))
#     pause()
#     return df

# def menu_box(title, options, prompt="Select an option: "): #--> k is 1,2,3... and v is title for menu [[]] each nested list is for new row
#     print(f"\n{BRIGHT_YELLOW}{title}")
#     if type(options) is list:
#         print(tabulate([[i] for i in options], tablefmt="fancy_grid"))
#     elif type(options) is dict:
#         print(tabulate([[k + ". " + v] for k, v in options.items()], tablefmt="fancy_grid"))
#     else:
#         print(f"{BRIGHT_RED}Invalid options format.")
#         return None
#     return input(f"{BRIGHT_CYAN}{prompt}").strip()

# def dashboard_loop(title, options):
#     while True:
#         choice = menu_box(title, {k: v[0] for k, v in options.items()})
#         func = options.get(choice, [None, None])[1]
#         if func:
#             func()
#         elif choice == "0" or func is None:
#             print(f"{BRIGHT_MAGENTA}↩ Back to previous menu.")
#             break
#         else:
#             print(f"{BRIGHT_RED}❌ Invalid choice.")
