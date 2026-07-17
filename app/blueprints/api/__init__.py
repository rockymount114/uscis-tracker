from flask import Blueprint, jsonify
from app.models.case import Case
from app.services import chart_service

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/stats')
def get_stats():
    """Returns aggregated data for Chart.js charts."""
    return jsonify({
        "status_distribution": chart_service.get_status_distribution(),
        "form_type_counts": chart_service.get_form_type_counts(),
        "timeline_data": chart_service.get_timeline_data()
    })

@api_bp.route('/cases')
def get_cases():
    """Returns JSON representation of all tracked cases."""
    cases = Case.query.all()
    cases_list = []
    for c in cases:
        cases_list.append({
            "id": c.id,
            "receipt_number": c.receipt_number,
            "form_type": c.form_type,
            "nickname": c.nickname,
            "current_status": c.current_status,
            "last_checked": c.last_checked.isoformat() if c.last_checked else None,
            "created_at": c.created_at.isoformat() if c.created_at else None,
            "history": c.history
        })
    return jsonify(cases_list)
