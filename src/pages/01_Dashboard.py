import json
import os
import streamlit as st
import sqlite3
from pathlib import Path
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils.many_utils import PATH, risali_sei_mesi_prima
import plotly.express as px
import pandas as pd
from utils.many_utils import crea_tabella_utente, ottieni_conti_correnti

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
    st.markdown(f"### Ecco la tua dashboard")
else:
    st.error("Non sei autenticato, torna alla pagina di login")
    st.stop()

DB = Path(PATH, f"utente_{st.session_state.user}.db")


# Funzione per ottenere i dati delle spese negli ultimi 12 mesi divisi per categoria
def ottieni_spese_ultimi_12_mesi(username, conto_corrente):
    today = datetime.now()
    data_inizio = today - timedelta(days=365)
    data_inizio = data_inizio.strftime("%Y-%m-%d")

    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute(
        """SELECT strftime('%Y-%m', data), categoria, SUM(importo)
                    FROM transazioni_utente
                    WHERE data >= ? AND conto_corrente = ? AND data <= ? AND tipo = 'Uscita'
                    GROUP BY strftime('%Y-%m', data), categoria
                    ORDER BY strftime('%Y-%m', data) DESC""",
        (data_inizio, conto_corrente, datetime.now().strftime("%Y-%m-%d")),
    )
    results = c.fetchall()
    conn.close()

    mesi = []
    categorie = []
    importi = []
    diz = {}

    for row in results:
        mese = row[0]
        categoria = row[1]
        importo = row[2]

        mesi.append(mese)
        categorie.append(categoria)
        importi.append(importo)

    return mesi, categorie, importi


def andamento_patrimonio(username, conto_corrente):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute(
        """SELECT strftime('%Y-%m', data), categoria, SUM(importo), tipo
                    FROM transazioni_utente
                    WHERE conto_corrente = ? AND data <= ? 
                    GROUP BY strftime('%Y-%m', data), tipo
                    ORDER BY strftime('%Y-%m', data) DESC""",
        (conto_corrente, datetime.now().strftime("%Y-%m-%d")),
    )
    results = c.fetchall()
    conn.close()
    storico = (
        pd.DataFrame(results, columns=["data", "categoria", "importo", "tipo"])
        .groupby(["data", "tipo"])
        .agg(euri=("importo", "sum"))
        .reset_index()
    )
    storico.loc[storico["tipo"] == "Uscita", "euri"] *= -1
    storico["patrimonio"] = storico["euri"].cumsum()
    storico = storico.drop_duplicates(subset=["data"], keep="last").drop(
        columns=["tipo", "euri"]
    )
    return storico


# Funzione per ottenere i dati delle spese per un mese specifico
def ottieni_spese_per_mese(username, conto_corrente, mese_selezionato):
    # Converte il mese selezionato nel formato "YYYY-MM"
    if len(str(mese_selezionato)) == 1:
        mese_selezionato = "0" + str(mese_selezionato)
    mese_formato = f"{datetime.now().year}-{mese_selezionato}"

    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute(
        """SELECT data, categoria, SUM(importo)
                    FROM transazioni_utente
                    WHERE strftime('%Y-%m', data) = ? AND conto_corrente = ? AND tipo = 'Uscita'
                    GROUP BY data, categoria""",
        (mese_formato, conto_corrente),
    )
    results = c.fetchall()
    conn.close()

    giorni = []
    categorie = []
    importi = []

    for row in results:
        giorno = row[0]
        categoria = row[1]
        importo = row[2]

        giorni.append(giorno)
        categorie.append(categoria)
        importi.append(importo)

    return giorni, categorie, importi


def entrate_uscite(username, conto_corrente, mese_selezionato):
    # Converte il mese selezionato nel formato "YYYY-MM"
    if len(str(mese_selezionato)) == 1:
        mese_selezionato = "0" + str(mese_selezionato)
    mese_formato = f"{datetime.now().year}-{mese_selezionato}"

    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute(
        """SELECT SUM(importo)
                    FROM transazioni_utente
                    WHERE strftime('%Y-%m', data) = ? AND conto_corrente = ? AND tipo = 'Uscita'
                    """,
        (mese_formato, conto_corrente),
    )
    results = c.fetchall()
    if results.__len__() == 0:
        results.append("0")
    if results[0] == (None,):
        results[0] = "0"
    uscite = results[0]

    c.execute(
        """SELECT SUM(importo)
                    FROM transazioni_utente
                    WHERE strftime('%Y-%m', data) = ? AND conto_corrente = ? AND tipo = 'Entrata'
                    """,
        (mese_formato, conto_corrente),
    )
    results = c.fetchall()
    if results.__len__() == 0:
        results.append("0")
    if results[0] == (None,):
        results[0] = "0"
    entr = results[0]

    conn.close()

    return entr, uscite


# Pagina di resoconto mensile
def mostra_pagina_resoconto_mensile():
    st.title("Resoconto Mensile")

    # Controllo che la tabella transazioni_utente sia creata
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
    # Selezione del mese

    mese_selezionato = st.selectbox(
        "Seleziona il mese", elenco_mesi, index=mese_corrente - 1
    )

    # Selezione del conto corrente
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
        st.session_state["user"],
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

    tupla_mese = ottieni_spese_per_mese(
        st.session_state["user"],
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

    # Ottieni i dati delle spese negli ultimi 12 mesi
    tupla_anno = ottieni_spese_ultimi_12_mesi(
        st.session_state["user"], conto_corrente_selezionato
    )
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

    storico = andamento_patrimonio(st.session_state["user"], conto_corrente_selezionato)
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
