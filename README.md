# Barcode Coupon Manager — Backend

API server for managing supermarket coupon barcodes received via SMS and email.

## Stack

- **FastAPI** — HTTP routes + auto Swagger UI
- **SQLModel** — ORM (built on SQLAlchemy + Pydantic)
- **PostgreSQL** — database
- **Docker** — local development and deployment (target: Raspberry Pi)
- **Cloudflare Tunnel** — public HTTPS access without port forwarding

## Project Structure

```
back/
├── api/          # FastAPI route handlers
├── models/       # SQLModel table definitions
├── services/     # business logic
├── parsers/      # email body parsing
├── workers/      # background jobs (email import)
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
| group_id | int (FK) | planned — see Roadmap |
| value | int | coupon value in NIS |
| code | str? (unique) | numeric code parsed from email |
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

### Group _(planned)_
| Field | Type |
|---|---|
| id | int (PK) |
| name | str |
| created_by_id | int (FK → User) |

### GroupMember _(planned)_
| Field | Type |
|---|---|
| group_id | int (FK → Group) |
| user_id | int (FK → User) |

## Authentication

JWT-based. All endpoints are protected.

- `POST /auth/register` — create account
- `POST /auth/login` — returns JWT token

Currently all users share access to the same coupon pool. The group model (see Roadmap) will scope coupon visibility per group.

## API Endpoints

| Method | Path | Description |
|---|---|---|
| POST | `/suppliers` | Create a supplier |
| GET | `/suppliers` | All suppliers with available balance |
| GET | `/suppliers/{id}/coupons` | All coupons for a supplier |
| POST | `/coupons` | Add a coupon manually |
| PATCH | `/coupons/{id}/use` | Toggle coupon used/unused |
| POST | `/import/email` | Manually trigger email import |

## Coupon Ingestion

### Manual
User enters supplier, value, and coupon code directly via `POST /coupons`.

### Email Auto Import
Connects to a Gmail inbox via IMAP, parses unread emails from coupon providers, extracts supplier name, value, and numeric coupon code, then creates coupons automatically. Triggered manually via `POST /import/email` or automatically once a day via APScheduler.

Email format supported: Cibus/supermarket coupon emails (Hebrew).

## Roadmap

| # | Stage | Status |
|---|-------|--------|
| 1 | Models — Supplier, Coupon, User | ✅ |
| 2 | JWT auth — register, login | ✅ |
| 3 | REST endpoints — suppliers, coupons, use/unuse | ✅ |
| 4 | Email import — IMAP + body parser, manual trigger | ✅ |
| 5 | Deployment — Docker Compose + Cloudflare Tunnel on Raspberry Pi | ✅ |
| 6 | Daily auto-import — APScheduler runs email import once a day | ⬜ |
| 7 | Groups — users create groups, invite others by email; coupons scoped to a group | ⬜ |
| 8 | Per-user coupon permissions — finer-grained access control within groups | 🔲 |

## Local Development

### Prerequisites
- Docker Desktop
- Python 3.14+

### Setup

```bash
cd back
cp .env.example .env   # fill in values
docker compose up --build
# Swagger UI: http://localhost:8000/docs
```

## Deployment

Runs on a Raspberry Pi via Docker Compose. Public access via Cloudflare Tunnel — set `CLOUDFLARE_TUNNEL_TOKEN` in `.env`.
