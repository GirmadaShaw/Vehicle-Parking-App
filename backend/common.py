import random
import os
from datetime import datetime
import smtplib as smtp
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from smtplib import SMTP, SMTPRecipientsRefused, SMTPAuthenticationError, SMTPException


def parse_time(time_str):
    try:
        return datetime.fromisoformat(time_str) 
    except ValueError:
        return datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")

def generateOTP():
    return ''.join(str(random.randint(0, 9)) for _ in range(4))

def send_email(email):
    sender_email = "girmadasingh@gmail.com"
    receiver_email = email
    otp = generateOTP()

    subject = "Verification Check From KwikPark"
    message = f'OTP for verification is: {otp}'
    text = f"Subject: {subject}\n\n{message}"

    try:
        password = os.getenv('GMAIL_PASSWORD')
        if not password:
            print("Pur your password in ENV")
            raise RuntimeError("Email password not configured in environment.")

        server = smtp.SMTP('smtp.gmail.com', 587)
        server.starttls()
        # server.set_debuglevel(1)  // check logs 
        server.login(sender_email, password)

        server.sendmail(sender_email, receiver_email, text)
        server.quit()

        return otp

    except SMTPRecipientsRefused:
        raise ValueError("Invalid email address. Please enter a valid one.")
    
    except SMTPAuthenticationError:
        raise ConnectionError("Authentication failed. Please check SMTP credentials.")
    
    except SMTPException as e:
        raise RuntimeError(f"Failed to send email: {str(e)}")


def send_email_html(to_email, subject, html_message):
    sender_email = "girmadasingh@gmail.com"
    receiver_email = to_email

    try:
        password = os.getenv("GMAIL_PASSWORD")
        if not password:
            raise RuntimeError("Email password not configured in environment.")

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = sender_email
        msg["To"] = receiver_email
        msg.attach(MIMEText(html_message, "html"))

        server = SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        print(f"Email sent to {receiver_email}")

    except SMTPRecipientsRefused:
        raise ValueError("Invalid email address.")
    except SMTPAuthenticationError:
        raise ConnectionError("Authentication failed. Check SMTP credentials.")
    except SMTPException as e:
        raise RuntimeError(f"Failed to send email: {str(e)}")
