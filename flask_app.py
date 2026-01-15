from flask import Flask, redirect, render_template, request, url_for
from dotenv import load_dotenv
import os
import git
import hmac
import hashlib
from db import db_read, db_write
from auth import login_manager, authenticate, register_user
from flask_login import login_user, logout_user, login_required, current_user
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

# Load .env variables
load_dotenv()
W_SECRET = os.getenv("W_SECRET")

# Init flask app
app = Flask(__name__)
app.config["DEBUG"] = True
app.secret_key = "supersecret"

# Init auth
login_manager.init_app(app)
login_manager.login_view = "login"

# DON'T CHANGE
def is_valid_signature(x_hub_signature, data, private_key):
    hash_algorithm, github_signature = x_hub_signature.split('=', 1)
    algorithm = hashlib.__dict__.get(hash_algorithm)
    encoded_key = bytes(private_key, 'latin-1')
    mac = hmac.new(encoded_key, msg=data, digestmod=algorithm)
    return hmac.compare_digest(mac.hexdigest(), github_signature)

# DON'T CHANGE
@app.post('/update_server')
def webhook():
    x_hub_signature = request.headers.get('X-Hub-Signature')
    if is_valid_signature(x_hub_signature, request.data, W_SECRET):
        repo = git.Repo('./mysite')
        origin = repo.remotes.origin
        origin.pull()
        return 'Updated PythonAnywhere successfully', 200
    return 'Unathorized', 401

# Auth routes
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        user = authenticate(
            request.form["username"],
            request.form["password"]
        )

        if user:
            login_user(user)
            return redirect(url_for("index"))

        error = "Benutzername oder Passwort ist falsch."

    return render_template(
        "auth.html",
        title="In dein Konto einloggen",
        action=url_for("login"),
        button_label="Einloggen",
        error=error,
        footer_text="Noch kein Konto?",
        footer_link_url=url_for("register"),
        footer_link_label="Registrieren"
    )


@app.route("/register", methods=["GET", "POST"])
def register():
    error = None

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        ok = register_user(username, password)
        if ok:
            return redirect(url_for("login"))

        error = "Benutzername existiert bereits."

    return render_template(
        "auth.html",
        title="Neues Konto erstellen",
        action=url_for("register"),
        button_label="Registrieren",
        error=error,
        footer_text="Du hast bereits ein Konto?",
        footer_link_url=url_for("login"),
        footer_link_label="Einloggen"
    )

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))



# App routes
@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    # GET
    if request.method == "GET":
        todos = db_read("SELECT id, content, due FROM todos WHERE user_id=%s ORDER BY due", (current_user.id,))
        return render_template("main_page.html", todos=todos)

    # POST
    content = request.form["contents"]
    due = request.form["due_at"]
    db_write("INSERT INTO todos (user_id, content, due) VALUES (%s, %s, %s)", (current_user.id, content, due, ))
    return redirect(url_for("index"))

@app.post("/complete")
@login_required
def complete():
    todo_id = request.form.get("id")
    db_write("DELETE FROM todos WHERE user_id=%s AND id=%s", (current_user.id, todo_id,))
    return redirect(url_for("index"))
@app.route("/dbexplorer", methods=["GET", "POST"])
@login_required
def dbexplorer():
    # 1) Alle Tabellennamen holen
    tables_raw = db_read("SHOW TABLES")

    # db_read liefert je nach Setup Liste von dicts oder tuples -> beides abfangen
    all_tables = []
    for row in (tables_raw or []):
        if isinstance(row, dict):
            all_tables.append(next(iter(row.values())))
        else:
            all_tables.append(row[0])

    selected_tables = []
    limit = 50
    results = {}

    if request.method == "POST":
        # 2) Inputs aus dem Formular
        selected_tables = request.form.getlist("tables")
        table_input = (request.form.get("table_input") or "").strip()

        # Limit (falls leer/kaputt -> 50)
        try:
            limit = int(request.form.get("limit", 50))
        except:
            limit = 50

        # Optional: Tabelle aus Textfeld hinzufügen
        if table_input and table_input in all_tables and table_input not in selected_tables:
            selected_tables.append(table_input)

        # 3) Gewählte Tabellen lesen
        for t in selected_tables:
            # Spaltennamen holen
            cols_raw = db_read(f"DESCRIBE `{t}`")
            columns = []
            for c in (cols_raw or []):
                if isinstance(c, dict):
                    columns.append(c.get("Field"))
                else:
                    columns.append(c[0])

            # Daten holen
            rows = db_read(f"SELECT * FROM `{t}` LIMIT {limit}")

            # rows kann dicts oder tuples enthalten -> normalisieren
            normalized_rows = []
            if rows:
                if isinstance(rows[0], dict):
                    normalized_rows = [[r.get(col) for col in columns] for r in rows]
                else:
                    normalized_rows = rows

            results[t] = {"columns": columns, "rows": normalized_rows}

    return render_template(
        "dbexplorer.html",
        tables=all_tables,
        selected=selected_tables,
        results=results,
        limit=limit
    )
if __name__ == "__main__":
    app.run()
