from backend import celery, db
from backend.models import User
from backend.common import send_email_html
import os



@celery.task(name="send_daily_reminders")
def send_daily_reminders():
    users = User.query.all()
    for user in users:
        if not user.has_visited_today():
            html_message = f"""
            <h3>Hi {user.first_name or user.username},</h3>
            <p>We noticed you haven't booked a parking spot today.</p>
            <p>Reserve your spot now to avoid last-minute hassle!</p>
            <br><p>– KwikPark Team</p>
            """
            send_email_html(user.email, "Parking Reminder", html_message)
    return "Daily reminder emails sent."