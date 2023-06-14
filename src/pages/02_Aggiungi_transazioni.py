import json
import os
from pathlib import Path
import sqlite3
import streamlit as st

from utils.many_utils import PATH, crea_tabella_utente, ottieni_conti_correnti
from utils.vars import categorie

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


def mostra_pagina_aggiunta_entrate_uscite():
    st.title("Aggiunta Entrate/Uscite")

    col1, col2 = st.columns(2)
    with col1:
        crea_tabella_utente(st.session_state["user"])

        conti_correnti = ottieni_conti_correnti(st.session_state["user"])
        conti_correnti.append("Altro")
        conto_corrente_selezionato = st.selectbox(
            "Seleziona il conto corrente", conti_correnti
        )
        if conto_corrente_selezionato == "Altro":
            cc_rivisto = st.text_input("Inserire conto corrente")

        tipo_transazione = st.selectbox(
            "Seleziona il tipo di transazione", ["Entrata", "Uscita"]
        )

        data_transazione = st.date_input("Data della transazione")
        descrizione = st.text_input("Descrizione")

    with col2:
        ## PAGINA 2
        importo = st.number_input("Importo", min_value=0.01)

        # Selezione della categoria
        # categorie = [
        #     "Affitto",
        #     "Bolletta",
        #     "Alimentari",
        #     "Abbigliamento",
        #     "Uscite Serali/Svago",
        #     "Regalo",
        #     "Altro",
        # ]
        categoria = st.selectbox("Seleziona la categoria", categorie)

        note = st.text_area("Inserire nota")

        if st.button("Aggiungi Transazione"):
            if conto_corrente_selezionato == "Altro":
                conto_corrente = cc_rivisto
            else:
                conto_corrente = conto_corrente_selezionato

            conn = sqlite3.connect(Path(PATH, f"utente_{st.session_state['user']}.db"))
            c = conn.cursor()
            c.execute(
                """INSERT INTO transazioni_utente (data, conto_corrente, tipo, descrizione, importo, categoria, note) 
            VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    data_transazione,
                    conto_corrente,
                    tipo_transazione,
                    descrizione,
                    importo,
                    categoria,
                    note,
                ),
            )
            conn.commit()
            conn.close()

            st.success("Transazione aggiunta con successo!")


################

mostra_pagina_aggiunta_entrate_uscite()
