FROM python:3.13

WORKDIR /opt/app

ENV DJANGO_SETTINGS_MODULE='config.settings'

# COPY run_uwsgi.sh run_uwsgi.sh
COPY requirements.txt requirements.txt
COPY uwsgi/uwsgi.ini uwsgi.ini

RUN pip install --upgrade pip \
  && pip install -r requirements.txt 

COPY . .

EXPOSE 8000

ENTRYPOINT ["uwsgi", "--strict", "--ini", "uwsgi.ini"]
