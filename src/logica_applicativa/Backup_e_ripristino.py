import os
from pathlib import Path
import sqlite3
from utils.many_utils import PATH, db_isempty
from pymongo import MongoClient


def download_database(st):
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


def ripristina_da_file(st, backup_file):
    try:
        with open(Path(PATH, f"utente_{st.session_state['user']}.db"), "wb") as file:
            file.write(backup_file.getvalue())
            st.success("Database ripristinato con successo!")
    except:
        st.error("Qualcosa è andato storto")


####################### MONGODB


def backup_su_mongo(coll, transazioni):
    # Prima cancello
    a = coll.delete_many({}).deleted_count
    # Poi popolo
    a = coll.insert_many(transazioni).inserted_ids
    return a


def get_all_data_mongo_collection(coll):
    return [t for t in coll.find()]


def ripristina_da_mongo(st, coll):
    transazioni = get_all_data_mongo_collection(coll)
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
    return transazioni


def get_collection(
    st,
    mongo_uri,
    mongo_db="solexiv_db",
):
    mongo_collection = f"utente_{st.session_state['user']}"

    client = MongoClient(mongo_uri)
    db = client[mongo_db]
    collection = db[mongo_collection]

    return collection


def get_transazioni(st):
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
