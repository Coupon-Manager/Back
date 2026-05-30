.PHONY: up down reset build logs shell backup restore

up:
	docker compose up

down:
	docker compose down

reset:
	docker compose down -v
	docker compose up --build

backup:
	docker compose exec api python scripts/backup.py

restore:
	docker compose exec api python scripts/restore.py
