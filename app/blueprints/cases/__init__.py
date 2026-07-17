from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models.case import Case
from app.services.uscis_client import fetch_case_status
from datetime import datetime

cases_bp = Blueprint('cases', __name__, url_prefix='/cases')

@cases_bp.route('/')
def list_cases():
    cases = Case.query.all()
    # Preset form types
    form_types = ["I-485", "I-129", "I-539", "I-765", "I-131", "I-130", "I-140", "N-400"]
    return render_template('cases/list.html', cases=cases, form_types=form_types)

@cases_bp.route('/add', methods=['POST'])
def add_case():
    receipt_number = request.form.get('receipt_number', '').strip().upper()
    form_type = request.form.get('form_type', '').strip()
    nickname = request.form.get('nickname', '').strip()
    
    if not receipt_number or not form_type:
        flash("Receipt number and form type are required.", "danger")
        return redirect(url_for('cases.list_cases'))
        
    existing = Case.query.filter_by(receipt_number=receipt_number).first()
    if existing:
        flash(f"Case with receipt number {receipt_number} is already being tracked.", "warning")
        return redirect(url_for('cases.list_cases'))
        
    # Fetch status immediately on addition
    status = fetch_case_status(receipt_number)
    
    new_case = Case(
        receipt_number=receipt_number,
        form_type=form_type,
        nickname=nickname
    )
    new_case.update_status(status)
    
    db.session.add(new_case)
    db.session.commit()
    
    flash(f"Successfully added case {receipt_number}!", "success")
    return redirect(url_for('cases.list_cases'))

@cases_bp.route('/<int:case_id>/edit', methods=['GET', 'POST'])
def edit_case(case_id):
    case = Case.query.get_or_404(case_id)
    form_types = ["I-485", "I-129", "I-539", "I-765", "I-131", "I-130", "I-140", "N-400"]
    
    if request.method == 'POST':
        receipt_number = request.form.get('receipt_number', '').strip().upper()
        form_type = request.form.get('form_type', '').strip()
        nickname = request.form.get('nickname', '').strip()
        
        if not receipt_number or not form_type:
            flash("Receipt number and form type are required.", "danger")
            return redirect(url_for('cases.edit_case', case_id=case_id))
            
        # Check uniqueness if receipt number changed
        if receipt_number != case.receipt_number:
            existing = Case.query.filter_by(receipt_number=receipt_number).first()
            if existing:
                flash(f"Another case with receipt number {receipt_number} is already tracked.", "warning")
                return redirect(url_for('cases.edit_case', case_id=case_id))
            case.receipt_number = receipt_number
            # Fetch updated status for the new number
            status = fetch_case_status(receipt_number)
            case.update_status(status)
            
        case.form_type = form_type
        case.nickname = nickname
        
        db.session.commit()
        flash("Case updated successfully!", "success")
        return redirect(url_for('cases.list_cases'))
        
    return render_template('cases/edit.html', case=case, form_types=form_types)

@cases_bp.route('/<int:case_id>/delete', methods=['POST'])
def delete_case(case_id):
    case = Case.query.get_or_404(case_id)
    receipt = case.receipt_number
    db.session.delete(case)
    db.session.commit()
    flash(f"Case {receipt} deleted successfully.", "success")
    return redirect(url_for('cases.list_cases'))

@cases_bp.route('/<int:case_id>/refresh', methods=['POST'])
def refresh_case(case_id):
    case = Case.query.get_or_404(case_id)
    status = fetch_case_status(case.receipt_number)
    
    if status != case.current_status:
        case.update_status(status)
        flash(f"Status updated to: {status}", "success")
    else:
        case.last_checked = datetime.utcnow()
        flash("Status is up-to-date.", "info")
        
    db.session.commit()
    return redirect(url_for('cases.list_cases'))

@cases_bp.route('/refresh-all', methods=['POST'])
def refresh_all_cases():
    cases = Case.query.all()
    if not cases:
        flash("No cases to refresh.", "info")
        return redirect(url_for('cases.list_cases'))
        
    updated_count = 0
    for case in cases:
        status = fetch_case_status(case.receipt_number)
        if status != case.current_status:
            case.update_status(status)
            updated_count += 1
        else:
            case.last_checked = datetime.utcnow()
            
    db.session.commit()
    if updated_count > 0:
        flash(f"Checked {len(cases)} cases. {updated_count} status updates found!", "success")
    else:
        flash(f"Checked {len(cases)} cases. All statuses are up-to-date.", "info")
    return redirect(url_for('cases.list_cases'))
