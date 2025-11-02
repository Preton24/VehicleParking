#🚗 SMART VEHICLE PARKING MANAGEMENT

A Flask-based web app for managing parking lots, slots, and reservations with separate dashboards for **admins** and **users**.

## Table of Contents

*   [Features](#features)
*   [Technologies Used](#technologies-used)
*   [Database Schema](#database-schema)
*   [Installation & Setup](#installation--setup)
*   [Admin Credentials](#admin-credentials)

---

## Features  

### 👩‍💼 Admin  
- Manage parking lots (CRUD operations)  
- Manage slots (Available, Booked, Maintenance, Occupied)  
- View and cancel any reservation  
- Track cost and status of all bookings  

### 👤 User  
- Register, log in, and view parking lots  
- Book available slots by **entering vehicle number** (no duration input)  
- Release slot when leaving — cost auto-calculated based on duration  
- View current and past reservations on dashboard  
- **Redirected to Payment Page** after ending reservation  
Once payment is completed, the reservation is marked as **Paid**, and users are redirected to their dashboard with a success message.  

---

## 🛠 Technologies Used
- **Flask**, **Flask-SQLAlchemy**, **Flask-Login**, **Flask-Migrate**  
- **SQLite** for data storage  
- **Bootstrap + Jinja2** for responsive UI  
- **Werkzeug** for secure password hashing  
- **Datetime** module for time tracking  

---

## 🧱 Database Schema  

| Table        | Key Fields                                                                 |
|---------------|---------------------------------------------------------------------------|
| **User**         | id, name, email, password, role                                          |
| **ParkingLot**   | id, name, location, price/hr, address, pin_code, max_spots               |
| **ParkingSlot**  | id, lot_id, slot_number, status                                          |
| **Reservation**  | id, user_id, slot_id, vehicle_number, start_time, end_time, cost, status |

---

## Installation & Setup

To get the project running locally:

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Preton24/VehicleParking
    cd VehicleParking
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    # On Windows:
    venv\Scripts\activate
    # On macOS/Linux:
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install Flask Flask-SQLAlchemy Flask-Login Werkzeug Flask-Migrate # Add Flask-Migrate if you install it
    ```

4.  **Set up the database:**
    Your `app.py` is configured to create the database automatically when run for the first time.
    If you've made schema changes (e.g., adding `price`, `address`, `pin_code`, `maximum_number_of_spots` to `ParkingLot` or `cost` to `Reservation`), you need to migrate your database.

    **Option A: Using Flask-Migrate (Recommended)**
    If you've integrated Flask-Migrate into your `app.py`:
    ```bash
    flask db init          # Run once to initialize migrations directory
    flask db migrate -m "Initial migration or schema updates"
    flask db upgrade
    ```
    Repeat `flask db migrate -m "..."` and `flask db upgrade` every time you change your models.

    **Option B: Recreate Database (CAUTION: Deletes all existing data)**
    If you are in early development and don't mind losing data, you can recreate the database:
    ```bash
    python create_db.py
    ```

5.  **Run the application:**
    ```bash
    flask run
    ```

## Admin Credentials

*   **Email:** `admin@example.com`
*   **Password:** `adminpassword`

---
