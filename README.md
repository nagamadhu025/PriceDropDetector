🛒 Price Drop Detector

A full-stack web application that tracks product prices and notifies users when prices drop.

Built with FastAPI (Backend) and React + Vite (Frontend).

🚀 Features

🔐 User Authentication (JWT-based login/signup)

➕ Add products by URL

💾 Store product details in database

🔔 Get notified when price drops

📧 Email notifications

🌐 Fully deployed (Backend + Frontend)

🏗️ Tech Stack
🔹 Backend

FastAPI

SQLAlchemy


🔹 Frontend

React

Vite

Axios

🔹 Deployment

Vercel (Frontend)

Render / Railway / VPS (Backend)

📂 Project Structure
PriceDropDetector/
│
├── backend/
│   ├── main.py
│   ├── models.py
│   ├── database.py
│   ├── routes/
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   ├── components/
│   ├── services/
│   └── package.json
│
└── README.md
⚙️ Environment Variables

Create a .env file in the backend folder:

JWT_SECRET=your_jwt_secret_key
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
EMAIL_HOST=smtp.mailtrap.io
EMAIL_PORT=2525
EMAIL_USER=your_email_user
EMAIL_PASS=your_email_password
OPENAI_API_KEY=your_openai_api_key
🛠️ Installation & Setup
1️⃣ Clone Repository
git clone https://github.com/your-username/PriceDropDetector.git
cd PriceDropDetector
2️⃣ Backend Setup
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

Backend runs at:

http://localhost:8000
3️⃣ Frontend Setup
cd frontend
npm install
npm run dev

Frontend runs at:

http://localhost:5173
🚀 Deployment
🔹 Backend

Deploy using:

Render

Railway

VPS

Make sure to add environment variables in the deployment dashboard.

🔹 Frontend (Vercel)
npm run build

Upload project to Vercel
Build Command:

vite build

Output Directory:

dist
🔐 Authentication Flow

User registers

Password is hashed

JWT token is generated

Token stored in frontend

Authenticated API requests include token in headers

📧 Email Notification Flow

Background task checks price

If price drops:

Email sent to registered user

Notification saved in DB

📸 Screenshots

(Add screenshots of your UI here)

📌 Future Improvements

🕒 Scheduled price tracking (Cron jobs)

📊 Price history chart

📱 Mobile responsiveness improvements

🔔 Push notifications

🛍️ Support for multiple e-commerce platforms

🤝 Contributing

Pull requests are welcome. For major changes, open an issue first to discuss improvements.

📜 License

This project is licensed under the MIT License.﻿# PriceDropDetector


