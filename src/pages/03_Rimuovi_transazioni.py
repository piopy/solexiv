import json
import os
from pathlib import Path
import streamlit as st
import sqlite3

from utils.many_utils import PATH, ottieni_conti_correnti

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
    st.markdown(f"### Qui puoi aggiungere una transazione")
else:
    st.error("Non sei autenticato, torna alla pagina di login")
    st.stop()


def rimuovi_transazioni(transazioni_selezionate, conto_corrente_selezionato):
    conn = sqlite3.connect(Path(PATH, f"utente_{st.session_state['user']}.db"))
    cursor = conn.cursor()

    for id_transazione in transazioni_selezionate:
        cursor.execute(
            "DELETE FROM transazioni_utente WHERE id = ? AND conto_corrente = ?",
            (id_transazione[0], conto_corrente_selezionato),
        )
    conn.commit()

    conn.close()


def rm_transazioni():
    st.title("Rimozione Transazioni")

    try:
        conti_correnti = ottieni_conti_correnti(st.session_state["user"])
    except:
        conti_correnti = ["Nessun conto corrente rilevato"]
        st.stop()

    conto_corrente_selezionato = st.selectbox(
        "Seleziona il conto corrente", conti_correnti
    )

    if conto_corrente_selezionato == None:
        st.stop()
    conn = sqlite3.connect(Path(PATH, f"utente_{st.session_state['user']}.db"))
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM transazioni_utente WHERE conto_corrente = ?",
        (conto_corrente_selezionato,),
    )
    transazioni = cursor.fetchall()
    conn.close()

    transazioni_selezionate = st.multiselect(
        "Seleziona le transazioni da rimuovere", transazioni
    )

    if st.button("Rimuovi Transazioni"):
        if transazioni_selezionate:
            rimuovi_transazioni(transazioni_selezionate, conto_corrente_selezionato)
            st.success("Transazioni rimosse con successo!")
        else:
            st.error("Seleziona almeno una transazione da rimuovere")


rm_transazioni()
