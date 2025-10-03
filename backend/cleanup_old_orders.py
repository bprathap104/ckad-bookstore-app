import os
import psycopg2
from datetime import date, timedelta
import logging

DB_HOST = os.environ.get("DB_HOST", "postgres-svc")
DB_USER = os.environ.get("DB_USER", "bookstore")
DB_PASS = os.environ.get("DB_PASS", "bookstore123")
DB_NAME = os.environ.get("DB_NAME", "bookstoredb")

log_file_path = "/var/log/cleanup.log"
logging.basicConfig(filename=log_file_path, level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

def get_conn():
    return psycopg2.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        dbname=DB_NAME
    )

def cleanup_old_orders():
    cutoff_date = date.today() - timedelta(days=30)
    try:
        conn = get_conn()
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM orders WHERE order_date < %s;",
                (cutoff_date,)
            )
            deleted_count = cur.rowcount
            conn.commit()
        conn.close()
        logging.info(f"Cleaned up {deleted_count} orders older than {cutoff_date}")
        print(f"Cleaned up {deleted_count} orders older than {cutoff_date}")
    except Exception as e:
        logging.error(f"Failed to cleanup old orders: {e}")
        print(f"Failed to cleanup old orders: {e}")

if __name__ == "__main__":
    cleanup_old_orders()
