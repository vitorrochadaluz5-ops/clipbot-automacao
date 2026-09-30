from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os

from database import init_db, get_db
from browser_manager import ensure_profile_dir, open_profile_browser

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "troque-por-uma-chave-forte")

init_db()


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            flash("Faça login para continuar.")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapper


@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""

        if not email or not password:
            flash("Email e senha são obrigatórios.")
            return redirect(url_for("register"))

        conn = get_db()
        existing = conn.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
        if existing:
            flash("Este email já está cadastrado.")
            return redirect(url_for("register"))

        conn.execute(
            "INSERT INTO users (email, password_hash) VALUES (?, ?)",
            (email, generate_password_hash(password)),
        )
        conn.commit()
        conn.close()

        flash("Cadastro realizado com sucesso. Faça login.")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""

        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        conn.close()

        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            session["email"] = user["email"]
            flash("Login realizado com sucesso.")
            return redirect(url_for("dashboard"))

        flash("Email ou senha inválidos.")
        return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Você saiu do sistema.")
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    conn = get_db()
    clients = conn.execute(
        "SELECT * FROM clients WHERE user_id = ? ORDER BY created_at DESC",
        (session["user_id"],),
    ).fetchall()
    conn.close()
    return render_template("dashboard.html", clients=clients)


@app.route("/clients/new", methods=["GET", "POST"])
@login_required
def add_client():
    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        tiktok_username = (request.form.get("tiktok_username") or "").strip()

        if not name:
            flash("Informe o nome do cliente.")
            return redirect(url_for("add_client"))

        conn = get_db()
        cursor = conn.execute(
            "INSERT INTO clients (user_id, name, tiktok_username, profile_path, active) VALUES (?, ?, ?, ?, ?)",
            (session["user_id"], name, tiktok_username, "", 1),
        )
        client_id = cursor.lastrowid
        profile_dir = ensure_profile_dir(client_id)

        conn.execute(
            "UPDATE clients SET profile_path = ? WHERE id = ?",
            (profile_dir, client_id),
        )
        conn.commit()
        conn.close()

        flash(f"Cliente '{name}' cadastrado com sucesso.")
        return redirect(url_for("dashboard"))

    return render_template("add_client.html")


@app.route("/clients/<int:client_id>/connect")
@login_required
def connect_client(client_id):
    conn = get_db()
    client = conn.execute(
        "SELECT * FROM clients WHERE id = ? AND user_id = ?",
        (client_id, session["user_id"]),
    ).fetchone()
    conn.close()

    if not client:
        flash("Cliente não encontrado.")
        return redirect(url_for("dashboard"))

    profile_dir = client["profile_path"] or ensure_profile_dir(client_id)
    open_profile_browser(profile_dir)
    flash(f"Perfil do cliente '{client['name']}' aberto. Faça login manualmente no TikTok.")
    return redirect(url_for("dashboard"))


@app.route("/clients/<int:client_id>/delete", methods=["POST"])
@login_required
def delete_client(client_id):
    conn = get_db()
    conn.execute(
        "DELETE FROM clients WHERE id = ? AND user_id = ?",
        (client_id, session["user_id"]),
    )
    conn.commit()
    conn.close()
    flash("Cliente removido.")
    return redirect(url_for("dashboard"))


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)
