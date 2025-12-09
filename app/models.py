from . import db
from datetime import datetime

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
