# Barcode Coupon Manager — Backend

API server for managing supermarket coupon barcodes received via SMS and email.

## Stack

- **FastAPI** — HTTP routes + auto Swagger UI
- **SQLModel** — ORM (built on SQLAlchemy + Pydantic)
- **PostgreSQL** — database
- **Docker** — local development and deployment (target: Raspberry Pi)

## Project Structure

```
back/
├── api/          # FastAPI route handlers
├── models/       # SQLModel table definitions
├── services/     # business logic
├── parsers/      # SMS/email parsing + barcode image code extraction (Phase 3)
├── workers/      # async background jobs
├── main.py       # FastAPI app entry point
└── database.py   # engine + session setup
```

## Data Models

### Supplier
| Field | Type |
|---|---|
| id | int (PK) |
| name | str |
| logo_url | str? |

### Coupon
| Field | Type | Notes |
|---|---|---|
| id | int (PK) | |
| supplier_id | int (FK) | |
| value | int | coupon value in NIS |
| code | str? | numeric code parsed from barcode image (Phase 3) |
| used | bool | |
| created_at | datetime | |
| used_at | datetime? | |
| added_by_id | int (FK) | |

### User
| Field | Type |
|---|---|
| id | int (PK) |
| email | str (unique) |
| password_hash | str |

## Authentication

JWT-based. All endpoints are protected.

- `POST /auth/register` — create account
- `POST /auth/login` — returns JWT token

Currently all users share access to the same coupon pool (shared household model). Per-user coupon visibility and permissions are planned for a future version.

## API Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/suppliers` | All suppliers with available balance |
| GET | `/suppliers/{id}/coupons` | All coupons for a supplier |
| POST | `/coupons` | Add a coupon manually |
| PATCH | `/coupons/{id}/use` | Mark a coupon as used |

## Coupon Ingestion Phases

### Phase 1 — Manual
User enters supplier, value, and coupon code directly.

### Phase 2 — Email Auto Import
App polls a dedicated inbox and extracts supplier and value from SMS/email text. Coupon code extraction handled in Phase 3.

### Phase 3 — Barcode Image Code Parsing
Parses the numeric coupon code from barcode images (received via email or uploaded manually). Stores result in `Coupon.code`.

## Local Development

### Prerequisites
- Docker Desktop
- Python 3.12+

### Setup

```bash
# from repo root (barcode/)
docker compose up -d          # start PostgreSQL

cd back
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt

python main.py                # starts FastAPI on http://localhost:8000
# Swagger UI: http://localhost:8000/docs
```

## Deployment

Intended to run on a Raspberry Pi via Docker Compose.
