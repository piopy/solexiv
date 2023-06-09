from datetime import date, datetime
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

    df = pd.DataFrame(
        transazioni,
        columns=["data", "tipo", "importo", "categoria", "descrizione", "note"],
    )

    selected = st.multiselect("Categorie", categorie, default=categorie)
    descrizione = st.text_input(
        "Cerca descrizione",
        value="",
    )
    tipo = st.multiselect(
        "Tipologia di transazione", ["Entrata", "Uscita"], default=["Entrata", "Uscita"]
    )
    data_min = (
        df["data"].min()
        if df.shape[0] > 0
        else datetime.strftime(datetime.now(), "%Y-%m-%d")
    )
    datarange = st.date_input(
        "Cerca per data",
        value=(datetime.strptime(data_min, "%Y-%m-%d"), datetime.now()),
        max_value=datetime.now(),
        min_value=datetime.strptime(data_min, "%Y-%m-%d"),
    )
    st.write(f"Ultime {n_transazioni} transazioni:")
    dates = [datetime.strftime(d, "%Y-%m-%d") for d in datarange]
    if len(dates) != 2:
        dates.append(datetime.now().strftime("%Y-%m-%d"))
    st.table(
        df[
            df["categoria"].isin(selected)
            & df["descrizione"].str.upper().str.contains(descrizione.upper())
            & df["data"].ge(dates[0])
            & df["data"].le(dates[1])
            & df["tipo"].isin(tipo)
        ]
    )


mostra_ultime_transazioni()
