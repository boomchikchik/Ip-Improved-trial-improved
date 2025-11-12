# =====================================================
#  core/utils_cli.py - OPTIMIZED
# =====================================================
import pandas as pd
from tabulate import tabulate
from db.sql_connect import mycon, cursor, engcon
from styles import *

# ================== HELPERS ==================
def get_inputs(fields: list, prompt=":",required=False): # returns dict {field:input_value}
    """Get multiple inputs from user as a dictionary
    IT CREATES A TEMPRORARY MEMORY MAPPED DATA TO LATER INSERT INTO DB OR UPDATE
    I HAVE USED IT 10 TIMES IN PROJECT SAVING MANY LINES OF CODE """
    result = {}
    for field in fields:
        field_label = field.replace('_', ' ').title()
        user_input = input(f"{B_Y}{field_label} {prompt} ").strip()
        if user_input or not required:
            result[field] = user_input
        else:
            print(f"{B_R}❌ {field_label} is required./n {prompt}")
            return get_inputs(fields, prompt, required)
    return result

def pause(msg="Press Enter to continue..."):
    """Pause execution until user presses Enter"""
    try: 
        input(f"{D_Y}{msg}")
    except EOFError: 
        pass

def fetch_df(sql, params=None): #Helps Fetching DataFrame
    """Execute SQL query and return DataFrame"""
    try:
        return pd.read_sql(sql, con=engcon, params=params) if params else pd.read_sql(sql, con=engcon)
    except Exception as e:
        print(f"{B_R}DB Error: {e}")
        return pd.DataFrame()


def exec_sql(sql, params=None, success="✅ Done."):
    """Execute SQL command (INSERT/UPDATE/DELETE) with auto-commit"""
    try:
        cursor.execute(sql, params or ())
        mycon.commit()
        print(f"{B_G}{success}")
        return True
    except Exception as e:
        mycon.rollback()
        print(f"{B_R}DB Error: {e}")
        return False


def show_table(sql, params=None, title=None,hide_cols=None,df_=None):
    """Fetch and display query results in table format"""
    df = fetch_df(sql, params) if not df_ else df_
    if hide_cols:
        df = df.drop(columns=[c for c in hide_cols], errors='ignore')
    if df.empty:
        print(f"{B_R}No records found.")
        return False  
    else:
        if title: 
            print(f"\n{B_C}{title}")
        print(tabulate(df, headers="keys", tablefmt="fancy_grid", showindex=False))
    pause()
    return True


def menu_box(title, options, prompt="Select an option: "):
    """Display menu and get user choice"""
    print(f"\n{B_Y}{title}") if title else ""
    
    if isinstance(options, list):
        print(tabulate([[opt] for opt in options], tablefmt="fancy_grid"))
    elif isinstance(options, dict):
        print(tabulate([[f"{k}. {v}"] for k, v in options.items()], tablefmt="fancy_grid"))
    else:
        print(f"{B_R}Invalid options format.")
        return None
    
    return input(f"{B_C}{prompt}").strip()

#THE KEY DIFFERENCE BETWEEN dashboard_loop and menu_loop is that dashboard_loop KEEPS THE LOOP TILL USER WANTS TO EXIT WHILE menu_loop RETURNS AFTER ONE CHOICE and menu_loop CAN BE USED INSIDE DASHBOARD_LOOP, allowing nested menus.

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
            print(f"{B_M}↩ Back to previous menu.")
            break
        else:
            print(f"{B_R}❌ Invalid choice.")

#WORKING OF DASHBOARD_LOOP:
# 1. vo TITLE lega , option ek dict hogi jiska format hoga {1:("subtitle",function_to_call),2:("subtitle2",function2)}
# menu_box ko call karke title aur options dict se subtitle nikalke menu dikhayega
# k jo hai vo 1,2,3.. hoga aur subtitle poora tuple hai (subtitle,function_to_call) jaise hi user choice karega vo choice variable me ayega
# k ko as it is rehne denge aur tutple me se subtitle extract karke new dict ko menu_box ko denge jisse tabulate me sirf subtitle hi dikhai dega
# 2. YE UPAR KA SAB TAM JAM WHILE TRUE LOOP ME CHALEGA
# 3. menu_box ko call karke user se choice lega, user ka choice dashboard_loop me function ko milega options dict se
# 4. TRY BLOCK MEIN OPTIONS DICT SE FUNCTION NIKALEGA JO USER NE CHUNA HOGA
# 5. AGAR FUNCTION MILEGA TOH USSE CALL KAREGA
# 6. AGAR USER "0" CHUNEGA YA FUNCTION NONE HOGA TOH BACK MESSAGE DEKE LOOP BREAK KAREGA
# 7. AGAR KUCHH BHI INVALID HOGA TOH ERROR MESSAGE DEKE LOOP CONTINUE KAREGA


# FOR PASSWORD ENCRYPTION, NOT USED CURRENTLY
"""
import bcrypt

# Hash
hashed = bcrypt.hashpw(b"mypassword", bcrypt.gensalt())

# Check
bcrypt.checkpw(b"mypassword", hashed)"""


# # core/utils_cli.py
# import pandas as pd
# from tabulate import tabulate
# from db.queries_sql import mycon, cursor, engcon
# from styles import *

# def pause(msg="Press Enter to continue..."):
#     try: input(f"{D_Y}{msg}")
#     except EOFError: pass

# def fetch_df(sql, params=None):
#     try:
#         if params:
#             return pd.read_sql(sql, con=engcon, params=params)
#         else:
#             return pd.read_sql(sql, con=engcon)
#     except Exception as e:
#         print(f"{B_R}DB Error: {e}")
#         return pd.DataFrame()


# def exec_sql(sql, params=None, ok="✅ Done.",success=None):
#     if success is not None:
#         ok = success
#     try:
#         cursor.execute(sql, params or ())
#         mycon.commit()
#         print(f"{B_G}{ok}")
#         return True
#     except Exception as e:
#         mycon.rollback()
#         print(f"{B_R}DB Error: {e}")
#         return False

# def show_table(sql, params=None, title=None):
#     df = fetch_df(sql, params)
#     if df.empty:
#         print(f"{B_R}No records found.")
#     else:
#         if title: print(f"\n{B_C}{title}")
#         print(tabulate(df, headers="keys", tablefmt="fancy_grid", showindex=False))
#     pause()
#     return df

# def menu_box(title, options, prompt="Select an option: "): #--> k is 1,2,3... and v is title for menu [[]] each nested list is for new row
#     print(f"\n{B_Y}{title}")
#     if type(options) is list:
#         print(tabulate([[i] for i in options], tablefmt="fancy_grid"))
#     elif type(options) is dict:
#         print(tabulate([[k + ". " + v] for k, v in options.items()], tablefmt="fancy_grid"))
#     else:
#         print(f"{B_R}Invalid options format.")
#         return None
#     return input(f"{B_C}{prompt}").strip()

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
#             print(f"{B_R}❌ Invalid choice.")
