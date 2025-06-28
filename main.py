from flask import Flask, render_template, request, jsonify
from db_config import get_connection
import json
import logging

# Set up logging to file
logging.basicConfig(
    filename='stationer_tracker.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s'
)

app = Flask(__name__)

@app.before_request
def log_request_info():
    logging.info(f"Request: {request.method} {request.path} - {request.remote_addr}")

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/projects')
def projects():
    return render_template("projects.html")

@app.route('/api/projects')
def get_projects():
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 10))
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM sp_get_project_list(%s, %s);", (page, limit))
            rows = cur.fetchall()
    return jsonify(rows)

@app.route('/api/project/<int:project_id>')
def get_project_by_id(project_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM sp_get_project_by_id(%s);", (project_id,))
            row = cur.fetchone()
    return jsonify(row)

@app.route('/api/project', methods=["POST"])
def save_project():
    data = request.get_json()
    logging.info(f"Payload received: {json.dumps(data, indent=2)}")  # 🔍 Log the payload
    
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT sp_save_project(%s);", (json.dumps(data),))
                result = cur.fetchone()
                if result and isinstance(result, tuple):
                    return result[0]
                elif isinstance(result, dict) and 'sp_save_project' in result:
                    return result['sp_save_project']
                else:
                    return "Saved successfully"
    except Exception as e:
        logging.error(f"Error in save_project: {str(e)}")
        return "Error saving project", 500

@app.route('/api/lov/<string:ref_name>')
def get_lov(ref_name):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM sp_get_lov_by_reference(%s);", (ref_name,))
            rows = cur.fetchall()
    return jsonify(rows)

import os

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5050))
    app.run(debug=True, host='0.0.0.0', port=port)
