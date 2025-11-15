from flask import Blueprint, render_template, request, redirect, url_for
from typing import cast, Dict, Any
from project.db import get_db

bp = Blueprint('faculty', __name__, url_prefix='/faculty')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        db = get_db()
        cursor = db.cursor(dictionary=True)
        query = "SELECT * FROM faculty WHERE email = %s AND password = %s"
        cursor.execute(query, (email, password))
        faculty_data = cursor.fetchone()
        cursor.close()
        
        if faculty_data:
            faculty = cast(Dict[str, Any], faculty_data)
            return redirect(url_for('faculty.dashboard', faculty_id=faculty['faculty_id']))
        else:
            return 'Invalid credentials', 401
    return render_template('faculty_login.html')

@bp.route('/dashboard/<int:faculty_id>')
def dashboard(faculty_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    # Fetch faculty details
    cursor.execute("SELECT * FROM faculty WHERE faculty_id = %s", (faculty_id,))
    faculty = cursor.fetchone()

    if not faculty:
        cursor.close()
        return "Faculty not found", 404
    
    # Fetch all complaints with all related info
    query = """
        SELECT 
            c.complaint_id, c.subject, c.description, c.date_filed, c.priority, c.last_updated,
            c.assigned_to_faculty_id,
            s.first_name as student_first_name, s.last_name as student_last_name, s.roll_no,
            cat.category,
            stat.status,
            f.first_name as faculty_first_name, f.last_name as faculty_last_name
        FROM complaint c
        LEFT JOIN student s ON c.student_roll_no = s.roll_no
        LEFT JOIN complaint_category cat ON c.category_id = cat.category_id
        LEFT JOIN complaint_status stat ON c.status_id = stat.status_id
        LEFT JOIN faculty f ON c.assigned_to_faculty_id = f.faculty_id
        ORDER BY c.last_updated DESC
    """
    cursor.execute(query)
    complaints = cursor.fetchall()

    # Fetch all possible statuses for the update dropdown
    cursor.execute("SELECT status_id, status FROM complaint_status ORDER BY status_id")
    all_statuses = cursor.fetchall()
    
    cursor.close()
    
    return render_template('faculty_dashboard.html', faculty=faculty, complaints=complaints, all_statuses=all_statuses)

@bp.route('/complaint/<int:complaint_id>/update/<int:faculty_id>', methods=['POST'])
def update_complaint(complaint_id, faculty_id):
    new_status_id = request.form.get('status_id')
    comment = request.form.get('comment', '')
    assign_to_me = 'assign_to_me' in request.form

    db = get_db()
    cursor = db.cursor(dictionary=True)

    try:
        # Fetch current state of the complaint for history tracking
        cursor.execute("SELECT status_id, assigned_to_faculty_id FROM complaint WHERE complaint_id = %s", (complaint_id,))
        current_complaint_data = cursor.fetchone()
        if not current_complaint_data:
            return "Complaint not found", 404
        
        current_complaint = cast(Dict[str, Any], current_complaint_data)
        previous_status_id = current_complaint['status_id']

        # Logic to assign the complaint
        if assign_to_me:
            cursor.execute("UPDATE complaint SET assigned_to_faculty_id = %s WHERE complaint_id = %s", (faculty_id, complaint_id))
            if not new_status_id: # If only assigning, set status to 'Under Review' (assuming ID 2)
                new_status_id = 2 

        # Logic to update the status
        if new_status_id:
            cursor.execute("UPDATE complaint SET status_id = %s WHERE complaint_id = %s", (new_status_id, complaint_id))
            
            # Add a record to the history table
            history_query = """
                INSERT INTO complaint_history (complaint_id, action_by_faculty_id, previous_status, new_status, comment)
                SELECT %s, %s, ps.status, ns.status, %s
                FROM complaint_status ps, complaint_status ns
                WHERE ps.status_id = %s AND ns.status_id = %s
            """
            cursor.execute(history_query, (complaint_id, faculty_id, comment, previous_status_id, new_status_id))

        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error updating complaint: {e}")
        # In a real app, flash an error message
    finally:
        cursor.close()

    return redirect(url_for('faculty.dashboard', faculty_id=faculty_id))
