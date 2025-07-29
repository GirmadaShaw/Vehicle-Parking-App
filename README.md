# 🚗 Smart Vehicle Parking Management System

## 📌 Overview
This project is a **Vehicle Parking Web Application** that allows users to seamlessly book parking spaces for a specific duration and pay accordingly. The platform provides a **user-friendly interface** for customers and a **powerful admin dashboard** to manage parking lots and monitor performance.

### ✨ Key Features
- ✅ **User Features**
  - Register and log in with **OTP verification**.
  - Secure password storage with **bcrypt encryption**.
  - **JWT token-based authentication** for all secured routes.
  - Real-time **booking of parking spaces** for specified durations.
  - View reservations, payments, and usage history.
  - Monthly usage reports delivered via email.

- ✅ **Admin Features**
  - Add, update, and delete parking lots.
  - View analytics and charts related to **revenues** and **user activity**.
  - Monitor overall system performance.

- ✅ **Technical Highlights**
  - **Database**: Built from scratch with optimized schema.
  - **Caching**: Integrated **Redis** for caching frequently accessed data to enhance performance.
  - **Background Jobs**: Used **Celery** for asynchronous tasks such as sending monthly reports.
  - **Validation**: All user inputs undergo validation with instant feedback via frontend toasts.
  - **Security**: Secure authentication, encrypted passwords, and OTP-based verification.

---

## 🏗️ Tech Stack
- **Backend**: Flask, SQLAlchemy, Celery, Redis
- **Frontend**: Vue.js
- **Database**: SQLite3 (can be switched to other RDBMS if needed)
- **Caching**: Redis
- **Authentication**: JWT (JSON Web Token)
- **Task Queue**: Celery
- **Other**: Axios, Marshmallow, Flask-CORS, bcrypt

---

## 🔥 System Architecture
1. **Frontend (Vue.js)** interacts with the Flask backend via REST APIs.
2. **Backend (Flask)** handles business logic, authentication, and database operations.
3. **SQLite3** serves as the relational database.
4. **Redis** is used for caching and to optimize response times.
5. **Celery** handles asynchronous tasks like sending periodic email reports.
6. **JWT** secures user sessions.

---

## 🗄️ Database
The database is fully normalized and optimized for fast queries. It includes tables for:
- Users  
- Parking Locations  
- Parking Slots  
- Reservations  
- Payments  
- Reviews  
- OTP (for signup verification)

---

## ⚙️ Installation and Setup

Follow the steps below to set up and run the project locally:

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/vehicle-parking-app.git
cd vehicle-parking-app

### ✅ 2. Backend Setup
1. Create the virtual environment
```bash
python -m venv .venv
source .venv/bin/activate   # (Linux/Mac)
.venv\Scripts\activate      # (Windows)

2. Install backend dependencies
pip install -r requirements.txt

3. Configure the .env file
JWT_SECRET=your_secret_key
DATABASE_URL=sqlite:///parking.db
REDIS_URL=redis://localhost:6379/0
MAIL_SERVER=smtp.yourprovider.com
MAIL_USERNAME=your_email
MAIL_PASSWORD=your_password

4. Initialize the DB
```bash
python run.py 

### 3. Frontend Setup
1. Navigate to the frontend directory
```bash
cd vpa-frontend

2. Install Frontend Dependencies
```bash
npm install


### 4. Start the required services
1. Install redis server and run redisinsight
2. To run celery, run the cmd celery -A backend.celery_worker.celery worker --loglevel=info
3. Now run the backend by the cmd python run.py 
4. Start the frontend server as well, use cmd npm run dev (in frontend folder)

