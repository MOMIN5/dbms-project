from flask import Blueprint, render_template, request, redirect, url_for
from typing import cast, Dict, Any
from project.db import get_db

bp = Blueprint('student', __name__, url_prefix='/student')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        roll_no = request.form['roll_no']
        password = request.form['password']
        
        db = get_db()
        cursor = db.cursor()
        query = "INSERT INTO student (name, roll_no, password) VALUES (%s, %s, %s)"
        cursor.execute(query, (name, roll_no, password))
        db.commit()
        cursor.close()
        
        return redirect(url_for('student.login'))
    return render_template('student_register.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        roll_no = request.form['roll_no']
        password = request.form['password']
        
        db = get_db()
        cursor = db.cursor(dictionary=True)
        query = "SELECT * FROM student WHERE roll_no = %s AND password = %s"
        cursor.execute(query, (roll_no, password))
        student_data = cursor.fetchone()
        cursor.close()
        
        if student_data:
            student = cast(Dict[str, Any], student_data)
            return redirect(url_for('student.dashboard', student_id=student['id']))
        else:
            return 'Invalid credentials', 401
    return render_template('student_login.html')

@bp.route('/dashboard/<int:student_id>')
def dashboard(student_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    # Fetch student details
    cursor.execute("SELECT * FROM student WHERE id = %s", (student_id,))
    student = cursor.fetchone()
    
    if not student:
        return "Student not found", 404

    # Fetch complaints with feedback
    query = """
        SELECT c.*, f.feedback_text 
        FROM complaint c 
        LEFT JOIN feedback f ON c.id = f.complaint_id 
        WHERE c.student_id = %s
        ORDER BY c.id DESC
    """
    cursor.execute(query, (student_id,))
    complaints = cursor.fetchall()
    
    cursor.close()
    
    return render_template('student_dashboard.html', student=student, complaints=complaints)
