from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(__file__), 'users.db')

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

@app.route('/insecure/search')
def insecure_search():
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
    return jsonify({'query': query, 'results': rows})

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
