# Docker Compose Lab: Flask + SQLite + Nginx + PostgreSQL + pgAdmin

## Start project
docker compose up -d --build

## Open in browser
- Flask web app: http://localhost:8080
- Direct Flask: http://localhost:5000
- pgAdmin: http://localhost:8081
    - Email: admin@example.com
    - Password: admin

## Stop project
docker compose down

## Full clean (remove DB volume)
docker compose down -v
