from flask import Blueprint, render_template
from app.models.case import Case

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
def index():
    # Render main dashboard index page.
    # We pass the count of total cases and updated counts for display cards
    total_cases = Case.query.count()
    return render_template('dashboard/index.html', total_cases=total_cases)
