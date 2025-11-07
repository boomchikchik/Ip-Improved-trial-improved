# =====================================================
#  Admin Management System - SIMPLE VERSION
# =====================================================

import pandas as pd
import stdiomask
from db.queries_sql import engcon
from styles import *
from core.graph import plot_from_sql
from core.utils_cli import fetch_df, exec_sql, show_table, pause, dashboard_loop,menu_box

# ================== HELPERS ==================
def get_inputs(fields, prompt=":"):
    result = {}
    for field in fields:
        field_label = field.replace('_', ' ').title()
        user_input = input(f"{BRIGHT_YELLOW}{field_label} {prompt} ").strip()
        if user_input:
            result[field] = user_input
    return result

# ================== AUTH ==================
def admin_login():
    while True:
        creds = get_inputs(['username', 'password']) 
        username = creds['username']
        password = creds['password']
        
        if not username or not password:
            print(f"{BRIGHT_RED}❌ Both required.")
            retry = input(f"{DIM_YELLOW}Retry/exit: ").lower()
            if retry == "exit":
                return
            continue
        
        sql = "SELECT * FROM users WHERE (username=%s OR email=%s) AND password=%s AND user_role='Admin'"
        df = fetch_df(sql, (username, username, password))
        
        if not df.empty:
            print(f"\n{BRIGHT_GREEN}✅ ADMIN LOGIN SUCCESSFUL!")
            admin_dashboard(df)
            return
        
        print(f"{BRIGHT_RED}❌ Invalid credentials.")

# ================== USERS ==================
def create_user():
    fields = ['name', 'username', 'email', 'phone', 'address', 'city', 'state', 'password']
    print("Enter Your Details as Asked Below: ")
    data = get_inputs(fields)
    role = input(f"{BRIGHT_YELLOW}Role (Admin/Mechanic/Customer): ").strip().title()
    
    if role.lower() == "mechanic":
        mechanic_sql = "INSERT INTO mechanics_info(full_name,email) VALUES(%s,%s)"
        exec_sql(mechanic_sql, (data['name'], data['email']), success=f"{BRIGHT_GREEN}✅ Mechanic profile created.")
    
    user_sql = "INSERT INTO users(name,username,email,phone,address,city,state,password,user_role,registered_at) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,NOW())"
    user_values = (data['name'], data['username'], data['email'], data['phone'], data['address'], data['city'], data['state'], data['password'], role)
    exec_sql(user_sql, user_values, success=f"{BRIGHT_GREEN}✅ User created.")

def list_users():
    print(f"{BRIGHT_CYAN}ENTER USER ID TO FILTER/ LEAVE BLANK FOR ALL")
    uid = input(f"{BRIGHT_YELLOW}blank for all/User ID: ").strip()
    
    if uid:
        sql = "SELECT * FROM users WHERE user_id=%s ORDER BY registered_at DESC"
        show_table(sql, (uid,), hide_cols=['password'], title=f"{BRIGHT_CYAN}User ID: {uid}")
    else:
        sql = "SELECT * FROM users ORDER BY registered_at DESC"
        show_table(sql, hide_cols=['password'], title=f"{BRIGHT_CYAN}Users")

def update_user():
    uid = input(f"{BRIGHT_YELLOW}User ID: ").strip()
    fields = ['name', 'username', 'email', 'phone', 'address', 'city', 'state', 'user_role']
    values = get_inputs(fields,"(Leave blank to skip: )")
    for field in values:
        val = values[field]
        sql = f"UPDATE users SET {field}=%s WHERE user_id=%s"
        exec_sql(sql, (val, uid), success=f"{BRIGHT_GREEN}✅ Updated {field}.")

def delete_user():
    uid = input(f"{BRIGHT_YELLOW}User ID: ").strip()
    sql = "DELETE FROM users WHERE user_id=%s"
    exec_sql(sql, (uid,), success=f"{BRIGHT_GREEN}✅ Deleted.")

def manage_role_pwd():
    uid = input(f"{BRIGHT_YELLOW}User ID: ").strip()
    action = menu_box('',options=["1) Change Role", "2) Reset Password"], prompt="Select an option: ")
    
    if action == "1":
        role = input(f"{BRIGHT_YELLOW}New role (Admin/Mechanic/Customer): ").strip().title()
        sql = "UPDATE users SET user_role=%s WHERE user_id=%s"
        exec_sql(sql, (role, uid), success=f"{BRIGHT_GREEN}✅ Role updated.")
        
        if role.lower() == "mechanic":
            info_sql = "SELECT name,email FROM users WHERE user_id=%s"
            info = fetch_df(info_sql, (uid,)).squeeze() # Squeeze converts single-row DataFrame to Series
            if not info.empty:
                name = info['name']
                email = info['email']
                mechanic_sql = "INSERT IGNORE INTO mechanics_info(full_name,email) VALUES(%s,%s)"
                exec_sql(mechanic_sql, (name, email), success=f"{BRIGHT_GREEN}✅ Mechanic profile created.")
    
    elif action == "2":
        pwd = stdiomask.getpass(f"{BRIGHT_YELLOW}New Password: ")
        sql = "UPDATE users SET password=%s WHERE user_id=%s"
        exec_sql(sql, (pwd, uid), success=f"{BRIGHT_GREEN}✅ Password reset.")

# ================== VEHICLES & SERVICES ==================
def add_vehicle():
    fields = ['user_id','vehicle_no', 'brand', 'model', 'type']
    data = get_inputs(fields)
    sql = "INSERT INTO vehicles VALUES(%s,%s,%s,%s,%s)"
    values = ( data['user_id'],data['vehicle_no'], data['brand'], data['model'], data['type'])
    exec_sql(sql, values, success=f"{BRIGHT_GREEN}✅ Vehicle added.")

def list_vehicles():
    choice = input(f"{BRIGHT_CYAN}SEARCH VEHICLE (leave blank for all): ").strip()
    user_id = input(f"{BRIGHT_YELLOW}Filter by User ID (leave blank for all): ").strip()
    if choice:
        sql = "select u.name,v.* from users u,vehicles v where vehicle_no = %s and (u.user_id=v.user_id)"
        show_table(sql, (choice,), title=f"{BRIGHT_CYAN}Vehicle No: {choice}")
    elif user_id:
        sql = "select u.name,v.* from users u,vehicles v where u.user_id = %s and (u.user_id=v.user_id)"
        show_table(sql, (user_id,), title=f"{BRIGHT_CYAN}User ID: {user_id}")
    else:
        sql = "select u.name,v.* from users u,vehicles v where (u.user_id=v.user_id) order by v.vehicle_no"
        show_table(sql, title=f"{BRIGHT_CYAN}Vehicles")

def add_service():
    fields = ['service_name', 'description', 'base_price', 'estimated_hours', 'warranty_months', 'category']
    data = get_inputs(fields)
    status = input(f"{BRIGHT_YELLOW}Status (Active/Inactive) [Active]: ").strip().title()
    if not status:
        status = "Active"
    
    sql = "INSERT INTO services VALUES(DEFAULT,%s,%s,%s,%s,%s,%s,%s,NOW())"
    values = (data['service_name'], data['description'], data['base_price'], data['estimated_hours'], data['warranty_months'], data['category'], status)
    exec_sql(sql, values, success=f"{BRIGHT_GREEN}✅ Service added.")

def list_services():
    # I CAN USE * HERE BUT TO KEEP CONSISTENT WITH OTHER LISTS, SPECIFY COLUMNS
    sql = "SELECT service_id,service_name,category,base_price,estimated_hours,warranty_months,status,created_at FROM services ORDER BY created_at DESC"
    show_table(sql, title=f"{BRIGHT_CYAN}Services")

def update_service():
    #FIELDS is KEY,VALUE pair of field name and label
    fields = ['service_name', 'description', 'base_price', 'estimated_hours', 'warranty_months', 'category', 'status']
    list_services()
    uid = input(f"{BRIGHT_YELLOW}Service ID: ").strip()
    choice = get_inputs(fields,"(Leave blank to skip: )")
    for field,val in choice.items():
        if not val: return
        sql = f"UPDATE services SET {field}=%s WHERE service_id=%s"
        exec_sql(sql, (val, uid), success=f"{BRIGHT_GREEN}✅ Updated {field}.")
    

# ================== MECHANICS ==================
def add_mechanic():
    fields = ['full_name', 'specialization', 'phone', 'email']
    data = get_inputs(fields)
    sql = "INSERT INTO mechanics_info VALUES(DEFAULT,%s,%s,%s,%s)"
    values = (data['full_name'], data['specialization'], data['phone'], data['email'])
    exec_sql(sql, values, success=f"{BRIGHT_GREEN}✅ Mechanic added.")

def list_mechanics():
    sql = "SELECT * FROM mechanics_info"
    show_table(sql, title=f"{BRIGHT_CYAN}Mechanics")

def assign_mechanic():
    sql = "SELECT b.booking_id, b.service_name, b.vehicle_no, b.booking_date FROM service_bookings b WHERE b.status='Pending' AND b.mechanic_id IS NULL ORDER BY b.booking_date"
    df = fetch_df(sql)
    
    if df.empty:
        print(f"{BRIGHT_RED}❌ No pending jobs.")
        return
    
    print(df.to_string(index=False))
    bid = input(f"{BRIGHT_YELLOW}Booking ID: ").strip()
    mid = input(f"{BRIGHT_YELLOW}Mechanic ID: ").strip()
    
    if bid and mid:
        update_sql = "UPDATE service_bookings SET mechanic_id=%s, status='In Progress' WHERE booking_id=%s AND mechanic_id IS NULL AND status='Pending'"
        exec_sql(update_sql, (mid, bid), success=f"{BRIGHT_GREEN}✅ Assigned & moved to In Progress.")

# ================== INVENTORY ==================
def add_part():
    fields = ['part_name', 'description', 'unit_price', 'stock_quantity', 'supplier']
    data = get_inputs(fields)
    sql = "INSERT INTO parts_inventory VALUES(DEFAULT,%s,%s,%s,%s,%s)"
    values = (data['part_name'], data['description'], data['unit_price'], data['stock_quantity'], data['supplier'])
    exec_sql(sql, values, success=f"{BRIGHT_GREEN}✅ Part added.")

def list_parts():
    part_name = input(f"{BRIGHT_YELLOW}Search Part Name (leave blank for all): ").strip()
    if part_name:
        sql = "SELECT * FROM parts_inventory WHERE part_name LIKE %s ORDER BY part_name"
        show_table(sql, (f"%{part_name}%",), title=f"{BRIGHT_CYAN}Parts matching: {part_name}")
        return
    sql = "SELECT * FROM parts_inventory ORDER BY part_name"
    show_table(sql, title=f"{BRIGHT_CYAN}Parts")

# ================== INVOICES ==================
def search_edit_invoice():
    inv = input(f"{BRIGHT_YELLOW}Invoice ID (blank=all): ").strip()
    if inv:
        sql = f"SELECT * FROM invoices WHERE invoice_id=%s"
        df = fetch_df(sql, (inv,))
        show_table(sql, (inv,))
    else:
        st = input(f"{BRIGHT_YELLOW}Status [Unpaid/Paid/Pending/Failed/All]: ").strip().title()
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
        print(f"{BRIGHT_RED}No invoices.")
        pause()
        return

    eid = input(f"{BRIGHT_YELLOW}Invoice ID to edit (blank=exit): ").strip()
    
    if eid:
        val = input(f"{BRIGHT_YELLOW}New status [Unpaid/Paid/Pending/Failed]: ").strip().title()
        if val in ('Unpaid', 'Paid', 'Pending', 'Failed'):
            sql = "UPDATE invoices SET payment_status=%s WHERE invoice_id=%s"
            exec_sql(sql, (val, eid), success=f"{BRIGHT_GREEN}✅ Updated.")

# ================== FEEDBACK & REPORTS ==================
def list_feedback():
    sql = "SELECT f.feedback_id,f.rating,f.comments,f.created_at,b.service_name,b.booking_id FROM feedback f JOIN service_bookings b ON f.booking_id=b.booking_id ORDER BY f.created_at DESC"
    show_table(sql, title=f"{BRIGHT_CYAN}Feedbacks")

def revenue_report():
    grp = input(f"{BRIGHT_YELLOW}Group (D/W/M): ").strip().upper()
    if not grp:
        grp = "D"
    
    sql_w = "SELECT YEAR(invoice_date) y,WEEK(invoice_date) w,SUM(amount) revenue FROM invoices GROUP BY y,w ORDER BY y DESC,w DESC"
    sql_m = "SELECT YEAR(invoice_date) y,MONTH(invoice_date) m,SUM(amount) revenue FROM invoices GROUP BY y,m ORDER BY y DESC,m DESC"
    sql_d = "SELECT DATE(invoice_date) d,SUM(amount) revenue FROM invoices GROUP BY d ORDER BY d DESC"
    
    if grp == 'W':
        show_table(sql_w, title=f"{BRIGHT_CYAN}Revenue Report")
    elif grp == 'M':
        show_table(sql_m, title=f"{BRIGHT_CYAN}Revenue Report")
    else:
        show_table(sql_d, title=f"{BRIGHT_CYAN}Revenue Report")

def revenue_graph():
    grp = input(f"{BRIGHT_YELLOW}Group (D/M): ").strip().upper()
    if not grp:
        grp = "D"
    
    if grp == 'M':
        sql = "SELECT DATE_FORMAT(invoice_date,'%Y-%m') AS period,SUM(amount) AS revenue FROM invoices GROUP BY period ORDER BY period"
        plot_from_sql(sql, "period", "revenue", "Monthly Revenue", "bar")
    else:
        sql = "SELECT DATE(invoice_date) AS period,SUM(amount) AS revenue FROM invoices GROUP BY period ORDER BY period"
        plot_from_sql(sql, "period", "revenue", "Daily Revenue", "barh")

def payment_graph():
    sql = "SELECT payment_status,COUNT(*) AS count FROM invoices GROUP BY payment_status"
    plot_from_sql(sql, "payment_status", "count", "Payment Status", "pie")

def service_revenue_graph():
    sql = "SELECT b.service_name,COALESCE(SUM(i.amount),0) AS total_revenue FROM service_bookings b LEFT JOIN invoices i ON b.booking_id=i.booking_id GROUP BY b.service_name ORDER BY total_revenue DESC LIMIT 10"
    plot_from_sql(sql, "service_name", "total_revenue", "Top Services by Revenue")

def service_bookings_graph():
    sql = "SELECT b.service_name,COUNT(*) AS total_bookings FROM service_bookings b GROUP BY b.service_name ORDER BY total_bookings DESC LIMIT 10"
    plot_from_sql(sql, "service_name", "total_bookings", "Top Services by Bookings")

# ================== DASHBOARD ==================
def admin_dashboard(df):
    name = df.iloc[0].get("name", "Admin")
    uid = str(df.iloc[0].get("user_id", ""))
    print(f"{BRIGHT_GREEN}Welcome, {name}!{RESET}")

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
    dashboard_loop(f"{BRIGHT_CYAN}🚘 ADMIN DASHBOARD (ID: {uid}){RESET}", main_menu)

# # =====================================================
# #  Admin Management System - ULTRA CONDENSED (~180 lines)
# # =====================================================

# import pandas as pd
# import stdiomask
# from db.queries_sql import engcon
# from styles import *
# from core.graph import plot_from_sql
# from core.utils_cli import fetch_df, exec_sql, show_table, pause, dashboard_loop

# # ================== HELPERS ==================
# def get_inputs(fields):
#     return {f: input(f"{BRIGHT_YELLOW}{f.replace('_', ' ').title()}: ").strip() for f in fields}

# def search_list(table, cols, search_fields=None, join="", order=""):
#     q = input(f"{DIM_YELLOW}Search (empty=all): ").strip()
#     if q and search_fields:
#         where = " OR ".join([f"{f} LIKE %s" for f in search_fields])
#         df = fetch_df(f"SELECT {cols} FROM {table} {join} WHERE {where} {order}", tuple([f"%{q}%"]*len(search_fields)))
#     else:
#         df = fetch_df(f"SELECT {cols} FROM {table} {join} {order}")
#     print(df.to_string(index=False) if not df.empty else f"{BRIGHT_RED}No records.")
#     pause()

# def safe_update(table, uid_col, allowed_fields):
#     uid = input(f"{BRIGHT_YELLOW}{uid_col.upper()}: ").strip()
#     print(f"{BRIGHT_YELLOW}Fields: " + ", ".join([f"{k}={v[1]}" for k,v in allowed_fields.items()]))
#     ch = input("Select: ").strip()
#     if ch not in allowed_fields:
#         print(f"{BRIGHT_RED}❌ Invalid.")
#         return
#     field, label = allowed_fields[ch]
#     val = input(f"{BRIGHT_YELLOW}New {label}: ").strip()
#     exec_sql(f"UPDATE {table} SET {field}=%s WHERE {uid_col}=%s", (val, uid), success=f"{BRIGHT_GREEN}✅ Updated.")

# # ================== AUTH ==================
# def admin_login():
#     while True:
#         creds = get_inputs(['username', 'password'])
#         if not all(creds.values()):
#             print(f"{BRIGHT_RED}❌ Both required.")
#             if input(f"{DIM_YELLOW}Retry/exit: ").lower() == "exit": return
#             continue
#         df = fetch_df(
#             "SELECT * FROM users "
#             "WHERE (username=%s OR email=%s) AND password=%s AND user_role='Admin'",
#             (creds['username'], creds['username'], creds['password'])
#         )
#         if not df.empty:
#             print(f"\n{BRIGHT_GREEN}✅ ADMIN LOGIN SUCCESSFUL!")
#             admin_dashboard(df)
#             return
#         print(f"{BRIGHT_RED}❌ Invalid credentials.")

# # ================== USERS ==================
# def create_user():
#     data = get_inputs(['name','username','email','phone','address','city','state','password'])
#     role = input(f"{BRIGHT_YELLOW}Role (Admin/Mechanic/Customer): ").strip().title()
#     if role.lower() == "mechanic":
#         exec_sql("INSERT INTO mechanics_info(full_name,email) VALUES(%s,%s)", (data['name'], data['email']), success=f"{BRIGHT_GREEN}✅ Mechanic profile created.")
#     exec_sql(
#         "INSERT INTO users(name,username,email,phone,address,city,state,password,user_role,registered_at) "
#         "VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,NOW())",
#         (*data.values(), role),
#         success=f"{BRIGHT_GREEN}✅ User created."
#     )

# def list_users():
#     print(f"{BRIGHT_CYAN}ENTER USER ID TO FILTER/ LEAVE BLANK FOR ALL")
#     uid = input(f"{BRIGHT_YELLOW}blank for all/User ID: ").strip()
#     if uid:
#         show_table("SELECT * FROM users WHERE user_id=%s ORDER BY registered_at DESC", (uid,), hide_cols=['password'], title=f"{BRIGHT_CYAN}User ID: {uid}")
#     else:
#         show_table("SELECT * FROM users ORDER BY registered_at DESC",hide_cols=['password'],title=f"{BRIGHT_CYAN}Users")
   

# def update_user():
#     uid = input(f"{BRIGHT_YELLOW}User ID: ").strip()
#     fields = ['name','username','email','phone','address','city','state','user_role']
#     values = {}
#     for i, field in enumerate(fields, start=1):
#         print(f"{BRIGHT_YELLOW} ENTER NEW {field.replace('_',' ').upper()} (leave blank to skip): ")
#         val = input().strip()
#         if val:
#             values[field] = val
#     for field, val in values.items():
#         exec_sql(f"UPDATE users SET {field}=%s WHERE user_id=%s", (val, uid), success=f"{BRIGHT_GREEN}✅ Updated {field}.")
    
# def delete_user():
#     uid = input(f"{BRIGHT_YELLOW}User ID: ").strip()
#     exec_sql("DELETE FROM users WHERE user_id=%s", (uid,), success=f"{BRIGHT_GREEN}✅ Deleted.")

# def manage_role_pwd():
#     uid = input(f"{BRIGHT_YELLOW}User ID: ").strip()
#     action = input(f"{BRIGHT_YELLOW}1=Change Role, 2=Reset Password: ").strip()
#     if action == "1":
#         role = input(f"{BRIGHT_YELLOW}New role (Admin/Mechanic/Customer): ").strip().title()
#         exec_sql("UPDATE users SET user_role=%s WHERE user_id=%s", (role, uid), success=f"{BRIGHT_GREEN}✅ Role updated.")
#         if role.lower() == "mechanic":
#             info = fetch_df("SELECT name,email FROM users WHERE user_id=%s", (uid,))
#             if not info.empty:
#                 exec_sql("INSERT IGNORE INTO mechanics_info(full_name,email) VALUES(%s,%s)", tuple(info.iloc[0]), success=f"{BRIGHT_GREEN}✅ Mechanic profile created.")
#     elif action == "2":
#         pwd = stdiomask.getpass(f"{BRIGHT_YELLOW}New Password: ")
#         exec_sql("UPDATE users SET password=%s WHERE user_id=%s", (pwd, uid), success=f"{BRIGHT_GREEN}✅ Password reset.")

# # ================== VEHICLES & SERVICES ==================
# def add_vehicle():
#     data = get_inputs(['vehicle_no','brand','model','type','user_id'])
#     exec_sql(
#         "INSERT INTO vehicles(vehicle_no,vehicle_brand,model,type,user_id) VALUES(%s,%s,%s,%s,%s)",
#         (data['vehicle_no'], data['brand'], data['model'], data['type'], data['user_id']),
#         success=f"{BRIGHT_GREEN}✅ Vehicle added."
#     )

# def list_vehicles():
#     search_list("vehicles v",
#         "v.vehicle_no,v.vehicle_brand,v.model,v.type,u.name AS owner",
#         ["v.vehicle_no","v.vehicle_brand","v.model","u.name"],
#         "JOIN users u ON v.user_id=u.user_id",
#         "ORDER BY v.vehicle_no")

# def add_service():
#     data = get_inputs(['service_name','description','base_price','estimated_hours','warranty_months','category'])
#     status = input(f"{BRIGHT_YELLOW}Status (Active/Inactive) [Active]: ").strip().title() or "Active"
#     exec_sql(
#         "INSERT INTO services(service_name,description,base_price,estimated_hours,warranty_months,category,status,created_at) "
#         "VALUES(%s,%s,%s,%s,%s,%s,%s,NOW())",
#         (*data.values(), status),
#         success=f"{BRIGHT_GREEN}✅ Service added."
#     )

# def list_services():
#     show_table(
#         "SELECT service_id,service_name,category,base_price,estimated_hours,warranty_months,status,created_at "
#         "FROM services ORDER BY created_at DESC",
#         title=f"{BRIGHT_CYAN}Services"
#     )

# def update_service():
#     safe_update("services", "service_id",
#         {'1':('service_name','Name'),'2':('description','Description'),'3':('base_price','Price'),
#          '4':('estimated_hours','Hours'),'5':('warranty_months','Warranty'),
#          '6':('category','Category'),'7':('status','Status')})

# # ================== MECHANICS ==================
# def add_mechanic():
#     data = get_inputs(['full_name','specialization','phone','email'])
#     exec_sql("INSERT INTO mechanics_info(full_name,specialization,phone,email) VALUES(%s,%s,%s,%s)",
#              tuple(data.values()), success=f"{BRIGHT_GREEN}✅ Mechanic added.")

# def list_mechanics():
#     show_table("SELECT mechanic_id,full_name,specialization,phone,email FROM mechanics_info",
#                title=f"{BRIGHT_CYAN}Mechanics")

# def assign_mechanic():
#     # Pending & unassigned — use service_bookings.mechanic_id directly
#     df = fetch_df(
#         "SELECT b.booking_id, b.service_name, b.vehicle_no, b.booking_date "
#         "FROM service_bookings b "
#         "WHERE b.status='Pending' AND b.mechanic_id IS NULL "
#         "ORDER BY b.booking_date"
#     )
#     if df.empty:
#         print(f"{BRIGHT_RED}❌ No pending jobs.")
#         return
#     print(df.to_string(index=False))
#     bid = input(f"{BRIGHT_YELLOW}Booking ID: ").strip()
#     mid = input(f"{BRIGHT_YELLOW}Mechanic ID: ").strip()
#     if bid and mid:
#         exec_sql(
#             "UPDATE service_bookings "
#             "SET mechanic_id=%s, status='In Progress' "
#             "WHERE booking_id=%s AND mechanic_id IS NULL AND status='Pending'",
#             (mid, bid),
#             success=f"{BRIGHT_GREEN}✅ Assigned & moved to In Progress."
#         )
#         # (Optional audit) also record in mechanic_assignments:
#         # exec_sql("INSERT INTO mechanic_assignments(booking_id,mechanic_id,assigned_date) VALUES(%s,%s,NOW())", (bid, mid))

# # ================== INVENTORY ==================
# def add_part():
#     data = get_inputs(['part_name','description','unit_price','stock_quantity','supplier'])
#     exec_sql(
#         "INSERT INTO parts_inventory(part_name,description,unit_price,stock_quantity,supplier) "
#         "VALUES(%s,%s,%s,%s,%s)",
#         tuple(data.values()),
#         success=f"{BRIGHT_GREEN}✅ Part added."
#     )

# def list_parts():
#     show_table("SELECT part_id,part_name,unit_price,stock_quantity,supplier FROM parts_inventory ORDER BY part_name",
#                title=f"{BRIGHT_CYAN}Parts")

# # ================== INVOICES ==================
# def search_edit_invoice():
#     inv = input(f"{BRIGHT_YELLOW}Invoice ID (blank=all): ").strip()
#     if inv:
#         df = fetch_df(
#             "SELECT invoice_id,booking_id,user_id,amount,payment_status,payment_method,invoice_date "
#             "FROM invoices WHERE invoice_id=%s", (inv,))
#     else:
#         st = input(f"{BRIGHT_YELLOW}Status [Unpaid/Paid/Pending/Failed/All]: ").strip().title() or "All"
#         df = fetch_df(
#             "SELECT invoice_id,booking_id,user_id,amount,payment_status,payment_method,invoice_date FROM invoices"
#             + ("" if st=="All" else " WHERE payment_status=%s") + " ORDER BY invoice_date DESC",
#             () if st=="All" else (st,))
#     if df.empty:
#         print(f"{BRIGHT_RED}No invoices."); pause(); return
#     print(df.to_string(index=False))
#     eid = input(f"{BRIGHT_YELLOW}Invoice ID to edit (blank=exit): ").strip()
#     if eid:
#         val = input(f"{BRIGHT_YELLOW}New status [Unpaid/Paid/Pending/Failed]: ").strip().title()
#         if val in ('Unpaid','Paid','Pending','Failed'):
#             exec_sql("UPDATE invoices SET payment_status=%s WHERE invoice_id=%s", (val, eid), success=f"{BRIGHT_GREEN}✅ Updated.")

# # ================== FEEDBACK & REPORTS ==================
# def list_feedback():
#     # use denormalized service_name from bookings; no services join
#     show_table(
#         "SELECT f.feedback_id,f.rating,f.comments,f.created_at,b.service_name,b.booking_id "
#         "FROM feedback f JOIN service_bookings b ON f.booking_id=b.booking_id "
#         "ORDER BY f.created_at DESC",
#         title=f"{BRIGHT_CYAN}Feedbacks"
#     )

# def revenue_report():
#     grp = input(f"{BRIGHT_YELLOW}Group (D/W/M): ").strip().upper() or "D"
#     queries = {
#         'W':"SELECT YEAR(invoice_date) y,WEEK(invoice_date) w,SUM(amount) revenue FROM invoices GROUP BY y,w ORDER BY y DESC,w DESC",
#         'M':"SELECT YEAR(invoice_date) y,MONTH(invoice_date) m,SUM(amount) revenue FROM invoices GROUP BY y,m ORDER BY y DESC,m DESC",
#         'D':"SELECT DATE(invoice_date) d,SUM(amount) revenue FROM invoices GROUP BY d ORDER BY d DESC"
#     }
#     show_table(queries.get(grp, queries['D']), title=f"{BRIGHT_CYAN}Revenue Report")

# def revenue_graph():
#     grp = input(f"{BRIGHT_YELLOW}Group (D/M): ").strip().upper() or "D"
#     if grp == 'M':
#         plot_from_sql(
#             "SELECT DATE_FORMAT(invoice_date,'%%Y-%%m') AS period,SUM(amount) AS revenue "
#             "FROM invoices GROUP BY period ORDER BY period",
#             "period","revenue","Monthly Revenue","bar"
#         )
#     else:
#         plot_from_sql(
#             "SELECT DATE(invoice_date) AS period,SUM(amount) AS revenue "
#             "FROM invoices GROUP BY period ORDER BY period",
#             "period","revenue","Daily Revenue","barh"
#         )

# def payment_graph():
#     plot_from_sql(
#         "SELECT payment_status,COUNT(*) AS count FROM invoices GROUP BY payment_status",
#         "payment_status","count","Payment Status","pie"
#     )

# def service_revenue_graph():
#     # aggregate by service_bookings.service_name directly
#     plot_from_sql(
#         "SELECT b.service_name,COALESCE(SUM(i.amount),0) AS total_revenue "
#         "FROM service_bookings b "
#         "LEFT JOIN invoices i ON b.booking_id=i.booking_id "
#         "GROUP BY b.service_name "
#         "ORDER BY total_revenue DESC LIMIT 10",
#         "service_name","total_revenue","Top Services by Revenue"
#     )

# def service_bookings_graph():
#     plot_from_sql(
#         "SELECT b.service_name,COUNT(*) AS total_bookings "
#         "FROM service_bookings b "
#         "GROUP BY b.service_name "
#         "ORDER BY total_bookings DESC LIMIT 10",
#         "service_name","total_bookings","Top Services by Bookings"
#     )

# # ================== DASHBOARD ==================
# def admin_dashboard(df):
#     name = df.iloc[0].get("name", "Admin")
#     uid = str(df.iloc[0].get("user_id", ""))
#     print(f"{BRIGHT_GREEN}Welcome, {name}!{RESET}")

#     menus = {
#         'users': {"1":("Create User",create_user),"2":("List Users",list_users),
#                   "3":("Update User",update_user),"4":("Delete User",delete_user),
#                   "5":("Manage Role/Password",manage_role_pwd),"0":("Back",None)},
#         'vehicles': {"1":("Add Vehicle",add_vehicle),"2":("List Vehicles",list_vehicles),
#                      "3":("Add Service",add_service),"4":("List Services",list_services),
#                      "5":("Update Service",update_service),"6":("Service Revenue",service_revenue_graph),
#                      "7":("Service Bookings",service_bookings_graph),"0":("Back",None)},
#         'mechanics': {"1":("Add Mechanic",add_mechanic),"2":("List Mechanics",list_mechanics),
#                       "3":("Assign to Booking",assign_mechanic),"0":("Back",None)},
#         'inventory': {"1":("Add Part",add_part),"2":("List Parts",list_parts),"0":("Back",None)},
#         'invoices': {"1":("Search/Edit Invoice",search_edit_invoice),"0":("Back",None)},
#         'feedback': {"1":("View Feedbacks",list_feedback),"0":("Back",None)},
#         'reports': {"1":("Revenue Report",revenue_report),"2":("Revenue Graph",revenue_graph),
#                     "3":("Payment Graph",payment_graph),"4":("Service Revenue",service_revenue_graph),"0":("Back",None)}
#     }

#     main_menu = {
#         "1":("Manage Users", lambda: dashboard_loop("👥 USERS", menus['users'])),
#         "2":("Vehicles & Services", lambda: dashboard_loop("🚗 VEHICLES", menus['vehicles'])),
#         "3":("Mechanics", lambda: dashboard_loop("🧰 MECHANICS", menus['mechanics'])),
#         "4":("Inventory", lambda: dashboard_loop("📦 INVENTORY", menus['inventory'])),
#         "5":("Invoices", lambda: dashboard_loop("🧾 INVOICES", menus['invoices'])),
#         "6":("Feedback", lambda: dashboard_loop("⭐ FEEDBACK", menus['feedback'])),
#         "7":("Reports", lambda: dashboard_loop("📈 REPORTS", menus['reports'])),
#         "0":("Logout", None)
#     }

#     dashboard_loop(f"{BRIGHT_CYAN}🚘 ADMIN DASHBOARD (ID: {uid}){RESET}", main_menu)
