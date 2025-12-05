from . import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import uuid

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(120))
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Game(db.Model):
    __tablename__ = 'games'
    id = db.Column(db.Integer, primary_key=True)
    bgg_id = db.Column(db.Integer, unique=True, nullable=False)
    name = db.Column(db.String, nullable=False)
    image = db.Column(db.String)
    thumbnail = db.Column(db.String)
    description = db.Column(db.Text)
    year_published = db.Column(db.String)
    min_players = db.Column(db.String)
    max_players = db.Column(db.String)
    playing_time = db.Column(db.String)
    average_weight = db.Column(db.Float)
    designers = db.Column(db.String) # Stored as JSON string or comma-separated
    artists = db.Column(db.String)   # Stored as JSON string or comma-separated
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
