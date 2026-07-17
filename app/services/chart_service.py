from app.models.case import Case
from collections import Counter, defaultdict

def get_status_distribution():
    cases = Case.query.all()
    # Simple count of current status
    counts = Counter(case.current_status for case in cases)
    return dict(counts)

def get_form_type_counts():
    cases = Case.query.all()
    # Simple count of form types (e.g., I-485, I-765)
    counts = Counter(case.form_type for case in cases)
    return dict(counts)

def get_timeline_data():
    """
    Aggregates history entries over time to show case activity.
    Returns a dictionary with 'labels' (sorted date strings) and 'values' (count of updates).
    """
    cases = Case.query.all()
    date_counts = defaultdict(int)
    
    for case in cases:
        if case.history:
            for entry in case.history:
                try:
                    # Get date component of ISO format timestamp (e.g., 2026-07-17)
                    date_str = entry.get('at', '').split('T')[0]
                    if date_str:
                        date_counts[date_str] += 1
                except Exception:
                    pass
        else:
            # Fallback to created_at
            date_str = case.created_at.strftime('%Y-%m-%d')
            date_counts[date_str] += 1
            
    # If empty database, add today as a dummy entry so chart loads cleanly
    if not date_counts:
        from datetime import datetime
        date_counts[datetime.utcnow().strftime('%Y-%m-%d')] = 0
        
    sorted_dates = sorted(date_counts.keys())
    return {
        "labels": sorted_dates,
        "values": [date_counts[d] for d in sorted_dates]
    }
