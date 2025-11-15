from flask import Blueprint, request, redirect, url_for
from project.db import get_db
from typing import cast, Dict, Any

bp = Blueprint('complaint', __name__, url_prefix='/complaint')

@bp.route('/submit/<string:student_roll_no>', methods=['POST'])
def submit(student_roll_no):
    # Extract form data
    subject = request.form['subject']
    category_id = request.form['category_id']
    description = request.form['description']
    priority = request.form['priority']
    is_anonymous = 'is_anonymous' in request.form

    # If anonymous, the student_roll_no is not stored
    roll_no_to_store = None if is_anonymous else student_roll_no

    db = get_db()
    cursor = db.cursor()
    try:
        # Set initial status to 'Filed' (assuming status_id 1 is 'Filed')
        initial_status_id = 1
        
        # Insert the new complaint with the initial status
        query = """
            INSERT INTO complaint (subject, category_id, description, priority, is_anonymous, student_roll_no, status_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (subject, category_id, description, priority, is_anonymous, roll_no_to_store, initial_status_id))
        
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error submitting complaint: {e}")
        # Optionally, flash an error message to the user
    finally:
        cursor.close()
    
    return redirect(url_for('student.dashboard', roll_no=student_roll_no))

@bp.route('/feedback/<int:complaint_id>', methods=['POST'])
def add_feedback(complaint_id):
    # Extract form data
    rating = request.form['rating']
    comments = request.form.get('comments')

    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        # Insert feedback
        query = "INSERT INTO feedback (complaint_id, rating, comments) VALUES (%s, %s, %s)"
        cursor.execute(query, (complaint_id, rating, comments))
        
        # Get the student's roll_no for redirection
        cursor.execute("SELECT student_roll_no FROM complaint WHERE complaint_id = %s", (complaint_id,))
        complaint_data = cursor.fetchone()
        
        db.commit()

        if complaint_data:
            complaint = cast(Dict[str, Any], complaint_data)
            if complaint['student_roll_no']:
                return redirect(url_for('student.dashboard', roll_no=complaint['student_roll_no']))

        # Handle case for anonymous complaint or if student is not found
        return redirect(url_for('main.index'))

    except Exception as e:
        db.rollback()
        print(f"Error adding feedback: {e}")
        # Redirect to a generic error page or back to the dashboard
        return redirect(url_for('main.index'))
    finally:
        cursor.close()

# Note: The 'assign' and 'solve' routes have been removed.
# This logic will be re-implemented within the faculty dashboard or a dedicated admin panel.
