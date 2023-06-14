import json
import os
from pathlib import Path
import sqlite3
import streamlit as st
import pandas as pd

from utils.many_utils import PATH

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
    st.markdown(f"### Qui puoi aggiungere transazioni a partire da un template")
else:
    st.error("Non sei autenticato, torna alla pagina di login")
    st.stop()


def injection(file):
    df = (
        pd.read_excel(file, sheet_name="Template")
        .dropna(subset=["Data", "Tipo", "Importo", "Categoria", "Conto corrente"])
        .fillna("")
    )
    conn = sqlite3.connect(Path(PATH, "utente_" + st.session_state["user"] + ".db"))
    c = conn.cursor()

    for _, row in df.iterrows():
        c.execute(
            """INSERT INTO transazioni_utente 
            (data, descrizione, tipo, importo, categoria, conto_corrente, note) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(row["Data"]),
                row["Descrizione"],
                row["Tipo"],
                row["Importo"],
                row["Categoria"],
                row["Conto corrente"],
                row["Note"],
            ),
        )
    conn.commit()
    conn.close()


def aggiungi_da_template():
    st.markdown("### Template:")
    try:
        with open(Path("..", "data", "Template.xlsx"), "rb") as file:
            data = file.read()
        if st.download_button(
            "Scarica il template", data=data, file_name="Template.xlsx"
        ):
            st.success("Template scaricato")
    except:
        st.error("Template non disponibile")
    st.write("Una volta compilato, carica qui il template")
    template_file = st.file_uploader(
        "Carica il template", type=["xlsx"], accept_multiple_files=False
    )
    if template_file is not None:
        if st.button("Inserisci le transazioni"):
            try:
                injection(template_file.getvalue())
                st.success("Transazioni aggiunte con successo")
            except:
                st.error("Qualcosa è andato storto")


#################

aggiungi_da_template()
