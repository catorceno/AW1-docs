from app import create_app

# En producción, SESSION_COOKIE_SECURE y BEHIND_PROXY llegan desde el entorno
# (docker-compose.prod.yml), así que ya no hace falta ProductionConfig.
app = create_app()