FROM python:3.11-slim

WORKDIR /srv/ctf

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /srv/ctf

RUN chmod +x /srv/ctf/entrypoint.sh

ENV FLASK_ENV=production
ENV FLASK_APP=app.py
ENV CTF_DB_PATH=/srv/ctf/ctf.db
ENV FLASK_SECRET=change_this_secret_for_local_dev

EXPOSE 5000
ENTRYPOINT ["/srv/ctf/entrypoint.sh"]
