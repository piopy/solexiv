import io
import os
from pathlib import Path
import sqlite3

import pandas as pd
from utils.many_utils import PATH, db_isempty, db_isempty_mongo, get_collection
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
                st.toast("Database scaricato")
        else:
            st.warning("Database non trovato")
    except:
        st.error("Qualcosa è andato storto")


def ripristina_da_file(st, backup_file):
    try:
        with open(Path(PATH, f"utente_{st.session_state['user']}.db"), "wb") as file:
            file.write(backup_file.getvalue())
            st.toast("Database ripristinato con successo!")
    except:
        st.error("Qualcosa è andato storto")


####################### MONGODB


def backup_su_mongo(coll, transazioni):
    # Prima cancello
    a = coll.delete_many({}).deleted_count
    # Poi popolo
    a = coll.insert_many(transazioni).inserted_ids
    return a


def get_all_data_mongo_collection(coll):  # equivalente della select *
    return [t for t in coll.find()]


def ripristina_transazioni_da_mongo(st, coll):
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


def ripristina_scadenze_da_mongo(st, coll):
    scadenze = get_all_data_mongo_collection(coll)
    db_file = Path(PATH, f'utente_{st.session_state["user"]}.db')
    conn_sqlite = sqlite3.connect(db_file)
    cursor = conn_sqlite.cursor()

    # Prima cancello
    cursor.execute("DELETE FROM scadenze")

    # Poi popolo
    for record in scadenze:
        # id = record.get("id")
        nome = record.get("nome")
        data_inserimento = record.get("data_inserimento")
        data_scadenza = record.get("data_scadenza")
        data_completamento = record.get("data_completamento")
        dettagli = record.get("dettagli")
        importo = record.get("importo")
        categoria = record.get("categoria")
        frequenza = record.get("frequenza")
        notifiche = record.get("notifiche")
        completata = record.get("completata")

        cursor.execute(
            """
            INSERT INTO scadenze (nome, data_inserimento, data_scadenza, data_completamento, dettagli, importo, categoria, frequenza, notifiche,completata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                nome,
                data_inserimento,
                data_scadenza,
                data_completamento,
                dettagli,
                importo,
                categoria,
                frequenza,
                notifiche,
                completata,
            ),
        )
    conn_sqlite.commit()
    conn_sqlite.close()
    return scadenze


# def get_collection_transazioni(
#     st,
#     mongo_uri,
#     mongo_db="solexiv_db",
# ):
#     mongo_collection = f"utente_{st.session_state['user']}"

#     client = MongoClient(mongo_uri)
#     db = client[mongo_db]
#     collection = db[mongo_collection]

#     return collection


def get_collection_scadenze(
    st,
    mongo_uri,
    mongo_db="solexiv_db",
):
    mongo_collection = f"scadenze_{st.session_state['user']}"

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


def get_scadenze(st):
    db_file = Path(PATH, f'utente_{st.session_state["user"]}.db')
    conn_sqlite = sqlite3.connect(db_file)
    cursor_sqlite = conn_sqlite.cursor()
    cursor_sqlite.execute("SELECT * FROM scadenze")

    rows = cursor_sqlite.fetchall()
    scadenze = []
    for row in rows:
        scadenza = {
            "id": row[0],
            "nome": row[1],
            "data_inserimento": row[2],
            "data_scadenza": row[3],
            "data_completamento": row[4],
            "dettagli": row[5],
            "importo": row[6],
            "categoria": row[7],
            "frequenza": row[8],
            "notifiche": row[9],
            "completata": row[10],
        }
        scadenze.append(scadenza)
    conn_sqlite.close()
    return scadenze


############### Mongo


def download_database_mongo(st, mongouri):
    collection = get_collection(
        st.session_state["user"],
        "utente",
        mongouri,
        mongo_db="solexiv_db",
    )

    empty = db_isempty_mongo(st.session_state["user"], "utente", mongouri)
    download_file_name = f"utente_{st.session_state['user']}_TRANSAZIONI.solexiv"
    try:
        buffer = io.BytesIO()
        if not empty:
            documenti = list(collection.find())
            df = pd.DataFrame(documenti)

            csv_file = df.to_csv(buffer, sep=";", index=False, encoding="utf-8")

        if st.download_button(
            "Clicca qui per scaricare il database",
            data=buffer,
            file_name=download_file_name,
            mime="application/json",
            disabled=empty,
        ):
            st.toast("Database scaricato")
    except:
        st.error("Qualcosa è andato storto")

    return True


def ripristina_da_file_mongo(st, file, mongouri):  # .drop(columns=["_id", "id"])
    collection = get_collection(
        st.session_state["user"],
        "utente",
        mongouri,
        mongo_db="solexiv_db",
    )
    df = pd.read_csv(file, sep=";", encoding="utf-8")
    st.toast("Cancello i record presenti su MongoDB")
    collection.delete_many({})
    documenti = df.drop(columns=["_id"]).to_dict(orient="records")
    if documenti:
        st.toast("Carico i record su MongoDB")
        collection.insert_many(documenti)

    return True


def download_database_scadenze_mongo(st, mongouri):
    collection = get_collection(
        st.session_state["user"],
        "scadenze",
        mongouri,
        mongo_db="solexiv_db",
    )

    empty = db_isempty_mongo(st.session_state["user"], "scadenze", mongouri)

    download_file_name = f"utente_{st.session_state['user']}_SCADENZE.solexiv"
    try:
        buffer = io.BytesIO()
        if not empty:
            documenti = list(collection.find())
            df = pd.DataFrame(documenti)

            csv_file = df.to_csv(buffer, sep=";", index=False, encoding="utf-8")

        if st.download_button(
            "Clicca qui per scaricare il database",
            data=buffer,
            file_name=download_file_name,
            mime="application/json",
            disabled=empty,
        ):
            st.toast("Database scaricato")
    except:
        st.error("Qualcosa è andato storto")

    return True


def ripristina_scadenze_da_file_mongo(
    st, file, mongouri
):  # .drop(columns=["_id", "id"])
    collection = get_collection(
        st.session_state["user"],
        "scadenze",
        mongouri,
        mongo_db="solexiv_db",
    )
    df = pd.read_csv(file, sep=";", encoding="utf-8")
    st.toast("Cancello i record presenti su MongoDB")
    collection.delete_many({})
    documenti = df.drop(columns=["_id", "id"]).to_dict(orient="records")
    if documenti:
        st.toast("Carico i record su MongoDB")
        collection.insert_many(documenti)

    return True
