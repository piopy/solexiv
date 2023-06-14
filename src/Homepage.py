import os
from time import sleep
import streamlit as st
import sqlite3
import bcrypt
from pathlib import Path
from PIL import Image
from utils.many_utils import crea_tabella_utente, cancella_account
from utils.many_utils import PATH
from utils.session_utils import (
    recupera_sessione_attiva,
    rimuovi_sessione_attiva,
    salva_sessione_attiva,
)

UTENTI_DB = Path(PATH, "utenti.db")


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


def session_start(username, hash_pw, persistenza):
    st.session_state["user"] = username
    st.session_state["password"] = hash_pw
    if Path(PATH, f"utente_{username}.db_").exists():
        st.session_state["encrypted"] = True
    else:
        st.session_state["encrypted"] = False
    if persistenza:
        salva_sessione_attiva(st)


# Funzione per autenticare l'utente
def autenticazione(username, password, persistenza):
    global HASH
    conn = sqlite3.connect(UTENTI_DB)
    c = conn.cursor()
    c.execute("SELECT password FROM utenti WHERE username=?", (username,))
    result = c.fetchone()
    conn.close()
    if result:
        hashed_password = result[0]
        if bcrypt.checkpw(password.encode("utf-8"), hashed_password):
            session_start(username, hashed_password.decode("utf-8"), persistenza)
            return True
    return False


# Funzione per creare un nuovo utente nel database
def crea_utente(username, password):
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


def crea_tabella_utenti():
    conn = sqlite3.connect(UTENTI_DB)
    c = conn.cursor()

    # Crea la tabella se non esiste già
    c.execute(
        """CREATE TABLE IF NOT EXISTS utenti
                (username TEXT PRIMARY KEY, password TEXT)"""
    )
    conn.commit()
    conn.close()


# Pagina di accesso e registrazione
def login():
    try:
        temp = st.session_state["user"]
    except:
        st.session_state["user"] = None
    if os.path.exists(Path(PATH, "_active_session")):
        recupera_sessione_attiva(st)

    if st.session_state["user"]:
        st.title(f"Ciao, {st.session_state.user.title()}!")
        st.success("<- Ora puoi navigare tra le pagine")
        crea_tabella_utente(st.session_state["user"])
        if st.button("Logout"):
            st.session_state["user"] = None
            st.session_state["password"] = None
            st.success("Hai effettuato il logout")
            rimuovi_sessione_attiva(st)
            st.experimental_rerun()
        if st.button(
            "Cancella account - Attenzione! Verrà eliminato anche il database!"
        ):
            cancella_account(st.session_state["user"])
            st.session_state["user"] = None
            st.session_state["password"] = None
            rimuovi_sessione_attiva(st)
            st.image(
                "https://media.giphy.com/media/o0eOCNkn7cSD6/giphy.gif",
                use_column_width=False,
            )
            st.success(
                "Hai eliminato l'account. Verrai rispedito alla pagina di login a breve."
            )
            sleep(4)
            st.experimental_rerun()

        st.image(
            "https://media.giphy.com/media/Zhpvn5KvGEvJu/giphy.gif",
            use_column_width=True,
        )

        st.stop()

    crea_tabella_utenti()

    st.title("ACCESSO")
    username = st.text_input("Nome utente")
    password = st.text_input("Password", type="password")
    if os.getenv("SAFEBOX", 0) == 0:
        persistenza = st.checkbox("Ricordami")

    # Controllo dell'autenticazione
    if st.button("Accedi"):
        # Input del nome utente
        if autenticazione(username, password, persistenza):
            st.success("Accesso effettuato con successo.")
            st.experimental_rerun()
        else:
            st.error("Nome utente o password non validi.")

    st.title("Registrazione")

    new_username = st.text_input("Nuovo nome utente")
    new_password = st.text_input("Nuova password", type="password")

    if st.button("Registra"):
        esito = crea_utente(new_username, new_password)
        if esito:
            st.success(
                "Registrazione effettuata con successo. Ora puoi effettuare l'accesso."
            )
            st.balloons()


# Esegui la funzione login per visualizzare la pagina di accesso e registrazione

login()
