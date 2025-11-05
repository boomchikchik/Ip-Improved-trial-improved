from db.queries_sql import mycon, cursor, engine

def create_tables():
    # users
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            username VARCHAR(50) UNIQUE NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            phone VARCHAR(15),
            address VARCHAR(225),
            city VARCHAR(50),
            state VARCHAR(50),
            password VARCHAR(100) NOT NULL,
            user_role ENUM('Admin','Mechanic','Customer') DEFAULT 'Customer',
            registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB
    """)

    # vehicles
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vehicles (
            vehicle_no VARCHAR(30) PRIMARY KEY,
            vehicle_brand VARCHAR(50),
            model VARCHAR(50),
            type ENUM('Car','Bike','Truck','Bus','Tractor','other') NOT NULL,
            user_id INT,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        ) ENGINE=InnoDB
    """)

    # services
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS services (
            service_id INT AUTO_INCREMENT PRIMARY KEY,
            service_name VARCHAR(100) UNIQUE NOT NULL,
            description TEXT,
            base_price DECIMAL(10,2) NOT NULL,
            estimated_hours DECIMAL(4,2),
            warranty_months INT DEFAULT 0,
            category ENUM('Maintenance','Repair','Inspection','Upgrade','Painting') NOT NULL,
            status ENUM('Active','Inactive') DEFAULT 'Active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB
    """)

    # --- CREATE mechanics_info BEFORE service_bookings ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mechanics_info (
            mechanic_id INT AUTO_INCREMENT PRIMARY KEY,
            full_name VARCHAR(100) NOT NULL,
            specialization VARCHAR(100),
            phone VARCHAR(15),
            email VARCHAR(100)
        ) ENGINE=InnoDB
    """)

    # service_bookings (note: service_id is NULLABLE because ON DELETE SET NULL is used)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS service_bookings (
            booking_id INT AUTO_INCREMENT PRIMARY KEY,
            vehicle_no VARCHAR(30) NOT NULL,
            service_id INT,                     -- nullable to allow ON DELETE SET NULL
            user_id INT NOT NULL,
            service_name VARCHAR(100) NOT NULL,
            mechanic_id INT NULL,
            booking_date DATE NOT NULL,
            status ENUM('Pending','In Progress','Completed','Cancelled') DEFAULT 'Pending',
            FOREIGN KEY (vehicle_no) REFERENCES vehicles(vehicle_no) ON DELETE CASCADE,
            FOREIGN KEY (service_id) REFERENCES services(service_id) ON DELETE SET NULL,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
            FOREIGN KEY (mechanic_id) REFERENCES mechanics_info(mechanic_id) ON DELETE SET NULL
        ) ENGINE=InnoDB
    """)

    # mechanic_assignments
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mechanic_assignments (
            assignment_id INT AUTO_INCREMENT PRIMARY KEY,
            booking_id INT,
            mechanic_id INT,
            assigned_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (booking_id) REFERENCES service_bookings(booking_id) ON DELETE CASCADE,
            FOREIGN KEY (mechanic_id) REFERENCES mechanics_info(mechanic_id) ON DELETE CASCADE
        ) ENGINE=InnoDB
    """)

    # invoices
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS invoices (
            invoice_id INT AUTO_INCREMENT PRIMARY KEY,
            booking_id INT,
            user_id INT,
            amount DECIMAL(10, 2) NOT NULL,
            payment_status ENUM('Unpaid','Pending','Paid','Failed') DEFAULT 'Unpaid',
            payment_method ENUM('Cash','Card','UPI','Bank Transfer') DEFAULT 'Cash',
            invoice_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (booking_id) REFERENCES service_bookings(booking_id),
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        ) ENGINE=InnoDB
    """)

    # parts_inventory
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS parts_inventory (
            part_id INT AUTO_INCREMENT PRIMARY KEY,
            part_name VARCHAR(100) NOT NULL,
            description TEXT,
            unit_price DECIMAL(10,2) NOT NULL,
            stock_quantity INT DEFAULT 0,
            supplier VARCHAR(100)
        ) ENGINE=InnoDB
    """)

    # feedback
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            feedback_id INT AUTO_INCREMENT PRIMARY KEY,
            booking_id INT,
            rating INT CHECK (rating BETWEEN 1 AND 5),
            comments VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (booking_id) REFERENCES service_bookings(booking_id)
        ) ENGINE=InnoDB
    """)

# #Creating all tables in the database
# def create_tables():
#     cursor.execute("""
#         CREATE TABLE IF NOT EXISTS users (
#             user_id INT AUTO_INCREMENT PRIMARY KEY,
#             name VARCHAR(100) NOT NULL,
#             username VARCHAR(50) UNIQUE NOT NULL,
#             email VARCHAR(100) UNIQUE NOT NULL,
#             phone VARCHAR(15),
#             address VARCHAR(225),
#             city VARCHAR(50),
#             state VARCHAR(50),
#             password VARCHAR(100) NOT NULL,
#             user_role ENUM('Admin','Mechanic','Customer') DEFAULT 'Customer',
#             registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#         )
#     """)

#     cursor.execute("""
#         CREATE TABLE IF NOT EXISTS vehicles (
#             vehicle_no VARCHAR(30) PRIMARY KEY,
#             vehicle_brand VARCHAR(50),
#             model VARCHAR(50),
#             type ENUM('Car','Bike','Truck','Bus','Tractor','other') NOT NULL,
#             user_id INT,
#             FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
#         )
#     """)

#     cursor.execute("""
#         CREATE TABLE IF NOT EXISTS services (
#             service_id INT AUTO_INCREMENT PRIMARY KEY,
#             service_name VARCHAR(100) UNIQUE NOT NULL,
#             description TEXT,
#             base_price DECIMAL(10,2) NOT NULL,
#             estimated_hours DECIMAL(4,2),
#             warranty_months INT DEFAULT 0,
#             category ENUM('Maintenance','Repair','Inspection','Upgrade','Painting') NOT NULL,
#             status ENUM('Active','Inactive') DEFAULT 'Active',
#             created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#         )
#     """)

#     cursor.execute("""
#         CREATE TABLE IF NOT EXISTS service_bookings (
#             booking_id INT AUTO_INCREMENT PRIMARY KEY,
#             vehicle_no VARCHAR(30),
#             service_id INT,
#             booking_date DATE NOT NULL,
#             status ENUM('Pending','In Progress','Completed','Cancelled') DEFAULT 'Pending',
#             FOREIGN KEY (vehicle_no) REFERENCES vehicles(vehicle_no) ON DELETE CASCADE,
#             FOREIGN KEY (service_id) REFERENCES services(service_id)
#         )
#     """)

#     cursor.execute("""
#         CREATE TABLE IF NOT EXISTS mechanics_info (
#             mechanic_id INT AUTO_INCREMENT PRIMARY KEY,
#             full_name VARCHAR(100) NOT NULL,
#             specialization VARCHAR(100),
#             phone VARCHAR(15),
#             email VARCHAR(100)
#         )
#     """)

#     cursor.execute("""
#         CREATE TABLE IF NOT EXISTS mechanic_assignments (
#             assignment_id INT AUTO_INCREMENT PRIMARY KEY,
#             booking_id INT,
#             mechanic_id INT,
#             assigned_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#             FOREIGN KEY (booking_id) REFERENCES service_bookings(booking_id) ON DELETE CASCADE,
#             FOREIGN KEY (mechanic_id) REFERENCES mechanics_info(mechanic_id) ON DELETE CASCADE
#         )
#     """)

#     cursor.execute("""
#         CREATE TABLE IF NOT EXISTS invoices (
#             invoice_id INT AUTO_INCREMENT PRIMARY KEY,
#             booking_id INT,
#             user_id INT,
#             amount DECIMAL(10, 2) NOT NULL,
#             payment_status ENUM('Unpaid','Pending','Paid','Failed') DEFAULT 'Unpaid',
#             payment_method ENUM('Cash','Card','UPI','Bank Transfer') DEFAULT 'Cash',
#             invoice_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#             FOREIGN KEY (booking_id) REFERENCES service_bookings(booking_id),
#             FOREIGN KEY (user_id) REFERENCES users(user_id)
#         )
#     """)

#     cursor.execute("""
#         CREATE TABLE IF NOT EXISTS parts_inventory (
#             part_id INT AUTO_INCREMENT PRIMARY KEY,
#             part_name VARCHAR(100) NOT NULL,
#             description TEXT,
#             unit_price DECIMAL(10,2) NOT NULL,
#             stock_quantity INT DEFAULT 0,
#             supplier VARCHAR(100)
#         )
#     """)

#     cursor.execute("""
#         CREATE TABLE IF NOT EXISTS feedback (
#             feedback_id INT AUTO_INCREMENT PRIMARY KEY,
#             booking_id INT,
#             rating INT CHECK (rating BETWEEN 1 AND 5),
#             comments VARCHAR(255),
#             created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#             FOREIGN KEY (booking_id) REFERENCES service_bookings(booking_id)
#         )
#     """)


