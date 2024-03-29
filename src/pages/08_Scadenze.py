from pathlib import Path
from time import sleep
import pandas as pd
import streamlit as st
from logica_applicativa.Scadenze import (
    aggiorna_stato_scadenza,
    aggiorna_stato_scadenza_mongo,
    elimina_scadenza,
    elimina_scadenza_mongo,
    genera_body_scadenza,
    get_scadenze,
    get_scadenze_mongo,
    inserisci_scadenza,
    inserisci_scadenza_mongo,
)
from streamlit_card import card


from utils.many_utils import check_active_session, logo_and_page_title


logo_and_page_title(st)
check_active_session(st, "Qui puoi aggiungere scadenze")


def mostra_pagina_scadenze():
    st.header("Aggiungi una nuova scadenza")
    nome = st.text_input("Nome")
    data_scadenza = st.date_input("Data di scadenza")
    dettagli = st.text_area("Dettagli")
    importo = st.number_input("Importo", min_value=0.0, step=0.01)
    stato = st.selectbox("Stato", ["Da fare", "Completata"])
    # frequenza = st.selectbox(
    #     "Frequenza",
    #     ["Nessuna frequenza", "Settimanale", "Mensile", "Annuale"],
    #     disabled=True,
    # )
    categoria = st.text_input("Categoria")
    # notifiche = st.checkbox("Abilita notifiche", disabled=True)

    #### Per ora questi parametri sono nascosti
    notifiche = False
    frequenza = "Nessuna frequenza"
    ####

    if st.button("Aggiungi scadenza"):
        if (
            nome == ""
            or categoria == ""
            or stato == ""
            or categoria == ""
            or data_scadenza == ""
        ):
            st.error("Tutti i campi, ad eccezione dei dettagli, sono obbligatori")
            st.stop()
        inserisci_scadenza_mongo(
            st,
            nome,
            data_scadenza,
            dettagli,
            importo,
            stato,
            categoria,
            frequenza,
            notifiche,
        )
        # st.success("Scadenza aggiunta con successo.")

    # # Scadenze
    scadenze = get_scadenze_mongo(st, st.session_state["mongo_uri"])
    scadenze_non_completate = scadenze[scadenze["completata"].lt(1)]
    # if scadenze.shape[0] > 0:

    #     for i, s in scadenze.iterrows():
    #         body = genera_body_scadenza(s)
    #         st.code(
    #             body,
    #             language="json",
    #         )

    #         st.markdown("---")
    st.markdown("---")
    with st.expander("Segna una scadenza come completata"):
        completate = st.multiselect(
            "Seleziona le scadenze completate",
            scadenze_non_completate.values.tolist(),
        )
        if st.button("Segna come completate"):
            if len(completate) > 0:
                for scadenza_id in completate:
                    aggiorna_stato_scadenza_mongo(st, scadenza_id[0])
                st.toast("Scadenze segnate come completate.")
                sleep(1)
                st.experimental_rerun()

    with st.expander("Elimina scadenze"):
        completate = st.multiselect(
            "Seleziona le scadenze da cancellare",
            scadenze.values.tolist(),
        )
        if st.button("Elimina"):
            if len(completate) > 0:
                for scadenza_id in completate:
                    elimina_scadenza_mongo(st, scadenza_id[0])
                st.toast("Scadenze eliminate.")
                sleep(1)
                st.experimental_rerun()


mostra_pagina_scadenze()
