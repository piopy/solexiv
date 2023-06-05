import os
from pathlib import Path
import sqlite3
import pandas as pd
import streamlit as st
import json

from utils.many_utils import PATH, crea_tabella_utente, ottieni_conti_correnti

from PIL import Image

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

if st.session_state.user:
    if st.session_state.encrypted:
        st.error(
            "Il tuo archivio è crittografato, sbloccalo nella pagina di sicurezza."
        )
        st.stop()
    st.title(f"Ciao, {st.session_state.user.title()}")
    st.markdown(f"### Ecco le tue ultime transazioni")
else:
    st.error("Non sei autenticato, torna alla pagina di login")
    st.stop()


def ottieni_ultime_transazioni(conto_corrente):
    # Connessione al database
    conn = sqlite3.connect(Path(PATH, "utente_" + st.session_state["user"] + ".db"))
    c = conn.cursor()

    # Esecuzione della query per ottenere le ultime 20 transazioni del conto corrente
    c.execute(
        f"""
    SELECT data as data ,tipo , printf("%.2f", importo) ,categoria , descrizione, note
    FROM transazioni_utente 
    WHERE conto_corrente=? ORDER BY data DESC 
    LIMIT 20""",
        (conto_corrente,),
    )
    transazioni = c.fetchall()

    # Chiusura della connessione al database
    conn.close()

    return transazioni


def mostra_ultime_transazioni():
    try:
        conti_correnti = ottieni_conti_correnti(st.session_state["user"])
    except:
        conti_correnti = ["Nessun conto corrente rilevato"]
    conto_corrente_selezionato = st.selectbox(
        "Seleziona il conto corrente", conti_correnti
    )
    # Seleziona le ultime 20 transazioni del conto corrente selezionato
    transazioni = ottieni_ultime_transazioni(conto_corrente_selezionato)

    # Mostra le transazioni in una tabella
    st.write("Ultime 20 transazioni:")
    st.table(
        pd.DataFrame(
            transazioni,
            columns=["data", "tipo", "descrizione", "importo", "categoria", "note"],
        )
    )


# Chiamata alla funzione per mostrare le ultime transazioni
mostra_ultime_transazioni()
