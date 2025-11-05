# 🚗 Vehicle Garage CLI Database Schema (v1.0)

This document serves as a concise, developer-friendly reference for the **data model** of the Garage CLI project. It maps all Primary Key (PK) / Foreign Key (FK) relationships, cardinality, and data deletion rules for quick reference.

---

## 🗺️ Big Picture: Entity Relationship Map

The core of the database revolves around **USERS** and the **SERVICE_BOOKINGS** table, which acts as a central link for vehicles, services, and mechanics.

```mermaid
flowchart LR
  U["USERS (PK: user_id)"]:::entity
  V["VEHICLES (PK: vehicle_no)\nFK: user_id → USERS.user_id"]:::entity
  Svc["SERVICES (PK: service_id)\nUNIQUE: service_name"]:::entity
  M["MECHANICS_INFO (PK: mechanic_id)"]:::entity
  SB["SERVICE_BOOKINGS (PK: booking_id)\nFKs: vehicle_no→VEHICLES, user_id→USERS,\nservice_id→SERVICES (NULL, ON DELETE SET NULL),\nmechanic_id→MECHANICS_INFO (NULL, ON DELETE SET NULL)"]:::link
  MA["MECHANIC_ASSIGNMENTS (PK: assignment_id)\nFKs: booking_id→SERVICE_BOOKINGS,\nmechanic_id→MECHANICS_INFO"]:::link
  I["INVOICES (PK: invoice_id)\nFKs: booking_id→SERVICE_BOOKINGS, user_id→USERS"]:::entity
  F["FEEDBACK (PK: feedback_id)\nFK: booking_id→SERVICE_BOOKINGS"]:::entity
  P["PARTS_INVENTORY (PK: part_id)\n(no FKs)"]:::entity

  V -->|belongs to| U
  SB -->|for vehicle| V
  SB -->|booked by| U
  SB -->|chooses| Svc
  SB -->|handled by| M

  MA -->|assignment for| SB
  MA -->|assigned to| M

  I -->|bill for| SB
  I -->|billed to| U

  F -->|feedback on| SB

  classDef entity fill:#eef6ff,stroke:#1f6feb,stroke-width:1px;
  classDef link fill:#ecfdf5,stroke:#059669,stroke-width:1px;


## 3) Table-by-Table (What it stores + Constraints)

**USERS**

**Purpose:** All people: Admins, Mechanics, Customers  
**PK:** `user_id` (INT AUTO_INCREMENT)  
**Important:** `username` **UNIQUE**, `email` **UNIQUE**, `user_role` ENUM('Admin','Mechanic','Customer') DEFAULT 'Customer'  
**Relationships:**  
- 1 User → N Vehicles  
- 1 User → N Service Bookings  
- 1 User → N Invoices  
**Example:** `(1, 'Ravi Sharma', 'ravi12', 'ravi@example.com', ..., 'Customer')`


**VEHICLES**

**Purpose:** Assets owned by users  
**PK:** `vehicle_no` (e.g., `GJ-01-AB-1234`)  
**FK:** `user_id → USERS.user_id` (**ON DELETE CASCADE**)  
**Why CASCADE?** Vehicle without owner = meaningless  
**Example:** `('GJ01AB1234', 'Hyundai', 'i20', 'Car', 2)`


**SERVICES**

**Purpose:** Menu of jobs (oil change, paint…)  
**PK:** `service_id`  
**Important:** `service_name` **UNIQUE**, `base_price`, `estimated_hours`, `category`  
**Referenced by:** `SERVICE_BOOKINGS.service_id` (**NULL, ON DELETE SET NULL**)  
**Why SET NULL?** Preserve booking history if a service is removed  
**Example:** `(10, 'Oil Change', '...', 799.00, 1.00, 0, 'Maintenance', 'Active')`


**MECHANICS_INFO**

**Purpose:** Mechanics roster  
**PK:** `mechanic_id`  
**Referenced by:**  
- `SERVICE_BOOKINGS.mechanic_id` (**NULL, ON DELETE SET NULL**)  
- `MECHANIC_ASSIGNMENTS.mechanic_id` (**ON DELETE CASCADE**)  
**Why SET NULL on bookings?** Keep job history if a mechanic leaves  
**Example:** `(5, 'Anil Mehta', 'Engine', '98xxxxxx12', 'anil@garage.com')`


**SERVICE_BOOKINGS (heart)**

**Purpose:** Each order/job  
**PK:** `booking_id`  
**FKs:**  
- `vehicle_no → VEHICLES.vehicle_no` (**ON DELETE CASCADE**)  
- `service_id → SERVICES.service_id` (**NULL, ON DELETE SET NULL**)  
- `user_id → USERS.user_id` (**ON DELETE CASCADE**)  
- `mechanic_id → MECHANICS_INFO.mechanic_id` (**NULL, ON DELETE SET NULL**)  
**Status:** ENUM('Pending','In Progress','Completed','Cancelled')  
**Note:** Has both `service_id` (FK) and `service_name` (snapshot) — good for audit/history  
**Example:** `(101, 'GJ01AB1234', 10, 2, 'Oil Change', 5, '2025-11-06', 'Pending')`


**MECHANIC_ASSIGNMENTS**

**Purpose:** Assignment history / reassignments / multi-helper  
**PK:** `assignment_id`  
**FKs:**  
- `booking_id → SERVICE_BOOKINGS.booking_id` (**ON DELETE CASCADE**)  
- `mechanic_id → MECHANICS_INFO.mechanic_id` (**ON DELETE CASCADE**)  
**Example:** `(9001, 101, 5, '2025-11-06 10:00:00')`


**INVOICES**

**Purpose:** Billing  
**PK:** `invoice_id`  
**FKs:** `booking_id → SERVICE_BOOKINGS.booking_id`, `user_id → USERS.user_id`  
**Typical:** 1 Booking → 1 Invoice (enforce with UNIQUE if required)  
**Example:** `(7001, 101, 2, 799.00, 'Pending', 'UPI', '2025-11-06 12:00:00')`


**FEEDBACK**

**Purpose:** Rating/comments per booking  
**PK:** `feedback_id`  
**FK:** `booking_id → SERVICE_BOOKINGS.booking_id`  
**Constraint:** `rating` CHECK 1..5 (MySQL 8+)  
**Typical:** 0/1 per booking (enforce with UNIQUE if needed)  
**Example:** `(3001, 101, 5, 'Great service!', '2025-11-07 09:00:00')`


**PARTS_INVENTORY**

**Purpose:** Spare parts stock  
**PK:** `part_id`  
**FKs:** none (standalone)  
**Extend later:** junction `booking_parts(booking_id FK, part_id FK, qty, price_at_use)`


---

## 4) Cardinality (Beginner English)

- One user → many vehicles  
- One user → many bookings  
- One vehicle → many bookings over time  
- One service → many bookings (if service deleted → old bookings keep `service_id = NULL`)  
- One mechanic → many bookings (if mechanic deleted → old bookings keep `mechanic_id = NULL`)  
- One booking → usually one invoice and zero/one feedback  
- One booking → many mechanic_assignments (timeline/history)

---

## 5) Delete Rules (Exact Effects)

- Delete **USER** → their **VEHICLES** and **BOOKINGS** cascade; dependent **INVOICES/FEEDBACK** tied to those bookings go too  
- Delete **VEHICLE** → its **BOOKINGS** (and their invoices/feedback/assignments) cascade  
- Delete **SERVICE** → `SERVICE_BOOKINGS.service_id` becomes **NULL** (history preserved)  
- Delete **MECHANIC** → `SERVICE_BOOKINGS.mechanic_id` becomes **NULL**; `MECHANIC_ASSIGNMENTS` for that mechanic **CASCADE delete**  
- Delete **BOOKING** → related **INVOICES**, **FEEDBACK**, and **MECHANIC_ASSIGNMENTS** are deleted

---

## 6) Why Some FKs Are NULLable

- `service_id` in bookings: service catalog item may be removed later → keep booking; set FK to **NULL** (but `service_name` snapshot remains).  
- `mechanic_id` in bookings: mechanic may leave → keep booking; set FK to **NULL**.
