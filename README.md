# Order Service API

A Django-based backend service for managing customer registrations and orders. This project integrates user authentication (OIDC), PostgreSQL for persistent storage, and optional SMS notifications via Africa's Talking.

---

## Live Deployment

**Production URL**: [https://order-service-twcc.onrender.com](https://order-service-twcc.onrender.com)

---

## Features

- Customer registration
- Order creation and listing
- Google OIDC login integration
- SMS notifications (via Africa's Talking)
- RESTful API (JSON responses)
- PostgreSQL database (hosted on Render)

---

## Setup & Deployment

### Requirements

- Python 3.12+
- Django 5+
- PostgreSQL
- Render account (for deployment)
- Africa's Talking credentials (optional)

### Project Setup (Local)


- Clone repo
```{code}
git clone https://github.com/yourusername/order-service-python.git
cd order-service-python
```

- Set up environment
```{code}
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

- Add .env file
```{code}
cp .env.example .env
```
- Apply migrations
```{code}
python manage.py migrate
```
- Run server
```{code}
python manage.py runserver
```