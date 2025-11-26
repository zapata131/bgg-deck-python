from . import db, login_manager
from flask_login import UserMixin
from datetime import datetime
import uuid

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String)
    email = db.Column(db.String, unique=True, nullable=False)
    image = db.Column(db.String)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    accounts = db.relationship('Account', backref='user', lazy=True)

class Account(db.Model):
    __tablename__ = 'accounts'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    provider = db.Column(db.String, nullable=False)
    provider_account_id = db.Column(db.String, nullable=False)
    access_token = db.Column(db.String)
    refresh_token = db.Column(db.String)
    expires_at = db.Column(db.Integer)
    
    __table_args__ = (db.UniqueConstraint('provider', 'provider_account_id', name='_provider_unique'),)

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
