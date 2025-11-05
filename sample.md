# 🚗 Vehicle Garage CLI Database Schema (v1.0)

This document serves as a concise, developer-friendly reference for the **data model** of the Garage CLI project. It maps all Primary Key (PK) / Foreign Key (FK) relationships, cardinality, and data deletion rules for quick reference.

---

## 🗺️ Big Picture: Entity Relationship Map

The core of the database revolves around **USERS** and the **SERVICE_BOOKINGS** table, which acts as a central link for vehicles, services, and mechanics.
Vehicle Garage DB — Relationships & Reference

A concise, developer-friendly map of PK/FK links, cardinality, and delete rules for the Garage CLI project.

1) Big Picture (Who connects to whom)
USERS (user_id PK)
 ├─< VEHICLES (vehicle_no PK, user_id FK → USERS.user_id)
 ├─< SERVICE_BOOKINGS (booking_id PK, user_id FK → USERS.user_id)
 │     ├─→ VEHICLES via vehicle_no FK
 │     ├─→ SERVICES via service_id FK (NULL allowed; ON DELETE SET NULL)
 │     └─→ MECHANICS via mechanic_id FK (NULL allowed; ON DELETE SET NULL)
 │
 ├─< INVOICES (invoice_id PK, user_id FK → USERS.user_id, booking_id FK → SERVICE_BOOKINGS.booking_id)
 └─< FEEDBACK (feedback_id PK, booking_id FK → SERVICE_BOOKINGS.booking_id)

MECHANICS_INFO (mechanic_id PK)
 └─< MECHANIC_ASSIGNMENTS (assignment_id PK, booking_id FK → SERVICE_BOOKINGS.booking_id, mechanic_id FK → MECHANICS_INFO.mechanic_id)

PARTS_INVENTORY (part_id PK)    -- standalone (no FKs)


Legend

PK = Primary Key (unique ID of a row)

FK = Foreign Key (points to another table’s PK)

A ├─< B = A has many B (one-to-many)

2) Visual (Mermaid)

Renders on GitHub automatically.

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

3) Table-by-Table (What it stores + Constraints)
USERS

Purpose: All people: Admins, Mechanics, Customers

PK: user_id (INT AUTO_INCREMENT)

Important: username UNIQUE, email UNIQUE, user_role ENUM('Admin','Mechanic','Customer') DEFAULT 'Customer'

Relationships:

1 User → N Vehicles

1 User → N Service Bookings

1 User → N Invoices

Example: (1, 'Ravi Sharma', 'ravi12', 'ravi@example.com', ..., 'Customer')

VEHICLES

Purpose: Assets owned by users

PK: vehicle_no (e.g., GJ-01-AB-1234)

FK: user_id → USERS.user_id (ON DELETE CASCADE)

Why CASCADE? Vehicle without owner = meaningless

Example: ('GJ01AB1234', 'Hyundai', 'i20', 'Car', 2)

SERVICES

Purpose: Menu of jobs (oil change, paint…)

PK: service_id

Important: service_name UNIQUE, base_price, estimated_hours, category

Referenced by: SERVICE_BOOKINGS.service_id (NULL, ON DELETE SET NULL)

Why SET NULL? Preserve booking history if a service is removed

Example: (10, 'Oil Change', '...', 799.00, 1.00, 0, 'Maintenance', 'Active')

MECHANICS_INFO

Purpose: Mechanics roster

PK: mechanic_id

Referenced by:

SERVICE_BOOKINGS.mechanic_id (NULL, ON DELETE SET NULL)

MECHANIC_ASSIGNMENTS.mechanic_id (ON DELETE CASCADE)

Why SET NULL on bookings? Keep job history if a mechanic leaves

Example: (5, 'Anil Mehta', 'Engine', '98xxxxxx12', 'anil@garage.com')

SERVICE_BOOKINGS (heart)

Purpose: Each order/job

PK: booking_id

FKs:

vehicle_no → VEHICLES.vehicle_no (ON DELETE CASCADE)

service_id → SERVICES.service_id (NULL, ON DELETE SET NULL)

user_id → USERS.user_id (ON DELETE CASCADE)

mechanic_id → MECHANICS_INFO.mechanic_id (NULL, ON DELETE SET NULL)

Status: ENUM('Pending','In Progress','Completed','Cancelled')

Note: Has both service_id (FK) and service_name (snapshot) — good for audit/history

Example: (101, 'GJ01AB1234', 10, 2, 'Oil Change', 5, '2025-11-06', 'Pending')

MECHANIC_ASSIGNMENTS

Purpose: Assignment history / reassignments / multi-helper

PK: assignment_id

FKs:

booking_id → SERVICE_BOOKINGS.booking_id (ON DELETE CASCADE)

mechanic_id → MECHANICS_INFO.mechanic_id (ON DELETE CASCADE)

Example: (9001, 101, 5, '2025-11-06 10:00:00')

INVOICES

Purpose: Billing

PK: invoice_id

FKs: booking_id → SERVICE_BOOKINGS.booking_id, user_id → USERS.user_id

Typical: 1 Booking → 1 Invoice (enforce with UNIQUE if required)

Example: (7001, 101, 2, 799.00, 'Pending', 'UPI', '2025-11-06 12:00:00')

FEEDBACK

Purpose: Rating/comments per booking

PK: feedback_id

FK: booking_id → SERVICE_BOOKINGS.booking_id

Constraint: rating CHECK 1..5 (MySQL 8+)

Typical: 0/1 per booking (enforce with UNIQUE if needed)

Example: (3001, 101, 5, 'Great service!', '2025-11-07 09:00:00')

PARTS_INVENTORY

Purpose: Spare parts stock

PK: part_id

FKs: none (standalone).

Extend later: junction booking_parts(booking_id FK, part_id FK, qty, price_at_use)

4) Cardinality (Beginner English)

One user → many vehicles

One user → many bookings

One vehicle → many bookings over time

One service → many bookings (if service deleted → old bookings keep service_id = NULL)

One mechanic → many bookings (if mechanic deleted → old bookings keep mechanic_id = NULL)

One booking → usually one invoice and zero/one feedback

One booking → many mechanic_assignments (timeline/history)

5) Delete Rules (Exact Effects)

Delete USER → their VEHICLES and BOOKINGS cascade; dependent INVOICES/FEEDBACK tied to those bookings go too

Delete VEHICLE → its BOOKINGS (and their invoices/feedback/assignments) cascade

Delete SERVICE → SERVICE_BOOKINGS.service_id becomes NULL (history preserved)

Delete MECHANIC → SERVICE_BOOKINGS.mechanic_id becomes NULL; MECHANIC_ASSIGNMENTS for that mechanic CASCADE delete

Delete BOOKING → related INVOICES, FEEDBACK, and MECHANIC_ASSIGNMENTS are deleted

6) Why Some FKs Are NULLable

service_id in bookings: service catalog item may be removed later → keep booking; set FK to NULL (but service_name snapshot remains).

mechanic_id in bookings: mechanic may leave → keep booking; set FK to NULL.

7) Optional Tightening (Indexes & Uniques)
-- VEHICLES
CREATE INDEX idx_vehicles_user ON vehicles(user_id);

-- SERVICE_BOOKINGS
CREATE INDEX idx_sb_user ON service_bookings(user_id);
CREATE INDEX idx_sb_vehicle ON service_bookings(vehicle_no);
CREATE INDEX idx_sb_service ON service_bookings(service_id);
CREATE INDEX idx_sb_mechanic ON service_bookings(mechanic_id);
CREATE INDEX idx_sb_status_date ON service_bookings(status, booking_date);

-- INVOICES
CREATE INDEX idx_invoices_user ON invoices(user_id);
-- enforce 1 invoice per booking (optional)
CREATE UNIQUE INDEX uq_invoices_booking ON invoices(booking_id);

-- FEEDBACK (at most one per booking, optional)
CREATE UNIQUE INDEX uq_feedback_booking ON feedback(booking_id);

-- MECHANIC_ASSIGNMENTS
CREATE INDEX idx_ma_booking ON mechanic_assignments(booking_id);
CREATE INDEX idx_ma_mechanic ON mechanic_assignments(mechanic_id);

8) Handy Queries
-- All bookings for a user (with vehicle, service, mechanic)
SELECT sb.booking_id, sb.booking_date, sb.status,
       v.vehicle_no, v.vehicle_brand, v.model,
       COALESCE(s.service_name, sb.service_name) AS chosen_service,
       m.full_name AS mechanic
FROM service_bookings sb
JOIN vehicles v       ON v.vehicle_no = sb.vehicle_no
JOIN users u          ON u.user_id = sb.user_id
LEFT JOIN services s  ON s.service_id = sb.service_id
LEFT JOIN mechanics_info m ON m.mechanic_id = sb.mechanic_id
WHERE sb.user_id = ? 
ORDER BY sb.booking_date DESC;

-- Revenue by month
SELECT DATE_FORMAT(invoice_date, '%Y-%m') AS period,
       SUM(amount) AS revenue
FROM invoices
GROUP BY DATE_FORMAT(invoice_date, '%Y-%m')
ORDER BY period;

-- Mechanic workload (open jobs)
SELECT m.mechanic_id, m.full_name, COUNT(*) AS open_jobs
FROM service_bookings sb
JOIN mechanics_info m ON m.mechanic_id = sb.mechanic_id
WHERE sb.status IN ('Pending','In Progress')
GROUP BY m.mechanic_id, m.full_name
ORDER BY open_jobs DESC;

-- Feedback with vehicle & user
SELECT f.feedback_id, f.rating, f.comments, f.created_at,
       sb.booking_id, v.vehicle_no, u.name
FROM feedback f
JOIN service_bookings sb ON sb.booking_id = f.booking_id
JOIN vehicles v          ON v.vehicle_no = sb.vehicle_no
JOIN users u             ON u.user_id = sb.user_id
ORDER BY f.created_at DESC;

-- Assignment history for a booking
SELECT ma.assigned_date, m.full_name
FROM mechanic_assignments ma
JOIN mechanics_info m ON m.mechanic_id = ma.mechanic_id
WHERE ma.booking_id = ?
ORDER BY ma.assigned_date;

9) Data Flow (Story)

User signs up → USERS

Adds a vehicle → VEHICLES(user_id)

Books a service → SERVICE_BOOKINGS(vehicle_no, user_id, service_id?, mechanic_id?)

Assign mechanic(s) → SERVICE_BOOKINGS.mechanic_id and/or MECHANIC_ASSIGNMENTS history

Complete job → update SERVICE_BOOKINGS.status

Create invoice → INVOICES(booking_id, user_id, amount, ...)

Collect feedback → FEEDBACK(booking_id, rating, comments)
