from models import db

class ParkingLot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    location = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=True)
    address = db.Column(db.String(255), nullable=True)
    pin_code = db.Column(db.String(20), nullable=True)
    maximum_number_of_spots = db.Column(db.Integer, nullable=True)

    slots = db.relationship('ParkingSlot', backref='lot', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<ParkingLot {self.name}>'