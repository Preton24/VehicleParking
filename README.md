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

## Technologies Used
- **Flask**, **Flask-SQLAlchemy**, **Flask-Login**, **Flask-Migrate**  
- **SQLite** for data storage  
- **Bootstrap + Jinja2** for responsive UI  
- **Werkzeug** for secure password hashing  
- **Datetime** module for time tracking  

---

## Database Schema  

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
    pip install Flask Flask-SQLAlchemy Flask-Login Werkzeug Flask-Migrate
     ```

4.  **Run the application:**
    ```bash
    python app.py
    ```

## Admin Credentials

*   **Email:** `admin@example.com`
*   **Password:** `adminpassword`

---
