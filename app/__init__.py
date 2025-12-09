from flask import Flask
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
migrate = Migrate()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    from app.routes.main import main_bp
    
    app.register_blueprint(main_bp)

    @app.context_processor
    def inject_now():
        return {'now': datetime.utcnow()}

    return app
