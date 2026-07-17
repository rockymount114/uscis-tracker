from app import db
from datetime import datetime

class Case(db.Model):
    __tablename__ = 'cases'
    
    id = db.Column(db.Integer, primary_key=True)
    receipt_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    form_type = db.Column(db.String(20), nullable=False) # I-485, I-129, I-539, I-765, I-131, etc.
    nickname = db.Column(db.String(100))
    current_status = db.Column(db.String(200), default="Pending")
    history = db.Column(db.JSON, default=list)
    last_checked = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    usps_tracking = db.Column(db.String(30), nullable=True)
    mailed_date = db.Column(db.DateTime, nullable=True)
    is_simulated = db.Column(db.Boolean, default=False)

    def update_status(self, new_status, detail_text=None, is_simulated=False):
        if not self.history: 
            self.history = []
        # Append to history
        self.history.append({
            "status": new_status, 
            "at": datetime.utcnow().isoformat()
        })
        self.current_status = new_status
        self.last_checked = datetime.utcnow()
        self.is_simulated = is_simulated

        # Parse tracking and mailed date
        parsed_tracking = None
        parsed_date = None
        import re

        if detail_text:
            # Parse tracking number
            tracking_match = re.search(r'\b(9\d{21}|[A-Z]{2}\d{9}US)\b', detail_text)
            if tracking_match:
                parsed_tracking = tracking_match.group(1)
            
            # Parse date (e.g., "On July 17, 2026...")
            date_match = re.search(r'On\s+([A-Za-z]+\s+\d{1,2},\s+\d{4})', detail_text)
            if date_match:
                try:
                    parsed_date = datetime.strptime(date_match.group(1), "%B %d, %Y")
                except ValueError:
                    pass

        # Fallback to status parsing for tracking
        if not parsed_tracking and new_status:
            match = re.search(r'USPS Tracking:\s*([A-Z0-9]+)', new_status)
            if match:
                parsed_tracking = match.group(1).replace(')', '').strip()
            else:
                match_raw = re.search(r'\b(9\d{21}|[A-Z]{2}\d{9}US)\b', new_status)
                if match_raw:
                    parsed_tracking = match_raw.group(1)

        # Fallback for mailed date
        if not parsed_date and new_status:
            s = new_status.lower()
            if 'deliver' in s or 'mail' in s:
                parsed_date = datetime.utcnow()

        if parsed_tracking:
            self.usps_tracking = parsed_tracking
        if parsed_date:
            self.mailed_date = parsed_date

    @property
    def service_center(self):
        if not self.receipt_number or len(self.receipt_number) < 3:
            return "Unknown Service Center"
        
        prefix = self.receipt_number[:3].upper()
        mapping = {
            "MSC": "National Benefits Center (MSC)",
            "LIN": "Nebraska Service Center (LIN)",
            "SRC": "Texas Service Center (SRC)",
            "WAC": "California Service Center (WAC)",
            "EAC": "Vermont Service Center (EAC)",
            "YSC": "Potomac Service Center (YSC)",
            "IOE": "USCIS Electronic Filing (IOE)",
            "NBC": "National Benefits Center (NBC)",
            "VSC": "Vermont Service Center (VSC)",
            "CSC": "California Service Center (CSC)",
            "TSC": "Texas Service Center (TSC)"
        }
        return mapping.get(prefix, f"{prefix} Service Center")

    @property
    def rfe_deadline(self):
        import re
        if not self.current_status:
            return None
        # Look for (Respond by YYYY-MM-DD)
        match = re.search(r'Respond by\s+(\d{4}-\d{2}-\d{2})', self.current_status, re.IGNORECASE)
        if match:
            try:
                return datetime.strptime(match.group(1), "%Y-%m-%d")
            except:
                pass
        return None

    @property
    def days_left_to_respond(self):
        deadline = self.rfe_deadline
        if not deadline:
            return None
        # Calculate diff (comparing dates only to avoid timezone issues)
        today = datetime.utcnow().date()
        diff = deadline.date() - today
        return diff.days

    @property
    def progress_stage(self):
        """
        Determines case progress stages (1-5):
        1: Submission Received
        2: Biometrics & Fingerprints
        3: Under Active Review / Interview / RFE
        4: Decision Approved
        5: Card Delivered / Mailed
        """
        s = (self.current_status or '').lower()
        
        if 'deliver' in s or 'mail' in s:
            return {"number": 5, "name": "Delivery", "percent": 100}
        elif 'approve' in s:
            return {"number": 4, "name": "Decision", "percent": 80}
        elif 'evidence' in s or 'interview' in s or 'ready' in s or 'rfe' in s:
            return {"number": 3, "name": "Active Review", "percent": 60}
        elif 'fingerprint' in s or 'biometric' in s:
            return {"number": 2, "name": "Biometrics", "percent": 40}
        else:
            return {"number": 1, "name": "Submission", "percent": 20}
