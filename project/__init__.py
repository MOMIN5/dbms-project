from flask import Flask
from .db import close_db
from .routes.main import bp as main_bp
from .routes.student import bp as student_bp
from .routes.faculty import bp as faculty_bp
from .routes.complaint import bp as complaint_bp

def create_app():
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__, instance_relative_config=True, template_folder='../templates')
    app.config.from_mapping(
        SECRET_KEY='dev',
    )

    # Initialize DB
    app.teardown_appcontext(close_db)

    # Register Blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(faculty_bp)
    app.register_blueprint(complaint_bp)

    return app
