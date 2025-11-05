# 🚗 Vehicle Garage CLI Database Schema (v1.0)

This document serves as a concise, developer-friendly reference for the **data model** of the Garage CLI project. It maps all Primary Key (PK) / Foreign Key (FK) relationships, cardinality, and data deletion rules for quick reference.

---

## 🗺️ Big Picture: Entity Relationship Map

The core of the database revolves around **USERS** and the **SERVICE_BOOKINGS** table, which acts as a central link for vehicles, services, and mechanics.

---

## 3) 🛠️ Table-by-Table: Structure and Constraints

This section provides a detailed breakdown of each table's purpose, keys, and important constraints.

### USERS
* **Purpose:** Stores all system users (Admins, Mechanics, Customers).
* **PK:** `user_id` (INT AUTO_INCREMENT)
* **Constraints:** `username` **UNIQUE**, `email` **UNIQUE**, `user_role` ENUM('Admin','Mechanic','Customer') DEFAULT 'Customer'
* **Relationships:** One User → N Vehicles, N Service Bookings, N Invoices.
* **Example:** `(1, 'Ravi Sharma', 'ravi12', 'ravi@example.com', ..., 'Customer')`

### VEHICLES
* **Purpose:** Assets owned by users.
* **PK:** `vehicle_no` (e.g., `GJ-01-AB-1234`)
* **FK:** `user_id` → `USERS.user_id` (**ON DELETE CASCADE**)
* **Rationale:** A vehicle is meaningless without an owner.
* **Example:** `('GJ01AB1234', 'Hyundai', 'i20', 'Car', 2)`

### SERVICES
* **Purpose:** Menu of available services (oil change, paint, etc.).
* **PK:** `service_id`
* **Constraints:** `service_name` **UNIQUE**, `base_price`, `estimated_hours`, `category`
* **Referenced by:** `SERVICE_BOOKINGS.service_id` (**NULL, ON DELETE SET NULL**)
* **Rationale:** Preserves booking history if a service is removed.
* **Example:** `(10, 'Oil Change', '...', 799.00, 1.00, 0, 'Maintenance', 'Active')`

### MECHANICS\_INFO
* **Purpose:** Roster of mechanics.
* **PK:** `mechanic_id`
* **Referenced by:**
    * `SERVICE_BOOKINGS.mechanic_id` (**NULL, ON DELETE SET NULL**)
    * `MECHANIC_ASSIGNMENTS.mechanic_id` (**ON DELETE CASCADE**)
* **Rationale:** Uses SET NULL on bookings to keep job history, but CASCADE on assignments to remove work schedule history.
* **Example:** `(5, 'Anil Mehta', 'Engine', '98xxxxxx12', 'anil@garage.com')`

### SERVICE\_BOOKINGS (The Heart of the System)
* **Purpose:** Each customer order/job record.
* **PK:** `booking_id`
* **FKs:**
    * `vehicle_no` → `VEHICLES.vehicle_no` (**ON DELETE CASCADE**)
    * `service_id` → `SERVICES.service_id` (**NULL, ON DELETE SET NULL**)
    * `user_id` → `USERS.user_id` (**ON DELETE CASCADE**)
    * `mechanic_id` → `MECHANICS_INFO.mechanic_id` (**NULL, ON DELETE SET NULL**)
* **Status:** ENUM('Pending','In Progress','Completed','Cancelled')
* **Note:** Stores both FK (`service_id`) and a snapshot of the service name (`service_name`) for historical audit.
* **Example:** `(101, 'GJ01AB1234', 10, 2, 'Oil Change', 5, '2025-11-06', 'Pending')`

### MECHANIC\_ASSIGNMENTS
* **Purpose:** Tracking assignment history, reassignments, or multiple mechanics per job.
* **PK:** `assignment_id`
* **FKs:**
    * `booking_id` → `SERVICE_BOOKINGS.booking_id` (**ON DELETE CASCADE**)
    * `mechanic_id` → `MECHANICS_INFO.mechanic_id` (**ON DELETE CASCADE**)
* **Example:** `(9001, 101, 5, '2025-11-06 10:00:00')`

### INVOICES
* **Purpose:** Billing records.
* **PK:** `invoice_id`
* **FKs:** `booking_id` → `SERVICE_BOOKINGS.booking_id`, `user_id` → `USERS.user_id`
* **Typical Constraint:** 1 Booking → 1 Invoice (can be enforced with a UNIQUE constraint on `booking_id`).
* **Example:** `(7001, 101, 2, 799.00, 'Pending', 'UPI', '2025-11-06 12:00:00')`

### FEEDBACK
* **Purpose:** Captures ratings and comments per booking.
* **PK:** `feedback_id`
* **FK:** `booking_id` → `SERVICE_BOOKINGS.booking_id`
* **Constraints:** `rating` CHECK 1..5 (MySQL 8+).
* **Typical Constraint:** 0/1 per booking (can be enforced with a UNIQUE constraint on `booking_id`).
* **Example:** `(3001, 101, 5, 'Great service!', '2025-11-07 09:00:00')`

### PARTS\_INVENTORY
* **Purpose:** Spare parts stock management.
* **PK:** `part_id`
* **FKs:** none (standalone).
* **Extension Note:** Future extension requires a junction table (e.g., `booking_parts`) to link parts used to a specific booking.

---

## 4) ↔️ Cardinality (In Simple Terms)

* **One user** has **many vehicles** and **many bookings**.
* **One vehicle** can have **many bookings** over its lifetime.
* **One service** is used by **many bookings** (if service deleted, old bookings keep `service_id = NULL`).
* **One mechanic** is assigned to **many bookings** (if mechanic deleted, old bookings keep `mechanic_id = NULL`).
* **One booking** usually generates **one invoice** and receives **zero or one feedback**.
* **One booking** can have **many mechanic\_assignments** (for history or multiple helpers).

---

## 5) 💥 Delete Rules (Exact Effects)

This outlines the precise consequence of deleting a primary record due to `ON DELETE` constraints.

* Delete **USER** → their **VEHICLES** and **BOOKINGS** **CASCADE**; dependent **INVOICES** and **FEEDBACK** tied to those bookings are deleted too.
* Delete **VEHICLE** → its **BOOKINGS** (and their invoices/feedback/assignments) **CASCADE**.
* Delete **SERVICE** → `SERVICE_BOOKINGS.service_id` becomes **NULL** (history preserved via `service_name` snapshot).
* Delete **MECHANIC** → `SERVICE_BOOKINGS.mechanic_id` becomes **NULL**; **MECHANIC\_ASSIGNMENTS** for that mechanic **CASCADE** delete.
* Delete **BOOKING** → related **INVOICES**, **FEEDBACK**, and **MECHANIC\_ASSIGNMENTS** are deleted.

---

## 6) ❓ Why Some FKs Are NULLable

The `NULL` allowance in `SERVICE_BOOKINGS` is a deliberate design choice to ensure auditability:

* **`service_id` in bookings:** Allows the service catalog item to be removed later without deleting the historical booking record. The descriptive `service_name` snapshot preserves what was done.
* **`mechanic_id` in bookings:** Allows a mechanic to leave the system (be deleted) without losing the historical record of the job itself. The record simply shows the job was completed but the mechanic is no longer in the roster.



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


