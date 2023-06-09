import json
import sqlite3
from pathlib import Path
from datetime import datetime
from PIL import Image
import os

PATH = "../data/"


def logo_and_page_title(st):
    try:
        im = Image.open(Path(PATH, "favicon.ico"))
        st.set_page_config(
            page_title="SOLEXIV",
            page_icon=im,
            layout="wide",
        )
    except:
        st.set_page_config(
            page_title="SOLEXIV",
            layout="wide",
        )

    hide_streamlit_style = """
                <style>
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                </style>
                """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)


def check_active_session(st, title):
    if os.path.exists(Path(PATH, "_active_session")):
        with open(Path(PATH, "_active_session"), "r") as f:
            dizi = json.load(f)
            st.session_state["user"] = dizi["username"]
            st.session_state["password"] = dizi["hash_pw"]
            st.session_state["encrypted"] = dizi["encrypted"]

    if st.session_state.user:
        if st.session_state.encrypted:
            st.error(
                "Il tuo archivio è crittografato, sbloccalo nella pagina di sicurezza."
            )
            st.stop()
        st.title(f"Ciao, {st.session_state.user.title()}")
        st.markdown(f"### {title}")
    else:
        st.error("Non sei autenticato, torna alla pagina di login")
        st.stop()


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
