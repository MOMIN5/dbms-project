import mysql.connector

# --- Database Configuration ---
# IMPORTANT: Make sure this matches the configuration in your app.py
DB_CONFIG = {
    'user': 'root',
    'password': '',
    'host': 'localhost',
    'database': 'grievance_db',
}

def create_tables():
    """Connects to the database and creates the required tables."""
    db = None
    cursor = None
    try:
        # Establish the database connection
        db = mysql.connector.connect(**DB_CONFIG)
        cursor = db.cursor()
        print("Successfully connected to the database.")

        # SQL statements to create tables
        # Using 'IF NOT EXISTS' to prevent errors if tables are already there.
        
        create_student_table = """
        CREATE TABLE IF NOT EXISTS student (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            roll_no VARCHAR(50) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL
        ) ENGINE=InnoDB;
        """

        create_staff_table = """
        CREATE TABLE IF NOT EXISTS staff (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL
        ) ENGINE=InnoDB;
        """

        create_complaint_table = """
        CREATE TABLE IF NOT EXISTS complaint (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(200) NOT NULL,
            description TEXT NOT NULL,
            status VARCHAR(20) NOT NULL DEFAULT 'Pending',
            student_id INT NOT NULL,
            staff_id INT,
            FOREIGN KEY (student_id) REFERENCES student(id) ON DELETE CASCADE,
            FOREIGN KEY (staff_id) REFERENCES staff(id) ON DELETE SET NULL
        ) ENGINE=InnoDB;
        """

        create_feedback_table = """
        CREATE TABLE IF NOT EXISTS feedback (
            id INT AUTO_INCREMENT PRIMARY KEY,
            feedback_text TEXT NOT NULL,
            complaint_id INT NOT NULL,
            FOREIGN KEY (complaint_id) REFERENCES complaint(id) ON DELETE CASCADE
        ) ENGINE=InnoDB;
        """

        # Execute the creation statements
        print("Creating 'student' table...")
        cursor.execute(create_student_table)
        
        print("Creating 'staff' table...")
        cursor.execute(create_staff_table)
        
        print("Creating 'complaint' table...")
        cursor.execute(create_complaint_table)
        
        print("Creating 'feedback' table...")
        cursor.execute(create_feedback_table)

        # Commit the changes
        db.commit()
        print("All tables created successfully!")

    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        # Clean up the connection
        if cursor:
            cursor.close()
        if db and db.is_connected():
            db.close()
            print("Database connection closed.")

if __name__ == '__main__':
    create_tables()
