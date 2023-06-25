from pathlib import Path
import sqlite3
import streamlit as st

from utils.many_utils import (
    PATH,
    check_active_session,
    logo_and_page_title,
    ottieni_conti_correnti,
)
from utils.vars import categorie
from logica_applicativa.Creazioni_tabelle import crea_tabella_utente


logo_and_page_title(st)
check_active_session(st, "Qui puoi aggiungere una transazione")


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
