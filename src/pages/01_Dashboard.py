import streamlit as st
from pathlib import Path
from datetime import datetime
from logica_applicativa.Creazioni_tabelle import crea_tabella_utente
from logica_applicativa.Dashboard import (
    andamento_patrimonio,
    entrate_uscite,
    ottieni_spese_per_mese,
    ottieni_spese_per_mese_descr,
    ottieni_spese_ultimi_12_mesi,
)
from utils.many_utils import (
    PATH,
    check_active_session,
    logo_and_page_title,
    risali_sei_mesi_prima,
)
import plotly.express as px
import pandas as pd
from utils.many_utils import ottieni_conti_correnti


logo_and_page_title(st)
check_active_session(st, "Ecco la tua dashboard")

DB = Path(PATH, f"utente_{st.session_state.user}.db")


# Pagina di resoconto mensile
def mostra_pagina_resoconto_mensile():
    st.title("Resoconto Mensile")

    crea_tabella_utente(st.session_state["user"])

    mese_corrente = datetime.now().month
    elenco_mesi = [
        "Gennaio",
        "Febbraio",
        "Marzo",
        "Aprile",
        "Maggio",
        "Giugno",
        "Luglio",
        "Agosto",
        "Settembre",
        "Ottobre",
        "Novembre",
        "Dicembre",
    ]

    mese_selezionato = st.selectbox(
        "Seleziona il mese", elenco_mesi, index=mese_corrente - 1
    )

    # Ottieni i conti correnti distinti
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
    e, u = entrate_uscite(
        DB,
        conto_corrente_selezionato,
        elenco_mesi.index(mese_selezionato) + 1,
    )
    st.write(
        "Entrate questo mese:",
        f"<span style='color:green'>{e[0]}€</span>",
        unsafe_allow_html=True,
    )
    st.write(
        "Uscite questo mese:",
        f"<span style='color:red'>{u[0]}€</span>",
        unsafe_allow_html=True,
    )

    # SPESE PER CATEGORIA
    scelta_dett = st.checkbox("Modalità dettagliata", value=False)
    if not scelta_dett:
        tupla_mese = ottieni_spese_per_mese(
            DB,
            conto_corrente_selezionato,
            elenco_mesi.index(mese_selezionato) + 1,
        )
        df_mese = pd.DataFrame(tupla_mese, index=["Data", "Tipologia", "Importo"]).T

        # Grafico a torta delle spese per categoria
        fig = px.pie(df_mese, values="Importo", names="Tipologia", hole=0.3)

        fig.update_traces(hoverinfo="label+percent", textfont_size=12)

        fig.update_layout(
            title=f"Distribuzione delle spese per categoria nel mese di {mese_selezionato} (Conto corrente: {conto_corrente_selezionato})",
            showlegend=True,
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        tupla_mese = ottieni_spese_per_mese_descr(
            DB,
            conto_corrente_selezionato,
            elenco_mesi.index(mese_selezionato) + 1,
        )
        df_mese_des = pd.DataFrame(
            tupla_mese, index=["Data", "Tipologia", "Descrizione", "Importo"]
        ).T
        fig = px.sunburst(
            data_frame=df_mese_des.fillna("null").assign(
                hole=f"Spese {mese_selezionato}"
            ),
            path=[
                "hole",
                "Tipologia",
                "Descrizione",
            ],
            values="Importo",
        )
        fig.update_traces(
            hovertemplate="<b> %{percentParent:.2%} </b> of %{parent}<br><i>%{value:.2f}€</i>",
        )
        fig.update_layout(
            autosize=False,
            height=650,
            margin=dict(l=0, r=0, t=20, b=20),
            hoverlabel_font_size=18,
        )
        st.plotly_chart(fig, use_container_width=True)

    # Ottieni i dati delle spese negli ultimi 12 mesi
    tupla_anno = ottieni_spese_ultimi_12_mesi(DB, conto_corrente_selezionato)
    df_anno = pd.DataFrame(tupla_anno, index=["Data", "Tipologia", "Importo"]).T

    # Grafico a barre delle spese per categoria
    fig = px.histogram(df_anno, x="Tipologia", y="Importo", color="Tipologia")

    fig.update_layout(
        title=f"Spese per categoria negli ultimi 12 mesi (Conto corrente: {conto_corrente_selezionato})",
        xaxis_title="Categoria",
        yaxis_title="Importo",
        showlegend=False,
        template="simple_white",
        hovermode="closest",
        hoverlabel=dict(bgcolor="white"),
    )
    fig.update_traces(
        hovertemplate="<br>".join(
            [
                "Tipologia: %{x}",
                "Quota spesa: %{y}€",
            ]
        ),
        marker_showscale=False,
        showlegend=False,
    )

    st.plotly_chart(fig, use_container_width=True)

    # Andamento patrimonio

    storico = andamento_patrimonio(DB, conto_corrente_selezionato)
    sto = storico[
        storico["data"].gt(
            risali_sei_mesi_prima(elenco_mesi.index(mese_selezionato) + 1)
        )
    ]
    sto["data"] = sto["data"].astype(str)
    fig = px.line(
        sto,
        x="data",
        y="patrimonio",
        # range_x=sto["data"].unique().tolist(),
        markers="bullet",
    )
    fig.update_layout(
        title=f"Andamento del patrimonio negli ultimi 12 mesi (Conto corrente: {conto_corrente_selezionato})",
        xaxis_title="Mesi",
        yaxis_title="Patrimonio",
        showlegend=False,
        template="simple_white",
        hovermode="closest",
        hoverlabel=dict(bgcolor="white"),
    )
    fig.update_traces(
        hovertemplate="<br>".join(
            [
                "Mese: %{x}",
                "Patrimonio: %{y}€",
            ]
        ),
        marker_showscale=False,
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)


#########################

mostra_pagina_resoconto_mensile()
