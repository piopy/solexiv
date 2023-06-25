import json
import os
import base64, hashlib

from pathlib import Path
from cryptography.fernet import Fernet

from utils.many_utils import PATH


def check_active_session_proteggi_db(st):
    if os.path.exists(Path(PATH, "_active_session")):
        with open(Path(PATH, "_active_session"), "r") as f:
            dizi = json.load(f)
            st.session_state["user"] = dizi["username"]
            st.session_state["password"] = dizi["hash_pw"]
            st.session_state["encrypted"] = dizi["encrypted"]

    if st.session_state.user:
        st.title(f"Ciao, {st.session_state.user.title()}")
        if st.session_state["encrypted"] == False:
            st.markdown(f"### Proteggi qui il tuo database")
        else:
            st.markdown(f"### Sblocca qui il tuo database")
    else:
        st.error("Non sei autenticato, torna alla pagina di login")
        st.stop()


def gen_fernet_key(passcode: bytes) -> bytes:
    assert isinstance(passcode, bytes)
    hlib = hashlib.md5()
    hlib.update(passcode)
    return base64.urlsafe_b64encode(hlib.hexdigest().encode("latin-1"))


def crittografa_database(chiave, nome_database):
    with open(nome_database, "rb") as file:
        dati = file.read()
    fernet = Fernet(chiave)
    dati_crittografati = fernet.encrypt(dati)
    with open(nome_database + "_", "wb") as file:
        file.write(dati_crittografati)


def decrittografa_database(chiave, nome_database):
    with open(nome_database + "_", "rb") as file:
        dati_crittografati = file.read()
    fernet = Fernet(chiave)
    dati_decrittografati = fernet.decrypt(dati_crittografati)
    with open(nome_database, "wb") as file:
        file.write(dati_decrittografati)


def modifica_session_encrypted(st, encrypted):
    if os.path.exists(Path(PATH, "_active_session")):
        with open(Path(PATH, "_active_session"), "r") as f:
            dizi = json.load(f)
            st.session_state["user"] = dizi["username"]
            st.session_state["password"] = dizi["hash_pw"]

        st.session_state["encrypted"] = encrypted
        with open(Path(PATH, "_active_session"), "w") as f:
            dizi = {
                "username": st.session_state["user"],
                "hash_pw": st.session_state["password"],
                "encrypted": st.session_state["encrypted"],
            }
            f.write(json.dumps(dizi))
