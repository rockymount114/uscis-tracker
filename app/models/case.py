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
