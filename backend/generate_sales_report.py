import os
import psycopg2
from datetime import date
import logging

DB_HOST = os.environ.get("DB_HOST", "postgres-svc")
DB_USER = os.environ.get("DB_USER", "bookstore")
DB_PASS = os.environ.get("DB_PASS", "bookstore123")
DB_NAME = os.environ.get("DB_NAME", "bookstoredb")

log_file_path = "/var/log/sales_report.log"
logging.basicConfig(filename=log_file_path, level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

def get_conn():
    return psycopg2.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        dbname=DB_NAME
    )

def generate_daily_sales_report():
    today = date.today()
    try:
        conn = get_conn()
        with conn.cursor() as cur:
            cur.execute(
                "SELECT COALESCE(SUM(total_amount), 0) FROM orders WHERE order_date = %s;",
                (today,)
            )
            total_sales = cur.fetchone()[0]
        conn.close()
        logging.info(f"Daily sales report for {today}: Total Sales = ${total_sales:.2f}")
        print(f"Daily sales report for {today}: Total Sales = ${total_sales:.2f}")
    except Exception as e:
        logging.error(f"Failed to generate sales report: {e}")
        print(f"Failed to generate sales report: {e}")

if __name__ == "__main__":
    generate_daily_sales_report()
