# IDOR-Challenge

ctf-idor/
├─ app.py
├─ seed_db.py
├─ entrypoint.sh
├─ requirements.txt
├─ Dockerfile
├─ docker-compose.yml
├─ README.md
├─ ctf.db (optionnel - créé au démarrage)
├─ templates/
│  ├─ base.html
│  ├─ register.html
│  ├─ login.html
│  ├─ home.html
│  └─ user.html
└─ static/
   └─ style.css


http://localhost:5000

ER{succ3ss_JP0!}

sudo docker build -t ctf_idor .
sudo docker run -d -p 5000:5000 --name ctf_idor_app ctf_idor
sudo docker ps
sudo docker stop ctf_idor_app
sudo docker rm ctf_idor_app


sudo docker build -t ctf_idor .
sudo docker stop ctf_idor_app
sudo docker rm ctf_idor_app
sudo docker run -d -p 5000:5000 --name ctf_idor_app ctf_idor
