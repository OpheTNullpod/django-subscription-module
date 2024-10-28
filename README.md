# Django Subscription Module with MIPS Integration

## Overview
This Django-based module manages subscriptions with MIPS as the payment gateway. It provides plans, subscriptions, and payment handling, incorporating Celery for asynchronous tasks and FSM for state management.

## Table of Contents
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Testing](#testing)
- [Contributing](#contributing)
- [License](#license)

## Features
- Plan creation and management.
- Subscription handling with Finite State Machine (FSM).
- MIPS payment gateway integration.
- User-friendly UI for managing subscriptions.
- Automated tasks using Celery and Redis.

## Installation

### Prerequisites
- Python 3.x
- Django
- Redis for Celery backend

### Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/mips-subscription-module.git
   cd mips-subscription-module

2. Set up a virtual environment:
   ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows, use .\venv\Scripts\activate

3. Install dependencies:
   ```bash
    pip install -r requirements.txt

4. Run initial database migrations:
   ```bash
    python manage.py makemigrations
    python manage.py migrate

5. Start the development server:
   ```bash
    python manage.py runserver

### Usage
1. Visit /subscriptions/plans/ to see the available subscription plans.
2. Choose a plan and proceed to subscription.
3. Manage your subscription from the /subscriptions/manage/ endpoint.

### Testing 
```bash
    python manage.py test subscriptions

### Final Summary
This guide provides:
- **Isolated environment for the module**, preventing dependency conflicts.
- **Multiple payment options** with Stripe, Internet Banking, and MCB Juice.