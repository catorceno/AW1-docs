# archivo de la factory

from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_cors import CORS
from .config import Config
from .extensions import db, migrate

# Application Factory porque hace Flask(__name__)
# (config_class): es lo que permite crear apps distintas con el mismo código
def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    if len(app.config["JWT_SECRET_KEY"].encode()) < 32:
        raise RuntimeError("JWT_SECRET_KEY must be at least 32 bytes long.")

    origenes = app.config["CORS_ORIGINS"]
    CORS(
        app,
        resources={r"/api/*": {"origins": origenes}},
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization"],
        supports_credentials=True,
        max_age=600,
    )

    db.init_app(app)
    migrate.init_app(app, db)

    # imports dentro de la función para evitar imports circulares
    from . import models # noqa: F401
    from .api import bp as api_bp
    from .auth import AuthError
    from .auth.handlers import handle_auth_error
    from .auth.routes import bp as auth_bp
    from .routes import bp as todos_bp

    app.register_blueprint(todos_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp)

    app.register_error_handler(AuthError, handle_auth_error) # conecta la excepción con el manejador

    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

    return app