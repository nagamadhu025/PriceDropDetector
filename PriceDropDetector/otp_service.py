"""
OTP Service - Generate and send verification codes
Configured for Gmail
"""

import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

load_dotenv()

# Email configuration - Using your Gmail
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = os.getenv("EMAIL")  # nagamadhu025@gmail.com
SENDER_PASSWORD = os.getenv("APP_PASSWORD")  # iovcuziyocufxbue


def generate_otp():
    """Generate a 6-digit OTP code"""
    return str(random.randint(100000, 999999))


def send_otp_email(recipient_email, otp_code, user_name):
    """Send OTP verification email"""
    try:
        # Create message
        message = MIMEMultipart("alternative")
        message["Subject"] = "🔐 Verify Your PriceDrop Account"
        message["From"] = f"PriceDrop <{SENDER_EMAIL}>"
        message["To"] = recipient_email

        # HTML email template
        html_content = f"""
        <html>
          <head>
            <style>
              body {{
                font-family: 'Segoe UI', Arial, sans-serif;
                background-color: #f5f7fa;
                margin: 0;
                padding: 0;
              }}
              .container {{
                max-width: 600px;
                margin: 40px auto;
                background: white;
                border-radius: 16px;
                overflow: hidden;
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
              }}
              .header {{
                background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
                padding: 40px 30px;
                text-align: center;
                color: white;
              }}
              .header h1 {{
                margin: 0;
                font-size: 28px;
                font-weight: 700;
              }}
              .content {{
                padding: 40px 30px;
              }}
              .greeting {{
                font-size: 18px;
                color: #111827;
                margin-bottom: 20px;
              }}
              .otp-box {{
                background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%);
                border: 2px dashed #3b82f6;
                border-radius: 12px;
                padding: 30px;
                text-align: center;
                margin: 30px 0;
              }}
              .otp-label {{
                font-size: 14px;
                color: #6b7280;
                text-transform: uppercase;
                letter-spacing: 1px;
                margin-bottom: 10px;
              }}
              .otp-code {{
                font-size: 36px;
                font-weight: 700;
                color: #3b82f6;
                letter-spacing: 8px;
                font-family: 'Courier New', monospace;
              }}
              .info {{
                color: #6b7280;
                font-size: 14px;
                line-height: 1.6;
                margin: 20px 0;
              }}
              .warning {{
                background: #fef3c7;
                border-left: 4px solid #f59e0b;
                padding: 15px;
                margin: 20px 0;
                border-radius: 8px;
              }}
              .warning p {{
                margin: 0;
                color: #92400e;
                font-size: 14px;
              }}
              .footer {{
                background: #f9fafb;
                padding: 30px;
                text-align: center;
                border-top: 1px solid #e5e7eb;
              }}
              .footer p {{
                margin: 5px 0;
                color: #6b7280;
                font-size: 13px;
              }}
            </style>
          </head>
          <body>
            <div class="container">
              <div class="header">
                <h1>💰 PriceDrop</h1>
                <p style="margin: 10px 0 0 0; opacity: 0.9;">Email Verification</p>
              </div>
              
              <div class="content">
                <p class="greeting">Hi {user_name},</p>
                
                <p>Welcome to PriceDrop! 🎉</p>
                
                <p>To complete your registration and start tracking amazing deals, please verify your email address using the code below:</p>
                
                <div class="otp-box">
                  <div class="otp-label">Your Verification Code</div>
                  <div class="otp-code">{otp_code}</div>
                </div>
                
                <p class="info">
                  This code will expire in <strong>10 minutes</strong>. 
                  Enter it on the verification page to activate your account.
                </p>
                
                <div class="warning">
                  <p>⚠️ <strong>Security Note:</strong> Never share this code with anyone. PriceDrop will never ask for your verification code via phone or email.</p>
                </div>
                
                <p class="info">
                  If you didn't request this verification code, please ignore this email.
                </p>
              </div>
              
              <div class="footer">
                <p><strong>PriceDrop</strong> - Your Smart Price Tracker</p>
                <p>Track prices • Get alerts • Save money</p>
                <p style="margin-top: 15px; font-size: 12px;">
                  © 2024 PriceDrop. All rights reserved.
                </p>
              </div>
            </div>
          </body>
        </html>
        """

        # Attach HTML content
        html_part = MIMEText(html_content, "html")
        message.attach(html_part)

        # Send email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(message)

        print(f"✅ OTP email sent to {recipient_email}")
        return True

    except Exception as e:
        print(f"❌ Failed to send OTP email: {e}")
        return False


def get_otp_expiry():
    """Get OTP expiry time (10 minutes from now)"""
    return datetime.utcnow() + timedelta(minutes=10)


# Test function
if __name__ == "__main__":
    print("Testing OTP email...")
    test_otp = generate_otp()
    print(f"Generated OTP: {test_otp}")
    
    # Test email send
    success = send_otp_email(
        "test@example.com",  # Replace with your email to test
        test_otp,
        "Test User"
    )
    
    if success:
        print("✅ Test email sent successfully!")
    else:
        print("❌ Test email failed!")