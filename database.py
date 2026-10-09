
import sqlite3

connexion = sqlite3.connect("coiffeurpro.db")

curseur = connexion.cursor()

curseur.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
)
""")

curseur.execute("""
CREATE TABLE IF NOT EXISTS clients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    nom TEXT NOT NULL,
    telephone TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
)
""")

connexion.commit()

connexion.close()

print("Base de données créée avec succès !")