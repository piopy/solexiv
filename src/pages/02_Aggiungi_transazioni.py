from pathlib import Path
import sqlite3
import streamlit as st
from logica_applicativa.Aggiungi_transazione import (
    aggiungi_transazione,
    aggiungi_transazione_mongo,
)

from utils.many_utils import (
    PATH,
    check_active_session,
    disable_form_border,
    logo_and_page_title,
    ottieni_conti_correnti,
    ottieni_conti_correnti_mongo,
)
from utils.vars import categorie
from logica_applicativa.Creazioni_tabelle import (
    crea_tabella_utente,
    crea_tabella_utente_mongo,
)


logo_and_page_title(st)
check_active_session(st, "Qui puoi aggiungere una transazione")
disable_form_border(st)


def mostra_pagina_aggiunta_entrate_uscite():
    st.title("Aggiunta Entrate/Uscite")
    st.markdown("")
    with st.form("aggiunta_transazioni"):
        col1, col2 = st.columns(2)
        with col1:
            crea_tabella_utente_mongo(
                st.session_state["user"], st.session_state["mongo_uri"]
            )

            conti_correnti = ottieni_conti_correnti_mongo(
                st.session_state["user"], st.session_state["mongo_uri"]
            )
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

            # if st.button("Aggiungi Transazione"):
            if st.form_submit_button("Aggiungi Transazione"):
                if (
                    conto_corrente_selezionato == ""
                    or categoria == ""
                    or tipo_transazione == ""
                    or descrizione == ""
                ):
                    st.error("Tutti i campi, ad eccezione delle note sono obbligatori")
                    st.stop()
                if conto_corrente_selezionato == "Altro":
                    conto_corrente = cc_rivisto
                else:
                    conto_corrente = conto_corrente_selezionato

                if aggiungi_transazione_mongo(
                    st,
                    data_transazione,
                    conto_corrente,
                    tipo_transazione,
                    descrizione,
                    importo,
                    categoria,
                    note,
                ):
                    st.toast("Transazione aggiunta con successo!")


################

mostra_pagina_aggiunta_entrate_uscite()
