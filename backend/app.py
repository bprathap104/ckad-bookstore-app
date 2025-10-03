from flask import Flask, request, jsonify
import logging
import os
import psycopg2
from flask_cors import CORS

DB_HOST = os.environ.get("DB_HOST", "postgres-svc")
DB_USER = os.environ.get("DB_USER", "bookstore")
DB_PASS = os.environ.get("DB_PASS", "bookstore123")
DB_NAME = os.environ.get("DB_NAME", "bookstoredb")

app = Flask(__name__)
CORS(app)

# Setup logging to /var/log/backend.log
log_file_path = "/var/log/backend.log"
logging.basicConfig(filename=log_file_path, level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

@app.before_request
def log_request_info():
    if request.path != "/health":
        app.logger.info(f"{request.remote_addr} {request.method} {request.path}")

def get_conn():
    return psycopg2.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        dbname=DB_NAME
    )



@app.route("/books", methods=["GET"])
def get_books():
    try:
        conn = get_conn()
        with conn.cursor() as cur:
            cur.execute("SELECT id, title, author FROM books;")
            rows = cur.fetchall()
            books = [{"id": row[0], "title": row[1], "author": row[2]} for row in rows]
        conn.close()
        return jsonify(books)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
