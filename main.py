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

@app.route('/tasks')
def tasks():
    return render_template("tasks.html")

@app.route('/posts')
def posts():
    return render_template("posts.html")

@app.route('/issues')
def issues():
    return render_template("issues.html")

@app.route('/inquiry')
def inquiry():
    return render_template("inquiry.html")

@app.route('/time')
def time_log_page():
    return render_template("time.html")

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
    search = request.args.get("search", "")

    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM sp_get_project_list(%s, %s, %s);", (page, limit, search))
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
# Monthly Task APIs
# --------------------------------------
@app.route('/api/monthly-tasks')
def get_monthly_tasks():
    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM sp_get_monthly_task_category_list();")
                return jsonify(cur.fetchall())
    except Exception:
        logging.exception("Error fetching task categories")
        return jsonify({"success": False, "error": "Failed to fetch task categories"}), 500

@app.route('/api/monthly-task/by-category/<string:category_code>')
def get_monthly_tasks_by_category(category_code):
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 10))
    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM sp_get_monthly_task_by_category(%s, %s, %s);", 
                            (category_code, page, limit))
                return jsonify(cur.fetchall())
    except Exception:
        logging.exception("Error fetching tasks by category")
        return jsonify({"success": False, "error": "Failed to fetch tasks"}), 500

@app.route('/api/monthly-task/<int:task_id>')
def get_monthly_task_by_id(task_id):
    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Since there's no dedicated function for getting a single task,
                # we'll use a direct query
                cur.execute("""
                    SELECT task_id, category_code, task_name, scheduled_date, 
                           is_done, completed_date, notes
                    FROM monthly_task_log
                    WHERE task_id = %s
                """, (task_id,))
                return jsonify(cur.fetchone())
    except Exception:
        logging.exception("Error fetching task by ID")
        return jsonify({"success": False, "error": "Failed to fetch task"}), 500

@app.route('/api/monthly-task', methods=["POST"])
def save_monthly_task():
    try:
        payload = request.get_json()
        with get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:  # Use RealDictCursor
                cur.execute("SELECT sp_save_monthly_task(%s)", [json.dumps(payload)])
                result = cur.fetchone()
                conn.commit()
                message = result['sp_save_monthly_task'] if result and 'sp_save_monthly_task' in result else "No response"
        return jsonify({"status": "success", "message": message})
    except Exception as e:
        logging.exception(f"Error saving task: {str(e)}")
        return jsonify({"status": "error", "message": "Failed to save task"}), 500

@app.route('/api/monthly-task/<int:task_id>', methods=["DELETE"])
def delete_monthly_task(task_id):
    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:  # Use RealDictCursor
                cur.execute("SELECT sp_delete_monthly_task(%s)", (task_id,))
                result = cur.fetchone()
                conn.commit()
                message = result['sp_delete_monthly_task'] if result and 'sp_delete_monthly_task' in result else "No response"
        return jsonify({"status": "success", "message": message})
    except Exception:
        logging.exception("Error deleting task")
        return jsonify({"status": "error", "message": "Failed to delete task"}), 500

@app.route('/api/monthly-task/dashboard')
def get_monthly_task_dashboard():
    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM sp_get_monthly_task_dashboard()")
                result = cur.fetchone()
        if result:
            # Clean up the percentage values by removing '%' if present
            overall_completion = result.get("overall_completion", "0")
            if isinstance(overall_completion, str) and overall_completion.endswith('%'):
                overall_completion = overall_completion[:-1]  # Remove the '%' symbol
            
            return jsonify({
                "overall_completion": overall_completion,
                "best_performing_category": result.get("best_performing_category", "-"),
                "worst_performing_category": result.get("worst_performing_category", "-"),
                "upcoming_tasks": result.get("upcoming_tasks", "")
            })
        return jsonify({
            "overall_completion": "0",
            "best_performing_category": "-",
            "worst_performing_category": "-",
            "upcoming_tasks": ""
        })
    except Exception as e:
        logging.exception(f"Error loading task dashboard: {str(e)}")
        return jsonify({
            "error": "Failed to fetch dashboard",
            "overall_completion": "0",
            "best_performing_category": "-", 
            "worst_performing_category": "-",
            "upcoming_tasks": ""
        }), 500

@app.route('/api/task-master-list')
def get_task_master_list():
    search = request.args.get('search', '').strip()
    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                if search:
                    cur.execute("""
                        SELECT * FROM sp_get_task_master_list()
                        WHERE task_name ILIKE %s OR category_name ILIKE %s OR frequency_name ILIKE %s
                    """, (f'%{search}%', f'%{search}%', f'%{search}%'))
                else:
                    cur.execute("SELECT * FROM sp_get_task_master_list();")
                return jsonify(cur.fetchall())
    except Exception:
        logging.exception("Error fetching task master list")
        return jsonify({"success": False, "error": "Failed to fetch task master list"}), 500

@app.route('/api/task-master')
def get_task_master():
    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM sp_get_task_master_list();")
                return jsonify(cur.fetchall())
    except Exception:
        logging.exception("Error fetching task master list")
        return jsonify({"success": False, "error": "Failed to fetch task master list"}), 500
    
@app.route('/api/task-master', methods=["POST"])
def save_task_master():
    try:
        payload = request.get_json()
        with get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT sp_save_task_master(%s)", [json.dumps(payload)])
                result = cur.fetchone()
                conn.commit()
                message = result['sp_save_task_master'] if result and 'sp_save_task_master' in result else "No response"
        return jsonify({"status": "success", "message": message})
    except Exception:
        logging.exception("Error saving task master")
        return jsonify({"status": "error", "message": "Failed to save task master"}), 500
    
# --------------------------------------
# Content & Ideas APIs
# --------------------------------------
@app.route('/api/content-posts')
def get_content_posts():
    month = request.args.get("month")
    post_type = request.args.get("post_type")
    platform = request.args.get("platform")
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 10))
    
    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT * FROM sp_get_content_post_list(%s, %s, %s, %s, %s);", 
                    (month, post_type, platform, page, limit)
                )
                return jsonify(cur.fetchall())
    except Exception:
        logging.exception("Error fetching content posts")
        return jsonify({"success": False, "error": "Failed to fetch content posts"}), 500

@app.route('/api/content-post/<int:post_id>')
def get_content_post_by_id(post_id):
    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM sp_get_content_post_by_id(%s);", (post_id,))
                return jsonify(cur.fetchone())
    except Exception:
        logging.exception("Error fetching content post by ID")
        return jsonify({"success": False, "error": "Failed to fetch content post"}), 500

@app.route('/api/content-post', methods=["POST"])
def save_content_post():
    try:
        payload = request.get_json()
        
        # Fix for empty post_id - convert empty string to 0 or remove it
        if 'post_id' in payload and (payload['post_id'] == '' or payload['post_id'] is None):
            payload['post_id'] = 0  # Set to 0 which the stored procedure treats as a new record
        
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT sp_save_content_post(%s)", [json.dumps(payload)])
                result = cur.fetchone()
                conn.commit()
                message = result['sp_save_content_post'] if result and 'sp_save_content_post' in result else "No response"
        return jsonify({"status": "success", "message": message})
    except Exception:
        logging.exception("Error saving content post")
        return jsonify({"status": "error", "message": "Failed to save content post"}), 500

@app.route('/api/content-post/<int:post_id>', methods=["DELETE"])
def delete_content_post(post_id):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT sp_delete_content_post(%s)", (post_id,))
                result = cur.fetchone()
                conn.commit()
                message = result['sp_delete_content_post'] if result and 'sp_delete_content_post' in result else "No response"
        return jsonify({"status": "success", "message": "Content post deleted successfully"})
    except Exception:
        logging.exception("Error deleting content post")
        return jsonify({"status": "error", "message": "Failed to delete content post"}), 500

@app.route('/api/content-post/dashboard')
def get_content_post_dashboard():
    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM sp_get_content_post_dashboard()")
                result = cur.fetchone()
        if result:
            return jsonify({
                "bestPerformingPost": result["best_post"],
                "topTopic": result["top_topic"],
                "mostUsedPlatform": result["most_used_platform"],
                "avgEngagementPerPost": result["avg_engagement_per_post"]
            })
        return jsonify({
            "bestPerformingPost": "-",
            "topTopic": "-",
            "mostUsedPlatform": "-",
            "avgEngagementPerPost": "0.00"
        })
    except Exception:
        logging.exception("Error loading content post dashboard")
        return jsonify({"error": "Failed to fetch dashboard"}), 500

# --------------------------------------
# Project Issues APIs
# --------------------------------------
@app.route('/api/project-issues')
def get_project_issues():
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 10))
    search = request.args.get("search", "")
    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM sp_get_project_issues_list(%s, %s, %s);", (page, limit, search))
                return jsonify(cur.fetchall())
    except Exception:
        logging.exception("Error fetching project issues")
        return jsonify({"success": False, "error": "Failed to fetch project issues"}), 500

@app.route('/api/project-issue/<int:project_id>')
def get_project_issue_by_id(project_id):
    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM sp_get_project_issues_by_id(%s);", (project_id,))
                return jsonify(cur.fetchall())
    except Exception:
        logging.exception("Error fetching issues by ID")
        return jsonify({"success": False, "error": "Failed to fetch issues"}), 500

@app.route('/api/project-issue', methods=["POST"])
def save_project_issue():
    try:
        payload = request.get_json()
        with get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:  # Add RealDictCursor
                cur.execute("SELECT sp_save_project_issue(%s)", [json.dumps(payload)])
                result = cur.fetchone()
                conn.commit()
                message = result['sp_save_project_issue'] if result and 'sp_save_project_issue' in result else "No response"
        return jsonify({"status": "success", "message": message})
    except Exception as e:
        logging.exception(f"Error saving issue: {str(e)}")
        return jsonify({"status": "error", "message": "Failed to save issue"}), 500

@app.route('/api/project-issue/<int:issue_id>', methods=["DELETE"])
def delete_project_issue(issue_id):
    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:  # Add RealDictCursor
                cur.execute("SELECT sp_delete_project_issue(%s)", (issue_id,))
                result = cur.fetchone()
                conn.commit()
                message = result['sp_delete_project_issue'] if result and 'sp_delete_project_issue' in result else "No response"
        return jsonify({"status": "success", "message": "Issue deleted successfully"})
    except Exception:
        logging.exception("Error deleting issue")
        return jsonify({"status": "error", "message": "Failed to delete issue"}), 500

@app.route('/api/project-issue/dashboard')
def get_project_issue_dashboard():
    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM sp_get_project_issues_dashboard()")
                result = cur.fetchall()
        return jsonify(result if result else [])
    except Exception:
        logging.exception("Error loading issue dashboard")
        return jsonify({"error": "Failed to fetch dashboard"}), 500

# --------------------------------------
# Inquiry Tracker APIs
# --------------------------------------
@app.route('/api/inquiry-tracker')
def get_inquiry_tracker():
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 10))
    search = request.args.get("search", "")
    year = request.args.get("year", type=int)
    month = request.args.get("month", type=int)

    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT * FROM sp_get_sales_inquiry_list(%s, %s, %s, %s, %s);",
                    (page, limit, search, year, month)
                )
                return jsonify(cur.fetchall())
    except Exception:
        logging.exception("Error fetching inquiry tracker list")
        return jsonify({"success": False, "error": "Failed to fetch inquiry tracker list"}), 500

@app.route('/api/inquiry-tracker/dashboard')
def get_inquiry_dashboard():
    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM sp_get_sales_inquiry_dashboard();")
                result = cur.fetchone()
        return jsonify(result if result else {
            "inquiries_this_month": 0,
            "converted_projects": 0,
            "conversion_rate": 0,
            "avg_time_to_convert": 0
        })
    except Exception:
        logging.exception("Error fetching inquiry dashboard")
        return jsonify({"error": "Failed to fetch inquiry dashboard"}), 500

# --------------------------------------
# Time Log APIs
# --------------------------------------
@app.route('/api/time-log/dashboard')
def get_time_log_dashboard():
    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM sp_get_time_log_dashboard();")
                result = cur.fetchone()

        return jsonify(result if result else {
            "total_hours_spent": 0,
            "total_task_entries": 0,
            "top_project": "-",
            "top_project_hours": 0,
            "avg_task_json": []
        })

    except Exception:
        logging.exception("Error fetching time log dashboard")
        return jsonify({
            "error": "Failed to fetch dashboard",
            "total_hours_spent": 0,
            "total_task_entries": 0,
            "top_project": "-",
            "top_project_hours": 0,
            "avg_task_json": []
        }), 500

@app.route('/api/time-log-summary')
def get_time_log_summary():
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 10))
    search = request.args.get("search", "")
    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM sp_get_time_log_summary(%s, %s, %s);", (page, limit, search))
                return jsonify(cur.fetchall())
    except Exception:
        logging.exception("Error fetching time log summary")
        return jsonify({"success": False, "error": "Failed to fetch summary"}), 500

@app.route('/api/time-log')
def get_time_logs_by_project():
    project_id = request.args.get("project_id", type=int)
    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM sp_get_time_logs_by_project(%s);", (project_id,))
                return jsonify(cur.fetchall())
    except Exception:
        logging.exception("Error fetching time log list")
        return jsonify({"success": False, "error": "Failed to fetch time logs"}), 500

@app.route('/api/time-log', methods=["POST"])
def save_time_log():
    try:
        payload = request.get_json()
        with get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:  # Add RealDictCursor
                cur.execute("SELECT sp_save_time_log(%s)", [json.dumps(payload)])
                result = cur.fetchone()
                conn.commit()
                message = result['sp_save_time_log'] if result and 'sp_save_time_log' in result else "No response"
        return jsonify({"status": "success", "message": message})
    except Exception as e:
        logging.exception(f"Error saving time log: {str(e)}")
        return jsonify({"status": "error", "message": "Failed to save time log"}), 500

@app.route('/api/time-log/<int:time_log_id>', methods=["DELETE"])
def delete_time_log(time_log_id):
    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:  # Add RealDictCursor
                cur.execute("SELECT sp_delete_time_log(%s)", (time_log_id,))
                result = cur.fetchone()
                conn.commit()
                message = result['sp_delete_time_log'] if result and 'sp_delete_time_log' in result else "No response"
        return jsonify({"status": "success", "message": "Time log deleted successfully"})
    except Exception as e:
        logging.exception(f"Error deleting time log: {str(e)}")
        return jsonify({"status": "error", "message": "Failed to delete time log"}), 500

# --------------------------------------
# App Entry Point
# --------------------------------------
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5050))
    app.run(debug=True, host='0.0.0.0', port=port)