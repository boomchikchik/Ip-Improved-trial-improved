# =====================================================
#  Admin Management System - SIMPLE VERSION
# =====================================================

import pandas as pd
import stdiomask
from db.sql_connect import engcon
from styles import *
from core.graph import plot_from_sql
from core.utils_cli import fetch_df, exec_sql, show_table, pause, dashboard_loop,menu_box,get_inputs


# ================== AUTH ==================
def admin_login():
    while True:
        creds = get_inputs(['username', 'password']) 
        username = creds['username']
        password = creds['password']
        
        if not username or not password:
            print(f"{B_R}❌ Both required.")
            retry = input(f"{D_Y}Retry/exit: ").lower()
            if retry == "exit":
                return
            continue
        
        sql = "SELECT * FROM users WHERE (username=%s OR email=%s) AND password=%s AND user_role='Admin'"
        df = fetch_df(sql, (username, username, password))
        
        if not df.empty:
            print(f"\n{B_G}✅ ADMIN LOGIN SUCCESSFUL!")
            admin_dashboard(df)
            return
        
        print(f"{B_R}❌ Invalid credentials.")

# ================== USERS ==================
def create_user():
    fields = ['name', 'username', 'email', 'phone', 'address', 'city', 'state', 'password']
    print("Enter Your Details as Asked Below: ")
    data = get_inputs(fields)
    role = input(f"{B_Y}Role (Admin/Mechanic/Customer): ").strip().title()
    
    if role.lower() == "mechanic":
        mechanic_sql = "INSERT INTO mechanics_info(full_name,email) VALUES(%s,%s)"
        exec_sql(mechanic_sql, (data['name'], data['email']), success=f"{B_G}✅ Mechanic profile created.")
    
    user_sql = "INSERT INTO users(name,username,email,phone,address,city,state,password,user_role,registered_at) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,NOW())"
    user_values = (data['name'], data['username'], data['email'], data['phone'], data['address'], data['city'], data['state'], data['password'], role)
    exec_sql(user_sql, user_values, success=f"{B_G}✅ User created.")

def list_users():
    print(f"{B_C}ENTER USER ID TO FILTER/ LEAVE BLANK FOR ALL")
    uid = input(f"{B_Y}blank for all/User ID: ").strip()
    
    if uid:
        sql = "SELECT * FROM users WHERE user_id=%s ORDER BY registered_at DESC"
        show_table(sql, (uid,), hide_cols=['password'], title=f"{B_C}User ID: {uid}")
    else:
        sql = "SELECT * FROM users ORDER BY registered_at DESC"
        show_table(sql, hide_cols=['password'], title=f"{B_C}Users")

def update_user():
    uid = input(f"{B_Y}User ID: ").strip()
    if not uid:
        print(f"{B_R}❌ Invalid.")
        return
    fields = ['name', 'username', 'email', 'phone', 'address', 'city', 'state']
    values = get_inputs(fields,"(Leave blank to skip: )")
    for field in values:
        val = values[field]
        sql = f"UPDATE users SET {field}=%s WHERE user_id=%s"
        exec_sql(sql, (val, uid), success=f"{B_G}✅ Updated {field}.")

def delete_user():
    uid = input(f"{B_Y}User ID: ").strip()
    if not uid:
        print(f"{B_R}❌ Invalid.")
        return
    sql = "DELETE FROM users WHERE user_id=%s"
    exec_sql(sql, (uid,), success=f"{B_G}✅ Deleted.")

def manage_role_pwd():
    uid = input(f"{B_Y}User ID: ").strip()
    action = menu_box('',options=["1) Change Role", "2) Reset Password"], prompt="Select an option: ")
    
    if action == "1":
        role = input(f"{B_Y}New role (Admin/Mechanic/Customer): ").strip().title()
        sql = "UPDATE users SET user_role=%s WHERE user_id=%s"
        exec_sql(sql, (role, uid), success=f"{B_G}✅ Role updated.")
        
        if role.lower() == "mechanic":
            info_sql = "SELECT name,email FROM users WHERE user_id=%s"
            info = fetch_df(info_sql, (uid,)).squeeze() # Squeeze converts single-row DataFrame to Series
            if not info.empty:
                name = info['name']
                email = info['email']
                mechanic_sql = "INSERT IGNORE INTO mechanics_info(full_name,email) VALUES(%s,%s)"
                exec_sql(mechanic_sql, (name, email), success=f"{B_G}✅ Mechanic profile created.")
    
    elif action == "2":
        pwd = stdiomask.getpass(f"{B_Y}New Password: ")
        sql = "UPDATE users SET password=%s WHERE user_id=%s"
        exec_sql(sql, (pwd, uid), success=f"{B_G}✅ Password reset.")

# ================== VEHICLES & SERVICES ==================
def add_vehicle():
    fields = ['user_id','vehicle_no', 'brand', 'model', 'type']
    data = get_inputs(fields)
    sql = "INSERT INTO vehicles VALUES(%s,%s,%s,%s,%s)"
    values = (data['user_id'],data['vehicle_no'], data['brand'], data['model'], data['type'])
    exec_sql(sql, values, success=f"{B_G}✅ Vehicle added.")

def list_vehicles():
    choice = input(f"{B_C}SEARCH VEHICLE (leave blank for all): ").strip()
    user_id = input(f"{B_Y}Filter by User ID (leave blank for all): ").strip()
    if choice:
        sql = "select u.name,v.* from users u,vehicles v where vehicle_no = %s and (u.user_id=v.user_id)"
        show_table(sql, (choice,), title=f"{B_C}Vehicle No: {choice}")
    elif user_id:
        sql = "select u.name,v.* from users u,vehicles v where u.user_id = %s and (u.user_id=v.user_id)"
        show_table(sql, (user_id,), title=f"{B_C}User ID: {user_id}")
    else:
        sql = "select u.name,v.* from users u,vehicles v where (u.user_id=v.user_id) order by v.vehicle_no"
        show_table(sql, title=f"{B_C}Vehicles")

def add_service():
    fields = ['service_name', 'description', 'base_price', 'estimated_hours', 'warranty_months', 'category']
    data = get_inputs(fields)
    status = input(f"{B_Y}Status (Active/Inactive) [Active]: ").strip().title()
    if not status:
        status = "Active"
    
    sql = "INSERT INTO services VALUES(DEFAULT,%s,%s,%s,%s,%s,%s,%s,NOW())"
    values = (data['service_name'], data['description'], data['base_price'], data['estimated_hours'], data['warranty_months'], data['category'], status)
    exec_sql(sql, values, success=f"{B_G}✅ Service added.")

def list_services():
    # I CAN USE * HERE BUT TO KEEP CONSISTENT WITH OTHER LISTS, SPECIFY COLUMNS
    sql = "SELECT service_id,service_name,category,base_price,estimated_hours,warranty_months,status,created_at FROM services ORDER BY created_at DESC"
    show_table(sql, title=f"{B_C}Services")

def update_service():
    #FIELDS is KEY,VALUE pair of field name and label
    fields = ['service_name', 'description', 'base_price', 'estimated_hours', 'warranty_months', 'category', 'status']
    list_services()
    uid = input(f"{B_Y}Service ID: ").strip()
    choice = get_inputs(fields,"(Leave blank to skip: )")
    for field,val in choice.items():
        if not val: return
        sql = f"UPDATE services SET {field}=%s WHERE service_id=%s"
        exec_sql(sql, (val, uid), success=f"{B_G}✅ Updated {field}.")
    

# ================== MECHANICS ==================
def add_mechanic():
    fields = ['full_name', 'specialization', 'phone', 'email']
    data = get_inputs(fields)
    sql = "INSERT INTO mechanics_info VALUES(DEFAULT,%s,%s,%s,%s)"
    values = (data['full_name'], data['specialization'], data['phone'], data['email'])
    exec_sql(sql, values, success=f"{B_G}✅ Mechanic added.")

def list_mechanics():
    sql = "SELECT * FROM mechanics_info"
    show_table(sql, title=f"{B_C}Mechanics")

def assign_mechanic():
    sql = "SELECT b.booking_id, b.service_name, b.vehicle_no, b.booking_date FROM service_bookings b WHERE b.status='Pending' AND b.mechanic_id IS NULL ORDER BY b.booking_date"
    df = fetch_df(sql)
    
    if df.empty:
        print(f"{B_R}❌ No pending jobs.")
        return
    
    print(df.to_string(index=False))
    bid = input(f"{B_Y}Booking ID: ").strip()
    mid = input(f"{B_Y}Mechanic ID: ").strip()
    
    if bid and mid:
        update_sql = "UPDATE service_bookings SET mechanic_id=%s, status='In Progress' WHERE booking_id=%s AND mechanic_id IS NULL AND status='Pending'"
        exec_sql(update_sql, (mid, bid), success=f"{B_G}✅ Assigned & moved to In Progress.")

# ================== INVENTORY ==================
def add_part():
    fields = ['part_name', 'description', 'unit_price', 'stock_quantity', 'supplier']
    data = get_inputs(fields)
    sql = "INSERT INTO parts_inventory VALUES(DEFAULT,%s,%s,%s,%s,%s)"
    values = (data['part_name'], data['description'], data['unit_price'], data['stock_quantity'], data['supplier'])
    exec_sql(sql, values, success=f"{B_G}✅ Part added.")

def list_parts():
    part_name = input(f"{B_Y}Search Part Name (leave blank for all): ").strip()
    if part_name:
        sql = "SELECT * FROM parts_inventory WHERE part_name LIKE %s ORDER BY part_name"
        show_table(sql, (f"%{part_name}%",), title=f"{B_C}Parts matching: {part_name}")
        return
    sql = "SELECT * FROM parts_inventory ORDER BY part_name"
    show_table(sql, title=f"{B_C}Parts")

# ================== INVOICES ==================
def search_edit_invoice():
    inv = input(f"{B_Y}Invoice ID (blank=all): ").strip()
    if inv:
        sql = f"SELECT * FROM invoices WHERE invoice_id=%s"
        df = fetch_df(sql, (inv,))
        show_table(sql, (inv,))
    else:
        st = input(f"{B_Y}Status [Unpaid/Paid/Pending/Failed/All]: ").strip().title()
        if not st:
            st = "All"
        
        if st == "All":
            sql = f"SELECT * FROM invoices ORDER BY invoice_date DESC"
            df = fetch_df(sql)
            show_table(sql)
        else:
            sql = f"SELECT * FROM invoices WHERE payment_status=%s ORDER BY invoice_date DESC"
            show_table(sql, (st,))
            df = fetch_df(sql, (st,))
        
    if df.empty:
        print(f"{B_R}No invoices.")
        pause()
        return

    eid = input(f"{B_Y}Invoice ID to edit (blank=exit): ").strip()
    
    if eid:
        val = input(f"{B_Y}New status [Unpaid/Paid/Pending/Failed]: ").strip().title()
        if val in ('Unpaid', 'Paid', 'Pending', 'Failed'):
            sql = "UPDATE invoices SET payment_status=%s WHERE invoice_id=%s"
            exec_sql(sql, (val, eid), success=f"{B_G}✅ Updated.")

# ================== FEEDBACK & REPORTS ==================
def list_feedback():
    sql = "SELECT f.feedback_id,f.rating,f.comments,f.created_at,b.service_name,b.booking_id FROM feedback f JOIN service_bookings b ON f.booking_id=b.booking_id ORDER BY f.created_at DESC"
    show_table(sql, title=f"{B_C}Feedbacks")

def revenue_report():
    grp = input(f"{B_Y}Group (D/W/M): ").strip().upper()
    if not grp:
        grp = "D"
    
    sql_w = "SELECT YEAR(invoice_date) y,WEEK(invoice_date) w,SUM(amount) revenue FROM invoices GROUP BY y,w ORDER BY y DESC,w DESC"
    sql_m = "SELECT YEAR(invoice_date) y,MONTH(invoice_date) m,SUM(amount) revenue FROM invoices GROUP BY y,m ORDER BY y DESC,m DESC"
    sql_d = "SELECT DATE(invoice_date) d,SUM(amount) revenue FROM invoices GROUP BY d ORDER BY d DESC"
    
    if grp == 'W':
        show_table(sql_w, title=f"{B_C}Revenue Report")
    elif grp == 'M':
        show_table(sql_m, title=f"{B_C}Revenue Report")
    else:
        show_table(sql_d, title=f"{B_C}Revenue Report")

def revenue_graph():
    grp = input(f"{B_Y}Group (D/M): ").strip().upper()
    if not grp:
        grp = "D"
    
    if grp == 'M':
        sql = "SELECT DATE_FORMAT(invoice_date,'%%Y-%%m') AS period,SUM(amount) AS revenue FROM invoices GROUP BY period ORDER BY period"
        plot_from_sql(sql, "period", "revenue", "Monthly Revenue", "bar")
    else:
        sql = "SELECT DATE(invoice_date) AS period,SUM(amount) AS revenue FROM invoices GROUP BY period ORDER BY period"
        plot_from_sql(sql, "period","revenue", "Daily Revenue", "line")

def payment_graph():
    sql = "SELECT payment_status,COUNT(*) AS count FROM invoices GROUP BY payment_status"
    plot_from_sql(sql, x_col="payment_status", y_col="count",title="Payment Status",kind="pie")

def service_revenue_graph():
    # COALESCE is a MySql function Return the first non-null value in a list:
    sql = "SELECT b.service_name,COALESCE(SUM(i.amount),0) AS total_revenue FROM service_bookings b LEFT JOIN invoices i ON b.booking_id=i.booking_id GROUP BY b.service_name ORDER BY total_revenue DESC LIMIT 10"
    plot_from_sql(sql, "service_name", "total_revenue", "Top Services by Revenue")

def service_bookings_graph():
    sql = "SELECT b.service_name,COUNT(*) AS total_bookings FROM service_bookings b GROUP BY b.service_name ORDER BY total_bookings DESC LIMIT 10"
    plot_from_sql(sql, "service_name", "total_bookings", "Top Services by Bookings")

# ================== DASHBOARD ==================
def admin_dashboard(df):
    name = df.iloc[0].get("name", default="Admin")
    uid = str(df.iloc[0].get("user_id", ""))
    print(f"{B_G}Welcome, {name}!")

    # Users menu
    users_menu = {
        "1": ("Create User", create_user),
        "2": ("List Users", list_users),
        "3": ("Update User", update_user),
        "4": ("Delete User", delete_user),
        "5": ("Manage Role/Password", manage_role_pwd),
        "0": ("Back", None)
    }
    
    # Vehicles menu
    vehicles_menu = {
        "1": ("Add Vehicle", add_vehicle),
        "2": ("List Vehicles", list_vehicles),
        "3": ("Add Service", add_service),
        "4": ("List Services", list_services),
        "5": ("Update Service", update_service),
        "6": ("Service Revenue", service_revenue_graph),
        "7": ("Service Bookings", service_bookings_graph),
        "0": ("Back", None)
    }
    
    # Mechanics menu
    mechanics_menu = {
                    "1": ("Add Mechanic", add_mechanic),
                    "2": ("List Mechanics", list_mechanics),
                    "3": ("Assign to Booking", assign_mechanic),
                    "0": ("Back", None)
                    }
    
    # Inventory menu
    inventory_menu = {
                    "1": ("Add Part", add_part),
                    "2": ("List Parts", list_parts),
                    "0": ("Back", None)
    }
    
    # Invoices menu
    invoices_menu = {
    "1": ("Search/Edit Invoice", search_edit_invoice),"0": ("Back", None)
    }
 
    # Feedback menu
    feedback_menu = {"1": ("View Feedbacks", list_feedback),"0": ("Back", None)}

    # Reports menu
    reports_menu = {
                   "1": ("Revenue Report", revenue_report),
                   "2": ("Revenue Graph", revenue_graph),
                   "3": ("Payment Graph", payment_graph),
                   "4": ("Service Revenue", service_revenue_graph),
                   "5": ("Service Bookings", service_bookings_graph),
                   "0": ("Back", None)
                    }

    # Main menu
    main_menu = {
              "1": ("Manage Users", lambda: dashboard_loop("👥 USERS", users_menu)),
              "2": ("Manage Vehicles", lambda: dashboard_loop("🚗 VEHICLES", vehicles_menu)),
                "3": ("Manage Mechanics", lambda: dashboard_loop("🧰 MECHANICS", mechanics_menu)),
                "4": ("Manage Inventory", lambda: dashboard_loop("📦 INVENTORY", inventory_menu)),
                "5": ("Manage Invoices", lambda: dashboard_loop("🧾 INVOICES", invoices_menu)),
                "6": ("View Feedback", lambda: dashboard_loop("⭐ FEEDBACK", feedback_menu)),
                "7": ("Generate Reports", lambda: dashboard_loop("📈 REPORTS", reports_menu)),
                "0": ("Logout", None)
    }
    dashboard_loop(f"{B_C}🚘 ADMIN DASHBOARD (ID: {uid}){RESET}", main_menu)


# def admin_dashboard(df):
#     name = df.iloc[0].get("name", "Admin")
#     uid = str(df.iloc[0].get("user_id", ""))
#     print(f"{B_G}Welcome, {name}!")

#     while True:
#         choice = menu_box(
#             f"🚘 ADMIN DASHBOARD (ID: {uid})",
#             ["1) 👥 Manage Users", "2) 🚗 Manage Vehicles", "3) 🧰 Manage Mechanics", 
#              "4) 📦 Manage Inventory", "5) 🧾 Manage Invoices", "6) ⭐ View Feedback", 
#              "7) 📈 Generate Reports", "0) 🚪 Logout"],
#             "Choice: "
#         )
        
#         if choice == "1":
#             manage_users()
#         elif choice == "2":
#             manage_vehicles()
#         elif choice == "3":
#             manage_mechanics()
#         elif choice == "4":
#             manage_inventory()
#         elif choice == "5":
#             manage_invoices()
#         elif choice == "6":
#             manage_feedback()
#         elif choice == "7":
#             generate_reports()
#         elif choice == "0":
#             print(f"{B_G}👋 Logged out!")
#             break
#         else:
#             print(f"{B_R}Invalid choice.")
#             pause()

# def manage_users():
#     while True:
#         choice = menu_box(
#             "👥 USERS",
#             ["1) Create User", "2) List Users", "3) Update User", 
#              "4) Delete User", "5) Manage Role/Password", "0) Back"],
#             "Choice: "
#         )
        
#         if choice == "1":
#             create_user()
#         elif choice == "2":
#             list_users()
#         elif choice == "3":
#             update_user()
#         elif choice == "4":
#             delete_user()
#         elif choice == "5":
#             manage_role_pwd()
#         elif choice == "0":
#             break
#         else:
#             print(f"{B_R}Invalid choice.")
#             pause()

# def manage_vehicles():
#     while True:
#         choice = menu_box(
#             "🚗 VEHICLES",
#             ["1) Add Vehicle", "2) List Vehicles", "3) Add Service", 
#              "4) List Services", "5) Update Service", "6) Service Revenue Graph", 
#              "7) Service Bookings Graph", "0) Back"],
#             "Choice: "
#         )
        
#         if choice == "1":
#             add_vehicle()
#         elif choice == "2":
#             list_vehicles()
#         elif choice == "3":
#             add_service()
#         elif choice == "4":
#             list_services()
#         elif choice == "5":
#             update_service()
#         elif choice == "6":
#             service_revenue_graph()
#         elif choice == "7":
#             service_bookings_graph()
#         elif choice == "0":
#             break
#         else:
#             print(f"{B_R}Invalid choice.")
#             pause()

# def manage_mechanics():
#     while True:
#         choice = menu_box(
#             "🧰 MECHANICS",
#             ["1) Add Mechanic", "2) List Mechanics", "3) Assign to Booking", "0) Back"],
#             "Choice: "
#         )
        
#         if choice == "1":
#             add_mechanic()
#         elif choice == "2":
#             list_mechanics()
#         elif choice == "3":
#             assign_mechanic()
#         elif choice == "0":
#             break
#         else:
#             print(f"{B_R}Invalid choice.")
#             pause()

# def manage_inventory():
#     while True:
#         choice = menu_box(
#             "📦 INVENTORY",
#             ["1) Add Part", "2) List Parts", "0) Back"],
#             "Choice: "
#         )
        
#         if choice == "1":
#             add_part()
#         elif choice == "2":
#             list_parts()
#         elif choice == "0":
#             break
#         else:
#             print(f"{B_R}Invalid choice.")
#             pause()

# def manage_invoices():
#     while True:
#         choice = menu_box(
#             "🧾 INVOICES",
#             ["1) Search/Edit Invoice", "0) Back"],
#             "Choice: "
#         )
        
#         if choice == "1":
#             search_edit_invoice()
#         elif choice == "0":
#             break
#         else:
#             print(f"{B_R}Invalid choice.")
#             pause()

# def manage_feedback():
#     while True:
#         choice = menu_box(
#             "⭐ FEEDBACK",
#             ["1) View Feedbacks", "0) Back"],
#             "Choice: "
#         )
        
#         if choice == "1":
#             list_feedback()
#         elif choice == "0":
#             break
#         else:
#             print(f"{B_R}Invalid choice.")
#             pause()

# def generate_reports():
#     while True:
#         choice = menu_box(
#             "📈 REPORTS",
#             ["1) Revenue Report", "2) Revenue Graph", "3) Payment Graph", 
#              "4) Service Revenue Graph", "5) Service Bookings Graph", "0) Back"],
#             "Choice: "
#         )
        
#         if choice == "1":
#             revenue_report()
#         elif choice == "2":
#             revenue_graph()
#         elif choice == "3":
#             payment_graph()
#         elif choice == "4":
#             service_revenue_graph()
#         elif choice == "5":
#             service_bookings_graph()
#         elif choice == "0":
#             break
#         else:
#             print(f"{B_R}Invalid choice.")
#             pause()