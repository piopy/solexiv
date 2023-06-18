import sqlite3

import bcrypt
from utils.many_utils import PATH
from pathlib import Path

from utils.session_utils import salva_sessione_attiva

UTENTI_DB = Path(PATH, "utenti.db")


def session_start(st, username, hash_pw, persistenza):
    st.session_state["user"] = username
    st.session_state["password"] = hash_pw
    if Path(PATH, f"utente_{username}.db_").exists():
        st.session_state["encrypted"] = True
    else:
        st.session_state["encrypted"] = False
    if persistenza:
        salva_sessione_attiva(st)


def autenticazione(st, username, password, persistenza):
    global HASH
    conn = sqlite3.connect(UTENTI_DB)
    c = conn.cursor()
    c.execute("SELECT password FROM utenti WHERE username=?", (username,))
    result = c.fetchone()
    conn.close()
    if result:
        hashed_password = result[0]
        if bcrypt.checkpw(password.encode("utf-8"), hashed_password):
            session_start(st, username, hashed_password.decode("utf-8"), persistenza)
            return True
    return False


def crea_utente(st, username, password):
    conn = sqlite3.connect(UTENTI_DB)
    c = conn.cursor()
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    try:
        c.execute(
            "INSERT INTO utenti (username, password) VALUES (?, ?)",
            (username, hashed_password),
        )
    except sqlite3.IntegrityError:
        st.error("Utente esistente")
        return False
    except Exception as e:
        st.error(e)
        return False
    conn.commit()
    conn.close()
    return True
