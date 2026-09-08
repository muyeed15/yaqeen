# Yaqeen Backend

Islamic digital wallet API. Django REST + JWT + PostgreSQL.

**Islamic features:** Mudarabah savings, Zakat and Sadaqah, Qard Hasan financing, Islamic banking, Wakalah agents, and Hawala remittance.

> See the [project README](../README.md) for the full quick start and production deployment with PM2.

## Setup

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py seed
python manage.py runserver
```

The `.env` file and all required values are mandatory. The server address comes from `DJANGO_PORT` and `BACKEND_HOST`; PM2 uses `BACKEND_PORT` and `BACKEND_HOST`. Startup fails immediately when configuration is missing or blank.

## Production

The PM2 configuration runs `gunicorn` from `backend/.venv/bin/gunicorn` directly, so the virtual environment does not need to be activated before starting PM2. See the [project README](../README.md#production) for startup commands.

## Environment Variables

```
SECRET_KEY=django-insecure-changeme
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=https://wallet.example.com
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=False
SECURE_HSTS_PRELOAD=False

DB_NAME=yaqeen_db
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432
DB_CONN_MAX_AGE=60

ACCESS_TOKEN_MINUTES=1440
REFRESH_TOKEN_MINUTES=43200
DJANGO_PORT=8003
BACKEND_PORT=8003
BACKEND_HOST=127.0.0.1

TRANSFER_FEE_PERCENT=1.5
PAGE_SIZE=10
PAGE_SIZE_MAX=50
```

## Project Structure

```
config/          Django project settings, root URL config, WSGI/ASGI
accounts/        User, Wallet, Foundation, Nominee, KYC, OTP
cards/           Card (encrypted), block/unblock
transactions/    Transaction, Money Request
merchants/       Merchant profiles
notifications/   Notification + SSE streaming
savings/         Mudarabah plans, accounts, contributions
charity/         Zakat, Sadaqah, Hawl, Sadaqah Jariyah
common/          Pagination, middleware, seed command, utilities
recharge/        Mobile top-up operators, data packs
billpay/         Utility billers and payments (electricity, gas, water, etc.)
agents/          Agent network for cash-in/cash-out (Wakalah)
banking/         Islamic bank integration, add money, withdraw
loans/           Qard Hasan interest-free loans
remittance/      International money transfer (Hawala)
rewards/         Points, cashback offers, user rewards
gateway/         E-commerce payment API for merchants
tickets/         Bus, train, airline, cinema, event bookings
support/         Customer support ticket system
statements/      Monthly account statements
```

## All API Endpoints

All endpoints require `Authorization: Bearer <token>` except JWT login/refresh and the API-key-authenticated gateway webhook.

### Auth & Profile

| Method | URL                    | Description                                   |
| ------ | ---------------------- | --------------------------------------------- |
| POST   | `/api/token/`          | Obtain JWT (login)                            |
| POST   | `/api/token/refresh/`  | Refresh JWT                                   |
| GET    | `/api/me/`             | User profile                                  |
| GET    | `/api/wallet/`         | Wallet balance                                |
| GET    | `/api/qr/`             | Generate QR code                              |
| GET    | `/api/lookup/<phone>/` | Resolve user / merchant / agent name by phone |
| GET, POST | `/api/nominees/` | List / add nominees |
| DELETE | `/api/nominees/<pk>/` | Remove nominee |
| GET, PUT | `/api/kyc/` | View / submit KYC |
| GET | `/api/foundation-causes/` | List foundation causes |
| GET | `/api/foundations/` | List verified foundations |
| GET | `/api/foundations/<pk>/` | Foundation detail |

### Money Transfer

| Method | URL                                 | Description            |
| ------ | ----------------------------------- | ---------------------- |
| POST   | `/api/transfer/`                    | Send money             |
| GET    | `/api/transactions/`                | Transaction history    |
| GET    | `/api/transactions/<pk>/`           | Transaction detail     |
| POST   | `/api/money-requests/create/`       | Request money          |
| GET    | `/api/money-requests/`              | Money requests         |
| POST   | `/api/money-requests/<pk>/respond/` | Accept/decline request |

### Payments

| Method | URL                  | Description             |
| ------ | -------------------- | ----------------------- |
| GET    | `/api/merchants/`    | List verified merchants |
| POST   | `/api/pay/merchant/` | Pay a merchant          |

### Cards

| Method    | URL                        | Description      |
| --------- | -------------------------- | ---------------- |
| GET, POST | `/api/cards/`              | List / add cards |
| PATCH     | `/api/cards/<pk>/block/`   | Block card       |
| PATCH     | `/api/cards/<pk>/unblock/` | Unblock card     |

### Recharge

| Method | URL                | Description           |
| ------ | ------------------ | --------------------- |
| GET    | `/api/operators/`  | List mobile operators |
| GET    | `/api/data-packs/` | List data packs       |
| POST   | `/api/recharge/`   | Recharge phone        |
| GET    | `/api/recharges/`  | Recharge history      |

### Bill Pay

| Method | URL              | Description          |
| ------ | ---------------- | -------------------- |
| GET    | `/api/biller-categories/` | List bill categories |
| GET    | `/api/billers/`  | List billers         |
| POST   | `/api/pay-bill/` | Pay utility bill     |
| GET    | `/api/bills/`    | Bill payment history |

### Agents

| Method | URL                        | Description               |
| ------ | -------------------------- | ------------------------- |
| GET    | `/api/agents/`             | List agents               |
| GET    | `/api/agents/<pk>/`        | Agent detail              |
| POST   | `/api/cash-in/`            | Cash in through agent     |
| POST   | `/api/cash-out/`           | Cash out through agent    |
| GET    | `/api/agent-transactions/` | Agent transaction history |

### Banking

| Method    | URL                        | Description              |
| --------- | -------------------------- | ------------------------ |
| GET       | `/api/banks/`              | List Islamic banks       |
| GET, POST | `/api/bank-accounts/`      | List / add bank accounts |
| DELETE    | `/api/bank-accounts/<pk>/` | Remove bank account      |
| POST      | `/api/add-money/`          | Add money from bank      |
| POST      | `/api/withdraw/`           | Withdraw to bank         |
| GET       | `/api/bank-transactions/`  | Bank transaction history |

### Qard Hasan Loans

| Method | URL                           | Description        |
| ------ | ----------------------------- | ------------------ |
| GET    | `/api/qard-hasan-products/`   | List loan products |
| POST   | `/api/apply-qard-hasan/`      | Apply for loan     |
| GET    | `/api/qard-hasan/`            | My loans           |
| GET    | `/api/qard-hasan/<pk>/`       | Loan detail        |
| POST   | `/api/qard-hasan/<pk>/repay/` | Repay loan         |

### Remittance

| Method | URL                         | Description        |
| ------ | --------------------------- | ------------------ |
| GET    | `/api/remittance-partners/` | List partners      |
| POST   | `/api/receive-remittance/`  | Receive remittance |
| GET    | `/api/remittances/`         | Remittance history |

### Savings (Mudarabah)

| Method    | URL                                                       | Description          |
| --------- | --------------------------------------------------------- | -------------------- |
| GET       | `/api/mudarabah/plans/`                                   | List plans           |
| GET, POST | `/api/mudarabah/accounts/`                                | List / open account  |
| GET       | `/api/mudarabah/accounts/<account_number>/`               | Account detail       |
| POST      | `/api/mudarabah/pay/`                                     | Pay contribution     |
| GET       | `/api/mudarabah/accounts/<account_number>/contributions/` | Contribution history |

### Charity

| Method     | URL                                   | Description             |
| ---------- | ------------------------------------- | ----------------------- |
| POST       | `/api/zakat/calculate/`               | Calculate Zakat         |
| POST       | `/api/zakat/pay/`                     | Pay Zakat               |
| GET        | `/api/zakat/history/`                 | Zakat history           |
| GET, PUT   | `/api/hawl/`                          | Hawl tracking           |
| POST       | `/api/sadaqah/`                       | Give sadaqah            |
| GET        | `/api/sadaqah/history/`               | Sadaqah history         |
| GET, POST  | `/api/sadaqah-jariyah/`               | List / create recurring |
| GET, PATCH | `/api/sadaqah-jariyah/<donation_id>/` | Detail / toggle         |

### Tickets

| Method | URL                         | Description      |
| ------ | --------------------------- | ---------------- |
| GET    | `/api/ticket-categories/`   | List categories  |
| GET    | `/api/ticket-providers/`    | List providers   |
| GET    | `/api/ticket-trips/`        | List trips/shows |
| POST   | `/api/book-ticket/`         | Book ticket      |
| GET    | `/api/tickets/`             | Booking history  |
| POST   | `/api/tickets/<pk>/cancel/` | Cancel booking   |

### Rewards & Offers

| Method | URL                       | Description    |
| ------ | ------------------------- | -------------- |
| GET    | `/api/rewards/`           | Reward points  |
| GET    | `/api/points-history/`    | Points history |
| GET    | `/api/offers/`            | Active offers  |
| POST   | `/api/offers/<pk>/claim/` | Claim offer    |

### Gateway

| Method | URL                          | Description      |
| ------ | ---------------------------- | ---------------- |
| POST   | `/api/gateway/initiate/`     | Initiate payment |
| GET    | `/api/gateway/<txn_id>/`     | Payment status   |
| GET    | `/api/gateway-transactions/` | Gateway history  |
| POST   | `/api/gateway-webhook/`      | API-key merchant webhook |

### Support

| Method    | URL                                | Description           |
| --------- | ---------------------------------- | --------------------- |
| GET       | `/api/support-categories/`         | List support categories |
| GET, POST | `/api/support-tickets/`            | List / create tickets |
| GET       | `/api/support-tickets/<pk>/`       | Ticket detail         |
| POST      | `/api/support-tickets/<pk>/reply/` | Reply to ticket       |

### Notifications & Statements

| Method     | URL                            | Description        |
| ---------- | ------------------------------ | ------------------ |
| GET        | `/api/notifications/`          | Notification list  |
| GET        | `/api/notifications/stream/`   | SSE stream         |
| POST       | `/api/notifications/read-all/` | Mark all read      |
| GET, PATCH | `/api/notifications/<pk>/`     | Detail / mark read |
| GET        | `/api/statements/`             | Account statements |
| POST       | `/api/statements/generate/`    | Generate statement |

## Useful Commands

```bash
python manage.py seed              # populate with sample data (password: 12345678)
python manage.py createsuperuser   # create admin user
python manage.py migrate           # apply migrations
python manage.py test              # run tests
python manage.py check             # validate Django configuration
python manage.py makemigrations --check --dry-run  # verify model/migration sync
```

### Reset Database

Development only. This permanently deletes every table and row in the configured database.

```bash
# Wipe all data and re-seed from scratch
python -c "
import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django; django.setup()
from django.db import connection
with connection.cursor() as c:
    c.execute('DROP SCHEMA public CASCADE; CREATE SCHEMA public;')
"
python manage.py migrate
python manage.py seed
```
