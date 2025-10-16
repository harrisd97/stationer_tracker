# Stationer Success Tracker

![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.1-black.svg)
![Database](https://img.shields.io/badge/Database-PostgreSQL-blue.svg)
![Frontend](https://img.shields.io/badge/Frontend-Vanilla%20JS-yellow.svg)

A full-stack business management web application built for creative entrepreneurs. This tool provides a centralized dashboard to manage projects, track client feedback, and analyze financial performance, enabling smarter, data-driven business decisions.

> **Live Demo:** [https://stationer-tracker.onrender.com](https://stationer-tracker.onrender.com)

---

### Key Features

* **Project Management:** A central hub to track projects from inquiry to completion, including key dates, amounts, and statuses.
* **Client Experience Tracking:** Log client feedback, scores, and testimonials to measure satisfaction and gather marketing assets.
* **Financial Dashboards:** Monitor revenue, costs, and profitability with dynamically updated summary cards and detailed expense breakdowns.
* **Dynamic & Responsive UI:** A clean, fast, and mobile-friendly interface built with vanilla JavaScript and Bootstrap for a seamless user experience on any device.

---

## Technical Architecture

This application is built with a clean, decoupled architecture, featuring a robust Python/Flask backend that serves a RESTful API and a dynamic, framework-free JavaScript front-end.

#### Backend (Python & Flask)

The backend is engineered for reliability and maintainability.

* **RESTful API:** A comprehensive API provides endpoints for all CRUD (Create, Read, Update, Delete) operations for projects, client experiences, and expenses.
* [cite_start]**Database Integration:** Connects to a PostgreSQL database using the `psycopg2` library[cite: 1]. Business logic for data manipulation is encapsulated within **PostgreSQL stored procedures** (e.g., `sp_save_project`, `sp_get_project_cost_list`), centralizing data logic for enhanced security and performance.
* **Robust Logging:** Features built-in logging for every API request and response, writing to `stationer_tracker.log` for easy debugging and monitoring in a production environment.
* [cite_start]**Separation of Concerns:** Database connection details are cleanly separated in `db_config.py`, making the application easy to configure and deploy[cite: 1].

#### Frontend (Vanilla JavaScript & Bootstrap 5)

The user interface is designed to be intuitive and interactive without the overhead of a large front-end framework.

* **Dynamic UI:** The front-end is built with vanilla JavaScript, making asynchronous API calls using the `fetch()` API to load and submit data without page reloads.
* **Interactive Features:**
    * **Asynchronous Data Tables:** Project and expense lists are loaded on demand with client-side pagination.
    * **Live Search:** Project search fields offer real-time, "search-as-you-type" functionality by querying the backend API.
    * **User Feedback:** Toast notifications provide non-intrusive feedback for actions like "Save Successful" or "Error".

---

### Local Setup

To run this project locally, you will need Python 3.9+ and a running PostgreSQL instance.

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/your-username/stationer_tracker.git](https://github.com/your-username/stationer_tracker.git)
    cd stationer_tracker
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate

    # For Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Install dependencies from `requirements.txt`**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure the Database:**
    * Set up a PostgreSQL database.
    * [cite_start]Update the connection DSN string in `db_config.py` to point to your database instance[cite: 1].
    * Run the necessary SQL scripts to create tables and stored procedures.

5.  **Run the application using `main.py`**:
    ```bash
    python main.py
    ```
    The application will be available at `http://127.0.0.1:5050`.
