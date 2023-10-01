from datetime import date, datetime
import pandas as pd
import streamlit as st
from logica_applicativa.Ultime_transazioni import (
    download_excel,
    ottieni_ultime_transazioni,
    ottieni_ultime_transazioni_mongo,
)

from utils.many_utils import (
    check_active_session,
    disable_form_border,
    logo_and_page_title,
    ottieni_conti_correnti,
    ottieni_conti_correnti_mongo,
)
from utils.vars import categorie

logo_and_page_title(st)
check_active_session(st, "Ecco le tue ultime transazioni")
disable_form_border(st)


def mostra_ultime_transazioni():
    try:
        conti_correnti = ottieni_conti_correnti_mongo(
            st.session_state["user"], st.session_state["mongo_uri"]
        )
    except:
        conti_correnti = ["Nessun conto corrente rilevato"]
    conto_corrente_selezionato = st.selectbox(
        "Seleziona il conto corrente", conti_correnti
    )
    with st.form("ultime_transazioni"):
        n_transazioni = st.text_input("Transazioni visualizzate _(0 = tutte)_", value=0)
        transazioni = ottieni_ultime_transazioni_mongo(
            st,
            conto_corrente_selezionato,
            st.session_state["mongo_uri"],
            n_transazioni=n_transazioni,
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
            "Tipologia di transazione",
            ["Entrata", "Uscita"],
            default=["Entrata", "Uscita"],
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
        if n_transazioni != "0":
            st.write(f"Ultime {n_transazioni} transazioni:")
        else:
            st.write(f"Ultime transazioni:")

        dates = [datetime.strftime(d, "%Y-%m-%d") for d in datarange]
        if len(dates) != 2:
            dates.append(datetime.now().strftime("%Y-%m-%d"))
        out_df = (
            df[
                df["categoria"].isin(selected)
                & df["descrizione"]
                .fillna("")
                .str.upper()
                .str.contains(descrizione.upper())
                & df["data"].ge(dates[0])
                & df["data"].le(dates[1])
                & df["tipo"].isin(tipo)
            ]
            .fillna("")
            .style.format(subset=["importo"], formatter="{:.2f}")
        )
        if st.form_submit_button("Visualizza"):
            st.table(out_df)
    st.write("")
    st.write("")
    st.download_button(
        label="Scarica tabella (EXCEL)",
        data=download_excel(
            df=out_df,
            name=f"{conto_corrente_selezionato[0:9]}-{dates[0]}{dates[1]}",
        ),
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        file_name=f"Resoconto_{conto_corrente_selezionato}_{dates[0]}_{dates[1]}.xlsx",
    )


mostra_ultime_transazioni()
