from models import db

class ParkingSlot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lot_id = db.Column(db.Integer, db.ForeignKey('parking_lot.id'), nullable=False)
    slot_number = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), default='available')
    __table_args__ = (db.UniqueConstraint('lot_id', 'slot_number', name='_lot_slot_uc'),)

    reservations = db.relationship('Reservation', backref='slot', lazy=True)

    def __repr__(self):
        return f'<ParkingSlot {self.lot.name}-{self.slot_number}>'