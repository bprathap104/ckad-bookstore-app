FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
COPY init_db.py .
COPY generate_sales_report.py .
COPY cleanup_old_orders.py .
EXPOSE 5000
CMD ["python", "app.py"]
