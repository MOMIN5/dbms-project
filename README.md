University Complaint & Grievance Redressal Portal

A web-based system designed to streamline the process of filing, managing, and resolving student grievances within a universityenvironment. 
The portal provides a centralized platform where students can register complaints, track their progress, and give feedback after resolution. 
Administrative staff and faculty can review, update, and respond to complaints through a structured workflow, ensuring transparency, accountability, and timely redressal. 
The project is developed using Flask (Python) and MySQL, with a well-structured relational database adhering to DBMS principles. 
It is ideal as a full academic project demonstrating backend design, database normalization, and real-world workflow implementation.

Features:
Centralized Complaint Submission --> Students can file grievancesrelated to academics, administration, hostel, or other issues.
Role-Based Access Control --> Different user roles (Student, Staff, Admin) with specific permissions. 
Real-Time Status Tracking --> Students can view the current status of their complaint anytime. 
Complaint History Log --> Every action---status changes, updates, comments---is stored fortraceability. 
Feedback System --> Students can rate and provide feedback after resolution. 
Dummy Data Generation --> Automated scripts populate the database using Faker for testing. 
Robust Relational Database --> Normalized schema with proper foreign keys for integrity and scalability.

Tech Stack Backend: 
Flask (Python) 
Database: MySQL (via XAMPP)
Connector: mysql-connector-python 
Data Generation: Faker 
Frontend: HTML, CSS, Bootstrap

Installation and Setup:
1. Download the zip file and extract it. 
2. Install required packages, by running following commands in CLI:
   1. pip install mysql-connector-python 
   2. pip install flask 
   3. pip install faker 
4. Open phpMyAdmin in XAMPP and create a database named grievance_db
5. Initialize the database with following commands:
   1. Create the schema:
      python create_tables.py
   2. Insert Sample data:
      python insert_dummy_data.py
6. Start the flask application by running the command:
   flask --app run run
7. Access the application by opening http://localhost:5000 in your browser.

License:
This project is open-source and available under the MIT License.
You are free to use, modify, and distribute it.
