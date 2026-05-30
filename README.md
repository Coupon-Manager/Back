# Barcode Coupon Manager — Backend

API server for managing supermarket coupon barcodes received via SMS and email.

## Stack

- **FastAPI** — HTTP routes + auto Swagger UI
- **SQLModel** — ORM (built on SQLAlchemy + Pydantic)
- **PostgreSQL** — database
- **Docker** — local development and deployment (target: Raspberry Pi)
- **Cloudflare Tunnel** — public HTTPS access without port forwarding
- **Cloudflare R2** — backup storage

## Project Structure

```
back/
├── api/          # FastAPI route handlers
├── models/       # SQLModel table definitions
├── services/     # business logic
├── parsers/      # email body parsing
├── workers/      # background jobs (email import)
├── scripts/      # ops scripts (backup, restore)
├── main.py       # FastAPI app entry point
└── database.py   # engine + session setup
```

## Data Models

### Supplier
| Field | Type |
|---|---|
| id | int (PK) |
| name | str |

### Coupon
| Field | Type | Notes |
|---|---|---|
| id | int (PK) | |
| supplier_id | int (FK) | |
| value | int | coupon value in NIS |
| code | str? (unique) | numeric code parsed from email |
| used | bool | |
| created_at | datetime (TIMESTAMPTZ) | |
| used_at | datetime? (TIMESTAMPTZ) | |
| added_by_id | int (FK) | |

### User
| Field | Type |
|---|---|
| id | int (PK) |
| email | str (unique) |
| password_hash | str |
| last_email_sync | datetime? (TIMESTAMPTZ) |

### UserSupplierPreference
| Field | Type | Notes |
|---|---|---|
| user_id | int (FK → User, PK) | |
| supplier_id | int (FK → Supplier, PK) | |
| color | str? | per-user display color (e.g. `#ff5733`) |

### Group _(planned)_
| Field | Type |
|---|---|
| id | int (PK) |
| name | str |
| created_by_id | int (FK → User) |

### GroupMember _(planned)_
| Field | Type |
|---|---|
| group_id | int (FK → Group, PK) |
| user_id | int (FK → User, PK) |

## Authentication

JWT-based. All endpoints are protected.

- `POST /auth/register` — create account (restricted to allowlisted emails via `ALLOWED_EMAILS` env var)
- `POST /auth/login` — returns JWT token
- `GET /auth/me` — returns current user's public info (id, email, last_email_sync)

## API Endpoints

| Method | Path | Description |
|---|---|---|
| POST | `/suppliers` | Create a supplier |
| GET | `/suppliers` | All suppliers with available balance and user's color |
| PATCH | `/suppliers/{id}/preference` | Set per-user color for a supplier |
| GET | `/suppliers/{id}/coupons` | All coupons for a supplier |
| POST | `/coupons` | Add a coupon manually |
| PATCH | `/coupons/{id}/use` | Toggle coupon used/unused |
| POST | `/import/email` | Manually trigger email import |
| GET | `/auth/me` | Current user info including last sync time |

## Coupon Ingestion

### Manual
User enters supplier, value, and coupon code directly via `POST /coupons`.

### Email Auto Import
Connects to a Gmail inbox via IMAP, parses unread emails from coupon providers, extracts supplier name, value, and numeric coupon code, then creates coupons automatically. Triggered manually via `POST /import/email` or automatically once a day at 6am via APScheduler.

Email format supported: Cibus/supermarket coupon emails (Hebrew).

## Database Backup

Backups are stored as gzipped pg_dump files on Cloudflare R2 (`coupon-assets/backups/`).

```bash
make backup   # manual backup
make restore  # restore latest backup
```

Automated daily backup runs at 2am via APScheduler. Requires `R2_*` env vars to be set.

## Roadmap

| # | Stage | Status |
|---|-------|--------|
| 1 | Models — Supplier, Coupon, User | ✅ |
| 2 | JWT auth — register, login | ✅ |
| 3 | REST endpoints — suppliers, coupons, use/unuse | ✅ |
| 4 | Email import — IMAP + body parser, manual trigger | ✅ |
| 5 | Deployment — Docker Compose + Cloudflare Tunnel on Raspberry Pi | ✅ |
| 6 | Daily auto-import — APScheduler runs email import once a day | ✅ |
| 7 | Supplier logos | 🔲 |
| 8 | UTC timestamps — TIMESTAMPTZ columns, timezone-aware responses | ✅ |
| 9 | Groups — users create groups, invite others by email; coupons scoped to a group | ⬜ |
| 10 | Coupon code encryption — AES encryption at rest; key in `.env` now, KMS at scale | ⬜ |
| 11 | Per-user email import — each user connects their own Gmail via OAuth; coupons imported into their group | 🔲 |
| 12 | Per-user coupon permissions — finer-grained access control within groups | 🔲 |
| 13 | DB backup — daily pg_dump to Cloudflare R2, manual restore script | ✅ |
| 14 | Per-user supplier color — each user sets their own display color per supplier | ✅ |

## Local Development

### Prerequisites
- Docker Desktop
- Python 3.14+
- `make` (optional, for shorthand commands)

### Setup

```bash
cd back
cp .env.example .env   # fill in values
make build             # docker compose up --build
# Swagger UI: http://localhost:8000/docs
```

### Common commands

```bash
make up       # start containers
make down     # stop containers
make reset    # wipe DB and restart (docker compose down -v + up --build)
make logs     # tail api logs
make backup   # run backup manually
make restore  # restore latest backup from R2
```

## Deployment

Runs on a Raspberry Pi via Docker Compose. Public access via Cloudflare Tunnel — set `CLOUDFLARE_TUNNEL_TOKEN` in `.env`.
