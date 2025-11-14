from flask import Blueprint, render_template, request, redirect, url_for
from typing import cast, Dict, Any
from project.db import get_db

bp = Blueprint('staff', __name__, url_prefix='/staff')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        db = get_db()
        cursor = db.cursor(dictionary=True)
        query = "SELECT * FROM staff WHERE email = %s AND password = %s"
        cursor.execute(query, (email, password))
        staff_data = cursor.fetchone()
        cursor.close()
        
        if staff_data:
            staff = cast(Dict[str, Any], staff_data)
            return redirect(url_for('staff.dashboard', staff_id=staff['id']))
        else:
            return 'Invalid credentials', 401
    return render_template('staff_login.html')

@bp.route('/dashboard/<int:staff_id>')
def dashboard(staff_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    # Fetch staff details
    cursor.execute("SELECT * FROM staff WHERE id = %s", (staff_id,))
    staff = cursor.fetchone()

    if not staff:
        return "Staff not found", 404
    
    # Fetch all complaints with student info, including roll number
    query = """
        SELECT c.*, s.name as student_name, s.roll_no 
        FROM complaint c 
        JOIN student s ON c.student_id = s.id 
        ORDER BY c.id DESC
    """
    cursor.execute(query)
    complaints = cursor.fetchall()
    
    cursor.close()
    
    return render_template('staff_dashboard.html', staff=staff, complaints=complaints)
