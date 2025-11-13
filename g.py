import os
import textwrap
import subprocess
from pathlib import Path

PROJECT_DIR = Path("docker_compose_lab")
APP_DIR = PROJECT_DIR / "webapp"
STATIC_DIR = APP_DIR / "static"
TEMPLATES_DIR = APP_DIR / "templates"


def write_file(path: Path, content: str):
    """Создаёт файл с содержимым"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(content).lstrip(), encoding="utf-8")
    print(f"✅ Written: {path}")


def create_files():
    # Flask web app (frontend + API)
    write_file(
        APP_DIR / "app.py",
        """
        from flask import Flask, render_template, request, jsonify, redirect, url_for
        import sqlite3, os

        app = Flask(__name__)
        DB_PATH = os.path.join(os.path.dirname(__file__), 'data.db')

        def init_db():
            conn = sqlite3.connect(DB_PATH)
            conn.execute("CREATE TABLE IF NOT EXISTS notes(id INTEGER PRIMARY KEY, text TEXT)")
            conn.commit()
            conn.close()

        @app.route('/')
        def index():
            conn = sqlite3.connect(DB_PATH)
            notes = conn.execute("SELECT id, text FROM notes ORDER BY id DESC").fetchall()
            conn.close()
            return render_template("index.html", notes=notes)

        @app.route('/add', methods=['POST'])
        def add_note():
            text = request.form.get("text", "").strip()
            if text:
                conn = sqlite3.connect(DB_PATH)
                conn.execute("INSERT INTO notes(text) VALUES (?)", (text,))
                conn.commit()
                conn.close()
            return redirect(url_for('index'))

        @app.route('/api/notes')
        def api_notes():
            conn = sqlite3.connect(DB_PATH)
            notes = conn.execute("SELECT id, text FROM notes ORDER BY id DESC").fetchall()
            conn.close()
            return jsonify([{"id": n[0], "text": n[1]} for n in notes])

        if __name__ == "__main__":
            init_db()
            app.run(host="0.0.0.0", port=5000)
        """
    )

    # HTML template
    write_file(
        TEMPLATES_DIR / "index.html",
        """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Notes App</title>
            <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
        </head>
        <body>
            <div class="container">
                <h1>Docker Compose Notes</h1>
                <form method="POST" action="/add">
                    <input type="text" name="text" placeholder="Write a note..." required>
                    <button type="submit">Add</button>
                </form>
                <ul>
                {% for n in notes %}
                    <li>{{ n[1] }}</li>
                {% else %}
                    <li class="empty">No notes yet!</li>
                {% endfor %}
                </ul>
            </div>
        </body>
        </html>
        """
    )

    # CSS
    write_file(
        STATIC_DIR / "style.css",
        """
        body {
            background: #f7f7f7;
            font-family: system-ui, sans-serif;
        }
        .container {
            max-width: 600px;
            margin: 60px auto;
            background: white;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        h1 {
            margin-top: 0;
            text-align: center;
        }
        form {
            display: flex;
            gap: 8px;
            margin-bottom: 20px;
        }
        input {
            flex: 1;
            padding: 10px;
            border: 1px solid #ccc;
            border-radius: 8px;
        }
        button {
            background: #0066cc;
            color: white;
            border: none;
            padding: 10px 14px;
            border-radius: 8px;
            cursor: pointer;
        }
        button:hover {
            background: #004c99;
        }
        ul { list-style: none; padding: 0; }
        li {
            padding: 10px;
            border-bottom: 1px solid #eee;
        }
        .empty { color: #777; text-align: center; }
        """
    )

    # Flask requirements
    write_file(
        APP_DIR / "requirements.txt",
        "Flask==3.0.3\n"
    )

    # Dockerfile for Flask app
    write_file(
        PROJECT_DIR / "Dockerfile",
        """
        FROM python:3.11-slim
        WORKDIR /app
        COPY webapp/requirements.txt .
        RUN pip install --no-cache-dir -r requirements.txt
        COPY webapp /app
        EXPOSE 5000
        CMD ["python", "app.py"]
        """
    )

    # Nginx reverse proxy
    write_file(
        PROJECT_DIR / "nginx.conf",
        """
        events {}
        http {
            server {
                listen 80;
                location / {
                    proxy_pass http://web:5000;
                    proxy_set_header Host $host;
                    proxy_set_header X-Real-IP $remote_addr;
                }
            }
        }
        """
    )

    # PostgreSQL + pgAdmin services
    write_file(
        PROJECT_DIR / ".env",
        """
        POSTGRES_USER=appuser
        POSTGRES_PASSWORD=apppass
        POSTGRES_DB=appdb
        PGADMIN_DEFAULT_EMAIL=admin@example.com
        PGADMIN_DEFAULT_PASSWORD=admin
        """
    )

    # docker-compose.yml
    write_file(
        PROJECT_DIR / "docker-compose.yml",
        """
        services:
          web:
            build: .
            volumes:
              - ./webapp:/app
            ports:
              - "5000:5000"
            restart: always

          nginx:
            image: nginx:latest
            volumes:
              - ./nginx.conf:/etc/nginx/nginx.conf:ro
            ports:
              - "8080:80"
            depends_on:
              - web
            restart: always

          db:
            image: postgres:16-alpine
            env_file: .env
            volumes:
              - db_data:/var/lib/postgresql/data
            ports:
              - "5432:5432"
            restart: always

          pgadmin:
            image: dpage/pgadmin4:8
            env_file: .env
            ports:
              - "8081:80"
            depends_on:
              - db
            restart: always

        volumes:
          db_data:
        """
    )

    # README
    write_file(
        PROJECT_DIR / "README.md",
        """
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
        """
    )


def try_run():
    """Пробует запустить docker compose"""
    print("\n🚀 Attempting docker compose up...\n")
    try:
        subprocess.run(["docker", "compose", "up", "-d", "--build"], cwd=PROJECT_DIR, check=True)
        print("\n✅ Containers are running:")
        print("http://localhost:8080  — Web app (Nginx + Flask)")
        print("http://localhost:8081  — pgAdmin")
    except Exception as e:
        print("\n⚠️ Could not auto-start Docker Compose.")
        print(f"Manual start:\n  cd {PROJECT_DIR}\n  docker compose up -d --build\n\n{e}")


def main():
    create_files()
    try_run()
    print(f"\n📁 Project created at: {PROJECT_DIR.resolve()}")


if __name__ == "__main__":
    main()
