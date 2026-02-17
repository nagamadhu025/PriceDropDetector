# PriceDropDetector Email Setup

1. Copy `.env.example` to `.env` and fill in your Gmail address, app password, and recipient email.
2. If using Gmail, create an App Password (not your main password) in your Google Account security settings.
3. Your `.env` should look like:

EMAIL_ADDRESS=your_gmail_address@gmail.com
EMAIL_PASSWORD=your_gmail_app_password
TO_EMAIL=recipient_email@gmail.com

4. Restart your app. You will now receive real emails when a price drops.

Troubleshooting:

- Make sure 'Less secure app access' is enabled or use an App Password.
- Check your spam folder if you don't see the email.
- Errors will be printed in the console.
