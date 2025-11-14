import mysql.connector
from flask import g

# --- Database Configuration ---
DB_CONFIG = {
    'user': 'root',
    'password': '',
    'host': '127.0.0.1',
    'database': 'grievance_db',
}

def get_db():
    """Get a database connection for the current request."""
    if 'db' not in g:
        g.db = mysql.connector.connect(**DB_CONFIG)
    return g.db

def close_db(e=None):
    """Close the database connection at the end of the request."""
    db = g.pop('db', None)
    if db is not None:
        db.close()
