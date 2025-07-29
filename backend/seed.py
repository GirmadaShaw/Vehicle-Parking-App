# seed.py
from backend import db
from faker import Faker
import random
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
from backend.models import User, VehicleType, ParkingLocation, ParkingSlot, Reservation, \
                    Payment, Review

fake = Faker()

def seed_data():
    if User.query.first():  # Check if users already exist
        print("Database already seeded.")
        return

    print("Seeding Begins...")

    NUM_USERS = 10
    NUM_VEHICLE_TYPES = 3
    NUM_LOCATIONS = 2
    SLOTS_PER_LOCATION = 10
    NUM_RESERVATIONS = 6  # Not all users will book
    NUM_REVIEWS = 5
    PAYMENTS_FOR_RESERVATIONS = 5  # Some reservations not paid
    admin_passwd = "Girmada@123"

    # Generate Users
    users = []
    for i in range(NUM_USERS):
        users.append({
            "username": fake.user_name(),
            "email": fake.email(domain="gmail.com"),
            "password_hash": generate_password_hash("hashed_pwd", salt_length=10),
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "phone": fake.phone_number()
        })
    for u in users:
            db.session.add(User(**u))
    
    
    # add Admin
    admin = { "username": "girmada_shaw",
              "email" : "girmadasingh@gmail.com",
              "password_hash" : generate_password_hash(admin_passwd, salt_length=10),
              "first_name" : "Girmada",
              "last_name" : "Shaw",
              "phone" : "9699735697",
              "is_admin" : True
            }
    db.session.add(User(**admin))

    db.session.commit()
    print("\tSeeded users !")

    # Vehicle Types
    vehicle_types = [
        {"type_name": "Car", "description": "Standard car"},
        {"type_name": "Motorcycle", "description": "Two-wheeler"},
        {"type_name": "Truck", "description": "Heavy vehicle"}
    ]
    for vt in vehicle_types:
            db.session.add(VehicleType(**vt))
    db.session.commit()
    print("\tSeeded vehicle types !")

    # Parking Locations
    locations = []
    for i in range(NUM_LOCATIONS):
        locations.append({
            "name": f"{fake.company()} Parking",
            "address_line1": fake.street_address(),
            "city": fake.city(),
            "state": fake.state(),
            "postal_code": fake.postcode(),
            "country": "India",
            "phone": fake.phone_number(),
            "total_slots": SLOTS_PER_LOCATION,
            "hourly_rate": round(random.uniform(20, 50), 2)
        })

    for loc in locations:
        db.session.add(ParkingLocation(**loc))
    db.session.commit()
    print("\tSeeded parking locations !")

    # Parking Slots
    slots = []
    slot_id = 1
    for loc_id in range(1, NUM_LOCATIONS + 1):
        for i in range(1, SLOTS_PER_LOCATION + 1):
            slots.append({
                "slot_id": slot_id,
                "location_id": loc_id,
                "slot_number": f"S{i}",
                "vehicle_type_id": random.randint(1, NUM_VEHICLE_TYPES),
                "is_covered": random.choice([True, False])
            })
            slot_id += 1
    for s in slots:
        db.session.add(ParkingSlot(**s))
    db.session.commit()
    print("\tSeeded parking slots !")

    # Reservations
    reservations = []
    statuses = ['occupied', 'available']
    for i in range(1, NUM_RESERVATIONS + 1):
        user_id = i  # Use 1-to-1 for simplicity
        slot = random.choice(slots)
        start = datetime.now() + timedelta(hours=random.randint(1, 12))
        end = start + timedelta(hours=random.randint(1, 3))
        reservations.append({
            "reservation_id": i,
            "user_id": user_id,
            "slot_id": slot["slot_id"],
            "location_id": slot["location_id"],
            "vehicle_registration_number": fake.license_plate(),
            "start_time": start,
            "end_time": end,
            "status": statuses[random.randint(0,1)]
        })
    for r in reservations:
        db.session.add(Reservation(**r))
    db.session.commit()
    print("\tSeeded reservations !")

    # Payments
    payments = []
    for i in range(1, PAYMENTS_FOR_RESERVATIONS + 1):
        payments.append({
            "reservation_id": i,
            "amount": round(random.uniform(50, 200), 2),
            "payment_method": random.choice(["VISA", "UPI", "PayPal"]),
            "payment_status": "completed",
            "transaction_id": fake.uuid4()
        })
    for p in payments:
        db.session.add(Payment(**p))
    db.session.commit()
    print("\tSeeded payments !")

    # Reviews
    reviews = []
    for i in range(1, NUM_REVIEWS + 1):
        reviews.append({
            "user_id": i,
            "location_id": random.randint(1, NUM_LOCATIONS),
            "rating": random.randint(1, 5),
            "review_text": fake.sentence()
        })
    for rv in reviews:
        db.session.add(Review(**rv))
    
    db.session.commit()
    print("\tSeeded reviews !")
    print("Seeding Ends...")
