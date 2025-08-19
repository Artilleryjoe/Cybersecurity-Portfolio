from flask import Flask, request, jsonify, session, redirect
import sqlite3
import os
import logging
from collections import defaultdict

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev")
DB_PATH = os.path.join(os.path.dirname(__file__), 'users.db')

logging.basicConfig(level=logging.INFO)
ENABLE_VULNERABLE_ENDPOINTS = os.getenv("ENABLE_VULNERABLE_ENDPOINTS", "true").lower() == "true"
attempt_counts = defaultdict(int)

def init_db():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, email TEXT)')
    cur.executemany('INSERT INTO users (name, email) VALUES (?, ?)', [
        ('Alice', 'alice@example.com'),
        ('Bob', 'bob@example.com'),
        ('Charlie', 'charlie@example.com'),
    ])
    conn.commit()
    conn.close()

def is_suspicious(value: str) -> bool:
    patterns = ["'", '"', ';', '--', ' or ']
    val = value.lower()
    return any(p in val for p in patterns)

@app.route('/')
def disclaimer():
    if session.get('ack'):
        return "Disclaimer acknowledged."
    return (
        '<h1>Disclaimer</h1>'
        '<p>This demo includes intentionally vulnerable modules. Use only on authorized systems.</p>'
        '<form method="post" action="/ack"><button type="submit">I Understand</button></form>'
    )

@app.route('/ack', methods=['POST'])
def acknowledge():
    session['ack'] = True
    return redirect('/')

if ENABLE_VULNERABLE_ENDPOINTS:
    @app.route('/insecure/search')
    def insecure_search():
        if not session.get('ack'):
            return jsonify({'error': 'Disclaimer acknowledgment required'}), 403
        name = request.args.get('name', '')
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        query = f"SELECT id, name, email FROM users WHERE name = '{name}'"
        try:
            cur.execute(query)
            rows = cur.fetchall()
        except Exception:
            rows = []
        conn.close()
        if is_suspicious(name):
            ip = request.remote_addr or 'unknown'
            attempt_counts[ip] += 1
            if attempt_counts[ip] > 3:
                app.logger.warning(f"Repeated exploitation attempts from {ip}")
        return jsonify({'query': query, 'results': rows})
else:
    @app.route('/insecure/search')
    def insecure_search():
        return jsonify({'error': 'Vulnerable endpoint disabled'}), 404

@app.route('/secure/search')
def secure_search():
    name = request.args.get('name', '')
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    query = 'SELECT id, name, email FROM users WHERE name = ?'
    cur.execute(query, (name,))
    rows = cur.fetchall()
    conn.close()
    return jsonify({'query': query, 'results': rows})

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=8000)
