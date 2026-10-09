
import sqlite3

from flask import (
    Flask, render_template, request,
    redirect, url_for, session
)
from werkzeug.security import (
    generate_password_hash, check_password_hash
)

app = Flask(__name__)

# Clé de session pour le développement
app.secret_key = "cle-temporaire-a-remplacer"


@app.route("/")
def accueil():
    return render_template("index.html")


@app.route("/inscription", methods=["GET", "POST"])
def inscription():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        password_hash = generate_password_hash(password)

        connexion = sqlite3.connect("coiffeurpro.db")
        curseur = connexion.cursor()

        try:
            curseur.execute(
                "INSERT INTO users (email, password) VALUES (?, ?)",
                (email, password_hash)
            )
            connexion.commit()
        except sqlite3.IntegrityError:
            connexion.close()
            return "Cet email est déjà utilisé."

        connexion.close()

        return redirect(url_for("connexion"))

    return render_template("registrer.html")


@app.route("/connexion", methods=["GET", "POST"])
def connexion():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        connexion_db = sqlite3.connect("coiffeurpro.db")
        curseur = connexion_db.cursor()

        curseur.execute(
            "SELECT id, email, password FROM users WHERE email = ?",
            (email,)
        )
        utilisateur = curseur.fetchone()
        connexion_db.close()

        if utilisateur and check_password_hash(
            utilisateur[2], password
        ):
            session["user_id"] = utilisateur[0]
            session["email"] = utilisateur[1]

            return redirect(url_for("dashboard"))

        return "Email ou mot de passe incorrect."

    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("connexion"))

    return render_template(
        "dashboard.html",
        email=session["email"]
    )


@app.route("/deconnexion")
def deconnexion():
    session.clear()
    return redirect(url_for("accueil"))


@app.route("/clients", methods=["GET", "POST"])
def clients():
    if "user_id" not in session:
        return redirect(url_for("connexion"))

    connexion_db = sqlite3.connect("coiffeurpro.db")
    curseur = connexion_db.cursor()

    if request.method == "POST":
        nom = request.form["nom"].strip()
        telephone = request.form["telephone"].strip()

        if not nom:
            connexion_db.close()
            return "Le nom du client est obligatoire."

        curseur.execute(
            "INSERT INTO clients (user_id, nom, telephone) VALUES (?, ?, ?)",
            (session["user_id"], nom, telephone)
        )
        connexion_db.commit()

        connexion_db.close()
        return redirect(url_for("clients"))

    curseur.execute(
        "SELECT id, nom, telephone FROM clients WHERE user_id = ? ORDER BY id DESC",
        (session["user_id"],)
    )
    liste_clients = curseur.fetchall()
    connexion_db.close()

    return render_template("clients.html", clients=liste_clients)


@app.route("/clients/<int:client_id>/modifier", methods=["GET", "POST"])
def modifier_client(client_id):
    if "user_id" not in session:
        return redirect(url_for("connexion"))

    connexion_db = sqlite3.connect("coiffeurpro.db")
    curseur = connexion_db.cursor()

    if request.method == "POST":
        nom = request.form["nom"].strip()
        telephone = request.form["telephone"].strip()

        if not nom:
            connexion_db.close()
            return "Le nom du client est obligatoire."

        curseur.execute(
            """UPDATE clients
               SET nom = ?, telephone = ?
               WHERE id = ? AND user_id = ?""",
            (nom, telephone, client_id, session["user_id"])
        )
        connexion_db.commit()
        connexion_db.close()

        return redirect(url_for("clients"))

    curseur.execute(
        """SELECT id, nom, telephone FROM clients
           WHERE id = ? AND user_id = ?""",
        (client_id, session["user_id"])
    )
    client = curseur.fetchone()
    connexion_db.close()

    if client is None:
        return "Client introuvable.", 404

    return render_template("modifier_client.html", client=client)


@app.route("/clients/<int:client_id>/supprimer", methods=["POST"])
def supprimer_client(client_id):
    if "user_id" not in session:
        return redirect(url_for("connexion"))

    connexion_db = sqlite3.connect("coiffeurpro.db")
    curseur = connexion_db.cursor()

    curseur.execute(
        "DELETE FROM clients WHERE id = ? AND user_id = ?",
        (client_id, session["user_id"])
    )

    connexion_db.commit()
    connexion_db.close()

    return redirect(url_for("clients"))




if __name__ == "__main__":
    app.run(debug=True)
