from flask import Flask

from .config import Config
from .extensions import db, migrate
from werkzeug.middleware.proxy_fix import ProxyFix

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)

    from . import models # noqa: F401
    from .routes import bp as todos_bp

    app.register_blueprint(todos_bp)

    # Confía en las cabeceras X-Forwarded-* que envía NGINX
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

    return app