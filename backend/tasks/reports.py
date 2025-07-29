from backend import celery
from backend.models import User, ParkingSlot
from backend.common import send_email_html
from datetime import datetime

@celery.task(name="generate_monthly_reports")
def generate_monthly_reports():
    """
    Generates a monthly HTML activity report for each user and sends via email.
    """
    users = User.query.all()

    for user in users:

        bookings = (ParkingSlot.query
                    .filter_by(user_id=user.user_id)
                    .all())
        
        monthly_bookings = [b for b in bookings if b.is_this_month()]
        total_spent = sum(b.cost for b in monthly_bookings)
        most_used = user.get_most_used_lot()

        report_html = f"""
        <html>
        <body>
            <h2>Monthly Parking Report - {datetime.now().strftime('%B %Y')}</h2>
            <p>Hi {user.first_name or user.username},</p>
            <p>Here's a summary of your parking activity this month:</p>
            <ul>
                <li><strong>Total Bookings:</strong> {len(monthly_bookings)}</li>
                <li><strong>Most Used Parking Lot:</strong> {most_used}</li>
                <li><strong>Total Amount Spent:</strong> ₹{total_spent}</li>
            </ul>
            <p>Thank you for using KwikPark. Keep booking conveniently!</p>
            <br>
            <p>- KwikPark Team</p>
        </body>
        </html>
        """

        send_email_html(user.email, "Your Monthly Parking Activity Report", report_html)

    return "Monthly reports generated and sent successfully."