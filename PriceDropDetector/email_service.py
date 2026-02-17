"""
Email Service - Mobile-Optimized Price Alert Templates
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os

load_dotenv()

# Email configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = os.getenv("EMAIL")
SENDER_PASSWORD = os.getenv("APP_PASSWORD")


def send_email(recipient_email, product_name, old_price, new_price):
    """Send price drop alert email - Mobile optimized"""
    try:
        # Calculate savings
        savings = old_price - new_price
        discount_percent = ((savings / old_price) * 100) if old_price > 0 else 0

        message = MIMEMultipart("alternative")
        message["Subject"] = f"🎉 Price Drop: {product_name[:40]}..."
        message["From"] = f"PriceDrop <{SENDER_EMAIL}>"
        message["To"] = recipient_email

        html_content = f"""
        <!DOCTYPE html>
        <html>
          <head>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
            <style>
              /* Reset */
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
              table {{
                border-collapse: collapse;
              }}
              img {{
                border: 0;
                height: auto;
                line-height: 100%;
                outline: none;
                text-decoration: none;
              }}
              
              /* Container */
              .email-container {{
                max-width: 600px;
                margin: 0 auto;
              }}
              
              /* Header */
              .header {{
                background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                padding: 30px 20px;
                text-align: center;
              }}
              .header-emoji {{
                font-size: 60px;
                line-height: 1;
                margin-bottom: 10px;
              }}
              .header-title {{
                color: white;
                font-size: 26px;
                font-weight: 700;
                margin: 0;
                line-height: 1.3;
              }}
              .header-subtitle {{
                color: rgba(255,255,255,0.9);
                font-size: 14px;
                margin: 8px 0 0 0;
              }}
              
              /* Content */
              .content {{
                background: white;
                padding: 30px 20px;
              }}
              
              /* Product Name */
              .product-name {{
                font-size: 18px;
                font-weight: 600;
                color: #111827;
                line-height: 1.5;
                margin: 0 0 30px 0;
                text-align: center;
              }}
              
              /* Price Cards - Stacked on Mobile */
              .price-container {{
                margin-bottom: 20px;
              }}
              .price-card {{
                background: #f9fafb;
                border-radius: 12px;
                padding: 20px;
                margin-bottom: 15px;
                text-align: center;
              }}
              .price-card.old {{
                background: #fee2e2;
                border: 2px solid #fecaca;
              }}
              .price-card.new {{
                background: #d1fae5;
                border: 2px solid #a7f3d0;
              }}
              .price-label {{
                font-size: 12px;
                text-transform: uppercase;
                letter-spacing: 1px;
                font-weight: 700;
                margin-bottom: 10px;
              }}
              .price-card.old .price-label {{
                color: #991b1b;
              }}
              .price-card.new .price-label {{
                color: #065f46;
              }}
              .price-amount {{
                font-size: 36px;
                font-weight: 700;
                line-height: 1;
              }}
              .price-card.old .price-amount {{
                color: #dc2626;
                text-decoration: line-through;
              }}
              .price-card.new .price-amount {{
                color: #059669;
              }}
              
              /* Arrow */
              .arrow {{
                text-align: center;
                font-size: 32px;
                color: #10b981;
                margin: -10px 0;
              }}
              
              /* Savings Box */
              .savings-box {{
                background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                border-radius: 12px;
                padding: 25px 20px;
                text-align: center;
                margin: 25px 0;
              }}
              .savings-label {{
                color: rgba(255,255,255,0.9);
                font-size: 12px;
                text-transform: uppercase;
                letter-spacing: 1px;
                margin-bottom: 10px;
              }}
              .savings-amount {{
                color: white;
                font-size: 42px;
                font-weight: 700;
                line-height: 1;
                margin-bottom: 10px;
              }}
              .savings-percent {{
                color: rgba(255,255,255,0.9);
                font-size: 16px;
                font-weight: 600;
              }}
              
              /* Button */
              .cta-button {{
                display: block;
                background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
                color: white !important;
                text-decoration: none;
                padding: 16px 32px;
                border-radius: 12px;
                font-size: 16px;
                font-weight: 600;
                text-align: center;
                margin: 25px 0;
              }}
              
              /* Info Boxes */
              .info-box {{
                background: #fef3c7;
                border-left: 4px solid #f59e0b;
                padding: 15px;
                border-radius: 8px;
                margin: 15px 0;
              }}
              .info-box p {{
                margin: 0;
                font-size: 14px;
                color: #92400e;
                line-height: 1.6;
              }}
              
              /* Footer */
              .footer {{
                background: #f9fafb;
                padding: 25px 20px;
                text-align: center;
              }}
              .footer p {{
                margin: 5px 0;
                font-size: 13px;
                color: #6b7280;
              }}
              
              /* Mobile Specific */
              @media only screen and (max-width: 600px) {{
                .header-emoji {{
                  font-size: 48px;
                }}
                .header-title {{
                  font-size: 22px;
                }}
                .product-name {{
                  font-size: 16px;
                }}
                .price-amount {{
                  font-size: 32px;
                }}
                .savings-amount {{
                  font-size: 36px;
                }}
                .content {{
                  padding: 20px 15px;
                }}
              }}
            </style>
          </head>
          <body>
            <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
              <tr>
                <td align="center" style="padding: 20px 10px;">
                  <table role="presentation" class="email-container" width="600" cellpadding="0" cellspacing="0" border="0">
                    
                    <!-- Header -->
                    <tr>
                      <td class="header">
                        <div class="header-emoji">🎉</div>
                        <h1 class="header-title">Price Drop Alert!</h1>
                        <p class="header-subtitle">Your tracked product is now cheaper</p>
                      </td>
                    </tr>
                    
                    <!-- Content -->
                    <tr>
                      <td class="content">
                        <!-- Product Name -->
                        <h2 class="product-name">{product_name}</h2>
                        
                        <!-- Old Price -->
                        <div class="price-container">
                          <div class="price-card old">
                            <div class="price-label">Was</div>
                            <div class="price-amount">₹{old_price:,.0f}</div>
                          </div>
                          
                          <!-- Arrow -->
                          <div class="arrow">↓</div>
                          
                          <!-- New Price -->
                          <div class="price-card new">
                            <div class="price-label">Now</div>
                            <div class="price-amount">₹{new_price:,.0f}</div>
                          </div>
                        </div>
                        
                        <!-- Savings -->
                        <div class="savings-box">
                          <div class="savings-label">You Save</div>
                          <div class="savings-amount">₹{savings:,.0f}</div>
                          <div class="savings-percent">{discount_percent:.1f}% OFF</div>
                        </div>
                        
                        <!-- CTA Button -->
                        <a href="#" class="cta-button">🛒 Buy Now on Amazon</a>
                        
                        <!-- Info -->
                        <div class="info-box">
                          <p><strong>⚡ Act Fast!</strong> Amazon prices change frequently. This deal might not last long.</p>
                        </div>
                      </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                      <td class="footer">
                        <p><strong>PriceDrop</strong></p>
                        <p>Your Smart Price Tracker</p>
                        <p style="margin-top: 15px; font-size: 12px;">© 2024 PriceDrop</p>
                      </td>
                    </tr>
                    
                  </table>
                </td>
              </tr>
            </table>
          </body>
        </html>
        """

        html_part = MIMEText(html_content, "html")
        message.attach(html_part)

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(message)

        print(f"✅ Price alert email sent to {recipient_email}")
        return True

    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False


def send_target_price_alert(recipient_email, product_name, current_price, target_price):
    """Send target price reached alert - Mobile optimized"""
    try:
        message = MIMEMultipart("alternative")
        message["Subject"] = f"🎯 Target Reached: {product_name[:40]}..."
        message["From"] = f"PriceDrop <{SENDER_EMAIL}>"
        message["To"] = recipient_email

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
                background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
                padding: 30px 20px;
                text-align: center;
              }}
              .header-emoji {{
                font-size: 60px;
                line-height: 1;
                margin-bottom: 10px;
              }}
              .header-title {{
                color: white;
                font-size: 26px;
                font-weight: 700;
                margin: 0;
                line-height: 1.3;
              }}
              .header-subtitle {{
                color: rgba(255,255,255,0.9);
                font-size: 14px;
                margin: 8px 0 0 0;
              }}
              
              .content {{
                background: white;
                padding: 30px 20px;
              }}
              
              .success-badge {{
                background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
                border: 3px solid #10b981;
                border-radius: 12px;
                padding: 20px;
                text-align: center;
                margin-bottom: 25px;
              }}
              .success-badge h2 {{
                margin: 0;
                color: #065f46;
                font-size: 20px;
                font-weight: 700;
              }}
              
              .product-name {{
                font-size: 18px;
                font-weight: 600;
                color: #111827;
                line-height: 1.5;
                margin: 0 0 25px 0;
                text-align: center;
              }}
              
              .price-box {{
                background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
                border-radius: 12px;
                padding: 30px 20px;
                text-align: center;
                margin: 25px 0;
              }}
              .price-label {{
                color: rgba(255,255,255,0.9);
                font-size: 12px;
                text-transform: uppercase;
                letter-spacing: 1px;
                margin-bottom: 10px;
              }}
              .price-amount {{
                color: white;
                font-size: 42px;
                font-weight: 700;
                line-height: 1;
                margin-bottom: 15px;
              }}
              .target-info {{
                color: rgba(255,255,255,0.9);
                font-size: 14px;
              }}
              
              .cta-button {{
                display: block;
                background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                color: white !important;
                text-decoration: none;
                padding: 16px 32px;
                border-radius: 12px;
                font-size: 16px;
                font-weight: 600;
                text-align: center;
                margin: 25px 0;
              }}
              
              .info-box {{
                background: #fef3c7;
                border-left: 4px solid #f59e0b;
                padding: 15px;
                border-radius: 8px;
                margin: 15px 0;
              }}
              .info-box p {{
                margin: 0;
                font-size: 14px;
                color: #92400e;
                line-height: 1.6;
              }}
              
              .footer {{
                background: #f9fafb;
                padding: 25px 20px;
                text-align: center;
              }}
              .footer p {{
                margin: 5px 0;
                font-size: 13px;
                color: #6b7280;
              }}
              
              @media only screen and (max-width: 600px) {{
                .header-emoji {{ font-size: 48px; }}
                .header-title {{ font-size: 22px; }}
                .product-name {{ font-size: 16px; }}
                .price-amount {{ font-size: 36px; }}
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
                        <div class="header-emoji">🎯</div>
                        <h1 class="header-title">Target Price Reached!</h1>
                        <p class="header-subtitle">Your patience paid off</p>
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
                          <p><strong>⚡ Perfect Timing!</strong> The price is now at or below your target. This is a great opportunity to buy!</p>
                        </div>
                      </td>
                    </tr>
                    
                    <tr>
                      <td class="footer">
                        <p><strong>PriceDrop</strong></p>
                        <p>Your Smart Price Tracker</p>
                        <p style="margin-top: 15px; font-size: 12px;">© 2024 PriceDrop</p>
                      </td>
                    </tr>
                    
                  </table>
                </td>
              </tr>
            </table>
          </body>
        </html>
        """

        html_part = MIMEText(html_content, "html")
        message.attach(html_part)

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(message)

        print(f"✅ Target price alert sent to {recipient_email}")
        return True

    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False