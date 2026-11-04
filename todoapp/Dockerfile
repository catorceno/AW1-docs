FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    # makes Python write logs immediately instead of buffering
    PYTHONUNBUFFERED=1 \
    FLASK_APP=wsgi.py

WORKDIR /app

RUN apt-get update \
    # postgresql-client sirve solo para hacer pg_isready en el docker compose
    && apt-get install -y --no-install-recommends postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# so nginx can read the named volume mounted in /app/app/static
RUN cp -r /app/app/static /opt/static-dist

RUN chmod +x entrypoint.sh

EXPOSE 5000

# ENTRYPOINT always run
ENTRYPOINT ["./entrypoint.sh"]

# CMD is the default argument, runs with exec "$@"
# wsgi:app -> en el archivo wsgi.py la variable app
CMD ["gunicorn", "--config", "gunicorn.conf.py", "wsgi:app"]
