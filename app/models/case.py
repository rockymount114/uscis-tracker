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

    def update_status(self, new_status):
        if not self.history: 
            self.history = []
        # Append to history
        self.history.append({
            "status": new_status, 
            "at": datetime.utcnow().isoformat()
        })
        self.current_status = new_status
        self.last_checked = datetime.utcnow()

    @property
    def usps_tracking(self):
        import re
        if not self.current_status:
            return None
        match = re.search(r'USPS Tracking:\s*([A-Z0-9]+)', self.current_status)
        if match:
            return match.group(1).replace(')', '').strip()
        # Fallback regex for raw tracking number
        match_raw = re.search(r'\b(9\d{21}|[A-Z]{2}\d{9}US)\b', self.current_status)
        if match_raw:
            return match_raw.group(1)
        return None

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
