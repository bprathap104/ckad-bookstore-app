from flask import Flask, request, jsonify
import logging
import os
import psycopg2
from flask_cors import CORS
import requests
import time

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

@app.route("/trigger-report", methods=["POST"])
def trigger_report():
    try:
        with open('/var/run/secrets/kubernetes.io/serviceaccount/token') as f:
            token = f.read().strip()
        headers = {'Authorization': f'Bearer {token}'}
        k8s_api = 'https://kubernetes.default.svc'
        namespace = 'bookstore-app'
        ca_cert = '/var/run/secrets/kubernetes.io/serviceaccount/ca.crt'

        # Get cronjob spec
        url = f'{k8s_api}/apis/batch/v1/namespaces/{namespace}/cronjobs/generate-sales-report'
        resp = requests.get(url, headers=headers, verify=ca_cert)
        if resp.status_code != 200:
            return jsonify({'error': 'Failed to get cronjob'}), 500
        cronjob = resp.json()
        job_spec = cronjob['spec']['jobTemplate']['spec']

        # Create job
        job_name = f'generate-sales-report-manual-{int(time.time())}'
        job = {
            'apiVersion': 'batch/v1',
            'kind': 'Job',
            'metadata': {
                'name': job_name,
                'namespace': namespace
            },
            'spec': job_spec
        }
        resp = requests.post(f'{k8s_api}/apis/batch/v1/namespaces/{namespace}/jobs', headers=headers, json=job, verify=ca_cert)
        if resp.status_code != 201:
            return jsonify({'error': 'Failed to create job'}), 500

        # Wait for completion
        while True:
            resp = requests.get(f'{k8s_api}/apis/batch/v1/namespaces/{namespace}/jobs/{job_name}', headers=headers, verify=ca_cert)
            if resp.status_code != 200:
                return jsonify({'error': 'Failed to get job status'}), 500
            status = resp.json()['status']
            if status.get('succeeded'):
                break
            elif status.get('failed'):
                return jsonify({'error': 'Job failed'}), 500
            time.sleep(5)

        # Get pod
        resp = requests.get(f'{k8s_api}/api/v1/namespaces/{namespace}/pods?labelSelector=job-name={job_name}', headers=headers, verify=ca_cert)
        if resp.status_code != 200:
            return jsonify({'error': 'Failed to get pods'}), 500
        pods = resp.json()['items']
        if not pods:
            return jsonify({'error': 'No pods found'}), 500
        pod_name = pods[0]['metadata']['name']

        # Get logs
        resp = requests.get(f'{k8s_api}/api/v1/namespaces/{namespace}/pods/{pod_name}/log', headers=headers, verify=ca_cert)
        if resp.status_code != 200:
            return jsonify({'error': 'Failed to get logs'}), 500
        logs = resp.text
        return jsonify({'logs': logs})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
