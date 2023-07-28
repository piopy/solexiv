import streamlit as st
from logica_applicativa.Rimuovi_transazioni import (
    # rimuovi_transazioni,
    rimuovi_transazioni_mongo,
    # select_all_transazioni,
    select_all_transazioni_mongo,
)

from utils.many_utils import (
    check_active_session,
    logo_and_page_title,
    # ottieni_conti_correnti,
    ottieni_conti_correnti_mongo,
)


logo_and_page_title(st)
check_active_session(st, "Qui puoi rimuovere una transazione")


def rm_transazioni():
    st.title("Rimozione Transazioni")

    try:
        conti_correnti = ottieni_conti_correnti_mongo(
            st.session_state["user"], st.session_state["mongo_uri"]
        )
    except:
        conti_correnti = ["Nessun conto corrente rilevato"]
        st.stop()

    conto_corrente_selezionato = st.selectbox(
        "Seleziona il conto corrente", conti_correnti
    )

    if conto_corrente_selezionato == None:
        st.stop()

    transazioni = select_all_transazioni_mongo(st, conto_corrente_selezionato)

    transazioni_selezionate = st.multiselect(
        "Seleziona le transazioni da rimuovere",
        transazioni,
    )
    lista = transazioni_selezionate
    if st.button("Rimuovi Transazioni"):
        if lista:
            if rimuovi_transazioni_mongo(st, lista, conto_corrente_selezionato):
                st.toast("Transazioni rimosse con successo!")
        else:
            st.error("Seleziona almeno una transazione da rimuovere")


rm_transazioni()
