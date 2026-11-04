from flask import Flask

from .config import Config
from .extensions import db, migrate

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db) # conecta Flask-Migrate con db

    # is what executes the class definitions, which registers the tables on SQLAlchemy's metadata
    from . import models # noqa: F401
    from .routes import bp as todos_bp

    app.register_blueprint(todos_bp) # al ejecutarse esta línea, recién se registran los routes declarados en routes.py

    from .api import api_bp
    app.register_blueprint(api_bp, url_prefix="/api/v1")

    return app