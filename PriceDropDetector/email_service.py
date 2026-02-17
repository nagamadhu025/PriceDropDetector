"""
Email Service - Using Gmail API (More Reliable than SMTP)
"""

import pickle
import os
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from dotenv import load_dotenv


load_dotenv()

SENDER_EMAIL = os.getenv("EMAIL")  # nagamadhu025@gmail.com
TOKEN_PATH = os.getenv("TOKEN_PATH", "token.pkl")


def get_gmail_service():
    """Get authenticated Gmail API service"""
    creds = None

    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, "rb") as token_file:
            creds = pickle.load(token_file)

    # Refresh if expired
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            with open(TOKEN_PATH, "wb") as token_file:
                pickle.dump(creds, token_file)
            print("✅ Gmail token refreshed")
        except Exception as e:
            print(f"❌ Token refresh failed: {e}")
            return None

    if not creds or not creds.valid:
        print("❌ Invalid Gmail credentials")
        return None

    return build("gmail", "v1", credentials=creds)


def send_gmail(service, to_email, subject, html_content):
    """Send email via Gmail API"""
    try:
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = f"PriceDrop <{SENDER_EMAIL}>"
        message["To"] = to_email

        html_part = MIMEText(html_content, "html")
        message.attach(html_part)

        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

        service.users().messages().send(
            userId="me",
            body={"raw": raw}
        ).execute()

        return True

    except Exception as e:
        print(f"❌ Gmail API send failed: {e}")
        return False


def send_email(recipient_email, product_name, old_price, new_price):
    """Send price drop alert email via Gmail API"""
    try:
        service = get_gmail_service()
        if not service:
            return False

        savings = old_price - new_price
        discount_percent = ((savings / old_price) * 100) if old_price > 0 else 0

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
                margin: 0; padding: 0; width: 100% !important;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
                background-color: #f3f4f6;
              }}
              table {{ border-collapse: collapse; }}
              .email-container {{ max-width: 600px; margin: 0 auto; }}
              .header {{
                background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                padding: 30px 20px; text-align: center;
              }}
              .header-title {{
                color: white; font-size: 26px; font-weight: 700; margin: 0;
              }}
              .content {{ background: white; padding: 30px 20px; }}
              .product-name {{
                font-size: 18px; font-weight: 600; color: #111827;
                line-height: 1.5; margin: 0 0 25px 0; text-align: center;
              }}
              .price-card {{
                border-radius: 12px; padding: 20px;
                margin-bottom: 15px; text-align: center;
              }}
              .price-card.old {{
                background: #fee2e2; border: 2px solid #fecaca;
              }}
              .price-card.new {{
                background: #d1fae5; border: 2px solid #a7f3d0;
              }}
              .price-label {{
                font-size: 12px; text-transform: uppercase;
                letter-spacing: 1px; font-weight: 700; margin-bottom: 8px;
              }}
              .price-card.old .price-label {{ color: #991b1b; }}
              .price-card.new .price-label {{ color: #065f46; }}
              .price-amount {{ font-size: 36px; font-weight: 700; line-height: 1; }}
              .price-card.old .price-amount {{
                color: #dc2626; text-decoration: line-through;
              }}
              .price-card.new .price-amount {{ color: #059669; }}
              .arrow {{ text-align: center; font-size: 28px; color: #10b981; padding: 5px 0; }}
              .savings-box {{
                background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                border-radius: 12px; padding: 25px 20px;
                text-align: center; margin: 20px 0;
              }}
              .savings-label {{
                color: rgba(255,255,255,0.9); font-size: 12px;
                text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px;
              }}
              .savings-amount {{
                color: white; font-size: 40px; font-weight: 700;
                line-height: 1; margin-bottom: 8px;
              }}
              .savings-percent {{ color: rgba(255,255,255,0.9); font-size: 16px; font-weight: 600; }}
              .cta-button {{
                display: block;
                background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
                color: white !important; text-decoration: none;
                padding: 16px 32px; border-radius: 12px;
                font-size: 16px; font-weight: 600; text-align: center; margin: 20px 0;
              }}
              .info-box {{
                background: #fef3c7; border-left: 4px solid #f59e0b;
                padding: 15px; border-radius: 8px; margin: 15px 0;
              }}
              .info-box p {{ margin: 0; font-size: 14px; color: #92400e; line-height: 1.6; }}
              .footer {{
                background: #f9fafb; padding: 25px 20px; text-align: center;
              }}
              .footer p {{ margin: 5px 0; font-size: 13px; color: #6b7280; }}
              @media only screen and (max-width: 600px) {{
                .header-title {{ font-size: 22px; }}
                .product-name {{ font-size: 16px; }}
                .price-amount {{ font-size: 30px; }}
                .savings-amount {{ font-size: 32px; }}
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
                        <div style="font-size: 50px; line-height: 1; margin-bottom: 10px;">🎉</div>
                        <h1 class="header-title">Price Drop Alert!</h1>
                        <p style="color: rgba(255,255,255,0.9); font-size: 14px; margin: 8px 0 0 0;">
                          Your tracked product is now cheaper
                        </p>
                      </td>
                    </tr>
                    <tr>
                      <td class="content">
                        <h2 class="product-name">{product_name}</h2>

                        <div class="price-card old">
                          <div class="price-label">Was</div>
                          <div class="price-amount">₹{old_price:,.0f}</div>
                        </div>

                        <div class="arrow">↓</div>

                        <div class="price-card new">
                          <div class="price-label">Now</div>
                          <div class="price-amount">₹{new_price:,.0f}</div>
                        </div>

                        <div class="savings-box">
                          <div class="savings-label">You Save</div>
                          <div class="savings-amount">₹{savings:,.0f}</div>
                          <div class="savings-percent">{discount_percent:.1f}% OFF</div>
                        </div>

                        <a href="#" class="cta-button">🛒 Buy Now on Amazon</a>

                        <div class="info-box">
                          <p><strong>⚡ Act Fast!</strong> Amazon prices change frequently. This deal might not last long!</p>
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
            f"🎉 Price Drop: {product_name[:40]}...",
            html_content
        )

        if success:
            print(f"✅ Price alert email sent to {recipient_email}")
        return success

    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False


def send_target_price_alert(recipient_email, product_name, current_price, target_price):
    """Send target price reached alert via Gmail API"""
    try:
        service = get_gmail_service()
        if not service:
            return False

        html_content = f"""
        <!DOCTYPE html>
        <html>
          <head>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
            <style>
              body, table, td, a {{
                text-size-adjust: 100%; -webkit-text-size-adjust: 100%;
              }}
              body {{
                margin: 0; padding: 0; width: 100% !important;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
                background-color: #f3f4f6;
              }}
              table {{ border-collapse: collapse; }}
              .email-container {{ max-width: 600px; margin: 0 auto; }}
              .header {{
                background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
                padding: 30px 20px; text-align: center;
              }}
              .header-title {{ color: white; font-size: 26px; font-weight: 700; margin: 0; }}
              .content {{ background: white; padding: 30px 20px; }}
              .success-badge {{
                background: #d1fae5; border: 3px solid #10b981;
                border-radius: 12px; padding: 20px;
                text-align: center; margin-bottom: 25px;
              }}
              .success-badge h2 {{ margin: 0; color: #065f46; font-size: 20px; font-weight: 700; }}
              .product-name {{
                font-size: 18px; font-weight: 600; color: #111827;
                line-height: 1.5; margin: 0 0 25px 0; text-align: center;
              }}
              .price-box {{
                background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
                border-radius: 12px; padding: 30px 20px;
                text-align: center; margin: 20px 0;
              }}
              .price-label {{ color: rgba(255,255,255,0.9); font-size: 12px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px; }}
              .price-amount {{ color: white; font-size: 42px; font-weight: 700; line-height: 1; margin-bottom: 12px; }}
              .target-info {{ color: rgba(255,255,255,0.9); font-size: 14px; }}
              .cta-button {{
                display: block;
                background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                color: white !important; text-decoration: none;
                padding: 16px 32px; border-radius: 12px;
                font-size: 16px; font-weight: 600; text-align: center; margin: 20px 0;
              }}
              .info-box {{
                background: #fef3c7; border-left: 4px solid #f59e0b;
                padding: 15px; border-radius: 8px; margin: 15px 0;
              }}
              .info-box p {{ margin: 0; font-size: 14px; color: #92400e; line-height: 1.6; }}
              .footer {{ background: #f9fafb; padding: 25px 20px; text-align: center; }}
              .footer p {{ margin: 5px 0; font-size: 13px; color: #6b7280; }}
              @media only screen and (max-width: 600px) {{
                .header-title {{ font-size: 22px; }}
                .product-name {{ font-size: 16px; }}
                .price-amount {{ font-size: 34px; }}
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
                        <div style="font-size: 50px; line-height: 1; margin-bottom: 10px;">🎯</div>
                        <h1 class="header-title">Target Price Reached!</h1>
                        <p style="color: rgba(255,255,255,0.9); font-size: 14px; margin: 8px 0 0 0;">
                          Your patience paid off
                        </p>
                      </td>
                    </tr>
                    <tr>
                      <td class="content">
                        <div class="success-badge">
                          <h2>✅ Price Hit Your Target!</h2>
                        </div>

                        <h2 class="product-name">{product_name}</h2>

                        <div class="price-box">
                          <div class="price-label">Current Price</div>
                          <div class="price-amount">₹{current_price:,.0f}</div>
                          <div class="target-info">Your Target: ₹{target_price:,.0f}</div>
                        </div>

                        <a href="#" class="cta-button">🎉 Grab This Deal Now!</a>

                        <div class="info-box">
                          <p><strong>⚡ Perfect Timing!</strong> Price is now at or below your target. Great opportunity to buy!</p>
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
            f"🎯 Target Reached: {product_name[:40]}...",
            html_content
        )

        if success:
            print(f"✅ Target price alert sent to {recipient_email}")
        return success

    except Exception as e:
        print(f"❌ Failed to send target alert: {e}")
        return False
