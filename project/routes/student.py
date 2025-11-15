from flask import Blueprint, render_template, request, redirect, url_for
from typing import cast, Dict, Any
from project.db import get_db

bp = Blueprint('student', __name__, url_prefix='/student')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    # Fetch departments for the registration form dropdown
    cursor.execute("SELECT department_id, name FROM department WHERE type = 'Academic' ORDER BY name")
    departments = cursor.fetchall()

    if request.method == 'POST':
        # Extract form data
        roll_no = request.form['roll_no']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        phone = request.form.get('phone')
        course = request.form.get('course')
        department_id = request.form.get('department_id')
        year_of_study = request.form.get('year_of_study')
        password = request.form['password']
        
        try:
            # Insert new student into the database
            query = """
                INSERT INTO student (roll_no, first_name, last_name, email, phone, course, department_id, year_of_study, password) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (roll_no, first_name, last_name, email, phone, course, department_id, year_of_study, password))
            db.commit()
            return redirect(url_for('student.login'))
        except Exception as e:
            # Handle potential errors like duplicate roll_no or email
            # In a real app, you'd want to flash a message to the user
            print(f"Error during registration: {e}")
            return render_template('student_register.html', departments=departments, error="Registration failed. Please check your input.")
        finally:
            cursor.close()

    cursor.close()
    return render_template('student_register.html', departments=departments)

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
            return redirect(url_for('student.dashboard', roll_no=student['roll_no']))
        else:
            return 'Invalid credentials', 401
    return render_template('student_login.html')

@bp.route('/dashboard/<string:roll_no>')
def dashboard(roll_no):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    # Fetch student details
    cursor.execute("SELECT * FROM student WHERE roll_no = %s", (roll_no,))
    student = cursor.fetchone()
    
    if not student:
        cursor.close()
        return "Student not found", 404

    # Fetch student's complaints with all related details
    query = """
        SELECT 
            c.complaint_id, c.subject, c.description, c.date_filed, c.priority, c.last_updated,
            cat.category,
            stat.status,
            f.rating, f.comments as feedback_comments
        FROM complaint c
        LEFT JOIN complaint_category cat ON c.category_id = cat.category_id
        LEFT JOIN complaint_status stat ON c.status_id = stat.status_id
        LEFT JOIN feedback f ON c.complaint_id = f.complaint_id
        WHERE c.student_roll_no = %s
        ORDER BY c.last_updated DESC
    """
    cursor.execute(query, (roll_no,))
    complaints = cursor.fetchall()

    # Fetch complaint categories for the new complaint form
    cursor.execute("SELECT category_id, category FROM complaint_category ORDER BY category")
    categories = cursor.fetchall()
    
    cursor.close()
    
    return render_template('student_dashboard.html', student=student, complaints=complaints, categories=categories)
