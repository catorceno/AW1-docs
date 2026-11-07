import os

from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "postgresql://todo:todo@localhost:5432/todoapp")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    CORS_ORIGINS = [
        o.strip()
        for o in os.environ.get("CORS_ORIGINS", "http://localhost:5001").split(",")
        if o.strip()
    ]

class ProductionConfig(Config):
    SESSION_COOKIE_SECURE = True      # solo enviar cookies por HTTPS
    SESSION_COOKIE_HTTPONLY = True    # JavaScript no puede leerlas
    SESSION_COOKIE_SAMESITE = "Lax"   # protección básica contra CSRF
    PREFERRED_URL_SCHEME = "https"