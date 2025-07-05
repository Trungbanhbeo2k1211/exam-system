from models import db
from app import app  # hoặc wherever your Flask app is

with app.app_context():
    db.create_all()
