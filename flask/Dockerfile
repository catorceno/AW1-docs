FROM ubuntu:22.04

RUN apt-get update && apt-get install -y nano
RUN apt-get install -y python3 python3-pip
RUN pip3 install flask

COPY . /site/

EXPOSE 5001

CMD ["python3", "/site/app.py"]
