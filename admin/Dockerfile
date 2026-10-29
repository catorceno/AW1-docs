FROM python:3.10

WORKDIR /opt/admin

ENV DJANGO_SETTINGS_MODULE='config.settings'

COPY requirements.txt requirements.txt

RUN pip install --upgrade pip \
  && pip install -r requirements.txt

COPY . .

EXPOSE 8000

# ENTRYPOINT ["uwsgi", "--module=config.wsgi", "--http", ":8000"]
ENTRYPOINT [ "uwsgi", "--ini", "uwsgi.ini" ]