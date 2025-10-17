from flask import Flask, render_template, request, redirect, url_for, session, flash, g
from flask import jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os

DB_PATH = os.environ.get("CTF_DB_PATH", "ctf.db")
SECRET_KEY = os.environ.get("FLASK_SECRET", "change_this_secret_for_local_dev")

app = Flask(__name__)
app.secret_key = SECRET_KEY

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DB_PATH)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def query_db(query, args=(), one=False, commit=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    if commit:
        get_db().commit()
    cur.close()
    return (rv[0] if rv else None) if one else rv

@app.route('/')
def index():
    if 'user_id' not in session:
        return render_template('index.html')
    return render_template('home.html', username=session.get('username'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        if not username or not password:
            flash("Nom d'utilisateur et mot de passe requis.", "danger")
            return redirect(url_for('register'))
        password_hash = generate_password_hash(password)

        try:
            conn = get_db()
            cur = conn.execute(
                "INSERT INTO users (username, password_hash, role, profile_data, created_at) VALUES (?, ?, 'user', ?, datetime('now'))",
                (username, password_hash, f"Profil de {username}")
            )
            conn.commit()
            new_id = cur.lastrowid
            cur.close()
            session['user_id'] = new_id
            session['username'] = username
            session['role'] = 'user'
            flash("Compte créé et connecté.", "success")
            return redirect(f"/user?id={new_id}")
        except sqlite3.IntegrityError:
            flash("Nom d'utilisateur déjà pris.", "danger")
            return redirect(url_for('register'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        user = query_db("SELECT * FROM users WHERE username = ?", (username,), one=True)
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            flash("Connecté.", "success")
            return redirect(f"/user?id={user['id']}")
        flash("Identifiants incorrects.", "danger")
        return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("Déconnecté.", "info")
    return redirect(url_for('index'))

@app.route('/user')
def user_profile():
    """
    ENDPOINT INTENTIONNELLEMENT VULNÉRABLE (IDOR) POUR LE CHALLENGE :
    - Si ?id= est fourni, affiche ce profil (aucune vérification d'autorisation ici,
      c'est volontaire pour le challenge).
    - Si ?id= n'est pas fourni, affiche le profil de l'utilisateur connecté.
    Dans une vraie application, il faudrait vérifier les autorisations côté serveur.
    """
    if 'user_id' not in session:
        return redirect(url_for('login'))

    raw_id = request.args.get('id')
    if raw_id is None or raw_id == '':
        target_id = session['user_id']
    else:
        try:
            target_id = int(raw_id)
        except ValueError:
            flash("id invalide.", "danger")
            return redirect(url_for('index'))

    user = query_db("SELECT id, username, role, profile_data FROM users WHERE id = ?", (target_id,), one=True)
    if not user:
        flash("Utilisateur non trouvé.", "warning")
        return redirect(url_for('index'))
    return render_template('user.html', user=user)

@app.route('/submit-flag', methods=['POST'])
def submit_flag():
    if 'user_id' not in session:
        return jsonify({"status": "error", "message": "Non connecté"}), 403

    flag = request.form.get('flag', '').strip()
    if flag == "ER{succ3ss_JP0!}":
        return jsonify({"status": "success", "message": "Réussi ! 🎉"})
    else:
        return jsonify({"status": "fail", "message": "Incorrect."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
