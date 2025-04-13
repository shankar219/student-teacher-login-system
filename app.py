from flask import Flask, request, jsonify, render_template, session, redirect, url_for, send_file
from werkzeug.utils import secure_filename
import mysql.connector
from flask_cors import CORS
import os
import bcrypt
import logging

app = Flask(__name__)
CORS(app)
app.secret_key = 'your_secret_key'  # Replace with a secure random key in production

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Configure upload folder
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            port=3306,
            user="root",
            password="root1234",
            database="project_db"
        )
        return conn
    except mysql.connector.Error as err:
        logging.error(f"Database connection error: {err}")
        return None

def init_db():
    conn = get_db_connection()
    if conn is None:
        logging.error("Failed to initialize database")
        exit(1)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admin (
            id INT PRIMARY KEY AUTO_INCREMENT,
            username VARCHAR(50) UNIQUE NOT NULL,
            email VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT PRIMARY KEY AUTO_INCREMENT,
            username VARCHAR(50) UNIQUE NOT NULL,
            email VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pdfs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            course_code VARCHAR(20) NOT NULL,
            unit_number INT NOT NULL,
            filename VARCHAR(255) NOT NULL,
            filepath VARCHAR(255) NOT NULL,
            uploaded_by VARCHAR(50) NOT NULL,
            upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()
    logging.debug("Database initialized")

init_db()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/about.html")
def about():
    return render_template("about.html")

@app.route("/contact.html")
def contact():
    return render_template("contact.html")

@app.route("/login.html")
def login_page():
    return render_template("login.html")

@app.route("/register.html")
def register_page():
    return render_template("register.html")

@app.route('/admin_register.html')
def admin_register_page_view():
    return render_template('admin_register.html')

@app.route("/admin_login.html")
def admin_login_page():
    return render_template("admin_login.html")

@app.route("/dashboard")
def dashboard():
    logging.debug(f"Accessing dashboard, session: {dict(session)}")
    if 'username' in session and session.get('is_admin') == 0:
        return render_template("user_dashboard.html", username=session['username'])
    return redirect(url_for('login_page'))

@app.route("/admin_dashboard")
def admin_dashboard():
    logging.debug(f"Accessing admin_dashboard, session: {dict(session)}")
    if 'username' in session and session.get('is_admin') == 1:
        return render_template("admin_dashboard.html", username=session['username'])
    return redirect(url_for('login_page'))

@app.route('/register', methods=['POST'])
def register():
    if request.content_type != 'application/json':
        return jsonify({'success': False, 'message': 'Content-Type must be application/json'}), 415
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    if not username or not email or not password:
        return jsonify({"success": False, "message": "All fields are required"}), 400
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    conn = get_db_connection()
    if conn is None:
        return jsonify({'success': False, 'message': 'Database connection failed'}), 500
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
            (username, email, hashed_password)
        )
        conn.commit()
        logging.debug(f"User {username} registered")
        return jsonify({'success': True, 'message': 'User registered successfully'})
    except mysql.connector.Error as err:
        logging.error(f"Register error: {err}")
        return jsonify({'success': False, 'message': str(err)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/admin_register', methods=['POST'])
def admin_register():
    if request.content_type != 'application/json':
        return jsonify({'success': False, 'message': 'Content-Type must be application/json'}), 415
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    if not username or not email or not password:
        return jsonify({"success": False, "message": "All fields are required"}), 400
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    conn = get_db_connection()
    if conn is None:
        return jsonify({'success': False, 'message': 'Database connection failed'}), 500
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO admin (username, email, password) VALUES (%s, %s, %s)",
            (username, email, hashed_password)
        )
        conn.commit()
        logging.debug(f"Admin {username} registered")
        return jsonify({"success": True, "message": "Admin registered successfully!"}), 201
    except mysql.connector.Error as err:
        logging.error(f"Admin register error: {err}")
        return jsonify({"success": False, "message": str(err)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/login', methods=['POST'])
def login():
    if request.content_type != 'application/json':
        return jsonify({'success': False, 'message': 'Content-Type must be application/json'}), 415
    data = request.json
    username = data.get('username')
    password = data.get('password')
    logging.debug(f"User login attempt for {username}")
    conn = get_db_connection()
    if conn is None:
        return jsonify({'success': False, 'message': 'Database connection failed'}), 500
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
    user = cursor.fetchone()
    logging.debug(f"User query result: {user}")
    cursor.close()
    conn.close()
    if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
        session['loggedin'] = True
        session['username'] = user['username']
        session['is_admin'] = 0
        return jsonify({'success': True, 'role': 'user', 'redirect': '/dashboard'})
    return jsonify({'success': False, 'message': 'Invalid credentials'})

@app.route('/admin_login', methods=['POST'])
def admin_login():
    if request.content_type != 'application/json':
        return jsonify({'success': False, 'message': 'Content-Type must be application/json'}), 415
    data = request.json
    username = data.get('username')
    password = data.get('password')
    logging.debug(f"Admin login attempt for {username}")
    conn = get_db_connection()
    if conn is None:
        return jsonify({'success': False, 'message': 'Database connection failed'}), 500
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM admin WHERE username=%s", (username,))
    admin = cursor.fetchone()
    logging.debug(f"Admin query result: {admin}")
    cursor.close()
    conn.close()
    if admin and bcrypt.checkpw(password.encode('utf-8'), admin['password'].encode('utf-8')):
        session['loggedin'] = True
        session['username'] = admin['username']
        session['is_admin'] = 1
        logging.debug(f"Session after admin login: {dict(session)}")
        return jsonify({'success': True, 'role': 'admin', 'redirect': '/admin_dashboard'})
    logging.debug("Admin login failed")
    return jsonify({'success': False, 'message': 'Invalid credentials'})

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login_page'))

@app.route("/upload_pdf", methods=["POST"])
def upload_pdf():
    if 'username' not in session or session.get('is_admin') != 1:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    file = request.files.get('file')
    course_code = request.form.get('course_code')
    unit_number = request.form.get('unit_number')
    if not file or not course_code or not unit_number:
        return jsonify({"success": False, "message": "Missing required fields"}), 400
    if not allowed_file(file.filename):
        return jsonify({"success": False, "message": "Invalid file type"}), 400
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    conn = get_db_connection()
    if conn is None:
        return jsonify({'success': False, 'message': 'Database connection failed'}), 500
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO pdfs (course_code, unit_number, filename, filepath, uploaded_by) VALUES (%s, %s, %s, %s, %s)",
            (course_code, unit_number, filename, filepath, session['username'])
        )
        conn.commit()
        return jsonify({"success": True, "message": "PDF uploaded successfully"})
    except mysql.connector.Error as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    app.run(debug=True)