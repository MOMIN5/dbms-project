from flask import Flask
from .db import close_db
from .routes import student, staff, complaint, main

def create_app():
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
    )

    # Initialize DB
    app.teardown_appcontext(close_db)

    # Register Blueprints
    app.register_blueprint(main.bp)
    app.register_blueprint(student.bp)
    app.register_blueprint(staff.bp)
    app.register_blueprint(complaint.bp)

    # A simple main page
    @app.route('/')
    def index():
        return app.send_static_file('index.html')

    return app
