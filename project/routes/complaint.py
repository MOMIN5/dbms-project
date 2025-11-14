from flask import Blueprint, request, redirect, url_for
from project.db import get_db
from typing import cast, Dict, Any

bp = Blueprint('complaint', __name__, url_prefix='/complaint')

@bp.route('/submit/<int:student_id>', methods=['POST'])
def submit(student_id):
    title = request.form['title']
    description = request.form['description']
    
    db = get_db()
    cursor = db.cursor()
    query = "INSERT INTO complaint (title, description, student_id) VALUES (%s, %s, %s)"
    cursor.execute(query, (title, description, student_id))
    db.commit()
    cursor.close()
    
    return redirect(url_for('student.dashboard', student_id=student_id))

@bp.route('/assign/<int:complaint_id>', methods=['POST'])
def assign(complaint_id):
    staff_id = request.form['staff_id']
    
    db = get_db()
    cursor = db.cursor()
    query = "UPDATE complaint SET staff_id = %s, status = 'Assigned' WHERE id = %s"
    cursor.execute(query, (staff_id, complaint_id))
    db.commit()
    cursor.close()
    
    return redirect(url_for('staff.dashboard', staff_id=staff_id))

@bp.route('/solve/<int:complaint_id>', methods=['POST'])
def solve(complaint_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    # Update status
    query = "UPDATE complaint SET status = 'Solved' WHERE id = %s"
    cursor.execute(query, (complaint_id,))
    
    # Get staff_id for redirection
    cursor.execute("SELECT staff_id FROM complaint WHERE id = %s", (complaint_id,))
    complaint_data = cursor.fetchone()
    
    db.commit()
    
    if not complaint_data:
        cursor.close()
        return "Complaint not found", 404

    complaint = cast(Dict[str, Any], complaint_data)
    cursor.close()

    if not complaint['staff_id']:
        return redirect(url_for('main.index')) 
    
    return redirect(url_for('staff.dashboard', staff_id=complaint['staff_id']))

@bp.route('/feedback/<int:complaint_id>', methods=['POST'])
def add_feedback(complaint_id):
    feedback_text = request.form['feedback_text']
    
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    # Get student_id for redirection
    cursor.execute("SELECT student_id FROM complaint WHERE id = %s", (complaint_id,))
    complaint_data = cursor.fetchone()

    if not complaint_data:
        cursor.close()
        return "Complaint not found", 404
    
    complaint = cast(Dict[str, Any], complaint_data)

    # Insert feedback
    query = "INSERT INTO feedback (feedback_text, complaint_id) VALUES (%s, %s)"
    cursor.execute(query, (feedback_text, complaint_id))
    db.commit()
    cursor.close()
    
    return redirect(url_for('student.dashboard', student_id=complaint['student_id']))
