import sqlite3
from pathlib import Path
from datetime import datetime
import os

PATH = "../data/"


def cancella_account(user):
    conn = sqlite3.connect(Path(PATH, f"utenti.db"))
    c = conn.cursor()
    c.execute("DELETE FROM utenti WHERE username = ?", (user,))
    conn.commit()
    conn.close()
    os.remove(Path(PATH, f"utente_{user}.db"))


def db_isempty(user):
    conn = sqlite3.connect(Path(PATH, f"utente_{user}.db"))
    c = conn.cursor()
    res = c.execute("""SELECT * FROM transazioni_utente""").fetchall()
    if len(res) == 0:
        return True
    return False


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


def ottieni_conti_correnti(username):
    conn = sqlite3.connect(Path(PATH, f"utente_{username}.db"))
    c = conn.cursor()
    c.execute(f"SELECT DISTINCT conto_corrente FROM transazioni_utente")
    results = c.fetchall()
    conn.close()

    conti_correnti = [row[0] for row in results]
    return conti_correnti


def risali_sei_mesi_prima(mese):
    data_corrente = datetime.now()
    anno_corrente = data_corrente.year

    anno_sei_mesi_prima = anno_corrente
    mese_sei_mesi_prima = mese - 6

    if mese_sei_mesi_prima <= 0:
        # Sottrai l'anno e il mese necessari per ottenere sei mesi prima
        anno_sei_mesi_prima -= 1
        mese_sei_mesi_prima += 12

    # Formatta l'anno e il mese come stringa "YYYY-MM"
    mese_sei_mesi_prima_str = f"{anno_sei_mesi_prima:04d}-{mese_sei_mesi_prima:02d}"

    return mese_sei_mesi_prima_str
