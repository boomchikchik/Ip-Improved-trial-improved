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
