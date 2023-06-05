import base64
import os
import streamlit as st
import sqlite3
from cryptography.fernet import Fernet
from pathlib import Path
import base64, hashlib
import json
from utils.many_utils import PATH

from PIL import Image

from utils.session_utils import modifica_session_encrypted

im = Image.open(Path(PATH, "favicon.ico"))
st.set_page_config(
    page_title="SOLEXIV",
    page_icon=im,
    layout="wide",
)

hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

if os.path.exists(Path(PATH, "_active_session")):
    with open(Path(PATH, "_active_session"), "r") as f:
        dizi = json.load(f)
        st.session_state["user"] = dizi["username"]
        st.session_state["password"] = dizi["hash_pw"]
        st.session_state["encrypted"] = dizi["encrypted"]


def gen_fernet_key(passcode: bytes) -> bytes:
    assert isinstance(passcode, bytes)
    hlib = hashlib.md5()
    hlib.update(passcode)
    return base64.urlsafe_b64encode(hlib.hexdigest().encode("latin-1"))


if st.session_state.user:
    st.title(f"Ciao, {st.session_state.user.title()}")
    if st.session_state["encrypted"] == False:
        st.markdown(f"### Proteggi qui il tuo database")
    else:
        st.markdown(f"### Sblocca qui il tuo database")
else:
    st.error("Non sei autenticato, torna alla pagina di login")
    st.stop()

DB = Path(PATH, f"utente_{st.session_state.user}.db")


# Funzione per crittografare il database
def crittografa_database(chiave, nome_database):
    with open(nome_database, "rb") as file:
        dati = file.read()
    fernet = Fernet(chiave)
    dati_crittografati = fernet.encrypt(dati)
    with open(nome_database + "_", "wb") as file:
        file.write(dati_crittografati)


# Funzione per decrittografare il database
def decrittografa_database(chiave, nome_database):
    with open(nome_database + "_", "rb") as file:
        dati_crittografati = file.read()
    fernet = Fernet(chiave)
    dati_decrittografati = fernet.decrypt(dati_crittografati)
    with open(nome_database, "wb") as file:
        file.write(dati_decrittografati)


# Ottieni la password dall'utente
password = st.session_state["password"]
if st.session_state["encrypted"] == False:
    if st.button("Crittografa database"):
        # Genera la chiave di crittografia utilizzando la password
        chiave = gen_fernet_key(password.encode("utf-8"))

        # Crittografa il database
        crittografa_database(chiave, str(DB))
        st.success("Il database è stato crittografato con successo!")
        st.session_state["encrypted"] = True
        os.remove(DB)
        modifica_session_encrypted(st, True)
        st.experimental_rerun()
else:
    if st.button("Decrittografa database"):
        # Genera la chiave di crittografia utilizzando la password
        chiave = gen_fernet_key(password.encode("utf-8"))

        # Decrittografa il database
        decrittografa_database(chiave, str(DB))
        st.success("Il database è stato decrittografato con successo!")
        st.session_state["encrypted"] = False
        modifica_session_encrypted(st, False)

        os.remove(str(DB) + "_")

        st.experimental_rerun()
