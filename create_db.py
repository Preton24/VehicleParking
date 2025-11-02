# create_db.py
import app # This imports your app.py file as a module
from models import db # Assuming models.py has 'db' instance
from models.lot import ParkingLot
from models.slot import ParkingSlot
from models.reservation import Reservation
from models.user import User

with app.app.app_context():
    print("Dropping all existing database tables...")
    db.drop_all()
    print("Creating new database tables based on models...")
    db.create_all()
    print("Database tables dropped and recreated with new schema.")

    if not User.query.filter_by(role='admin').first():
        from werkzeug.security import generate_password_hash
        admin_user = User(
            name='Admin',
            email='admin@example.com',
            password=generate_password_hash('adminpassword', method='pbkdf2:sha256'),
            role='admin'
        )
        db.session.add(admin_user)
        db.session.commit()
        print("Admin user created: admin@example.com / adminpassword")
    else:
        print("Admin user already exists.")