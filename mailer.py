"""
mailer.py — Email Service for BOT-O-BRAIN
=========================================
Sends 6-digit OTP verification codes directly to user email addresses via SMTP.
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_EMAIL = os.getenv("SMTP_EMAIL", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")

def send_otp_email(recipient_email: str, otp_code: str, full_name: str = "User") -> bool:
    """
    Sends a 6-digit OTP verification email directly to recipient_email via SMTP.
    """
    load_dotenv(override=True)
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_email = os.getenv("SMTP_EMAIL", "").strip()
    smtp_password = os.getenv("SMTP_PASSWORD", "").strip()

    subject = f"Your BOT-O-BRAIN Verification Code: {otp_code}"
    
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; background-color: #FFF8F0; padding: 20px;">
        <div style="max-width: 500px; margin: 0 auto; background: #ffffff; border: 3px solid #1E1E24; border-radius: 16px; padding: 24px; box-shadow: 6px 6px 0px #1E1E24;">
            <h2 style="color: #FF6B6B; margin-bottom: 8px;">BOT-O-BRAIN Account Verification</h2>
            <p style="font-size: 15px; color: #333333;">Hi <strong>{full_name}</strong>,</p>
            <p style="font-size: 14px; color: #555555;">Thank you for registering! Please use the following 6-digit OTP code to verify your email address and activate your account:</p>
            <div style="background-color: #FFD166; border: 2px solid #1E1E24; border-radius: 12px; padding: 14px; text-align: center; margin: 20px 0;">
                <span style="font-size: 28px; font-weight: bold; letter-spacing: 6px; color: #1E1E24;">{otp_code}</span>
            </div>
            <p style="font-size: 13px; color: #777777;">If you did not request this code, please ignore this email.</p>
        </div>
    </body>
    </html>
    """

    if smtp_email and smtp_password:
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"BOT-O-BRAIN <{smtp_email}>"
            msg["To"] = recipient_email

            part_html = MIMEText(html_content, "html")
            msg.attach(part_html)

            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_email, smtp_password)
                server.sendmail(smtp_email, recipient_email, msg.as_string())
            print(f"[SUCCESS] OTP Email sent via SMTP to {recipient_email}")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to send email via SMTP to {recipient_email}: {e}")
            return False
    else:
        print(f"[ERROR] SMTP credentials (SMTP_EMAIL & SMTP_PASSWORD) not configured in .env.")
        return False

