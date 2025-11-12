import pandas as pd
import stdiomask
from tabulate import tabulate
from db.sql_connect import engcon
from styles import *
from core.utils_cli import fetch_df, exec_sql, pause, menu_box



#================HELPER==================
def get_job(ch, mech_id):
        
    # Base SQL query
    base_sql = """SELECT sb.booking_id, sb.status, sb.booking_date, sb.service_name, 
                  v.vehicle_no, v.vehicle_brand, v.model 
                  FROM service_bookings sb 
                  JOIN vehicles v ON v.vehicle_no = sb.vehicle_no 
                  WHERE sb.mechanic_id = %s"""
    
    # Execute query based on filter choice
    if ch == "1":  # Completed
        sql = f"{base_sql} AND sb.status = 'Completed' ORDER BY sb.booking_date DESC"
        df = fetch_df(sql, (mech_id,))
        filter_name = "Completed"
    elif ch == "2":  # Active
        sql = f"{base_sql} AND sb.status IN ('Pending','In Progress') ORDER BY sb.booking_date DESC"
        df = fetch_df(sql, (mech_id,))
        filter_name = "Active"
    elif ch == "3":  # Cancelled
        sql = f"{base_sql} AND sb.status = 'Cancelled' ORDER BY sb.booking_date DESC"
        df = fetch_df(sql, (mech_id,))
        filter_name = "Cancelled"
    elif ch == "4":  # All
        sql = f"{base_sql} ORDER BY FIELD(sb.status,'In Progress','Pending','Completed','Cancelled'), sb.booking_date DESC"
        df = fetch_df(sql, (mech_id,))
        filter_name = "All"
    else:
        print(f"{B_R}❌ Invalid.")
        pause()
        return pd.DataFrame()  # Return empty DataFrame instead of None
    
    print(f"\n{B_C}📊 {filter_name} Jobs")
    print(tabulate(df, headers="keys", tablefmt="fancy_grid", showindex=False) if not df.empty else f"{B_R}❌ No jobs.")
    pause()
    return df

# ================== AUTH ==================

def mechanic_login():
    print(f"{B_C}🛠️ MECHANIC LOGIN")
    username = input(f"{B_Y}Username/Email: ").strip()
    password = stdiomask.getpass(f"{B_Y}Password: ")
    
    if not (username and password):
        print(f"{B_R}❌ Both required.")
        return
    
    df = fetch_df("""SELECT u.user_id,u.username,u.name,mi.mechanic_id,mi.full_name FROM users u
                     JOIN mechanics_info mi ON mi.email=u.email
                     WHERE (u.username=%s OR u.email=%s) AND u.password=%s AND u.user_role='Mechanic'""",
                  (username, username, password))
    
    if not df.empty:
        mech_id, name = df.iloc[0][["mechanic_id", "full_name"]]
        print(f"{B_G}✅ Welcome {name} (ID: {mech_id})!")
        mechanic_dashboard(pd.DataFrame([{"mechanic_id": mech_id, "full_name": name}]))
    else:
        print(f"{B_R}❌ Invalid credentials.")

# ================== DASHBOARD ==================
def mechanic_dashboard(logindf):
    mech_id = int(logindf.iloc[0]["mechanic_id"])
    name = str(logindf.iloc[0]["full_name"])
    
    while True:
        choice = menu_box(
            f"🛠️  MECHANIC DASHBOARD — {name} (ID: {mech_id})",
            ["1) ✏️ Edit Profile", "2) 🔍  Filter Jobs 🗂️", "3) 🔄 Update Job Status", "0) 🚪 Logout"],
            "Choice: "
        )
        if choice == "1":
            edit_profile(mech_id)
        elif choice == "2":
            filter_jobs(mech_id)
        elif choice == "3":
            update_status(mech_id)   
        elif choice == "0":
            print(f"{B_B}👋 Logged out!")
            break
        else:
            print(f"{B_R}Invalid.")
            pause()

# ================== PROFILE ==================
def edit_profile(mech_id):
    print(f"\n{B_C}🧾 Edit Profile")
    fields = {'1':('full_name','Name','mechanics_info'),
              '2':('specialization','Specialization','mechanics_info'),
              '3':('phone','Phone','both'),
              '4':('email','Email','both'),
              '5':('password','Password','users')}
    
    ch = menu_box("Edit Fields", ["1) Name", "2) Specialization", "3) Phone", "4) Email", "5) Password", "0) Back"], "Select: ")
    if ch not in fields:
        print(f"{B_R}❌ Invalid.")
        pause()
        return
    
    field, label, table = fields[ch]
    val = stdiomask.getpass(f"{B_Y}New {label}: ") if field=='password' else input(f"{B_Y}New {label}: ").strip()
    
    if not val:
        print(f"{B_R}❌ Empty.")
        pause()
        return
    
    if table in ('users','both'):
        exec_sql(f"UPDATE users SET {field}=%s WHERE email=(SELECT email FROM mechanics_info WHERE mechanic_id=%s)", (val, mech_id), success=f"✅ Updated in users.")
    if table in ('mechanics_info','both') and field != 'password':
        exec_sql(f"UPDATE mechanics_info SET {field}=%s WHERE mechanic_id=%s", (val, mech_id), success=f"✅ Updated in profile.")
    pause()

# ================== JOBS ==================

def update_status(mech_id):
    print(f"\n{B_C}🔄 Update Status")
    
    # Get active jobs
    df = get_job("2", mech_id)
    if df.empty:
        print(f"{B_R}❌ No active jobs.")
        pause()
        return
    
    # Get booking ID
    bid = input(f"\n{B_Y}Booking ID: ").strip()
    if not bid or int(bid) not in df['booking_id'].values:
        print(f"{B_R}❌ Invalid booking ID.")
        pause()
        return
    
    # Get current status
    current_status = df[df['booking_id'] == int(bid)]['status'].iloc[0]
    
    # Show available options
    print(f"\n{B_Y}Current Status: {current_status}")
    if current_status == "Pending":
        print("  1) In Progress")
        print("  2) Cancelled")
        options = ["In Progress", "Cancelled"]
    elif current_status == "In Progress":
        print("  1) Completed")
        print("  2) Cancelled")
        options = ["Completed", "Cancelled"]
    else:
        print(f"{B_R}❌ Cannot change status from '{current_status}'.")
        pause()
        return
    
    # Get user choice
    choice = input(f"\n{B_Y}Select (1-2): ").strip()
    if choice == "1":
        new_status = options[0]
    elif choice == "2":
        new_status = options[1]
    else:
        print(f"{B_R}❌ Invalid choice.")
        pause()
        return
    
    # Update database
    exec_sql("UPDATE service_bookings SET status=%s WHERE booking_id=%s", 
             (new_status, bid), 
             success=f"{B_G}✅ Updated to '{new_status}'.")
    pause()

def filter_jobs(mech_id):
    print(f"\n{B_C}🗂️ Filter Jobs")
    ch = menu_box("Filter", ["1) ✅ Completed", "2) ⏳ Active", "3) ❌ Cancelled", "4) 📋 All", "0) Back"], "Select: ")
    if ch == "0":
        return
    get_job(ch, mech_id)