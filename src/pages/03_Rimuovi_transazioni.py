import streamlit as st
from logica_applicativa.Rimuovi_transazioni import (
    rimuovi_transazioni,
    select_all_transazioni,
)

from utils.many_utils import (
    check_active_session,
    logo_and_page_title,
    ottieni_conti_correnti,
)


logo_and_page_title(st)
check_active_session(st, "Qui puoi rimuovere una transazione")


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

    transazioni = select_all_transazioni(st, conto_corrente_selezionato)

    transazioni_selezionate = st.multiselect(
        "Seleziona le transazioni da rimuovere", transazioni
    )

    if st.button("Rimuovi Transazioni"):
        if transazioni_selezionate:
            rimuovi_transazioni(st, transazioni_selezionate, conto_corrente_selezionato)
            st.success("Transazioni rimosse con successo!")
        else:
            st.error("Seleziona almeno una transazione da rimuovere")


rm_transazioni()
