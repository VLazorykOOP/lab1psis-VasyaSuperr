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
