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
    faculty_data = cursor.fetchone()

    if not faculty_data:
        cursor.close()
        return "Faculty not found", 404

    faculty = cast(Dict[str, Any], faculty_data)
    is_admin = faculty['position'] == 'admin'

    # Base query parts
    base_query = """
        FROM complaint c
        LEFT JOIN student s ON c.student_roll_no = s.roll_no
        LEFT JOIN complaint_category cat ON c.category_id = cat.category_id
        LEFT JOIN complaint_status stat ON c.status_id = stat.status_id
        LEFT JOIN faculty f ON c.assigned_to_faculty_id = f.faculty_id
    """
    feedback_join = " LEFT JOIN feedback fb ON c.complaint_id = fb.complaint_id"

    # Common fields for all queries
    common_fields = """
        c.complaint_id, c.subject, c.description, c.date_filed, c.priority, c.last_updated,
        c.deadline, c.assigned_to_faculty_id, c.is_anonymous,
        s.first_name as student_first_name, s.last_name as student_last_name, s.roll_no,
        cat.category,
        stat.status,
        f.first_name as faculty_first_name, f.last_name as faculty_last_name
    """
    feedback_fields = ", fb.rating, fb.comments as feedback_comments"

    # Function to execute query
    def fetch_complaints(status_conditions, include_feedback=False):
        fields = common_fields + (feedback_fields if include_feedback else "")
        query = f"SELECT {fields} {base_query}"
        if include_feedback:
            query += feedback_join
        
        conditions = [status_conditions]
        params = []

        if not is_admin:
            conditions.append("c.assigned_to_faculty_id = %s")
            params.append(faculty_id)
        
        query += " WHERE " + " AND ".join(conditions)
        query += " ORDER BY c.last_updated DESC"
        
        cursor.execute(query, tuple(params))
        return cursor.fetchall()

    # Fetch complaints based on status
    active_complaints = fetch_complaints("stat.status NOT IN ('Closed', 'Rejected', 'Resolved')")
    resolved_complaints = fetch_complaints("stat.status = 'Resolved'", include_feedback=True)
    closed_complaints = fetch_complaints("stat.status IN ('Closed', 'Rejected')", include_feedback=True)

    # Fetch all possible statuses for the update dropdown
    cursor.execute("SELECT status_id, status FROM complaint_status ORDER BY status_id")
    all_statuses = cursor.fetchall()

    # Fetch all faculty for the assignment dropdown
    cursor.execute("SELECT faculty_id, first_name, last_name FROM faculty ORDER BY first_name, last_name")
    all_faculty = cursor.fetchall()
    
    cursor.close()
    
    return render_template('faculty_dashboard.html', faculty=faculty, active_complaints=active_complaints, closed_complaints=closed_complaints, resolved_complaints=resolved_complaints, all_statuses=all_statuses, all_faculty=all_faculty)

@bp.route('/complaint/<int:complaint_id>/update/<int:faculty_id>', methods=['POST'])
def update_complaint(complaint_id, faculty_id):
    new_status_id = request.form.get('status_id')
    comment = request.form.get('comment', '')
    priority = request.form.get('priority')
    assign_to_faculty_id = request.form.get('assign_to_faculty_id')
    deadline = request.form.get('deadline')

    db = get_db()
    cursor = db.cursor(dictionary=True)

    try:
        # Check if the acting faculty is an admin
        cursor.execute("SELECT position FROM faculty WHERE faculty_id = %s", (faculty_id,))
        faculty_data_result = cursor.fetchone()
        faculty_data = cast(Dict[str, Any], faculty_data_result)
        is_admin = faculty_data and faculty_data['position'] == 'admin'

        # Fetch current state of the complaint for history tracking
        cursor.execute("SELECT status_id, assigned_to_faculty_id FROM complaint WHERE complaint_id = %s", (complaint_id,))
        current_complaint_data = cursor.fetchone()
        if not current_complaint_data:
            return "Complaint not found", 404
        
        current_complaint = cast(Dict[str, Any], current_complaint_data)
        previous_status_id = current_complaint['status_id']

        # Logic to assign the complaint (only for admins)
        if is_admin and assign_to_faculty_id:
            # Update assigned faculty
            cursor.execute("UPDATE complaint SET assigned_to_faculty_id = %s WHERE complaint_id = %s", (assign_to_faculty_id, complaint_id))
            
            # Set deadline if provided
            if deadline:
                cursor.execute("UPDATE complaint SET deadline = %s WHERE complaint_id = %s", (deadline, complaint_id))

            # If only assigning (and not changing status), set status to 'Under Review'
            if not new_status_id:
                new_status_id = 2 # 'Under Review'


        # Logic to update the status
        if new_status_id and new_status_id != previous_status_id:
            cursor.execute("UPDATE complaint SET status_id = %s WHERE complaint_id = %s", (new_status_id, complaint_id))
            
            # Add a record to the history table for the status change
            history_query = """
                INSERT INTO complaint_history (complaint_id, action_by_faculty_id, previous_status_id, new_status_id, comment)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(history_query, (complaint_id, faculty_id, previous_status_id, new_status_id, comment))

        # Update priority if it's provided
        if priority:
            cursor.execute("UPDATE complaint SET priority = %s WHERE complaint_id = %s", (priority, complaint_id))

        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error updating complaint: {e}")
        # In a real app, flash an error message
    finally:
        cursor.close()

    return redirect(url_for('faculty.dashboard', faculty_id=faculty_id))


@bp.route('/complaint/<int:complaint_id>/reopen/<int:faculty_id>', methods=['POST'])
def reopen_complaint(complaint_id, faculty_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    try:
        # Fetch current state of the complaint for history tracking
        cursor.execute("SELECT status_id FROM complaint WHERE complaint_id = %s", (complaint_id,))
        current_complaint_data = cursor.fetchone()
        if not current_complaint_data:
            return "Complaint not found", 404
        
        current_complaint = cast(Dict[str, Any], current_complaint_data)
        previous_status_id = current_complaint['status_id']
        new_status_id = 2  # 'Under Review'

        # Update the complaint status
        cursor.execute("UPDATE complaint SET status_id = %s WHERE complaint_id = %s", (new_status_id, complaint_id))

        # Add a record to the history table for the status change
        history_query = """
            INSERT INTO complaint_history (complaint_id, action_by_faculty_id, previous_status_id, new_status_id, comment)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(history_query, (complaint_id, faculty_id, previous_status_id, new_status_id, "Complaint reopened by faculty."))

        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error reopening complaint: {e}")
    finally:
        cursor.close()

    return redirect(url_for('faculty.dashboard', faculty_id=faculty_id))
