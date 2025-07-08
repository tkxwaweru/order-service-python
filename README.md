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
- Comprehensive test coverage (71 test cases)

---
## Technical Stack

- **Backend:** Django REST Framework
- **Authentication:** Google OIDC via Mozilla Django OIDC
- **Database:** PostgreSQL (Render-managed)
- **Testing:** Django Test Framework 
- **CI/CD:** GitHub Actions
- **Deployment:** Render (Gunicorn with `entrypoint.sh`)

---
## API Documentation

| Method | Endpoint                | Description                      | Auth Required | Payload Format |
|--------|-------------------------|----------------------------------|---------------|----------------|
| GET    | `/`                     | Home page                        | No            | –              |
| GET    | `/register/`            | Registration form                | No            | –              |
| GET    | `/api/customers/`       | List all customers               | Yes           | –              |
| POST   | `/api/customers/`       | Register a new customer          | No            | `{ name, email, phone }` |
| GET    | `/api/orders/`          | List all orders                  | Yes           | –              |
| POST   | `/api/orders/`          | Create a new order               | Yes           | `{ customer_id, items }` |
| GET    | `/oidc/authenticate/`   | Initiate Google OIDC login       | No            | –              |
| GET    | `/oidc/callback/`       | OIDC callback                    | No            | –              |
| GET    | `/login-redirect/`      | Redirect after login             | No            | –              |
| GET    | `/run-migrations/`      | Run DB migrations (Render only) | Yes (token)   | –              |

---
## Setup & Deployment

### Requirements

- Python 3.12+
- Django 5+
- PostgreSQL
- Render account (for deployment)
- Africa's Talking credentials (optional)

### Project Setup (Local)


1.  Clone repo
```{code}
git clone https://github.com/yourusername/order-service-python.git
cd order-service-python
```

2.  Set up environment 
- Venv:
```{code}
python -m venv .venv
source venv/bin/activate
```

- Anaconda
```{code}
conda create -n <environment_name> python=<version>
conda activate <environment_name>
```

- Install requirements
```{code}
pip install -r requirements.txt
```

3. Add .env file - see `.env.example`
```{code}
cp .env.example .env
```
- *Here is an example snippet of `.env.example`. The full file can be found in the repository.*

```{code}
# .env.example
SECRET_KEY=your_secret_key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=your_db_url
OIDC_RP_CLIENT_ID=your_oidc_id
OIDC_RP_CLIENT_SECRET=your_oidc_secret
AFRICASTALKING_USERNAME=sandbox
AFRICASTALKING_API_KEY=your_at_key
MIGRATION_SECRET_TOKEN=your_token
```

4. Apply migrations
```{code}
python manage.py makemigrations

python manage.py migrate
```
5. Run server
```{code}
python manage.py runserver
```
6. Running tests
```{code}
coverage run -m pytest tests/

coverage html
```

---
## Deployment (Render)

### Environment variables:

Before running or deploying the project, make sure the following environment variables are configured. These can be added to a `.env` file (locally) or set in Render’s environment settings.

| Variable                   | Description                                   | Example Value / Notes                                |
|---------------------------|-----------------------------------------------|-------------------------------------------------------|
| `SECRET_KEY`              | Django secret key used for cryptographic signing | `django-insecure-xyz123!@#...`                     |
| `DEBUG`                   | Debug mode (use `False` in production)         | `False`                                               |
| `ALLOWED_HOSTS`           | Comma-separated list of allowed hosts          | `order-service-twcc.onrender.com`                    |
| `DATABASE_URL`            | PostgreSQL connection URL                      | `postgres://user:pass@host:port/dbname`              |
| `OIDC_RP_CLIENT_ID`       | OIDC Client ID (e.g., Firebase)                | `your-client-id.apps.googleusercontent.com`          |
| `OIDC_RP_CLIENT_SECRET`   | OIDC Client Secret                             | `your_client_secret`                                 |
| `AFRICASTALKING_USERNAME` | Africa’s Talking username                      | `sandbox` or `production_username`                   |
| `AFRICASTALKING_API_KEY`  | Africa’s Talking API key                       | `your_api_key_here`                                  |
| `MIGRATION_SECRET_TOKEN`  | Token to protect the `/run-migrations/` route  | `randomly_generated_secure_token`                    |

### Secrets

The `SECRET_KEY` & `MIGRATION_SECRET_TOKEN` can be manually generated and stored in `.env`.

- You can generate a new Django `SECRET_KEY` using Python:

```{code}
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```
- For the `/run-migrations/` route, you should also use a long, unpredictable secret. Use:

```{code}
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copy the generated code and place it in your `.env` file and Render environment variables.