from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Conversation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    speaker = db.Column(db.String(50))
    text = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.now)
