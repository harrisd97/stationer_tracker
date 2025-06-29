from flask import Flask, render_template, request, jsonify
from db_config import get_connection
from psycopg2.extras import RealDictCursor
import json
import logging
import 'os'

# Configure logging
logging.basicConfig(
    filename='stationer_tracker.log',
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s: %(message)s'
)

app = Flask(__name__)

@app.before_request
def log_request_info():
    logging.info(f"Request: {request.method} {request.path} - {request.remote_addr}")
    if request.is_json:
        logging.debug(f"Request JSON: {request.get_json()}")

@app.after_request
def log_response_info(response):
    try:
        logging.info(f"Response Status: {response.status}")
        logging.debug(f"Response Body: {response.get_data(as_text=True)}")
    except Exception as e:
        logging.warning(f"Error logging response: {e}")
    return response

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/projects')
def projects():
    return render_template("projects.html")

@app.route('/client-experiences')
def client_experience():
    return render_template("client.html")

@app.route('/api/projects')
def get_projects():
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 10))
    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                logging.debug("Executing sp_get_project_list with params: %s, %s", page, limit)
                cur.execute("SELECT * FROM sp_get_project_list(%s, %s);", (page, limit))
                rows = cur.fetchall()
                logging.info(f"Fetched {len(rows)} projects")
        return jsonify(rows)
    except Exception:
        logging.exception("Error fetching projects")
        return jsonify({"success": False, "error": "Failed to fetch projects"}), 500

@app.route('/api/project/<int:project_id>')
def get_project_by_id(project_id):
    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                logging.debug("Executing sp_get_project_by_id with id: %s", project_id)
                cur.execute("SELECT * FROM sp_get_project_by_id(%s);", (project_id,))
                row = cur.fetchone()
                if row:
                    logging.info(f"Found project ID: {project_id}")
                else:
                    logging.warning(f"No project found for ID: {project_id}")
        return jsonify(row)
    except Exception:
        logging.exception("Error fetching project by ID")
        return jsonify({"success": False, "error": "Failed to fetch project"}), 500

@app.route('/api/project', methods=["POST"])
def save_project():
    try:
        payload = request.get_json()
        logging.info(f"Received project payload: {json.dumps(payload)}")
        with get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                logging.debug("Calling sp_save_project with payload: %s", json.dumps(payload))
                cur.execute("SELECT sp_save_project(%s)", [json.dumps(payload)])
                result = cur.fetchone()
                message = result['sp_save_project'] if result and 'sp_save_project' in result else "No response from database"
                logging.info(f"DB response: {message}")
                return jsonify({"status": "success", "message": message})
    except Exception:
        logging.exception("Error saving project")
        return jsonify({"status": "error", "message": "Something went wrong while saving the project."}), 500

@app.route('/api/lov/<string:ref_name>')
def get_lov(ref_name):
    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                logging.debug("Fetching LOV for reference: %s", ref_name)
                cur.execute("SELECT * FROM sp_get_lov_by_reference(%s);", (ref_name,))
                rows = cur.fetchall()
                logging.info(f"Fetched {len(rows)} LOV entries for {ref_name}")
        return jsonify(rows)
    except Exception:
        logging.exception("Error fetching LOV")
        return jsonify({"success": False, "error": "Failed to fetch LOV"}), 500

@app.route('/api/client-experiences')
def get_client_experiences():
    try:
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 10))
        logging.info(f"Fetching client experiences: page={page}, limit={limit}")
        with get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                logging.debug("Executing sp_get_client_experience_list with params: %s, %s", page, limit)
                cur.execute("SELECT * FROM sp_get_client_experience_list(%s, %s);", (page, limit))
                rows = cur.fetchall()
                logging.info(f"Fetched {len(rows)} client experiences")
        return jsonify(rows)
    except Exception:
        logging.exception("Error fetching client experiences list")
        return jsonify({"success": False, "error": "Failed to fetch client experiences"}), 500

@app.route('/api/client-experience/<int:experience_id>')
def get_client_experience_by_id(experience_id):
    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                logging.debug("Fetching experience ID: %s", experience_id)
                cur.execute("SELECT * FROM sp_get_client_experience_by_id(%s);", (experience_id,))
                row = cur.fetchone()
                if row:
                    logging.info(f"Found experience ID: {experience_id}")
                else:
                    logging.warning(f"No experience for ID: {experience_id}")
        return jsonify(row)
    except Exception:
        logging.exception("Error fetching experience by ID")
        return jsonify({"success": False, "error": "Failed to fetch experience"}), 500

@app.route('/api/client-experience', methods=["POST"])
def save_client_experience():
    conn = None
    cur = None
    try:
        payload = request.get_json()
        logging.info(f"Received client experience payload: {json.dumps(payload)}")
        with get_connection() as conn:
            with conn.cursor() as cur:
                logging.debug("Calling sp_save_client_experience with payload: %s", json.dumps(payload))
                cur.execute("SELECT sp_save_client_experience(%s)", [json.dumps(payload)])
                result = cur.fetchone()
                conn.commit()
                message = result['sp_save_client_experience'] if result and 'sp_save_client_experience' in result else "No response"
                logging.info(f"DB response: {message}")
                return jsonify({"status": "success", "message": message})
    except Exception:
        logging.exception("Error saving client experience")
        return jsonify({"status": "error", "message": "Failed to save client experience"}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

@app.route('/api/client-experience/dashboard', methods=['GET'])
def get_dashboard_summary():
    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                logging.debug("Executing sp_get_client_experience_summary")
                cur.execute("SELECT * FROM sp_get_client_experience_summary()")
                result = cur.fetchone()
                logging.info(f"Dashboard summary: {result}")
        if result:
            return jsonify({
                "avgScore": result["avg_score"],
                "testimonialPct": result["testimonial_pct"],
                "referralPct": result["referral_pct"],
                "totalEntries": result["total_entries"]
            })
        else:
            logging.warning("No data in dashboard summary")
            return jsonify({
                "avgScore": "-",
                "testimonialPct": "-",
                "referralPct": "-",
                "totalEntries": "-"
            })
    except Exception:
        logging.exception("Error fetching dashboard summary")
        return jsonify({"error": "Failed to fetch dashboard data"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5050))
    app.run(debug=True, host='0.0.0.0', port=port)
