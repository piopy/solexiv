import base64
import hashlib
import sqlite3

import bcrypt
from cryptography.fernet import Fernet
from utils.many_utils import PATH
from pathlib import Path

from utils.session_utils import salva_sessione_attiva

UTENTI_DB = Path(PATH, "utenti.db")


def session_start(st, username, hash_pw, persistenza, mongo_uri):
    st.session_state["user"] = username
    st.session_state["password"] = hash_pw
    st.session_state["mongo_uri"] = mongo_uri
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
    c.execute("SELECT mongo_uri FROM utenti WHERE username=?", (username,))
    mongo_uri = c.fetchone()[0]
    # # # st.write(result, mongo_uri)  # debug only
    st.stop()
    conn.close()
    if result:
        hashed_password = result[0]
        if bcrypt.checkpw(password.encode("utf-8"), hashed_password):
            mongo_uri = decrittografa_stringa(password, mongo_uri)
            session_start(
                st, username, hashed_password.decode("utf-8"), persistenza, mongo_uri
            )
            return True
    return False


############### Update


def gen_fernet_key(passcode: bytes) -> bytes:
    assert isinstance(passcode, bytes)
    hlib = hashlib.md5()
    hlib.update(passcode)
    return base64.urlsafe_b64encode(hlib.hexdigest().encode("latin-1"))


def crittografa_stringa(chiave, stringa):
    chiave = gen_fernet_key(chiave.encode("utf-8"))
    dati = stringa.encode("utf-8")
    fernet = Fernet(chiave)
    dati_crittografati = fernet.encrypt(dati)
    return dati_crittografati.decode("utf-8")


def decrittografa_stringa(chiave, stringa):
    chiave = gen_fernet_key(chiave.encode("utf-8"))
    dati_crittografati = stringa.encode("utf-8")
    fernet = Fernet(chiave)
    dati_decrittografati = fernet.decrypt(dati_crittografati)
    return dati_decrittografati.decode("utf-8")


def crea_utente(st, username, password, mongo_uri):
    conn = sqlite3.connect(UTENTI_DB)
    # TODO registrazione e login con mongo uri crittografato
    c = conn.cursor()
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    mongo_uri = crittografa_stringa(password, mongo_uri)
    try:
        c.execute(
            "INSERT INTO utenti (username, password, mongo_uri) VALUES (?, ?, ?)",
            (username, hashed_password, mongo_uri),
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
