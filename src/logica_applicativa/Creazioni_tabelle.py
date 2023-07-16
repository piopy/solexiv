from pathlib import Path
from pymongo import MongoClient, ASCENDING

import sqlite3

from utils.many_utils import PATH, collection_exists, get_collection

UTENTI_DB = Path(PATH, "utenti.db")


def crea_tabella_utenti():
    conn = sqlite3.connect(UTENTI_DB)
    c = conn.cursor()

    # Crea la tabella se non esiste già
    c.execute(
        """CREATE TABLE IF NOT EXISTS utenti
                (username TEXT PRIMARY KEY, password TEXT, mongo_uri TEXT)"""
    )
    conn.commit()
    conn.close()


def crea_tabella_utente(username):
    conn = sqlite3.connect(Path(PATH, f"utente_{username}.db"))
    c = conn.cursor()
    c.execute(
        """CREATE TABLE IF NOT EXISTS transazioni_utente (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    data TEXT,
                    descrizione TEXT,
                    tipo TEXT,
                    importo REAL,
                    categoria TEXT,
                    conto_corrente TEXT,
                    note TEXT)"""
    )
    conn.commit()
    conn.close()


def crea_tabella_scadenze(st):
    conn = sqlite3.connect(Path(PATH, f"utente_{st.session_state['user']}.db"))
    c = conn.cursor()

    c.execute(
        """CREATE TABLE IF NOT EXISTS scadenze (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            data_inserimento TEXT,
            data_scadenza TEXT,
            data_completamento TEXT,
            dettagli TEXT,
            importo REAL,
            categoria TEXT,
            frequenza TEXT,
            notifiche TEXT,
            completata INTEGER)"""
    )

    conn.commit()
    conn.close()


####### Mongo


def crea_tabella_utente_mongo(username, mongo_uri):
    if not collection_exists(username, "utente", mongo_uri):
        coll = get_collection(
            username,
            "utente",
            mongo_uri,
            mongo_db="solexiv_db",
        )
        coll.create_index([("id", ASCENDING)])  # , unique=True)


def crea_tabella_scadenze_mongo(st, mongo_uri):
    username = st.session_state["user"]
    if not collection_exists(username, "scadenze", mongo_uri):
        coll = get_collection(
            username,
            "scadenze",
            mongo_uri,
            mongo_db="solexiv_db",
        )
        coll.create_index([("id", ASCENDING)])  # , unique=True)
