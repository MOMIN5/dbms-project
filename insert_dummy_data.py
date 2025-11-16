import mysql.connector
from werkzeug.security import generate_password_hash
from faker import Faker
import random

# --- Database Configuration ---
DB_CONFIG = {
    'user': 'root',
    'password': '',
    'host': 'localhost',
    'database': 'grievance_db',
}

def insert_dummy_data():
    """Connects to the database and inserts dummy data."""
    db = None
    cursor = None
    try:
        db = mysql.connector.connect(**DB_CONFIG)
        cursor = db.cursor()
        fake = Faker()

        print("Starting data population...")

        # --- 1. Populate Department Table ---
        print("Populating 'department' table...")
        departments = [
            (1, 'Computer Science', 'Academic'),
            (2, 'Electrical Engineering', 'Academic'),
            (3, 'Student Affairs', 'Administrative'),
            (4, 'Finance Office', 'Administrative'),
            (5, 'Library', 'Administrative')
        ]
        dept_insert_query = "INSERT INTO department (department_id, name, type) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE name=VALUES(name), type=VALUES(type)"
        cursor.executemany(dept_insert_query, departments)
        print(f"-> Inserted/Updated {cursor.rowcount} departments.")

        # --- 2. Populate Student Table ---
        print("Populating 'student' table...")
        students = []
        for i in range(10):
            first_name = fake.first_name()
            last_name = fake.last_name()
            email = f"{first_name.lower()}.{last_name.lower()}{i}@university.edu"
            students.append((
                f"B200{i+1:03d}CS",
                first_name,
                last_name,
                email,
                fake.phone_number(),
                'B.Tech',
                random.choice([1, 2]), # Assign to CS or EE
                random.randint(1, 4),
                generate_password_hash('student123')
            ))
        
        student_insert_query = """
            INSERT INTO student (roll_no, first_name, last_name, email, phone, course, department_id, year_of_study, password)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE email=VALUES(email);
        """
        # Add specific student for testing
        students.append((
            '1', 'Test', 'Student', 'test.student@university.edu', 'N/A', 'B.Tech', 1, 1, '123456'
        ))
        cursor.executemany(student_insert_query, students)
        print(f"-> Inserted/Updated {cursor.rowcount} students.")

        # --- 3. Populate Faculty Table ---
        print("Populating 'faculty' table...")
        faculty = []
        positions = ['Professor', 'Associate Professor', 'Assistant Professor', 'Head of Department']
        for i in range(5):
            first_name = fake.first_name()
            last_name = fake.last_name()
            email = f"{first_name.lower()}.{last_name.lower()}@faculty.university.edu"
            faculty.append((
                first_name,
                last_name,
                email,
                fake.phone_number(),
                random.choice(positions),
                random.choice([1, 2, 3, 4, 5]), # Assign to any department
                generate_password_hash('faculty123')
            ))

        faculty_insert_query = """
            INSERT INTO faculty (first_name, last_name, email, phone, position, department_id, password)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE email=VALUES(email);
        """

        faculty.append((
            'ADMIN', 'ADMIN', 'admin@nsut.com', '5552211111', 'admin', 1, '123456'
        ))
        cursor.executemany(faculty_insert_query, faculty)
        print(f"-> Inserted/Updated {cursor.rowcount} faculty members.")

        # --- 4. Populate Complaint Category Table ---
        print("Populating 'complaint_category' table...")
        categories = [
            (1, 'Academic', 'Issues related to courses, grading, and teaching.'),
            (2, 'Infrastructure', 'Issues related to campus facilities like classrooms, labs, and hostels.'),
            (3, 'Administrative', 'Issues related to admissions, fees, and other office procedures.'),
            (4, 'Library', 'Issues related to library services, books, and resources.'),
            (5, 'Harassment', 'Incidents of harassment or bullying.'),
            (6, 'Other', 'Miscellaneous issues not covered in other categories.')
        ]
        category_insert_query = "INSERT INTO complaint_category (category_id, category, description) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE category=VALUES(category)"
        cursor.executemany(category_insert_query, categories)
        print(f"-> Inserted/Updated {cursor.rowcount} complaint categories.")

        db.commit()
        print("\nDummy data has been successfully inserted and committed.")

    except mysql.connector.Error as err:
        print(f"\nAn error occurred: {err}")
        if db:
            db.rollback()
            print("Transaction rolled back.")
    finally:
        if cursor:
            cursor.close()
        if db and db.is_connected():
            db.close()
            print("Database connection closed.")

if __name__ == '__main__':
    insert_dummy_data()
