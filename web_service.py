import os
import sqlite3
from flask import Flask, request, jsonify, g, send_from_directory

app = Flask(__name__)

UPLOAD_FOLDER = os.path.abspath("uploads")
DB_PATH = "videos.db"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DB_PATH)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA journal_mode=WAL;")
        db.execute("PRAGMA busy_timeout=5000;")
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA busy_timeout=5000;")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS videos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_name TEXT NOT NULL UNIQUE,
                file_path TEXT NOT NULL,
                video_url TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now'))
            );
        """)
        conn.commit()

@app.route('/upload', methods=['POST'])
def upload_video():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    company_name = request.form.get('company_name')

    if not company_name or file.filename == '':
        return jsonify({"error": "Missing company_name or file"}), 400

    safe_name = "".join(c if c.isalnum() else "_" for c in company_name)
    filename = f"{safe_name}.webm"
    
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)

    base_url = request.host_url.rstrip('/')
    video_url = f"{base_url}/media/{filename}"
    absolute_file_path = os.path.abspath(file_path)

    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        INSERT INTO videos (company_name, file_path, video_url, updated_at)
        VALUES (?, ?, ?, datetime('now'))
        ON CONFLICT(company_name) DO UPDATE SET
            file_path = excluded.file_path,
            video_url = excluded.video_url,
            updated_at = datetime('now')
    """, (company_name, absolute_file_path, video_url))
    db.commit()

    return jsonify({
        "company_name": company_name,
        "video_url": video_url
    }), 200

@app.route('/get_video_url', methods=['GET'])
def get_video_url():
    company_name = request.args.get('company_name')
    if not company_name:
        return jsonify({"error": "Missing company_name parameter"}), 400

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT video_url FROM videos WHERE company_name = ?", (company_name,))
    row = cursor.fetchone()

    if not row:
        return jsonify({"error": "Company not found"}), 404

    return jsonify({
        "company_name": company_name,
        "video_url": row['video_url']
    }), 200

@app.route('/media/<path:filename>', methods=['GET'])
def serve_media(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/videos', methods=['GET'])
def list_videos():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id, company_name, video_url, file_path, created_at, updated_at FROM videos")
    rows = cursor.fetchall()
    return jsonify([dict(row) for row in rows]), 200

if __name__ == '__main__':
    init_db()
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', 8000))
    app.run(host=host, port=port, debug=False)