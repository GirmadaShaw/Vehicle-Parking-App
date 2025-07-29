from datetime import datetime, timedelta, date
from backend import db 

class User(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    def has_visited_today(self):
        """Check if this user has booked or visited a parking lot today."""
        from backend.models import ParkingSpot 
        
        today = date.today()
        booking = (ParkingSpot.query
                   .filter_by(user_id=self.user_id)
                   .filter(db.func.date(ParkingSpot.timestamp) == today)
                   .first())
        return booking is not None
    
    def get_most_used_lot(self):
        """Return the name of the most frequently used parking lot by the user."""
        from backend.models import ParkingSpot, ParkingLocation
        result = (db.session.query(ParkingLocation.name, db.func.count(ParkingSpot.spot_id))
                  .join(ParkingLocation, ParkingLocation.location_id == ParkingSpot.location_id)
                  .filter(ParkingSpot.user_id == self.user_id)
                  .group_by(ParkingLocation.name)
                  .order_by(db.func.count(ParkingSpot.spot_id).desc())
                  .first())
        return result[0] if result else "N/A"

class VehicleType(db.Model):
    __tablename__ = 'vehicle_types'

    vehicle_type_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type_name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255))

class ParkingLocation(db.Model):
    __tablename__ = 'parking_locations'

    location_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(150), nullable=False)
    address_line1 = db.Column(db.String(255), nullable=False)
    address_line2 = db.Column(db.String(255))
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100))
    postal_code = db.Column(db.String(20))
    country = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    total_slots = db.Column(db.Integer, nullable=False, default=0)
    hourly_rate = db.Column(db.Numeric(10, 2), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

class ParkingSlot(db.Model):
    __tablename__ = 'parking_slots'

    slot_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    location_id = db.Column(db.Integer, db.ForeignKey('parking_locations.location_id', ondelete='CASCADE'), nullable=False)
    slot_number = db.Column(db.String(50), nullable=False)
    vehicle_type_id = db.Column(db.Integer, db.ForeignKey('vehicle_types.vehicle_type_id'))
    is_covered = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    __table_args__ = (db.UniqueConstraint('location_id', 'slot_number', name='unique_slot_per_location'),)

    def is_this_month(self):
        now = datetime.now()
        return self.timestamp.year == now.year and self.timestamp.month == now.month

class Reservation(db.Model):
    __tablename__ = 'reservations'

    reservation_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    slot_id = db.Column(db.Integer, db.ForeignKey('parking_slots.slot_id', ondelete='RESTRICT'), nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey('parking_locations.location_id'), nullable=False)
    vehicle_registration_number = db.Column(db.String(30), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(50), nullable=False, default="available")
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    __table_args__ = (db.CheckConstraint('end_time > start_time', name='valid_time_range'),)

class Payment(db.Model):
    __tablename__ = 'payments'

    payment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    reservation_id = db.Column(db.Integer, db.ForeignKey('reservations.reservation_id'), nullable=False, unique=True)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)
    payment_status = db.Column(db.String(50), nullable=False)
    payment_date = db.Column(db.DateTime, default=datetime.now)
    transaction_id = db.Column(db.String(100))

class Review(db.Model):
    __tablename__ = 'reviews'

    review_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey('parking_locations.location_id', ondelete='CASCADE'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    review_text = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    __table_args__ = (db.UniqueConstraint('user_id', 'location_id', name='unique_user_review'),
                      db.CheckConstraint('rating BETWEEN 1 AND 5', name='valid_rating_range'))

class OTP(db.Model):
    __tablename__ = 'otp'

    otp_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    otp_code = db.Column(db.String(10), nullable=False)
    expires_at = db.Column(db.DateTime, default= datetime.now() + timedelta(minutes=10))
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

    user = db.relationship('User', backref=db.backref('otp_entries', cascade='all, delete-orphan'))