import os
from flask import Flask
from config import config_by_name
from app.extensions import db, login_manager

def create_app(config_name='development'):
    """Application factory function."""
    app = Flask(__name__)
    app.config.from_object(config_by_name.get(config_name, config_by_name['default']))

    # Ensure the instance folder exists for SQLite storage
    os.makedirs(app.instance_path, exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)

    # Register blueprints
    from app.routes.main_routes import main_bp
    from app.routes.auth_routes import auth_bp
    from app.routes.banking_routes import banking_bp
    from app.routes.manager_routes import manager_bp
    from app.routes.admin_routes import admin_bp
    from app.routes.services_routes import services_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(banking_bp)
    app.register_blueprint(manager_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(services_bp)

    # Initialize Database tables and Seed Data
    with app.app_context():
        from app.models import User, Account, Transaction
        db.create_all()
        from app.seed import seed_demo_data
        seed_demo_data()

    @app.errorhandler(404)
    def page_not_found(e):
        from flask import render_template
        return render_template('404.html'), 404

    return app
