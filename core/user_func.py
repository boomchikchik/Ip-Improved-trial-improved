# =====================================================
#  User LOGIN FUNCTIONS System 
# =====================================================
import pandas as pd
import stdiomask
from db.sql_connect import engcon
from styles import *
from core.utils_cli import *


def get_password():
    while True:
        pwd = stdiomask.getpass(f"{B_Y}Password (min 6 chars): ")
        if len(pwd) >= 6:
            if pwd == stdiomask.getpass(f"{B_Y}Confirm: "):
                return pwd
            print(f"{B_R}❌ Passwords don't match.")
        else:
            print(f"{B_R}❌ Too short.")

# ================== AUTH ==================
def user_registration():
    print("\n🧾 USER REGISTRATION")
    fields = ['Name', 'Email', 'Phone', 'Address', 'City', 'State', 'Username']
    data = get_inputs(fields, required=True)
    data['Password'] = get_password()
    exec_sql("""
        INSERT INTO users(name, email, phone, address, city, state, username, password, user_role)
        VALUES(%s,%s,%s,%s,%s,%s,%s,%s,'Customer')
    """, tuple(data.values()))
    print(f"{B_G}✅ Registration Successful!")


def user_login():
    print(f"{B_C}\n🔐 USER LOGIN")
    while True:
        username = input(f"{B_Y}Username/Email: ").strip()
        password = stdiomask.getpass(f"{B_Y}Password: ")
        if not (username and password):
            print(f"{B_R}❌ Both fields required.")
            if input(f"{D_Y}Retry/exit: ").lower() == "exit": 
                return
            continue
        df = fetch_df("SELECT * FROM users WHERE (username=%s OR email=%s) AND password=%s", (username, username, password))
        if not df.empty:
            print(f"{B_G}✅ Login successful!")
            user_dashboard(df)
            return
        print(f"{B_R}❌ Invalid credentials.")
        if input(f"{D_Y}Retry? (Enter/exit): ").lower() == "exit": 
            return

# ================== DASHBOARD ==================
def user_dashboard(df):
    uid = int(df.iloc[0]["user_id"])
    name = df.iloc[0]["name"]
    
    menu = {"0":("Logout", None),
        "1": ("Profile", lambda: manage_profile(uid)),
        "2": ("Add Vehicle", lambda: add_vehicle(uid)),
        "3": ("Manage Vehicles", lambda: manage_vehicles(uid)),
        "4": ("Browse Services", browse_services),
        "5": ("Book Service", lambda: book_service(uid)),
        "6": ("Make Payment", lambda: make_payment(uid)),
        "7": ("Booking History", lambda: show_user_view(uid, "history")),
        "8": ("Track Order", lambda: show_user_view(uid, "track")),
        "9": ("Cancel Order", lambda: cancel_order(uid)),
        "10": ("View Invoices", lambda: show_user_view(uid, "invoices")),
        "11": ("Payment Status", lambda: show_user_view(uid, "payments")),
        "12": ("Leave Feedback", lambda: leave_feedback(uid)),
    }
    
    print("WORKING")
    print(f"\n{B_C}===== USER DASHBOARD =====\n{B_G}Welcome, {name}!")
    dashboard_loop("User Menu", menu)

# ================== PROFILE ==================
def manage_profile(uid):
    df = fetch_df("SELECT name,email,phone,address,city,state,username FROM users WHERE user_id=%s", (uid,))
    series = df.squeeze() # Convert single-row DataFrame to Series
    print(f"\n{B_C}Your Profile:\n{df.iloc[0].to_string()}")
    action = menu_box("Profile Management", {"1": "Edit Profile", "2": "Change Password", "0": "Back"}, prompt="Select an option: ")
    # action = input(f"\n{B_Y}1=Edit Profile, 2=Change Password, 0=Back: ").strip()
    if action == "1":
        fields = ['name', 'email', 'phone', 'address', 'city', 'state']
        for field in fields:
            print(f"{B_Y} ENTER NEW {field.replace('_',' ').title()} (leave blank to keep current: [{series.get(field)}]): ")
            val = input().strip()
            if val:
                sql = f"UPDATE users SET {field}=%s WHERE user_id=%s"
                exec_sql(sql, (val, uid), success=f"{B_G}✅ Updated {field}.")

    elif action == "2":
        old = stdiomask.getpass("Old Password: ")
        if fetch_df("SELECT 1 FROM users WHERE user_id=%s AND password=%s", (uid, old)).empty:
            print(f"{B_R}❌ Wrong password.")
        else:
            pwd = get_password()
            exec_sql("UPDATE users SET password=%s WHERE user_id=%s", (pwd, uid), success=f"{B_G}✅ Password changed.")

# ================== VEHICLES ==================
def add_vehicle(uid):
    print(f"{B_C}\n🚗 ADD VEHICLE")
    data = [uid]
    for f in ['Vehicle No','Brand','Model','Type']:
        data_ = input(f"{B_Y}{f}: ").strip()
        data.append(data_)
    exec_sql("INSERT INTO vehicles(user_id,vehicle_no,vehicle_brand,model,type) VALUES(%s,%s,%s,%s,%s)",
             data, success=f"{B_G}✅ Vehicle added.")

def manage_vehicles(uid):
    df = fetch_df("SELECT vehicle_no,vehicle_brand,model,type FROM vehicles WHERE user_id=%s", (uid,))
    if df.empty:
        print(f"{B_R}No vehicles.")
        return
    print(f"\n{B_C}Your Vehicles:\n {df.to_string(index=False)}")
    vno = input(f"{B_Y}Vehicle No for (Edit/Delete): ").strip() 
    if not vno: 
        return
    if vno not in df['vehicle_no'].values:
        print(f"{B_R}❌ Vehicle not found."); return
    ch=menu_box('',options=["1.Edit Vehicle","2.Delete Vehicle"]) 
    if ch == "1":
        row = df[df['vehicle_no']==vno].iloc[0]
        brand = input(f"Brand [ {row.get('vehicle_brand')} ]: ").strip() or row.get('vehicle_brand')
        model = input(f"Model [ {row.get('model')} ]: ").strip() or row.get('model')
        vtype = input(f"Type [ {row.get('type')} ]: ").strip() or row.get('type')
        exec_sql("UPDATE vehicles SET vehicle_brand=%s,model=%s,type=%s WHERE vehicle_no=%s AND user_id=%s",
                 (brand, model, vtype, vno, uid), success=f"{B_G}✅ Updated.")
    elif ch == "2":
        exec_sql("DELETE FROM vehicles WHERE vehicle_no=%s AND user_id=%s", (vno, uid), success=f"{B_G}✅ Deleted.")
    else:
        print(f"{B_R}❌ Invalid choice."); return

# ================== SERVICES ==================
def browse_services():
    show_table("SELECT * FROM services WHERE status='Active' ORDER BY category",
               title=f"{B_C}Available Services",hide_cols=['created_at','status'])

def book_service(uid):
    vdf = fetch_df("SELECT vehicle_no,vehicle_brand,model FROM vehicles WHERE user_id=%s", (uid,))
    if vdf.empty:
        print(f"{B_R}Add vehicle first.")
        return
    print(f"\n{B_C}Your Vehicles:\n{vdf.to_string(index=False)}")
    vno = input(f"{B_Y}Vehicle No: ").strip()
    if not vno:
        return
    
    show_table("SELECT service_id,service_name,category,base_price FROM services WHERE status='Active'", title=f"{B_C}Services")
    sid = input(f"{B_Y}Service ID: ").strip()
    if sid:
        exec_sql(""" INSERT INTO service_bookings (vehicle_no, service_id, user_id, service_name, booking_date, status)
            SELECT %s, s.service_id, %s, s.service_name, NOW(), 'Pending'
            FROM services s
            WHERE s.service_id = %s""",
        (vno, uid, sid), success=f"{B_G}✅ Booked.")
        exec_sql("""INSERT INTO invoices (booking_id, user_id, amount, payment_status) SELECT LAST_INSERT_ID(), %s,
                  s.base_price,  'Unpaid' FROM services s WHERE s.service_id=%s""", 
            (uid, sid), success=f"{B_G}✅ Invoice created.")


# ================== PAYMENT ==================
def make_payment(uid):
    df = fetch_df("SELECT invoice_id,booking_id,amount FROM invoices WHERE user_id=%s AND payment_status='Unpaid'", (uid,))
    if df.empty:
        print(f"{B_R}No unpaid invoices.")
        return
    print(f"\n{B_C}Unpaid Invoices:\n{df.to_string(index=False)}")
    inv = input(f"{B_Y}Invoice ID: ").strip()
    if inv:
        method = input("Payment (Cash/Card/UPI/Bank) [Cash]: ").strip() or "Cash"
        exec_sql("UPDATE invoices SET payment_status='Pending',payment_method=%s WHERE invoice_id=%s", (method, inv), success=f"{B_G}✅ Payment done.")

# ================== VIEWS ==================
def show_user_view(uid, view_type):
    queries = {
    "history": ("SELECT booking_id, booking_date, status, vehicle_no, service_name "
        "FROM service_bookings "
        "WHERE user_id=%s "
        "ORDER BY booking_date DESC",
        "Booking History"
    ),
    "track": ("SELECT b.booking_id, b.status, b.service_name, "
        "COALESCE(m.full_name,'-') AS mechanic "
        "FROM service_bookings b "
        "LEFT JOIN mechanics_info m ON b.mechanic_id = m.mechanic_id "
        "WHERE b.user_id=%s "
        "ORDER BY b.booking_date DESC",
        "Order Tracking"
    ),
    "invoices": ("SELECT invoice_id, booking_id, amount, payment_status, "
        "payment_method, invoice_date "
        "FROM invoices "
        "WHERE user_id=%s "
        "ORDER BY invoice_date DESC",
        "Invoices"
    ),
    "payments": ("SELECT invoice_id, amount, payment_status "
        "FROM invoices "
        "WHERE user_id=%s "
        "ORDER BY invoice_id DESC",
        "Payment Status"
    )}
    show_table(queries[view_type][0], (uid,), f"{B_C}{queries[view_type][1]}")

def cancel_order(uid):
    c = show_table("SELECT booking_id, status, service_name, booking_date "
    "FROM service_bookings WHERE user_id=%s AND status IN ('Pending','In Progress')",(uid,), f"{B_C}Cancelable Orders")
    if c is False:
        return
    bid = input(f"{B_Y}Booking ID: ").strip()
    if bid:
        exec_sql("UPDATE service_bookings SET status='Cancelled' WHERE booking_id=%s", (bid,), success=f"{B_G}✅ Cancelled.")
        exec_sql("UPDATE invoices SET payment_status='Failed' WHERE booking_id=%s AND user_id=%s", (bid,uid))

def leave_feedback(uid):
    c = show_table("""SELECT b.booking_id, b.service_name, b.booking_date FROM service_bookings b LEFT JOIN feedback f ON f.booking_id = b.booking_id 
    WHERE b.user_id=%s AND b.status='Completed' AND f.booking_id IS NULL""",
    (uid,), f"{B_C}Pending Feedback")
    if c is False:
        return
    bid = input(f"{B_Y}Booking ID: ").strip()
    if bid:
        rating = int(input("Rating (1-5): ").strip() or 5)
        comment = input("Comments: ").strip()
        exec_sql("INSERT INTO feedback(booking_id,rating,comments,created_at) VALUES(%s,%s,%s,NOW())", (bid, rating, comment), success=f"{B_G}✅ Feedback submitted.")
