import sqlite3
from pymongo import MongoClient
import streamlit as st
from pathlib import Path
from utils.many_utils import crea_tabella_utente, db_isempty
from utils.many_utils import PATH
import json
import os


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
    st.markdown(
        f"### Qui puoi importare ed esportare il database in locale o su MongoDB"
    )
else:
    st.error("Non sei autenticato, torna alla pagina di login")
    st.stop()


# Funzione per il download del database
def download_database():
    empty = db_isempty(st.session_state["user"])

    db_file = Path(PATH, f"utente_{st.session_state['user']}.db")
    download_file_name = f"utente_{st.session_state['user']}.db"
    try:
        if os.path.exists(db_file):
            with open(db_file, "rb") as file:
                data = file.read()
            if st.download_button(
                "Clicca qui per scaricare il database",
                data,
                file_name=download_file_name,
                disabled=empty,
            ):
                st.success("Database scaricato")
        else:
            st.warning("Database non trovato")
    except:
        st.error("Qualcosa è andato storto")


def main_():
    st.markdown("### Da file")
    col1, col2 = st.columns(2)
    crea_tabella_utente(st.session_state["user"])

    with col1:
        st.markdown("Download del Database")
        download_database()
    with col2:
        st.markdown("Ripristino del Database")
        backup_file = st.file_uploader(
            "Seleziona il file di backup del database per il ripristino",
            type=["db"],
            accept_multiple_files=False,
        )
        if backup_file is not None:
            st.warning("Attenzione! Questo sovrascriverà l'attuale database locale!")
            if st.button("Ripristina"):
                try:
                    with open(
                        Path(PATH, f"utente_{st.session_state['user']}.db"), "wb"
                    ) as file:
                        file.write(backup_file.getvalue())
                        st.success("Database ripristinato con successo!")
                except:
                    st.error("Qualcosa è andato storto")


####################### MONGODB


def get_collection(
    mongo_uri,
    mongo_db="solexiv_db",
    mongo_collection=f"utente_{st.session_state['user']}",
):
    client = MongoClient(mongo_uri)
    db = client[mongo_db]
    collection = db[mongo_collection]

    return collection


def get_transazioni():
    db_file = Path(PATH, f'utente_{st.session_state["user"]}.db')
    conn_sqlite = sqlite3.connect(db_file)
    cursor_sqlite = conn_sqlite.cursor()
    cursor_sqlite.execute("SELECT * FROM transazioni_utente")

    rows = cursor_sqlite.fetchall()
    transazioni = []
    for row in rows:
        transazione = {
            "id": row[0],
            "data": row[1],
            "descrizione": row[2],
            "tipo": row[3],
            "importo": row[4],
            "categoria": row[5],
            "conto_corrente": row[6],
            "note": row[7],
        }
        transazioni.append(transazione)
    conn_sqlite.close()
    return transazioni


def main():
    uri = ""
    data = {}
    st.markdown("### MongoDB")
    crea_tabella_utente(st.session_state["user"])
    empty = db_isempty(st.session_state["user"])
    if os.path.exists(Path("..", "creds", "creds.json")):
        with open(Path("..", "creds", "creds.json"), "r") as f:
            data = json.load(f)

        uri = st.text_input("URI MongoDB", value=data["uri"])
        if not uri.endswith("/?retryWrites=true&w=majority"):
            uri += "/?retryWrites=true&w=majority"

    else:
        uri = st.text_input("URI MongoDB")
        if not uri.endswith("/?retryWrites=true&w=majority"):
            uri += "/?retryWrites=true&w=majority"
    col3, col4 = st.columns(2)
    with col3:
        st.warning("Attenzione! Questo sovrascriverà l'attuale database su MongoDB!")
        if st.button("Backup", disabled=empty):
            coll = get_collection(uri)
            transazioni = get_transazioni()
            # Prima cancello
            a = coll.delete_many({}).deleted_count
            # Poi popolo
            a = coll.insert_many(transazioni).inserted_ids

            st.success(f"Effettuato il backup di {len(a)} transazioni")
    with col4:
        st.warning("Attenzione! Questo sovrascriverà l'attuale database locale!")
        if st.button("Ripristina"):
            coll = get_collection(uri)
            transazioni = [t for t in coll.find()]

            db_file = Path(PATH, f'utente_{st.session_state["user"]}.db')
            conn_sqlite = sqlite3.connect(db_file)
            cursor = conn_sqlite.cursor()

            # Prima cancello
            cursor.execute("DELETE FROM transazioni_utente")

            # Poi popolo
            for record in transazioni:
                data = record.get("data")
                descrizione = record.get("descrizione")
                tipo = record.get("tipo")
                importo = record.get("importo")
                categoria = record.get("categoria")
                conto_corrente = record.get("conto_corrente")
                note = record.get("note")

                cursor.execute(
                    """
                    INSERT INTO transazioni_utente (data, descrizione, tipo, importo, categoria, conto_corrente, note)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        data,
                        descrizione,
                        tipo,
                        importo,
                        categoria,
                        conto_corrente,
                        note,
                    ),
                )
            conn_sqlite.commit()
            conn_sqlite.close()
            st.success(f"Effettuato il ripristino di {len(transazioni)} transazioni")


#########################

main_()
main()
