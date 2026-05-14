# 📦 Logistics — Warehouse Management API

A RESTful backend service for managing warehouses, products, stock, and inventory operations. Built with **FastAPI**, organized for clarity, and tested end-to-end.

---

## Table of Contents

- [Overview](#overview)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [API Reference](#api-reference)
- [Running Tests](#running-tests)
- [Database Migrations](#database-migrations)

---

## Overview

Logistics is a backend API designed to streamline warehouse and inventory management. It supports:

- User registration, authentication, and role management
- Creating and managing warehouses with activation/deactivation
- Product catalog management
- Real-time stock tracking
- Inventory operations (inbound/outbound)

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | [FastAPI](https://fastapi.tiangolo.com/) |
| Database ORM | SQLAlchemy + Alembic (migrations) |
| Validation | Pydantic (via schemas) |
| Testing | Pytest |
| Auth | JWT (via `auth` module) |
| Config | `.env` + `pyproject.toml` |

---

## Project Structure

```
Logistics/
├── app/
│   ├── api/           # Route definitions (FastAPI routers)
│   ├── auth/          # Authentication logic (JWT, password hashing)
│   ├── crud/          # Database query functions (Create, Read, Update, Delete)
│   ├── db/            # Database engine and session management
│   ├── schemas/       # Pydantic request/response models
│   ├── services/      # Business logic layer
│   ├── utils/         # Shared utilities and helpers
│   ├── main.py        # FastAPI app entry point
│   └── __init__.py
├── tests/
│   ├── conftest.py              # Pytest fixtures and test database setup
│   ├── test_user.py             # Auth & user endpoint tests
│   ├── test_warehouse.py        # Warehouse endpoint tests
│   ├── test_product.py          # Product endpoint tests
│   └── test_inv_operations.py   # Inventory operations tests
├── .env                  # Environment variables (not committed)
├── alembic.ini           # Alembic migration config
├── pyproject.toml        # Test config
└── requirements.txt      # Python dependencies
```

---

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/your-username/logistics.git
cd logistics
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy the example below into a `.env` file in the project root (see [Environment Variables](#environment-variables)).

### 5. Apply database migrations

```bash
alembic upgrade head
```

### 6. Run the development server

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`.  
Interactive docs (Swagger UI): `http://localhost:8000/docs`

---

## Environment Variables

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/logistics
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

> Never commit your `.env` file. It is already listed in `.gitignore`.

---

## API Reference

### Auth

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/auth/register/` | Register a new user |
| `POST` | `/auth/login/` | Log in and receive a JWT token |
| `POST` | `/auth/logout/` | Log out the current session |
| `GET` | `/auth/me/` | Get the currently authenticated user |
| `PATCH` | `/auth/change-role/{user_id}` | Change a user's role (admin only) |

### Warehouse

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/warehouse/` | Create a new warehouse |
| `GET` | `/warehouse/` | List all warehouses |
| `GET` | `/warehouse/{warehouse_id}` | Get a specific warehouse |
| `PATCH` | `/warehouse/{warehouse_id}` | Update warehouse details |
| `PATCH` | `/warehouse/{warehouse_id}/deactivate` | Deactivate a warehouse |
| `GET` | `/warehouse/{warehouse_id}/operations` | Get all operations for a warehouse |

### Product

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/product/` | Create a new product |
| `GET` | `/product/` | List all products |
| `GET` | `/product/{product_id}` | Get a specific product |
| `PATCH` | `/product/{product_id}` | Update product details |
| `PATCH` | `/product/{product_id}/deactivate` | Deactivate a product |

### Stock

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/stock/` | Get current stock levels |

### Inventory Operations

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/operations/` | Create an inventory operation (inbound / outbound) |

---

## Running Tests

```bash
pytest
```

To run a specific test file:

```bash
pytest tests/test_warehouse.py -v
```

Tests use a dedicated test database configured via `conftest.py`. Make sure your test database URL is set in the environment before running.

---

## Database Migrations

This project uses [Alembic](https://alembic.sqlalchemy.org/) for schema migrations.

```bash
# Apply all pending migrations
alembic upgrade head

# Create a new migration after model changes
alembic revision --autogenerate -m "describe your change"

# Roll back the last migration
alembic downgrade -1
```

---

## License

MIT
