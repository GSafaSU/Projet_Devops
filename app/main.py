"""API « cobaye » du TP DevOps : une mini liste de tâches stockée dans PostgreSQL."""
import os
import socket

import psycopg
from fastapi import FastAPI, HTTPException
from psycopg.rows import dict_row
from pydantic import BaseModel

# --- Configuration : lue dans les variables d'environnement ---------------
# Les valeurs après la virgule sont des valeurs par défaut (développement).
APP_VERSION = os.getenv("APP_VERSION", "dev")
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "dbname": os.getenv("DB_NAME", "tasks"),
    "user": os.getenv("DB_USER", "tasks"),
    "password": os.getenv("DB_PASSWORD", "tasks"),
    "connect_timeout": 3,
}

app = FastAPI(title="TP DevOps - API de tâches", version=APP_VERSION)
table_prete = False


class NouvelleTache(BaseModel):
    title: str


# --- Accès à la base ---------------------------------------------------------
def connexion():
    """Ouvre une connexion à PostgreSQL, ou répond 503 si la base est injoignable."""
    try:
        return psycopg.connect(**DB_CONFIG, row_factory=dict_row)
    except psycopg.OperationalError as erreur:
        print(f"[ERREUR] Base injoignable : {erreur}", flush=True)
        raise HTTPException(
            status_code=503,
            detail=f"Base de données injoignable ({DB_CONFIG['host']}:{DB_CONFIG['port']})",
        )


def connexion_avec_table():
    """Comme connexion(), mais crée la table 'tasks' la première fois."""
    global table_prete
    conn = connexion()
    if not table_prete:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS tasks ("
            " id SERIAL PRIMARY KEY,"
            " title TEXT NOT NULL,"
            " done BOOLEAN NOT NULL DEFAULT FALSE)"
        )
        conn.commit()
        table_prete = True
    return conn


# --- Routes de l'API -----------------------------------------------------------
@app.get("/")
def accueil():
    return {
        "message": "Bonjour depuis l'API du TP DevOps !",
        "version": APP_VERSION,
        "hostname": socket.gethostname(),
    }


@app.get("/health")
def health():
    # « Le processus est-il vivant ? » Ne dépend volontairement PAS de la base.
    return {"status": "ok"}


@app.get("/ready")
def ready():
    # « Es-tu prêt à servir ? » Vérifie que la base répond.
    with connexion() as conn:
        conn.execute("SELECT 1")
    return {"status": "ready"}


@app.get("/tasks")
def lister_taches():
    with connexion_avec_table() as conn:
        return conn.execute("SELECT id, title, done FROM tasks ORDER BY id").fetchall()


@app.post("/tasks", status_code=201)
def creer_tache(tache: NouvelleTache):
    with connexion_avec_table() as conn:
        return conn.execute(
            "INSERT INTO tasks (title) VALUES (%s) RETURNING id, title, done",
            (tache.title,),
        ).fetchone()