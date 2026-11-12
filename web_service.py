import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, request, jsonify, g, send_from_directory

app = Flask(__name__)


UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", "/app/uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


DB_HOST = os.environ.get("DB_HOST", "db")
DB_PORT = os.environ.get("DB_PORT", "5432")
DB_NAME = os.environ.get("DB_NAME", "videos")
DB_USER = os.environ.get("DB_USER", "video_user")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "video_pass")

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            cursor_factory=RealDictCursor
        )
    return db

@app.teardown_appcontext
def close_connection(exception):
    """Закрывает соединение с БД по окончании запроса."""
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            connect_timeout=5
        )
        conn.autocommit = True
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS videos (
                    id SERIAL PRIMARY KEY,
                    company_name TEXT NOT NULL UNIQUE,
                    file_path TEXT NOT NULL,
                    video_url TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
                );
            """)
        conn.close()
        print("[init_db] Table 'videos' verified/created.")
    except Exception as e:
        print(f"[init_db] Warning: {e}", file=sys.stderr)


init_db()

@app.route('/')
def index():
    return jsonify({
        "status": "online",
        "service": "Flask Video Web Service",
        "web_server": "Apache + mod_wsgi",
        "database": "PostgreSQL 16",
        "endpoints": {
            "upload": "POST /upload",
            "get_video_url": "GET /get_video_url?company_name=...",
            "list_videos": "GET /videos"
        }
    }), 200

@app.route('/upload', methods=['POST'])
def upload_video():
    file = request.files.get('file') or request.files.get('video')
    company_name = request.form.get('company_name')

    if not file or not company_name or file.filename == '':
        return jsonify({"error": "Missing company_name or file"}), 400

    company_name = company_name.strip()
    safe_name = "".join(c if c.isalnum() else "_" for c in company_name)
    
    _, ext = os.path.splitext(file.filename)
    if not ext:
        ext = '.webm'
    filename = f"{safe_name}{ext}"

    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)

    base_url = request.host_url.rstrip('/')
    video_url = f"{base_url}/media/{filename}"
    absolute_file_path = os.path.abspath(file_path)

    db = get_db()
    with db.cursor() as cursor:
        cursor.execute("""
            INSERT INTO videos (company_name, file_path, video_url, updated_at)
            VALUES (%s, %s, %s, NOW())
            ON CONFLICT (company_name) DO UPDATE SET
                file_path = EXCLUDED.file_path,
                video_url = EXCLUDED.video_url,
                updated_at = NOW();
        """, (company_name, absolute_file_path, video_url))
        db.commit()

    return jsonify({
        "status": "success",
        "company_name": company_name,
        "video_url": video_url
    }), 200

@app.route('/get_video_url', methods=['GET'])
def get_video_url():
    company_name = request.args.get('company_name')
    if not company_name:
        return jsonify({"error": "Missing company_name parameter"}), 400

    db = get_db()
    with db.cursor() as cursor:
        cursor.execute("SELECT video_url FROM videos WHERE company_name = %s LIMIT 1", (company_name.strip(),))
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
    with db.cursor() as cursor:
        cursor.execute("SELECT id, company_name, video_url, file_path, created_at, updated_at FROM videos ORDER BY id DESC")
        rows = cursor.fetchall()
    return jsonify([dict(row) for row in rows]), 200

if __name__ == '__main__':
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', 8000))
    app.run(host=host, port=port, debug=False)