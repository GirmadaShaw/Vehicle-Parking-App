import re, jwt, os
from dotenv import load_dotenv
from backend import app, db
from flask import request, jsonify, make_response, send_file
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
from werkzeug.security import generate_password_hash, check_password_hash
from backend.common import send_email, parse_time
from sqlalchemy import func
from backend.models import User, OTP, ParkingLocation, ParkingSlot, Reservation, Review, Payment 
from datetime import timedelta, datetime
from sqlalchemy.exc import IntegrityError
from backend.cache import cache_get, cache_set, cache_delete

load_dotenv()


# APIs USED BY USERS



# signup 
@app.route("/signup", methods = ['POST'] )
def signup():
    if( request.method == 'POST'):
        try:
            # parse data in json format and check existence
            data = request.get_json()        
            if data is None:
                return jsonify({
                    "success" : False,
                    "message" : "No data retrieved in request"
                }),401
            
            # validate email
            email = data.get('email')
            pattern = r'^[a-zA-Z0-9_.+-]+@gmail\.com$'
            if re.match(pattern, email) is None:
                return jsonify({
                    "success" : False,
                    "message" : "Only G-Mail is accepted" 
                }),401
            
            # check if user already exists
            user =  User.query.filter_by( email = email ).first()
            if user is not None:
                return jsonify({
                    "success" : False,
                    "message" : "User already exists"
                }),401

            # validate phone no.
            phone = data.get("phone")
            if phone[0] not in ['9', '8', '7' , '6' ] or len(phone) != 10 :
                return jsonify({
                    "success" : False,
                    "message" : "Use your Indian phone number"
                })
            
            # generate password hash
            password = data.get("password")
            password_hash = generate_password_hash(password, salt_length=10)

            try:
                # email the OTP
                otp = send_email(email)

            except (ValueError, ConnectionError, RuntimeError) as mail_err:
                return jsonify({
                    "success": False,
                    "message": f"Email sending failed: {str(mail_err)}"
                }), 401

            # insert into user db
            db.session.add(User(
                    username = data.get("username"),
                    email = email,
                    password_hash = password_hash,
                    first_name = data.get("first_name"),
                    last_name = data.get("last_name"),
                    phone = phone
                ))
            db.session.commit()
            

            # insert OTP into the db
            user =  User.query.filter_by(email = email).first()
            db.session.add(
                OTP(
                    user_id = user.user_id,
                    otp_code = otp
                ))
            db.session.commit()

         
            cache_set(f"otp:{user.user_id}", otp, 60)
            print("otp set in redis")

            response = make_response(jsonify({
                "success" : True,
                "message" : "User Registration Successful, OTP Mailed",
                }),200)
        
            return response
        
        except IntegrityError as e:
            db.session.rollback()

            if 'users.username' in str(e.orig):
                return jsonify({'success': False, 'message': 'Username already exists'}), 401
            elif 'users.email' in str(e.orig):
                return jsonify({'success': False, 'message': 'Email already exists'}), 401
            else:
                return jsonify({'success': False, 'message': 'Integrity error occurred'}), 401
            
        except Exception as e :
            print("Internal Server Error (in signup route)",str(e))
            return jsonify({
                "success" : False,
                "message" : "Internal Server Error (signup api)",
                "error" : str(e)
            }),500

# login
@app.route("/login", methods = ['POST'] )
def login():
    if request.method == 'POST':
        try:
            data = request.get_json()
            if data is None:
                return jsonify({
                    "success" : False,
                    "message" : "No data retrieved in request"
                }), 401
            
            # validate email
            email = data.get("email")

            pattern = r'^[a-zA-Z0-9_.+-]+@gmail\.com$'
            if re.match(pattern, email) is None:
                return jsonify({
                    "success" : False,
                    "message" : "Only G-Mail is accepted" 
                }),401

            # check if user has registered
            user =  User.query.filter_by(email = email).first()
            if user is None:
                return jsonify({
                    "success" : False,
                    "message" : "Register first"
                }), 401

            # validate password
            password = data.get("password")

            if check_password_hash(user.password_hash, password) == False :
                return jsonify({
                    "success" : False,
                    "message" : "Incorrect password"
                }), 402
            
            # generate token
            payload = {
                "user_id" : user.user_id
            }
            token =  jwt.encode(payload, os.getenv("JWT_SECRET"), algorithm="HS256" )

            response = make_response(
                jsonify({
                "success" : True,
                "message" : "Login Successfull",
                "token" : token
            }),200)

            response.set_cookie("token", token, 
                                expires = datetime.now() + timedelta(minutes=10),
                                samesite = None,
                                secure = True,
                                httponly= True )

            return response
        
        except Exception as e:
            return jsonify({
                "success" : False,
                "message" : "Internal Server Error (login api)",
                "error" : str(e)
            }),500
        
# verify otp
@app.route("/verify-otp", methods = ['POST'] )
def otp():
    if request.method == 'POST':
        try:
            data = request.get_json()
            if data is None:
                return jsonify({
                    "success" : False,
                    "message" : "No data exists in request"
                }),401
            
            email = data.get("email")
            if not email:
                return jsonify({
                    "success"  : False,
                    "message" : "Email doesn't exists or Session Expired"
                }), 401
            
            otp = data.get("otp")

            user =  User.query.filter_by( email = email ).first()
            otp_record =  OTP.query.filter_by(user_id=user.user_id) \
                                .order_by(OTP.created_at.desc())  \
                                .first()

            if not otp_record or otp_record.otp_code != otp:
                return jsonify({
                    "success" : False,
                    "message": "Invalid OTP"
                    }), 401

            otp_record.is_verified = True
            db.session.commit()

            payload = {
                "user_id" : user.user_id
            }

            token =  jwt.encode(payload, os.getenv("JWT_SECRET"), algorithm="HS256" )
            response = make_response(
                jsonify({
                "success" : True,
                "message" : "OTP verified, registration successfull",
                "token" : token
            }),200)

            response.set_cookie("token", token, 
                                expires = datetime.now() + timedelta(minutes=10),
                                samesite = "Lax",  # None for prod env
                                secure = False,    # True for prod env
                                httponly= True )
            
            return response
        
        except Exception as e:
            return jsonify({
                "success" : False,
                "message" : "Internal Server Error (otp api)",
                "error" : str(e)
            }),500

# book and reserve the spot 
@app.route("/reserve", methods = ['POST','PUT', 'OPTIONS'] )
def reserve():
    if request.method == 'POST':
        # try:
        #     data = request.get_json()
        #     if data is None:
        #         return jsonify({
        #             "success" : False,
        #             "message" : "No data retrieved in request"
        #         })
            
        #     token = request.cookies.get("token")
        #     decoded = jwt.decode(token, os.getenv("JWT_SECRET"), algorithms="HS256")
        #     if not decoded or decoded is None:
        #         return jsonify({
        #             "success" : False,
        #             "message" : "Token expired"
        #         }), 402

        #     name = data.get("name")
        #     start_time = data.get("start_time")
        #     end_time = data.get("end_time")
        #     vehicle_registration_number = data.get("vehicle_registration_number")

        #     # validate registraion number
        #     pattern = r'^[A-Z]{2}[0-9]{2}[A-Z]{1,2}[0-9]{4}$'
        #     if re.match(pattern , vehicle_registration_number) == False:
        #         return jsonify({
        #             "success" : False, 
        #             "message" : "Use Indian registration number format"
        #         }), 402

        #     # find the first empty slot in the chosen lot
        #     location = ParkingLocation.query.filter_by(name = name).first()
        #     slot = ParkingSlot.query.filter_by(is_covered = 0, 
        #                                        location_id = location.location_id).first() 

        #     if slot is None or not slot:
        #         return jsonify({
        #             "success": False,
        #             "message": "Slot under renovation"
        #         }), 402
                       

        #     reservation = Reservation(
        #             user_id = decoded['user_id'],
        #             slot_id = slot.slot_id,
        #             location_id = slot.location_id,
        #             start_time = datetime.fromisoformat(start_time),
        #             end_time = datetime.fromisoformat(end_time),
        #             vehicle_registration_number = vehicle_registration_number
        #         )
        #     db.session.add( reservation )
        #     db.session.flush()
        #     db.session.commit()
        #     cache_delete(f"userdashboard:{decoded['user_id']}")

        #     return jsonify({
        #         "success" : True,
        #         "message" : "Seat reserved successfully",
        #         "reservation_id": reservation.reservation_id,
        #     }), 200
        try:
            data = request.get_json()
            if data is None:
                return jsonify({
                    "success" : False,
                    "message" : "No data retrieved in request"
                })
            
            token = request.cookies.get("token")
            decoded = jwt.decode(token, os.getenv("JWT_SECRET"), algorithms="HS256")
            if not decoded or decoded is None:
                return jsonify({
                    "success" : False,
                    "message" : "Token expired"
                }), 402

            print(data)
            name = data.get("name")
            start_time = parse_time(data.get("start_time"))
            end_time = parse_time(data.get("end_time"))

            vehicle_registration_number = data.get("vehicle_registration_number")

            # validate registraion number
            pattern = r'^[A-Z]{2}[0-9]{2}[A-Z]{1,2}[0-9]{4}$'
            if re.match(pattern , vehicle_registration_number) == False:
                return jsonify({
                    "success" : False, 
                    "message" : "Use Indian registration number format"
                }), 402

            location = ParkingLocation.query.filter_by(name = name).first()
            slots = ParkingSlot.query.filter_by(location_id = location.location_id).all()


            allocated_slot = None
            for slot in slots:
                overlapping = (Reservation.query
                            .filter(Reservation.slot_id == slot.slot_id)
                            .filter(
                                (Reservation.start_time < start_time) &
                                (Reservation.end_time > end_time)
                            ).first())
                

                if not overlapping:
                    allocated_slot = slot
                    print("loop break", allocated_slot)
                    break

            if allocated_slot is None:
                return jsonify({
                    "success": False,
                    "message": "No available slot for the selected time range"
                }), 402
            
            print("reserve the seat")
            
            reservation = Reservation(
                user_id=decoded['user_id'],
                slot_id=allocated_slot.slot_id,
                location_id=allocated_slot.location_id,
                start_time=start_time,
                end_time=end_time,
                vehicle_registration_number=vehicle_registration_number
            )
            db.session.add(reservation)
            db.session.flush()
            db.session.commit()
            cache_delete(f"userdashboard:{decoded['user_id']}")

            print("Reservation ID", reservation.reservation_id)
            return jsonify({
                "success" : True,
                "message" : "Seat reserved successfully",
                "reservation_id": reservation.reservation_id,
            }), 200
           
        except Exception as e:
            return jsonify({
                "success" : False,
                "message" : "Internal Server Error (reserve post api)",
                "error" : str(e)
            }), 500      
    elif request.method == 'PUT':
        try:
            token = request.cookies.get("token")
            decoded = jwt.decode(token, os.getenv("JWT_SECRET"), algorithms=["HS256"])
            if decoded is None:
                return jsonify({
                    "success": False,
                    "message": "Token expired"
                }), 402

            data = request.get_json()
            new_status = data.get("new_status")
            location_name = data.get("location_name")

            print(data)
            
            location = ParkingLocation.query.filter_by(name = location_name).first()

            reservation = Reservation.query.filter_by(user_id=decoded['user_id'], 
                                                      location_id = location.location_id) \
                                            .first()
            
            
            if not reservation:
                return jsonify({
                    "success": False,
                    "message": "Reservation not found"
                }), 401

            reservation.status = new_status

            db.session.commit()
            cache_delete(f"userdashboard:{decoded['user_id']}")

            return jsonify({
                "success": True,
                "message": f"Reservation status updated to {new_status}"
            }), 200

        except Exception as e:
            return jsonify({
                "success": False,
                "message": "Internal Server Error (reserve PUT API)",
                "error": str(e)
            }), 500
    elif request.method == 'OPTIONS':
        return '', 200
    
# get all the reviews in the DB
@app.route("/get-reviews", methods = ['GET'] )
def reviews():
    try:
        results = db.session.query(
        User.username,
        Review.rating,
        Review.review_text
        ).join(Review, User.user_id == Review.user_id).all()

        reviews = []
        for username, rating, review_text in results:
            reviews.append({
                "username": username,
                "rating": rating,
                "review_text": review_text
            })

        return jsonify({
            "success" : True,
            "data": reviews
        }), 200
    
    except Exception as e:
        return jsonify({
            "success" : False,
            "message" : "Internal server error (get-reviews api)",
            "error" : str(e)
        }), 500
    
# presenting user dashboard
@app.route("/userdashboard", methods=["GET"])
def userdashboard():
        try:
            token = request.cookies.get("token")
            print(token)

            if not token:
                return jsonify({"success": False, "message": "Unauthorized User"}), 401
            
            decoded = jwt.decode(token, os.getenv("JWT_SECRET"), algorithms="HS256")
            if not decoded or decoded is None:
                    return jsonify({
                        "success" : False,
                        "message" : "Token expired"
                    }), 402
            
            cache_key = f"userdashboard:{decoded['user_id']}"
            cache_data = cache_get(cache_key)
            
            if cache_data:
                return jsonify({
                    "success" : True,
                    "message": "Dashboard data fetched successfully from REDIS",
                    "data" : cache_data
                }), 200
            
            user = User.query.filter_by( user_id = decoded['user_id'] ).first()
            if not user:
                return jsonify({"success": False, "message": "Couldn't find you in DB"}), 401
            user_id = user.user_id


            total_bookings = Reservation.query.filter_by(user_id=user_id).count()

            # Total parked hours (Released bookings only)
            released_reservations = Reservation.query.filter_by(user_id=user_id, status='available').all()
            
            total_seconds = sum((res.end_time - res.start_time).total_seconds() for res in released_reservations)
            total_hours_parked = round(total_seconds / 3600, 2)

            # Active bookings count (status = "Occupied")
            active_bookings = Reservation.query.filter_by(user_id=user_id, status='occupied').count()

            # Most visited parking location
            most_visited = (
                db.session.query(Reservation.location_id, func.count().label('count'))
                .filter_by(user_id=user_id)
                .group_by(Reservation.location_id)
                .order_by(func.count().desc())
                .first()
            )

            location_name = "N/A"
            if most_visited:
                location = ParkingLocation.query.get(most_visited.location_id)
                location_name = location.name if location else "Unknown"

            # Monthly booking count
            monthly_data = (
                db.session.query(
                    func.strftime('%Y-%m', Reservation.start_time).label('month'),
                    func.count().label('count')
                )
                .filter_by(user_id=user_id)
                .group_by('month')
                .order_by('month')
                .all()
            )

            monthly_chart_data = [{"month": month, "count": count} for month, count in monthly_data]

            cache_set(cache_key, {
                "first_name": user.first_name,
                "total_bookings": total_bookings,
                "total_hours_parked": total_hours_parked,
                "active_bookings": active_bookings,
                "most_visited_location": location_name,
                "monthly_chart_data": monthly_chart_data
            }, 120)

            return jsonify({
                "first_name": user.first_name,
                "total_bookings": total_bookings,
                "total_hours_parked": total_hours_parked,
                "active_bookings": active_bookings,
                "most_visited_location": location_name,
                "monthly_chart_data": monthly_chart_data
            })
        except Exception as e:
            return jsonify({
                "success": False, 
                "error": str(e), 
                "message" :"Internal Server Error (in userdashboard route)"
                }), 500

# fetches the user data to display in the dashboard
@app.route("/userdatadownload", methods=["GET"])
def download_user_data():
    try:
        token = request.cookies.get("token")
        # print(token)
        if not token:
            return jsonify({"success": False, "message": "Unauthorized User"}), 401
                
        decoded = jwt.decode(token, os.getenv("JWT_SECRET"), algorithms="HS256")
        if not decoded or decoded is None:
            return jsonify({
                "success" : False,
                "message" : "Token expired"
            }), 401
        user = User.query.filter_by( user_id = decoded['user_id'] ).first()
        # print(user, decoded)
        if not user:
            return jsonify({"success": False, "message": "Couldn't find you in DB"}), 401
        
        # print("USER", user)


        # Fetching data via ascending order of the start time 
        reservations = Reservation.query.filter_by(user_id=user.user_id).order_by(Reservation.start_time.desc()).all()
        

        # print("Reservations", reservations )


        reviews = Review.query.filter_by(user_id=user.user_id).all()

        # print("Reviews", reviews)


        # Summarizing
        total_reservations = len(reservations)
        total_locations = len(set(r.location_id for r in reservations))
        total_slots = len(set(r.slot_id for r in reservations))
        # user_reservations = Reservation.query.filter_by(user_id = user.user_id).all()
        total_amount = 0
        for reservation in reservations:
            # print(reservation)
            payment = Payment.query.filter_by(reservation_id = reservation.reservation_id).first() # update this 
            # print(payment)
            total_amount += payment.amount
            # print("\n")
        
        # print(total_amount, total_locations, total_reservations, total_slots)

        total_hours = sum(
            ((r.end_time - r.start_time).total_seconds() / 3600)
            for r in reservations
            if r.start_time and r.end_time
        )
        avg_duration = total_hours / total_reservations if total_reservations else 0

        # print("hoga")

        # PDF Setup
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        elements = []

        # Header
        header_style = styles["Title"]
        header = Paragraph("KwikPark - Parking Report", header_style)
        elements.append(header)
        elements.append(Spacer(1, 12))
        elements.append(Paragraph("Contact: support@kwikpark.com", styles["Normal"]))
        elements.append(Spacer(1, 20))

        # User Info
        elements.append(Paragraph(f"Name: {user.first_name} {user.last_name}", styles["Heading4"]))
        elements.append(Paragraph(f"Email: {user.email}", styles["Normal"]))
        elements.append(Spacer(1, 12))

        # Reservations
        elements.append(Paragraph("Reservation History", styles["Heading2"]))
        month_map = {}

        for r in reservations:
            month = r.start_time.strftime("%B %Y")
            month_map.setdefault(month, []).append(r)

        for month in sorted(month_map.keys(), reverse=True):
            elements.append(Paragraph(month, styles["Heading3"]))
            data = [["Location", "Slot", "In", "Out", "Amount"]]
            for r in month_map[month]:
                in_time = r.start_time.strftime("%d %b, %Y %H:%M") if r.start_time else "-"
                out_time = r.end_time.strftime("%d %b, %Y %H:%M") if r.end_time else "-"
                location = ParkingLocation.query.get(r.location_id)
                slot = ParkingSlot.query.get(r.slot_id)
                payment = Payment.query.filter_by(reservation_id = r.reservation_id).first()

                # print(location, slot, payment)

                data.append([
                    location.name if location.name else "N/A",
                    slot.slot_number if slot.slot_number else "N/A",
                    in_time,
                    out_time,
                    f"Rs. {payment.amount:.2f}" if payment.amount else "N/A"
                ])
            t = Table(data, hAlign='LEFT')
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                ('GRID', (0, 0), (-1, -1), 1, colors.gray),
            ]))
            elements.append(t)
            elements.append(Spacer(1, 12))

        # Reviews
        if reviews:
            elements.append(Paragraph("Reviews", styles["Heading2"]))
            for r in reviews:
                elements.append(Paragraph(f"Rating: {r.rating}/5 - {r.review_text}", styles["Normal"]))
                elements.append(Spacer(1, 6))

        # Summary
        elements.append(Spacer(1, 24))
        elements.append(Paragraph("Summary", styles["Heading2"]))
        summary_data = [
            ["Total Reservations Made", total_reservations],
            ["Total Locations Used", total_locations],
            ["Total Slots Booked", total_slots],
            ["Average Parking Duration (hrs)", f"{avg_duration:.2f}"],
            ["Total Amount Paid", f"Rs. {total_amount:.2f}"]
        ]
        summary_table = Table(summary_data, hAlign='LEFT')
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(summary_table)

        # Build PDF
        doc.build(elements)
        buffer.seek(0)

        return send_file(
            buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'{user.first_name}_kwikpark_report.pdf'
        )
    except Exception as err:
        return jsonify({
            "success" : False ,
            "message" : "Internal Server Error (User data download api)",
            "error": str(err)
        }), 500

# fetches the upcoming bookings for a user to display 
# in the dashboard
@app.route('/userupcomingbookings', methods=['GET'])
def get_upcoming_bookings():
    try:
        token = request.cookies.get("token")
        if not token:
            return jsonify({"success": False, "message": "Unauthorized User"}), 402
                
        decoded = jwt.decode(token, os.getenv("JWT_SECRET"), algorithms="HS256")
        if not decoded or decoded is None:
            return jsonify({
                "success" : False,
                "message" : "Token expired"
            }), 401
        user = User.query.filter_by( user_id = decoded['user_id'] ).first()
        if not user:
            return jsonify({"success": False, "message": "Couldn't find you in DB"}), 401
        
        now = datetime.now()

        upcoming = Reservation.query.filter(
            Reservation.user_id == user.user_id,
            Reservation.start_time > now,
            Reservation.status != 'cancelled'  # optional
        ).order_by(Reservation.start_time.asc()).all()

        result = []

        for b in upcoming:
            location = ParkingLocation.query.filter_by(location_id = b.location_id).first()
            slot = ParkingSlot.query.filter_by(slot_id = b.slot_id).first()
            result.append({
                "location": location.name,
                "slot": slot.slot_number,
                "start_time": b.start_time.isoformat(),
                "end_time": b.end_time.isoformat(),
                "status": b.status
            })

        return jsonify(result), 200
    except Exception as err:
        return jsonify({
            "success": False,
            "message": "Internal Server Error (in upcoming booking api)",
            "error": str(err)
        }), 500

# user makes the payment
@app.route('/payment', methods=['POST'])
def create_payment():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "No data provided"}), 401

        # Extract fields from request
        reservation_id = data.get("reservation_id")
        amount = data.get("amount")
        payment_method = data.get("payment_method")
        payment_status = data.get("payment_status")
        transaction_id = data.get("transaction_id")

        # Validate required fields
        if not all([reservation_id, amount, payment_method, payment_status]):
            return jsonify({"success": False, "message": "Missing required payment fields"}), 401

        # Check if reservation exists
        reservation = Reservation.query.get(reservation_id)
        if not reservation:
            return jsonify({"success": False, "message": "Reservation not found"}), 404

        # Create Payment entry
        new_payment = Payment(
            reservation_id=reservation_id,
            amount=amount,
            payment_method=payment_method,
            payment_status=payment_status,
            payment_date=datetime.now(),
            transaction_id=transaction_id
        )

        db.session.add(new_payment)
        db.session.commit()
        cache_delete(f"userdashboard:{Reservation.user_id}")

        return jsonify({
            "success": True,
            "message": "Payment recorded successfully",
            "payment_id": new_payment.payment_id
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": "Internal Server Error (create payment)",
            "error": str(e)
        }), 500




# APIs USED BY ADMIN



# create lot
@app.route("/createlot", methods = ['POST'])
def clot():
    if request.method == 'POST':
        try:
            data = request.get_json()
            if data is None:
                return jsonify({
                    "success" : False,
                    "message" : "No data retrieved in request"
                }),401
            
            new_location = ParkingLocation(
                    name = data.get("name"),
                    address_line1 = data.get("address_line1"),
                    address_line2 = data.get("address_line2"),
                    city = data.get("city"),
                    state = data.get("state"),
                    postal_code = data.get("postal_code"),
                    country = data.get("country"),
                    phone = data.get("phone"),
                    total_slots = data.get("total_slots"),
                    hourly_rate = data.get("hourly_rate"),
                    is_active = data.get("is_active")
                )
            
            db.session.add(new_location)
            db.session.flush()


            
            for i in range(1, new_location.total_slots + 1):
                slot = ParkingSlot(slot_number=f"S{i}", vehicle_type_id = 1, location_id=new_location.location_id, is_covered=0)
                db.session.add(slot)
            db.session.commit()

            return jsonify({
                "success" : True,
                "message" : "Lot created successfully"
            }),200
        except Exception as e:
            return jsonify({
                "success" : False,
                "message" : "Internal Server Error (create-lot api)"
            }),500

# def elot():
#     if request.method == 'PUT':
#         try:
#             data = request.get_json()
#             if data is None:
#                 return jsonify({
#                     "success" : False,
#                     "message" : "No data retrieved in request"
#                 }),401
            
#             db.session.add(
#                 ParkingLocation(
#                     name = data.get("name"),
#                     address_line1 = data.get("address_line1"),
#                     address_line2 = data.get("address_line2"),
#                     city = data.get("city"),
#                     state = data.get("state"),
#                     postal_code = data.get("postal_code"),
#                     country = data.get("country"),
#                     phone = data.get("phone"),
#                     total_slots = data.get("total_slots"),
#                     hourly_rate = data.get("hourly_rate"),
#                     is_active = data.get("is_active")
#                 ))
#             db.session.commit()

#             return jsonify({
#                 "success" : True,
#                 "message" : "Lot updated successfully"
#             }),200
        
#         except Exception as e:
#             print(str(e))
#             return jsonify({
#                 "success" : False,
#                 "message" : "Internal Server Error (edit-lot api)",
#                 "error" : str(e)
#             }),500
@app.route('/editlot', methods=['PUT'])
def edit_lot():
    try:
        data = request.get_json()

        lot_id = data.get("lot_id") 
        if not lot_id:
            return jsonify({"success": False, "message": "Lot ID is required"}), 400

        lot = ParkingLocation.query.get(lot_id)
        if not lot:
            return jsonify({"success": False, "message": "Lot not found"}), 404

        lot.name = data.get("name", lot.name)
        lot.address_line1 = data.get("address_line1", lot.address_line1)
        lot.address_line2 = data.get("address_line2", lot.address_line2)
        lot.city = data.get("city", lot.city)
        lot.state = data.get("state", lot.state)
        lot.postal_code = data.get("postal_code", lot.postal_code)
        lot.country = data.get("country", lot.country)
        lot.phone = data.get("phone", lot.phone)
        lot.total_slots = data.get("total_slots", lot.total_slots)
        lot.hourly_rate = data.get("hourly_rate", lot.hourly_rate)
        lot.is_active = data.get("is_active", lot.is_active)

        db.session.commit()

        return jsonify({"success": True, "message": "Lot updated successfully"}), 200
    except Exception as err:
        print(str(err))
        return jsonify({
            "success": False,
            "message" : "Internal Server Error (at edit lot)",
            "error" : str(err)
        }), 500
    
# delete lot
@app.route("/deletelot", methods = ['POST'])
def dlot():
    if request.method == 'POST':
        try:
            data = request.get_json()
            if data is None:
                return jsonify({
                    "success" : False,
                    "message" : "No data retrieved in request"
                }), 401
            
            name = data.get("name")
            lot = ParkingLocation.query.filter_by(name = name).first()
            slots = ParkingSlot.query.filter_by(location_id = lot.location_id).all()
            
            # check if all slots are empty in the lot
            if len(slots) > 0:
                return jsonify({
                    "success" : False,
                    "message" : "Cannot delete the slot unless empty"
            }), 402
            
            db.session.delete(lot)
            db.session.commit()

            cache_delete("admindashboard:Girmada")

            return jsonify({
                "success" : True,
                "message" : "Lot deleted successfully"
            }), 200
        
        except Exception as e:
            return jsonify({
                "success" : False,
                "message" : "Internal Server Error (delete-lot)",
                "error" : str(e)
            }), 500


# get all lots 
@app.route("/getlot", methods = ['GET'])
def glot():
    try:
        results = (
            db.session.query(
                ParkingLocation.name.label("lot_name"),
                ParkingLocation.city,
                ParkingLocation.country,
                ParkingLocation.state,
                ParkingLocation.postal_code,
                ParkingLocation.total_slots,
                ParkingLocation.hourly_rate,
                func.group_concat(ParkingSlot.slot_number).label("occupied_slots")
            )
            .outerjoin(
                ParkingSlot, 
                (ParkingSlot.location_id == ParkingLocation.location_id) &
                (ParkingSlot.is_covered == 1))
            .outerjoin(
                Reservation,
                (Reservation.slot_id == ParkingSlot.slot_id) &
                (Reservation.status == 'occupied')
            )
            .group_by(
                ParkingLocation.name,
                ParkingLocation.city,
                ParkingLocation.country,
                ParkingLocation.state,
                ParkingLocation.postal_code,
                ParkingLocation.total_slots,
                ParkingLocation.hourly_rate
            )
            .all()
        )
        location_slots = {}

        for row in results:
            location_slots[row.lot_name] = {
                "city": row.city,
                "country": row.country,
                "state": row.state,
                "postal_code": row.postal_code,
                "total_slots": row.total_slots,
                "hourly_rate": float(row.hourly_rate),
                "occupied_slots": row.occupied_slots.split(",") if row.occupied_slots else []
            }

        return jsonify({
                    "success" : True,
                    "message" : "Lot & slots data gathered",
                    "data" : location_slots
            }), 200
    
    except Exception as e:
        return jsonify({
            "success" : False,
            "message" : "Internal Server Error",
            "error" : str(e)
        }), 500
        
# get all users
@app.route("/getusers", methods = ['GET'])
def gusers():
    try:
        users = User.query.all()

        if len(users) == 0:
            return jsonify({
                "success" : False,
                "message"  : "No data available"
            })
        
        user_list = []
        for user in users:
            user_list.append({
                "user_id": user.user_id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "phone": user.phone,
                "is_admin": user.is_admin,
                "created_at": user.created_at.isoformat(),
                "updated_at": user.updated_at.isoformat()
            })

        return jsonify({
            "success" : True,
            "message"  : "User data gathered",
            "data" : user_list
        }), 200
    
    except Exception as e:
        return jsonify({
            "success" : False,
            "message"  : "Internal Server Error",
            "error"  : str(e)
        }), 500

# get all reservation data
@app.route("/getreservations", methods = ['GET'])  
def greservations():
    try:
        reservations = (
            db.session.query(Reservation)
            .join(User, Reservation.user_id == User.user_id)
            .join(ParkingLocation, Reservation.location_id == ParkingLocation.location_id)
            .join(ParkingSlot, Reservation.slot_id == ParkingSlot.slot_id)
            .all()
        )

        result = []
        for r in reservations:
            user = User.query.get(r.user_id)
            slot = ParkingSlot.query.get(r.slot_id)
            location = ParkingLocation.query.get(r.location_id)

            result.append({
                "reservation_id": r.reservation_id,
                "user": {
                    "user_id": user.user_id,
                    "username": user.username,
                    "email": user.email
                } if user else None,
                "lot": location.name if location else None,
                "slot": slot.slot_number if slot else None,
                "status": r.status,
                "vehicle_registration_number": r.vehicle_registration_number,
                "start_time": r.start_time.isoformat(),
                "end_time": r.end_time.isoformat()
            })


        return jsonify({
            "success": True,
            "message": "Reservations fetched successfully",
            "reservations": result
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "message": "Internal Server Error (get-reservations)",
            "error": str(e)
        }), 500

# get overall metrics 
@app.route("/admindashboard", methods = ["GET"])  
def admindashboard():
    try:

        cache_key = f"admindashboard:Girmada"
        cache_data = cache_get(cache_key)
        if cache_data:
            return jsonify({
                "success": True,
                "message" : "Data fetched successfully from REDIS",
                "metrics" : cache_data
            }), 200

        total_users = db.session.query(func.count(User.user_id)).scalar()
        total_reservations = db.session.query(func.count(Reservation.reservation_id)).scalar()
        total_revenue = db.session.query(func.coalesce(func.sum(Payment.amount), 0)).scalar()
        active_lots = db.session.query(func.count(ParkingLocation.location_id)).filter(ParkingLocation.is_active == True).scalar()
        total_slots = db.session.query(func.count(ParkingSlot.slot_id)).scalar()
        occupied_slots = db.session.query(func.count(Reservation.reservation_id))\
                                   .filter(Reservation.status.in_(["booked", "occupied"])).scalar()
        available_slots = total_slots - occupied_slots if total_slots else 0

        metrics = {
            "total_users": total_users,
            "total_reservations": total_reservations,
            "total_revenue": float(total_revenue),
            "active_parking_lots": active_lots,
            "total_slots": total_slots,
            "occupied_slots": occupied_slots,
            "available_slots": available_slots
        }

        cache_set("admindashboard:Girmada", metrics, 120)

        return jsonify({
            "success": True,
            "message": "Admin dashboard metrics fetched successfully",
            "metrics": metrics
        }), 200

    except Exception as e:
        print("Error in Admindashboard route", str(e))
        return jsonify({
            "success": False,
            "message": f"Error fetching dashboard metrics: {str(e)}"
        }), 500    
    
# get lot statistics
@app.route("/lotstats", methods=["GET"])  
def lot_stats():
    try:
        lots = db.session.query(ParkingLocation).all()
        stats = []

        for lot in lots:
            
            total_slots = db.session.query(func.count(ParkingSlot.slot_id))\
                                    .filter(ParkingSlot.location_id == lot.location_id).scalar()

            
            occupied_slots = db.session.query(func.count(Reservation.reservation_id))\
                                       .filter(Reservation.location_id == lot.location_id,
                                               Reservation.status.in_(["booked", "occupied"]))\
                                       .scalar()

            
            revenue = db.session.query(func.coalesce(func.sum(Payment.amount), 0))\
                                .join(Reservation, Payment.reservation_id == Reservation.reservation_id)\
                                .filter(Reservation.location_id == lot.location_id).scalar()

            
            reservations = db.session.query(func.count(Reservation.reservation_id))\
                                     .filter(Reservation.location_id == lot.location_id).scalar()

            stats.append({
                "lot_id": lot.location_id,
                "lot_name": lot.name,
                "city": lot.city,
                "total_slots": total_slots,
                "occupied_slots": occupied_slots,
                "available_slots": total_slots - occupied_slots,
                "total_reservations": reservations,
                "total_revenue": float(revenue)
            })

        return jsonify({
            "success": True,
            "message": "Per-lot statistics fetched successfully",
            "lot_stats": stats
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error fetching per-lot stats: {str(e)}"
        }), 500

# get user statistics
@app.route("/userstats", methods=["GET"])  
def user_stats():
    try:
        now = datetime.now()
        thirty_days_ago = now - timedelta(days=30)
        total_users = db.session.query(func.count(User.user_id)).filter_by(is_admin=False).scalar()

        # last 30 day users
        new_users = db.session.query(func.count(User.user_id)).filter(
            User.is_admin == False,
            User.created_at >= thirty_days_ago
        ).scalar()

        # Active users (made at least 1 reservation in last 30 days)
        active_users = db.session.query(func.count(func.distinct(Reservation.user_id))).filter(
            Reservation.start_time >= thirty_days_ago
        ).scalar()

        # Top 5 users with most reservations
        top_users = db.session.query(
            User.username,
            func.count(Reservation.reservation_id).label("reservation_count")
        ).join(Reservation, Reservation.user_id == User.user_id)\
         .filter(User.is_admin == False)\
         .group_by(User.username)\
         .order_by(func.count(Reservation.reservation_id).desc())\
         .limit(5).all()

        top_users_list = [{"username": u, "reservations": c} for u, c in top_users]

        return {
            "success": True,
            "message": "User stats fetched successfully",
            "data": {
                "total_users": total_users,
                "new_users_this_month": new_users,
                "active_users": active_users,
                "top_users": top_users_list
            }
        }, 200

    except Exception as e:
        return {"success": False, "message": str(e)}, 500
    
# get financial statistics
@app.route("/financialstats", methods=["GET"])  
def financial_stats():
    try:
        now = datetime.now()
        thirty_days_ago = now - timedelta(days=30)

        # Total revenue
        total_revenue = db.session.query(func.coalesce(func.sum(Payment.amount), 0)).scalar()

        # Revenue in last 30 days
        revenue_this_month = db.session.query(func.coalesce(func.sum(Payment.amount), 0)).filter(
            Payment.payment_date >= thirty_days_ago
        ).scalar()

        # Payment method breakdown
        method_breakdown_query = db.session.query(
            Payment.payment_method,
            func.count(Payment.payment_id).label("count"),
            func.sum(Payment.amount).label("total_amount")
        ).group_by(Payment.payment_method).all()

        payment_method_breakdown = [
            {
                "method": m,
                "count": c,
                "total_amount": float(a)
            } for m, c, a in method_breakdown_query
        ]

        # Latest 5 transactions
        latest_txn_query = db.session.query(
            Payment.payment_id,
            Payment.amount,
            Payment.payment_method,
            Payment.payment_status,
            Payment.payment_date,
            Payment.transaction_id,
            User.username,
            ParkingLocation.name.label("lot")
        ).join(Reservation, Reservation.reservation_id == Payment.reservation_id)\
         .join(User, User.user_id == Reservation.user_id)\
         .join(ParkingLocation, ParkingLocation.location_id == Reservation.location_id)\
         .order_by(Payment.payment_date.desc())\
         .limit(5).all()

        latest_transactions = [
            {
                "payment_id": p.payment_id,
                "amount": float(p.amount),
                "method": p.payment_method,
                "status": p.payment_status,
                "date": p.payment_date.isoformat(),
                "transaction_id": p.transaction_id,
                "user": p.username,
                "lot": p.lot
            } for p in latest_txn_query
        ]

        return {
            "success": True,
            "message": "Financial stats fetched successfully",
            "data": {
                "total_revenue": float(total_revenue),
                "revenue_this_month": float(revenue_this_month),
                "payment_method_breakdown": payment_method_breakdown,
                "latest_transactions": latest_transactions
            }
        }, 200

    except Exception as e:
        return {"success": False, "message": str(e)}, 500