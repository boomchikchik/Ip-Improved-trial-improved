# 🚗 Vehicle Garage CLI Database Schema (v1.0)

This document serves as a concise, developer-friendly reference for the **data model** of the Garage CLI project. It maps all Primary Key (PK) / Foreign Key (FK) relationships, cardinality, and data deletion rules for quick reference.

---

## 🗺️ Big Picture: Entity Relationship Map

The core of the database revolves around **USERS** and the **SERVICE_BOOKINGS** table, which acts as a central link for vehicles, services, and mechanics.

```mermaid
flowchart LR
  U["USERS (PK: user_id)"]:::entity
  V["VEHICLES (PK: vehicle_no)\nFK: user_id"]:::entity
  Svc["SERVICES (PK: service_id)"]:::entity
  M["MECHANICS_INFO (PK: mechanic_id)"]:::entity
  SB["SERVICE_BOOKINGS (PK: booking_id)\nFKs: vehicle_no, user_id, service_id, mechanic_id"]:::link
  MA["MECHANIC_ASSIGNMENTS (PK: assignment_id)\nFKs: booking_id, mechanic_id"]:::link
  I["INVOICES (PK: invoice_id)\nFKs: booking_id, user_id"]:::entity
  F["FEEDBACK (PK: feedback_id)\nFK: booking_id"]:::entity
  P["PARTS_INVENTORY (PK: part_id)"]:::entity

  V -->|1:N| U
  SB -->|N:1| V
  SB -->|N:1| U
  SB -->|N:1| Svc
  SB -->|N:1| M

  MA -->|N:1| SB
  MA -->|N:1| M

  I -->|1:1/N| SB
  I -->|N:1| U

  F -->|0/1:1| SB

  classDef entity fill:#eef6ff,stroke:#1f6feb,stroke-width:1px;
  classDef link fill:#ecfdf5,stroke:#059669,stroke-width:1px;





Parent Table (1),Child Table (N),Foreign Key (FK),Relationship Type,ON DELETE Rule,Notes
USERS,VEHICLES,user_id,One-to-Many,CASCADE,Vehicle must have an owner.
USERS,SERVICE_BOOKINGS,user_id,One-to-Many,CASCADE,Booking is deleted if user is deleted.
VEHICLES,SERVICE_BOOKINGS,vehicle_no,One-to-Many,CASCADE,Booking without vehicle is meaningless.
SERVICES,SERVICE_BOOKINGS,service_id,One-to-Many,SET NULL,Preserves booking history if service is deprecated.
MECHANICS_INFO,SERVICE_BOOKINGS,mechanic_id,One-to-Many,SET NULL,Preserves job history if mechanic leaves.
MECHANICS_INFO,MECHANIC_ASSIGNMENTS,mechanic_id,One-to-Many,CASCADE,Assignments are deleted if mechanic leaves.
SERVICE_BOOKINGS,MECHANIC_ASSIGNMENTS,booking_id,One-to-Many,CASCADE,Assignment deleted if the booking is deleted.
SERVICE_BOOKINGS,INVOICES,booking_id,One-to-One/Many,Default,Invoice is tied directly to the job.
SERVICE_BOOKINGS,FEEDBACK,booking_id,One-to-Zero/One,Default,Feedback is tied directly to the job.
USERS,INVOICES,user_id,One-to-Many,Default,Invoice tied to customer for audit.
