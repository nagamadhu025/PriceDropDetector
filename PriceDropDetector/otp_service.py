"""
OTP Service - Using Gmail API (More Reliable than SMTP)
"""

import random
import pickle
import os
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

SENDER_EMAIL = os.getenv("EMAIL")  # nagamadhu025@gmail.com
TOKEN_PATH = os.getenv("TOKEN_PATH", "token.pkl")  # Path to token.pkl


def get_gmail_service():
    """Get authenticated Gmail API service"""
    creds = None

    # Load token.pkl
    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, "rb") as token_file:
            creds = pickle.load(token_file)

    # Refresh token if expired
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            # Save refreshed token
            with open(TOKEN_PATH, "wb") as token_file:
                pickle.dump(creds, token_file)
            print("✅ Gmail token refreshed")
        except Exception as e:
            print(f"❌ Token refresh failed: {e}")
            return None

    if not creds or not creds.valid:
        print("❌ Invalid Gmail credentials - token.pkl missing or expired")
        return None

    return build("gmail", "v1", credentials=creds)


def send_gmail(service, to_email, subject, html_content):
    """Send email via Gmail API"""
    try:
        # Create message
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = f"PriceDrop <{SENDER_EMAIL}>"
        message["To"] = to_email

        # Attach HTML
        html_part = MIMEText(html_content, "html")
        message.attach(html_part)

        # Encode message
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

        # Send via Gmail API
        service.users().messages().send(
            userId="me",
            body={"raw": raw}
        ).execute()

        return True

    except Exception as e:
        print(f"❌ Gmail API send failed: {e}")
        return False


def generate_otp():
    """Generate a 6-digit OTP code"""
    return str(random.randint(100000, 999999))


def send_otp_email(recipient_email, otp_code, user_name):
    """Send OTP verification email via Gmail API"""
    try:
        service = get_gmail_service()
        if not service:
            print("❌ Gmail service not available")
            return False

        html_content = f"""
        <!DOCTYPE html>
        <html>
          <head>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
            <style>
              body, table, td, a {{
                text-size-adjust: 100%;
                -webkit-text-size-adjust: 100%;
              }}
              body {{
                margin: 0;
                padding: 0;
                width: 100% !important;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
                background-color: #f3f4f6;
              }}
              table {{ border-collapse: collapse; }}
              .email-container {{ max-width: 600px; margin: 0 auto; }}
              .header {{
                background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
                padding: 40px 30px;
                text-align: center;
              }}
              .header h1 {{
                margin: 0;
                font-size: 28px;
                font-weight: 700;
                color: white;
              }}
              .content {{
                background: white;
                padding: 40px 30px;
              }}
              .otp-box {{
                background: #f3f4f6;
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
                font-size: 42px;
                font-weight: 700;
                color: #3b82f6;
                letter-spacing: 10px;
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
              @media only screen and (max-width: 600px) {{
                .otp-code {{ font-size: 32px; letter-spacing: 6px; }}
                .content {{ padding: 20px 15px; }}
              }}
            </style>
          </head>
          <body>
            <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
              <tr>
                <td align="center" style="padding: 20px 10px;">
                  <table role="presentation" class="email-container" width="600" cellpadding="0" cellspacing="0" border="0">
                    <tr>
                      <td class="header">
                        <h1>💰 PriceDrop</h1>
                        <p style="margin: 10px 0 0 0; opacity: 0.9; color: white;">Email Verification</p>
                      </td>
                    </tr>
                    <tr>
                      <td class="content">
                        <p style="font-size: 18px; color: #111827;">Hi {user_name},</p>
                        <p style="color: #374151;">Welcome to PriceDrop! 🎉</p>
                        <p style="color: #374151;">Use the code below to verify your email:</p>

                        <div class="otp-box">
                          <div class="otp-label">Your Verification Code</div>
                          <div class="otp-code">{otp_code}</div>
                        </div>

                        <p class="info">
                          This code expires in <strong>10 minutes</strong>.
                        </p>

                        <div class="warning">
                          <p>⚠️ <strong>Security Note:</strong> Never share this code with anyone.</p>
                        </div>
                      </td>
                    </tr>
                    <tr>
                      <td class="footer">
                        <p><strong>PriceDrop</strong> - Your Smart Price Tracker</p>
                        <p>© 2024 PriceDrop. All rights reserved.</p>
                      </td>
                    </tr>
                  </table>
                </td>
              </tr>
            </table>
          </body>
        </html>
        """

        success = send_gmail(
            service,
            recipient_email,
            "🔐 Verify Your PriceDrop Account",
            html_content
        )

        if success:
            print(f"✅ OTP email sent to {recipient_email}")
        return success

    except Exception as e:
        print(f"❌ Failed to send OTP email: {e}")
        return False


def get_otp_expiry():
    """Get OTP expiry time (10 minutes from now)"""
    return datetime.utcnow() + timedelta(minutes=10)
