from flask import Flask, render_template, request, jsonify
from db_config import get_connection
from psycopg2.extras import RealDictCursor
import json
import logging
import os

# --------------------------------------
# Flask App Setup with Logging
# --------------------------------------
app = Flask(__name__)

logging.basicConfig(
    filename='stationer_tracker.log',
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s: %(message)s'
)

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

# --------------------------------------
# Page Routes
# --------------------------------------
@app.route('/')
def home():
    return render_template("index.html")

@app.route('/projects')
def projects():
    return render_template("projects.html")

@app.route('/client-experiences')
def client_experience():
    return render_template("client.html")

@app.route('/costs')
def expenses():
    return render_template("expenses.html")

# --------------------------------------
# LOV (List of Values)
# --------------------------------------
@app.route('/api/lov/<string:ref_name>')
def get_lov(ref_name):
    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM sp_get_lov_by_reference(%s);", (ref_name,))
                return jsonify(cur.fetchall())
    except Exception:
        logging.exception("Error fetching LOV")
        return jsonify({"success": False, "error": "Failed to fetch LOV"}), 500

# --------------------------------------
# Project APIs
# --------------------------------------
@app.route('/api/projects')
def get_projects():
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 10))
    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM sp_get_project_list(%s, %s);", (page, limit))
                return jsonify(cur.fetchall())
    except Exception:
        logging.exception("Error fetching projects")
        return jsonify({"success": False, "error": "Failed to fetch projects"}), 500

@app.route('/api/project/<int:project_id>')
def get_project_by_id(project_id):
    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM sp_get_project_by_id(%s);", (project_id,))
                return jsonify(cur.fetchone())
    except Exception:
        logging.exception("Error fetching project by ID")
        return jsonify({"success": False, "error": "Failed to fetch project"}), 500

@app.route('/api/project', methods=["POST"])
def save_project():
    try:
        payload = request.get_json()
        with get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT sp_save_project(%s)", [json.dumps(payload)])
                result = cur.fetchone()
                message = result['sp_save_project'] if result and 'sp_save_project' in result else "No response"
        return jsonify({"status": "success", "message": message})
    except Exception:
        logging.exception("Error saving project")
        return jsonify({"status": "error", "message": "Something went wrong while saving the project."}), 500

@app.route('/api/projects/search')
def search_projects():
    query = request.args.get('query', '', type=str)
    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM sp_search_projects(%s);", (query,))
                return jsonify(cur.fetchall())
    except Exception:
        logging.exception("Error fetching project search results")
        return jsonify({"success": False, "error": "Failed to fetch search results"}), 500

# --------------------------------------
# Client Experience APIs
# --------------------------------------
@app.route('/api/client-experiences')
def get_client_experiences():
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 10))
    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM sp_get_client_experience_list(%s, %s);", (page, limit))
                return jsonify(cur.fetchall())
    except Exception:
        logging.exception("Error fetching client experiences")
        return jsonify({"success": False, "error": "Failed to fetch client experiences"}), 500

@app.route('/api/client-experience/<int:experience_id>')
def get_client_experience_by_id(experience_id):
    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM sp_get_client_experience_by_id(%s);", (experience_id,))
                return jsonify(cur.fetchone())
    except Exception:
        logging.exception("Error fetching client experience by ID")
        return jsonify({"success": False, "error": "Failed to fetch experience"}), 500

@app.route('/api/client-experience', methods=["POST"])
def save_client_experience():
    try:
        payload = request.get_json()
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT sp_save_client_experience(%s)", [json.dumps(payload)])
                result = cur.fetchone()
                conn.commit()
                message = result['sp_save_client_experience'] if result and 'sp_save_client_experience' in result else "No response"
        return jsonify({"status": "success", "message": message})
    except Exception:
        logging.exception("Error saving client experience")
        return jsonify({"status": "error", "message": "Failed to save client experience"}), 500

@app.route('/api/client-experience/dashboard')
def get_dashboard_summary():
    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM sp_get_client_experience_summary()")
                result = cur.fetchone()
        return jsonify({
            "avgScore": result["avg_score"],
            "testimonialPct": result["testimonial_pct"],
            "referralPct": result["referral_pct"],
            "totalEntries": result["total_entries"]
        }) if result else jsonify({"avgScore": "-", "testimonialPct": "-", "referralPct": "-", "totalEntries": "-"})
    except Exception:
        logging.exception("Error fetching dashboard data")
        return jsonify({"error": "Failed to fetch dashboard data"}), 500

# --------------------------------------
# Project Cost (Expense) APIs
# --------------------------------------
@app.route('/api/project-costs')
def get_project_costs():
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 10))
    search = request.args.get("search", "")
    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM sp_get_project_cost_list(%s, %s, %s);", (page, limit, search))
                return jsonify(cur.fetchall())
    except Exception:
        logging.exception("Error fetching project costs")
        return jsonify({"success": False, "error": "Failed to fetch project costs"}), 500

@app.route('/api/project-cost/<int:project_id>')
def get_project_cost_by_id(project_id):
    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM sp_get_project_cost_by_id(%s);", (project_id,))
                return jsonify(cur.fetchall())
    except Exception:
        logging.exception("Error fetching cost by ID")
        return jsonify({"success": False, "error": "Failed to fetch cost"}), 500

@app.route('/api/project-cost', methods=["POST"])
def save_project_cost():
    try:
        payload = request.get_json()
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT sp_save_project_cost(%s)", [json.dumps(payload)])
                result = cur.fetchone()
                conn.commit()
                message = result['sp_save_project_cost'] if result and 'sp_save_project_cost' in result else "No response"
        return jsonify({"status": "success", "message": message})
    except Exception:
        logging.exception("Error saving cost")
        return jsonify({"status": "error", "message": "Failed to save cost"}), 500

@app.route('/api/project-cost/dashboard')
def get_project_cost_dashboard():
    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM sp_get_project_cost_dashboard()")
                result = cur.fetchone()
        return jsonify({
            "totalRevenue": result["total_revenue"],
            "totalCost": result["total_cost"],
            "totalProfit": result["total_profit"],
            "avgProfitPct": result["avg_profit_pct"]
        }) if result else jsonify({"totalRevenue": "-", "totalCost": "-", "totalProfit": "-", "avgProfitPct": "-"})
    except Exception:
        logging.exception("Error loading cost dashboard")
        return jsonify({"error": "Failed to fetch dashboard"}), 500

@app.route('/api/project-cost/<int:cost_id>', methods=["DELETE"])
def delete_project_cost(cost_id):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                # Delete the expense record by cost_id
                cur.execute("DELETE FROM project_cost WHERE cost_id = %s", (cost_id,))
                conn.commit()
        return jsonify({"status": "success", "message": "Expense deleted successfully"})
    except Exception:
        logging.exception("Error deleting cost")
        return jsonify({"status": "error", "message": "Failed to delete expense"}), 500

# --------------------------------------
# App Entry Point
# --------------------------------------
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5050))
    app.run(debug=True, host='0.0.0.0', port=port)