# Grocery Store

[![API tests](https://github.com/AtulJ505/Grocery_Store/actions/workflows/ci.yml/badge.svg)](https://github.com/AtulJ505/Grocery_Store/actions/workflows/ci.yml)

A Flask grocery-store application with a product catalog, customer accounts, JWT authentication, shopping carts, orders, and optional Stripe checkout and email integrations.

## Features

- Searchable, paginated catalog with bounded page sizes.
- Customer registration and login; product writes require an administrator role.
- Shopping carts validate positive integer quantities and available stock.
- Order creation records line items and updates inventory.
- HTML pages, JSON API routes, and Swagger UI.

This is a development project. The automated suite covers catalog and cart behavior; payments, concurrent inventory changes, and production security require additional validation.

## Run locally

Use Python 3.11 for the existing dependency set.

```bash
git clone https://github.com/AtulJ505/Grocery_Store.git
cd Grocery_Store
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
flask --app run.py db upgrade
flask --app run.py run
```

On Windows, activate the environment with `.venv\Scripts\activate`. The default database is a local SQLite file. Set `DATABASE_URL` for another SQLAlchemy-supported database and install its driver if needed. Configure independent, random signing secrets before a deployment. Keep `.env` and virtual environments out of Git.

The application does not require Stripe or mail credentials for catalog browsing or the automated tests. Supply test-mode Stripe credentials and a webhook secret only when testing checkout; use a mail sandbox for email integration tests.

## API overview

| Endpoint | Purpose |
| --- | --- |
| `GET /api/products/?q=apple&page=1&per_page=20` | Search the catalog |
| `POST /api/auth/register` | Create a customer account |
| `POST /api/auth/login` | Get a bearer token |
| `GET /api/cart/` | Read the authenticated customer's cart |
| `POST /api/cart/add` | Add a product and integer quantity |
| `POST /api/orders/` | Create an order from the cart |
| `GET /api/orders/<id>` | Read an authorized order |

Authenticated requests use `Authorization: Bearer <access_token>`. Catalog pagination requires `page >= 1` and `1 <= per_page <= 100`. Invalid values return HTTP 400.

## Tests

```bash
python -m pytest -q
```

Tests create a fresh in-memory SQLite database for each case. They do not connect to a local PostgreSQL/MySQL instance or send email or payment requests. The suite verifies successful catalog responses, search, invalid pagination, registration, cart quantities and cumulative stock limits. CI runs the tests on Python 3.11.

## Project structure

- `app/`: application factory, SQLAlchemy models and route blueprints.
- `app/templates/`: HTML pages.
- `migrations/`: database migrations.
- `tests/`: isolated API regression tests.
- `.env.example`: configuration names with placeholders.

## Maintenance

Before expanding the app, update and audit the legacy Flask dependency set, test payment authorization, and add concurrent order/inventory tests. Removing local configuration from the current Git tree does not remove earlier commits; any credentials previously committed should be replaced through their issuing services.

For a pull request, describe a reproducible problem, include a focused test for behavior changes, and run the suite above. Do not submit credentials or customer information.
