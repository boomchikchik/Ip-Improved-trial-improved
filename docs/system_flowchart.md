# Vehicle Garage Management CLI - Flowchart

The diagram below captures the high-level control flow across the CLI entry point (`main.py`), the role-specific dashboards in `core/`, and their interactions with the MySQL schema created in `db/`.

```mermaid
flowchart TD
    Start([Start CLI]) --> Init[Initialize logging & styles]
    Init --> SQLConn[sql_connect()]
    SQLConn --> EnsureDB[create_database()]
    EnsureDB --> EnsureTables[create_tables()]
    EnsureTables --> Menu{Main menu selection}

    Menu -->|1 New user| Register[user_registration()]
    Register -->|Insert user| DB
    Register --> Menu

    Menu -->|2 Existing user| UserLogin[user_login()]
    UserLogin -->|Invalid| Menu
    UserLogin -->|Valid| UserDash[User dashboard]

    subgraph User_Workflow [User workflow]
        UserDash --> Profile[Profile updates]
        Profile --> DB
        Profile --> UserDash

        UserDash --> VehicleOps[Add or manage vehicles]
        VehicleOps --> DB
        VehicleOps --> UserDash

        UserDash --> BrowseServices[Browse active services]
        BrowseServices --> DB
        BrowseServices --> UserDash

        UserDash --> BookService[Book service]
        BookService --> DB
        BookService --> UserDash

        UserDash --> Payments[Make payment]
        Payments --> DB
        Payments --> UserDash

        UserDash --> History[History / track / cancel bookings]
        History --> DB
        History --> UserDash

        UserDash --> InvoiceOps[View or download invoices]
        InvoiceOps --> DB
        InvoiceOps --> UserDash

        UserDash --> Feedback[Leave feedback]
        Feedback --> DB
        Feedback --> UserDash

        UserDash -->|Logout| Menu
    end

    Menu -->|3 Admin login| AdminLogin[admin_login()]
    AdminLogin -->|Invalid| Menu
    AdminLogin -->|Valid| AdminDash[Admin dashboard]

    subgraph Admin_Workspace [Admin workspace]
        AdminDash --> ManageUsers[Manage users]
        ManageUsers --> DB
        ManageUsers --> AdminDash

        AdminDash --> VehicleService[Manage vehicles and services]
        VehicleService --> DB
        VehicleService --> AdminDash

        AdminDash --> Mechanics[Manage mechanics and assignments]
        Mechanics --> DB
        Mechanics --> AdminDash

        AdminDash --> Inventory[Maintain parts inventory]
        Inventory --> DB
        Inventory --> AdminDash

        AdminDash --> InvoiceAdmin[Generate or edit invoices]
        InvoiceAdmin --> DB
        InvoiceAdmin --> AdminDash

        AdminDash --> FeedbackAdmin[Review feedback]
        FeedbackAdmin --> DB
        FeedbackAdmin --> AdminDash

        AdminDash --> Reports[Revenue and status reports]
        Reports --> DB
        Reports --> AdminDash

        AdminDash -->|Logout| Menu
    end

    Menu -->|4 Mechanic login| MechLogin[mechanic_login()]
    MechLogin -->|Invalid| Menu
    MechLogin -->|Valid| MechDash[Mechanic dashboard]

    subgraph Mechanic_Flow [Mechanic flow]
        MechDash --> EditProfile[Edit profile]
        EditProfile --> DB
        EditProfile --> MechDash

        MechDash --> AssignedJobs[View assigned jobs]
        AssignedJobs --> DB
        AssignedJobs --> MechDash

        MechDash --> UpdateStatus[Update job status]
        UpdateStatus --> DB
        UpdateStatus --> MechDash

        MechDash --> JobHistory[Job history]
        JobHistory --> DB
        JobHistory --> MechDash

        MechDash -->|Logout| Menu
    end

    Menu -->|0 Exit| Exit([Shutdown application])
    EnsureTables --> DB
    DB[(MySQL database\nvehiclemanagement)]
    Exit --> End([End])
```

Render the Mermaid snippet in any viewer (e.g. GitHub, VS Code with the Mermaid extension, or an online previewer) to visualise the complete flow.
