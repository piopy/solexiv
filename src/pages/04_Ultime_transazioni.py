import pandas as pd
import streamlit as st
from logica_applicativa.Ultime_transazioni import ottieni_ultime_transazioni

from utils.many_utils import (
    check_active_session,
    logo_and_page_title,
    ottieni_conti_correnti,
)
from utils.vars import categorie

logo_and_page_title(st)
check_active_session(st, "Ecco le tue ultime transazioni")


def mostra_ultime_transazioni():
    try:
        conti_correnti = ottieni_conti_correnti(st.session_state["user"])
    except:
        conti_correnti = ["Nessun conto corrente rilevato"]
    conto_corrente_selezionato = st.selectbox(
        "Seleziona il conto corrente", conti_correnti
    )
    n_transazioni = st.text_input("Transazioni visualizzate", value=20)
    transazioni = ottieni_ultime_transazioni(
        st, conto_corrente_selezionato, n_transazioni
    )
    selected = st.multiselect("Categorie", categorie, default=categorie)
    descrizione = st.text_input("Cerca descrizione", value="")
    st.write(f"Ultime {n_transazioni} transazioni:")
    df = pd.DataFrame(
        transazioni,
        columns=["data", "tipo", "importo", "categoria", "descrizione", "note"],
    )
    st.table(
        df[df["categoria"].isin(selected) & df["descrizione"].str.contains(descrizione)]
    )


mostra_ultime_transazioni()
