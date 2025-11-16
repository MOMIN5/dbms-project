from flask import Blueprint, render_template, request, redirect, url_for
from typing import cast, Dict, Any
from project.db import get_db

bp = Blueprint('student', __name__, url_prefix='/student')

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
            f.rating, f.comments as feedback_comments,
            c.is_anonymous
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

@bp.route('/complaint/<int:complaint_id>/feedback/<string:roll_no>', methods=['POST'])
def add_feedback(complaint_id, roll_no):
    rating = request.form.get('rating')
    comments = request.form.get('comments')

    if not roll_no:
        return "Student roll number is required.", 400

    db = get_db()
    cursor = db.cursor()
    try:
        query = """
            INSERT INTO feedback (complaint_id, student_roll_no, rating, comments)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE rating = VALUES(rating), comments = VALUES(comments)
        """
        cursor.execute(query, (complaint_id, roll_no, rating, comments))
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error adding feedback: {e}")
        # In a real app, you would flash an error message
    finally:
        cursor.close()

    return redirect(url_for('student.dashboard', roll_no=roll_no))
