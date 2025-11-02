# SMART VEHICLE PARKING MANAGEMENT

This is a Flask-based web application designed to manage parking lots, individual parking slots, and user reservations. It provides distinct interfaces for administrators to configure the system and for regular users to book and manage their parking spots.

## Table of Contents

*   [Features](#features)
*   [Technologies Used](#technologies-used)
*   [Architecture](#architecture)
*   [Database Schema](#database-schema)
*   [API Design](#api-design)
*   [Installation & Setup](#installation--setup)
*   [Usage](#usage)
*   [Admin Credentials](#admin-credentials)

## Features

The system implements a robust set of features for both administrators and regular users:

### Default Features:

*   **User Authentication & Authorization:** Secure user registration, login, and logout functionalities with password hashing. Role-based access control restricts views based on user roles (admin/user).
*   **Parking Lot Management (Admin):** Comprehensive CRUD operations for parking lots, including name, location, price per hour, physical address, PIN code, and maximum number of spots.
*   **Parking Slot Management (Admin):** Ability to add, update status (available, booked, maintenance, occupied), and delete individual parking slots within each lot. Includes optional enforcement of maximum capacity.
*   **User Parking Overview:** Authenticated users can browse all available parking lots, viewing lot details and real-time slot statuses.
*   **Reservation System:** Users can book available slots for a specified duration. The system includes crucial checks to prevent overlapping reservations.
*   **User Dashboard:** A personalized dashboard displaying current, completed, and cancelled reservations for regular users, and aggregated system statistics for administrators.
*   **Reservation Cancellation:** Users can cancel their active reservations (with minor time-based restrictions). Administrators have full control to cancel any reservation.

### Additional Features Implemented:

*   **Reservation Cost Tracking:** The total cost for each reservation is dynamically calculated at the time of booking (based on lot's price per hour and duration). This cost is stored in the database and transparently displayed to both users on their dashboard and to administrators in the reservation management view.

## Technologies Used

This project leverages the following technologies:

*   **Flask:** The core Python web framework for building the application.
*   **Flask-SQLAlchemy:** Flask extension for Object Relational Mapping (ORM), simplifying database interactions.
*   **SQLite:** The file-based relational database used for data persistence (`parking.db`).
*   **Flask-Login:** Flask extension for managing user sessions and authentication.
*   **Werkzeug.security:** Used for secure password hashing and verification.
*   **Jinja2:** The templating engine for generating dynamic HTML content.
*   **Bootstrap:** CSS framework used for styling and responsive design (indicated by class names in templates).
*   **Python's `datetime` module:** For handling and managing date and time objects (e.g., reservation times).
*   **Python's `os` module:** Used for environment variable management (e.g., `SECRET_KEY`).


The project follows a modular Flask application structure.
*   `app.py` is the application entry point, handling global configurations, database (`db`) initialization, Flask-Login setup, and blueprint registration.
*   `controllers/`: Contains blueprints (`auth_controller.py`, `main_controller.py`) which define API endpoints and implement the application's business logic.
*   `models/`: Defines the database schema using Flask-SQLAlchemy, mapping Python classes (e.g., `User`, `ParkingLot`, `ParkingSlot`, `Reservation`) to database tables.
*   `templates/`: Stores Jinja2 HTML templates for the user interface.
*   `static/`: Holds static assets like CSS files.

## Database Schema

The database is designed with the following tables:

*   **`User`**: `id` (PK), `name`, `email` (Unique), `password` (hashed), `role`.
*   **`ParkingLot`**: `id` (PK), `name` (Unique), `location`, `price`, `address`, `pin_code`, `maximum_number_of_spots`.
*   **`ParkingSlot`**: `id` (PK), `lot_id` (FK to `ParkingLot.id`), `slot_number`, `status`. (Composite Unique on `lot_id`, `slot_number`)
*   **`Reservation`**: `id` (PK), `user_id` (FK to `User.id`), `slot_id` (FK to `ParkingSlot.id`), `start_time`, `end_time`, `status`, `cost`.

This normalized design minimizes data redundancy and maintains integrity across user, lot, slot, and reservation records, allowing for clear relationships and flexible data management.

## API Design

The API exposes endpoints for managing core application entities: user authentication, CRUD operations for parking lots and their individual slots (primarily for administrative use), and user-specific booking and management of parking reservations. It's implemented using standard Flask routing, relying on Flask-SQLAlchemy for seamless interaction with the SQLite database, and secured with Flask-Login for session management and authorization. (A detailed YAML specification would provide precise endpoint definitions, request/response formats, and authentication mechanisms.)

## Installation & Setup

To get the project running locally:

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd <repository_directory>
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
    (Ensure `create_db.py` is configured correctly as per previous discussions to point to your `app` instance).

5.  **Run the application:**
    ```bash
    flask run
    ```
    The application will typically be accessible at `http://127.0.0.1:5000/`.

## Usage

*   **Access the application:** Open your web browser and navigate to the address provided by `flask run` (e.g., `http://127.0.0.1:5000/`).
*   **Register:** Create a new user account.
*   **Login:** Use your registered credentials to log in.
*   **Admin Access:** If you log in with the default admin credentials, you'll be redirected to the admin dashboard.
*   **View Parking:** Regular users can browse available parking lots and slots.
*   **Book Slots:** Select an available slot, choose a duration, and confirm your booking.
*   **Manage Reservations:** View your active, completed, and cancelled reservations from your dashboard.

## Admin Credentials

Upon the first run of the `app.py` (or `create_db.py`), a default admin user will be created if one doesn't exist:

*   **Email:** `admin@example.com`
*   **Password:** `adminpassword`

---
