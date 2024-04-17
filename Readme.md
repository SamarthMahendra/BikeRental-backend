# Bike Rental Service API

This Django project provides a backend API for a bike rental service, enabling users to manage bookings, handle payments, submit feedback, and much more. It includes an admin panel for additional management capabilities.

## Features

- User authentication (signup, login, logout).
- Bike booking and returns.
- Account balance management.
- Maintenance management for bikes.
- Feedback submission for services.
- Transaction and payment tracking.

## Prerequisites

- Python 3.8+
- Django 3.x
- Django REST Framework
- MySQL Server
- PyJWT

## Setup

1. **Clone the Repository:**
   ```bash
   git clone [your-repository-link]
   cd [your-project-directory]
    ```
   
2. **Install Dependencies:**

    ```bash
    pip install -r requirements.txt
    ```
   
Configure MySQL:

Ensure MySQL is installed and running.
Create a database named bike_rental_db.
Configure your database settings in settings.py to match your MySQL setup.

4. **Run Migrations:**

    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

**Start the Server:**
python manage.py runserver


Access the API at: http://127.0.0.1:8000/

## API Endpoints
POST /signup/: Register a new user.
POST /login/: Authenticate a user.
POST /logout/: Log out a user.
POST /get_nearby_stations/: Retrieve nearby station details.
GET /get_balance/: Get user's account balance.
POST /add_balance/: Add balance to user's account.
POST /search_stations/: Search stations by keyword.
POST /give_feedback/: Submit feedback.
POST /get_estimated_cost/: Estimate the cost of a ride.
POST /start_ride/: Start a bike ride.
POST /end_ride/: End a bike ride.
POST /make_payment/: Process a payment.
GET /get_payment_history/: Retrieve payment history.
DELETE /delete_transaction/: Delete a transaction record.
Admin Features
Manage user accounts and roles.
Push bikes to maintenance and mark them as maintained.
Review user feedbacks.
Security
The API uses JWT for secure token-based authentication.
Custom decorator @is_authenticated is used to protect sensitive endpoints.
