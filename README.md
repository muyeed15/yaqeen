# Yaqeen

Yaqeen is an Islamic digital wallet built with Django REST Framework, PostgreSQL, Next.js, and React. It supports wallet transfers, merchant payments, Mudarabah savings, Zakat and Sadaqah, Qard Hasan financing, Islamic banking, remittance, bills, recharge, tickets, rewards, and account services.

## Requirements

- Python 3.12+
- PostgreSQL
- Node.js 20+
- npm
- PM2 and Gunicorn for the documented production setup

## Local Setup

Both services require their own `.env` file. Configuration has no code-level fallbacks; a missing file or required value stops startup.

### Backend

```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
# Update DB_PASSWORD and any local connection values.
python manage.py migrate
python manage.py seed
python manage.py runserver
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

With the example environment values, the services are available at:

| Service | Address |
| --- | --- |
| Backend API | `http://127.0.0.1:8003` |
| Django admin | `http://127.0.0.1:8003/admin/` |
| Frontend | `http://127.0.0.1:3003` |

The frontend `DJANGO_API_URL` must point to the backend, and JWT lifetime values must match across both environment files.

## Architecture

```text
Browser
  → Next.js pages, route handlers, and server actions
  → Django REST API with JWT authentication
  → PostgreSQL
```

- JWTs are kept in HTTP-only cookies by Next.js and are not exposed to browser JavaScript.
- Next.js route handlers proxy browser reads to Django; server actions handle mutations.
- Financial mutations use database transactions and wallet row locks.
- Dashboard notifications arrive through an SSE stream proxied by Next.js.
- Both APIs enforce authenticated, user-scoped access except the JWT endpoints.

## Validation

```bash
# Backend
cd backend
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test

# Frontend
cd frontend
npm run lint
npm test
npx tsc --noEmit
npm run build
```

## Production

Set production values in both required `.env` files. In particular, use a strong backend `SECRET_KEY`, set `DEBUG=False`, configure allowed hosts/origins, and use HTTPS values appropriate for the deployment.

```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt

cd ..
cd frontend
npm ci
npm run build

cd ..
mkdir -p logs
pm2 start ecosystem.config.js
pm2 save
pm2 startup
```

The PM2 configuration starts:

- `yaqeen-backend`: Gunicorn with three workers
- `yaqeen-frontend`: the production Next.js custom server

Manage a service individually with:

```bash
pm2 start ecosystem.config.js --only yaqeen-backend
pm2 start ecosystem.config.js --only yaqeen-frontend
```

## Documentation

- [Backend API and model documentation](backend/README.md)
- [Frontend routes and architecture](frontend/README.md)
