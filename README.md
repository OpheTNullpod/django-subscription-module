
# Django Subscription Module with MIPS , juice MCB , PayPal Integration ...

## Overview
This Django-based module manages subscriptions with MIPS and PayPal as payment gateways. It provides comprehensive features for plan management, subscription handling with FSM (Finite State Machine), and payment processing. The module also supports Celery for asynchronous tasks.

## Table of Contents
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Testing](#testing)
- [PayPal Testing via Postman](#paypal-testing-via-postman)
- [Documentation](#documentation)
 

## Features
- **Plan Management**: Create and manage subscription plans.
- **Subscription Handling**: Utilizes FSM to manage subscription states such as activation, renewal, and expiration.
- **Multi-Gateway Payment Integration**:
  - **MIPS**: Supports multiple payment methods (e.g., MCB Juice, Standing Orders).
  - **PayPal**: Integrated PayPal REST API for payments.
- **User-friendly UI** for managing subscriptions.
- **Asynchronous Processing**: Uses Celery with Redis to handle tasks in the background.

## Installation

### Prerequisites
- Python 3.x
- Django
- Redis (for Celery backend)
- PayPal Developer Account

### Steps

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/mips-paypal-subscription-module.git
   cd mips-paypal-subscription-module
   ```

2. **Set up a virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set environment variables for PayPal**:
   Create a `.env` file in the root directory with the following:
   ```bash
   PAYPAL_CLIENT_ID='your-client-id'
   PAYPAL_CLIENT_SECRET='your-client-secret'
   PAYPAL_MODE='sandbox'  # Change to 'live' for production
   ```

5. **Run initial database migrations**:
   ```bash
   python manage.py makemigrations subscriptions
   python manage.py migrate
   ```

6. **Start the development server**:
   ```bash
   python manage.py runserver
   ```

### Usage
1. **Visit** `/subscriptions/plans/` to see the available subscription plans.
2. **Choose a plan** and proceed with the subscription.
3. **Manage your subscription** at `/subscriptions/manage/`.

## Testing

### Django Tests
To run automated tests for the module, use:
```bash
python manage.py test subscriptions
```

The test suite includes:
- **Subscription Creation**: Tests creating new subscriptions.
- **Payment Handling**: Simulates payment processes for MIPS and PayPal.
- **FSM Transitions**: Verifies transitions for subscription states (e.g., activation, renewal, expiration).
- **Recurring Payment Option**: Tests handling of recurring payments.

### PayPal Testing via Postman

1. **Setup**:
   - Install [Postman](https://www.postman.com/downloads/).
   - Log into your [PayPal Developer Dashboard](https://developer.paypal.com/) and obtain your **Client ID** and **Client Secret**.

2. **Test Authentication (Get Access Token)**:
   - In Postman, create a new request:
     - **Method**: POST
     - **URL**: `https://api-m.sandbox.paypal.com/v1/oauth2/token`
     - **Authorization**: Basic Auth (use your **Client ID** as the username and **Client Secret** as the password).
     - **Body**: Set to `x-www-form-urlencoded` with `grant_type=client_credentials`.
   - Click **Send** to receive an access token.

3. **Test Payment Creation**:
   - Create a new request in Postman:
     - **Method**: POST
     - **URL**: `https://api-m.sandbox.paypal.com/v1/payments/payment`
     - **Authorization**: Bearer Token (use the access token obtained earlier).
     - **Headers**: Set `Content-Type` to `application/json`.
     - **Body**:
       ```json
       {
         "intent": "sale",
         "payer": {
           "payment_method": "paypal"
         },
         "transactions": [{
           "amount": {
             "total": "10.00",
             "currency": "USD"
           },
           "description": "Test Subscription Payment"
         }],
         "redirect_urls": {
           "return_url": "http://localhost:8000/paypal/execute/",
           "cancel_url": "http://localhost:8000/paypal/cancel/"
         }
       }
       ```
   - Click **Send** to create a payment and get approval links.

4. **Execute Payment**:
   - After the user approves the payment, PayPal redirects to the return URL with a `paymentId` and `PayerID`.
   - Create a new request in Postman to execute the payment:
     - **Method**: POST
     - **URL**: `https://api-m.sandbox.paypal.com/v1/payments/payment/{paymentId}/execute`
     - **Authorization**: Bearer Token.
     - **Body**:
       ```json
       {
         "payer_id": "PayerID from the redirect URL"
       }
       ```
   - Click **Send** to complete the payment.

### Documentation
- [Django Documentation](https://docs.djangoproject.com/en/stable/)
- [PayPal REST API Documentation](https://developer.paypal.com/docs/api/overview/)
- [Celery Documentation](https://docs.celeryq.dev/en/stable/)
- [Django FSM](https://django-fsm.readthedocs.io/en/stable/)
 