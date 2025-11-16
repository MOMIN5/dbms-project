import mysql.connector
from mysql.connector import errorcode

# --- Database Configuration ---
DB_CONFIG = {
    'user': 'root',
    'password': '',
    'host': 'localhost',
    'database': 'grievance_db',
}

def create_database(cursor):
    try:
        cursor.execute(f"CREATE DATABASE {DB_CONFIG['database']} DEFAULT CHARACTER SET 'utf8'")
        print(f"Database '{DB_CONFIG['database']}' created successfully.")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_DB_CREATE_EXISTS:
            print(f"Database '{DB_CONFIG['database']}' already exists.")
        else:
            print(err)
            exit(1)

def execute_and_print(cursor, statement, table_name):
    try:
        print(f"Creating table '{table_name}': ", end='')
        cursor.execute(statement)
        print("OK")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            print("already exists.")
        else:
            print(f"Error: {err.msg}")
            raise err # Re-raise the error to stop execution

def create_tables():
    """Connects to the database and creates the required tables."""
    db = None
    cursor = None
    try:
        # Establish connection
        db = mysql.connector.connect(user=DB_CONFIG['user'], password=DB_CONFIG['password'], host=DB_CONFIG['host'])
        cursor = db.cursor()
        
        # Create and/or select the database
        create_database(cursor)
        cursor.execute(f"USE {DB_CONFIG['database']}")
        print(f"Successfully connected to database '{DB_CONFIG['database']}.")

        # --- Define Table Schemas ---
        department_table = """
            CREATE TABLE IF NOT EXISTS department (
                department_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                type VARCHAR(50) NOT NULL COMMENT 'Academic / Administrative'
            ) ENGINE=InnoDB;
        """
        student_table = """
            CREATE TABLE IF NOT EXISTS student (
                roll_no VARCHAR(50) PRIMARY KEY,
                first_name VARCHAR(50) NOT NULL,
                last_name VARCHAR(50) NOT NULL,
                email VARCHAR(100) NOT NULL UNIQUE,
                phone VARCHAR(20),
                course VARCHAR(100),
                department_id INT UNSIGNED,
                year_of_study INT,
                password VARCHAR(255) NOT NULL,
                FOREIGN KEY (department_id) REFERENCES department(department_id) ON DELETE SET NULL
            ) ENGINE=InnoDB;
        """
        faculty_table = """
            CREATE TABLE IF NOT EXISTS faculty (
                faculty_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
                first_name VARCHAR(50) NOT NULL,
                last_name VARCHAR(50) NOT NULL,
                email VARCHAR(100) NOT NULL UNIQUE,
                phone VARCHAR(20),
                position VARCHAR(100),
                department_id INT UNSIGNED,
                password VARCHAR(255) NOT NULL,
                FOREIGN KEY (department_id) REFERENCES department(department_id) ON DELETE SET NULL
            ) ENGINE=InnoDB;
        """
        complaint_category_table = """
            CREATE TABLE IF NOT EXISTS complaint_category (
                category_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
                category VARCHAR(100) NOT NULL,
                description TEXT
            ) ENGINE=InnoDB;
        """
        complaint_status_table = """
            CREATE TABLE IF NOT EXISTS complaint_status (
                status_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
                status VARCHAR(50) NOT NULL,
                remarks TEXT
            ) ENGINE=InnoDB;
        """
        complaint_table = """
            CREATE TABLE IF NOT EXISTS complaint (
                complaint_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
                is_anonymous BOOLEAN NOT NULL DEFAULT FALSE,
                student_roll_no VARCHAR(50),
                category_id INT UNSIGNED,
                subject VARCHAR(255) NOT NULL,
                description TEXT NOT NULL,
                date_filed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                assigned_to_faculty_id INT UNSIGNED,
                status_id INT UNSIGNED DEFAULT 1,
                priority ENUM('Low', 'Medium', 'High') DEFAULT 'Medium',
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                deadline DATE,
                FOREIGN KEY (student_roll_no) REFERENCES student(roll_no) ON DELETE CASCADE,
                FOREIGN KEY (category_id) REFERENCES complaint_category(category_id) ON DELETE SET NULL,
                FOREIGN KEY (assigned_to_faculty_id) REFERENCES faculty(faculty_id) ON DELETE SET NULL,
                FOREIGN KEY (status_id) REFERENCES complaint_status(status_id) ON DELETE SET NULL
            ) ENGINE=InnoDB;
        """
        complaint_history_table = """
            CREATE TABLE IF NOT EXISTS complaint_history (
                history_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
                complaint_id INT UNSIGNED NOT NULL,
                action_by_faculty_id INT UNSIGNED,
                action_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                previous_status_id INT UNSIGNED,
                new_status_id INT UNSIGNED,
                comment TEXT,
                FOREIGN KEY (complaint_id) REFERENCES complaint(complaint_id) ON DELETE CASCADE,
                FOREIGN KEY (action_by_faculty_id) REFERENCES faculty(faculty_id) ON DELETE SET NULL,
                FOREIGN KEY (previous_status_id) REFERENCES complaint_status(status_id) ON DELETE SET NULL,
                FOREIGN KEY (new_status_id) REFERENCES complaint_status(status_id) ON DELETE SET NULL
            ) ENGINE=InnoDB;
        """
        
        feedback_table = """
            CREATE TABLE IF NOT EXISTS feedback (
                feedback_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
                complaint_id INT UNSIGNED NOT NULL,
                student_roll_no VARCHAR(50) NOT NULL,
                rating INT CHECK (rating >= 1 AND rating <= 5),
                comments TEXT,
                date_submitted TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (complaint_id) REFERENCES complaint(complaint_id) ON DELETE CASCADE,
                FOREIGN KEY (student_roll_no) REFERENCES student(roll_no) ON DELETE CASCADE
            ) ENGINE=InnoDB;
        """

        # --- Execute statements in strict order ---
        execute_and_print(cursor, department_table, 'department')
        execute_and_print(cursor, student_table, 'student')
        execute_and_print(cursor, faculty_table, 'faculty')
        execute_and_print(cursor, complaint_category_table, 'complaint_category')
        execute_and_print(cursor, complaint_status_table, 'complaint_status')
        execute_and_print(cursor, complaint_table, 'complaint')
        execute_and_print(cursor, complaint_history_table, 'complaint_history')
        execute_and_print(cursor, feedback_table, 'feedback')

        # --- Populate initial data ---
        populate_status_table = """
            INSERT IGNORE INTO complaint_status (status_id, status) VALUES
            (1, 'Filed'),
            (2, 'Under Review'),
            (3, 'Resolved'),
            (4, 'Closed'),
            (5, 'Rejected');
        """
        print("Populating 'complaint_status' table... ", end='')
        cursor.execute(populate_status_table)
        print("OK")


        db.commit()
        print("\nAll tables created and populated successfully!")

    except mysql.connector.Error as err:
        print(f"\nA critical error occurred: {err}")
        if db:
            db.rollback()
    finally:
        # Clean up the connection
        if cursor:
            cursor.close()
        if db and db.is_connected():
            db.close()
            print("Database connection closed.")

if __name__ == '__main__':
    create_tables()
