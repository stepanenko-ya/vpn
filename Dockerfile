FROM python:3.8

RUN apt-get update && \
apt-get install -y sqlite3

COPY requirements.txt /tmp/requirements.txt
COPY vpn /vpn
WORKDIR /vpn

RUN pip install -r /tmp/requirements.txt



CMD ["sh", "-c", "sleep 10 && python manage.py makemigrations && python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]