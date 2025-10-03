import os
import psycopg2
import time
import sys

DB_HOST = os.environ.get("DB_HOST", "postgres-svc")
DB_USER = os.environ.get("DB_USER", "bookstore")
DB_PASS = os.environ.get("DB_PASS", "bookstore123")
DB_NAME = os.environ.get("DB_NAME", "bookstoredb")

def get_conn():
    return psycopg2.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        dbname=DB_NAME
    )

def wait_for_db():
    while True:
        try:
            conn = get_conn()
            conn.close()
            print("DB is ready")
            break
        except Exception as e:
            print(f"Waiting for DB: {e}")
            time.sleep(2)

def init_db():
    try:
        conn = get_conn()
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS books (
                    id SERIAL PRIMARY KEY,
                    title VARCHAR(255) NOT NULL,
                    author VARCHAR(255) NOT NULL
                );
                CREATE TABLE IF NOT EXISTS orders (
                    id SERIAL PRIMARY KEY,
                    order_date DATE NOT NULL,
                    total_amount NUMERIC(10, 2) NOT NULL
                );
            """)
            cur.execute("SELECT COUNT(*) FROM books;")
            count = cur.fetchone()[0]
            if count == 0:
                cur.execute("""
                    INSERT INTO books (title, author) VALUES
                    ('CKAD Essentials', 'OpenAI'),
                    ('Kubernetes Deep Dive', 'Cloud Guru'),
                    ('Docker Mastery', 'Bret Fisher'),
                    ('Microservices Patterns', 'Chris Richardson'),
                    ('The Phoenix Project', 'Gene Kim');
                """)
            conn.commit()
        conn.close()
        print("DB schema initialized")
    except Exception as e:
        print(f"DB init failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    wait_for_db()
    init_db()
