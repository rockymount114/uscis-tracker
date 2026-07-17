import os
import atexit
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from app.config import Config

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)

    # Register blueprints
    from app.blueprints.cases import cases_bp
    from app.blueprints.dashboard import dashboard_bp
    from app.blueprints.api import api_bp

    app.register_blueprint(cases_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(api_bp)

    # Initialize Background Scheduler
    init_scheduler(app)

    return app

def init_scheduler(app):
    from apscheduler.schedulers.background import BackgroundScheduler
    from app.models.case import Case
    from app.services.uscis_client import fetch_case_status
    from datetime import datetime

    scheduler = BackgroundScheduler()

    def check_cases():
        with app.app_context():
            print("APScheduler: Running background checks for USCIS cases...")
            cases = Case.query.all()
            updated_count = 0
            for case in cases:
                try:
                    status = fetch_case_status(case.receipt_number)
                    if status != case.current_status:
                        case.update_status(status)
                        updated_count += 1
                    else:
                        case.last_checked = datetime.utcnow()
                except Exception as e:
                    print(f"APScheduler: Error tracking case {case.receipt_number}: {e}")
            if cases:
                db.session.commit()
                print(f"APScheduler: Completed status update checks. Updated {updated_count}/{len(cases)} cases.")

    # Run check_cases every 12 hours
    scheduler.add_job(func=check_cases, trigger="interval", hours=12)

    # Avoid running multiple schedulers during Werkzeug reload (debug mode)
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true" or os.environ.get("FLASK_ENV") != "development":
        scheduler.start()
        print("APScheduler: Background task scheduler started.")
        atexit.register(lambda: scheduler.shutdown())
