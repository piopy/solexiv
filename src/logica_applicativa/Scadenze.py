from pathlib import Path
import sqlite3
from datetime import datetime
from pymongo import ASCENDING

import pandas as pd

from utils.many_utils import PATH, get_collection


def inserisci_scadenza(
    st,
    nome,
    data_scadenza,
    dettagli,
    importo,
    stato,
    categoria,
    frequenza,
    notifiche=False,
):
    conn = sqlite3.connect(Path(PATH, f"utente_{st.session_state['user']}.db"))
    c = conn.cursor()

    data_inserimento = datetime.now().strftime("%Y-%m-%d")
    data_completamento = None
    completata = 1 if stato == "Completata" else 0
    c.execute(
        """
        INSERT INTO scadenze (nome, data_inserimento, data_scadenza, data_completamento, dettagli, importo, categoria, frequenza, notifiche, completata)
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
            frequenza,  # mensile? annuale? settimanale?
            notifiche,  # o meglio, "quanti giorni prima della scadenza voglio essere notificato"
            completata,  # completata/da fare
        ),
    )

    conn.commit()
    conn.close()


def get_scadenze(st):
    conn = sqlite3.connect(Path(PATH, f"utente_{st.session_state['user']}.db"))
    c = conn.cursor()

    c.execute("SELECT * FROM scadenze ORDER BY data_scadenza")
    scadenze = c.fetchall()
    cols = [
        "id",
        "nome",
        "data_inserimento",
        "data_scadenza",
        "data_completamento",
        "dettagli",
        "importo",
        "categoria",
        "frequenza",
        "notifiche",
        "completata",
    ]
    st.write()
    conn.close()
    return pd.DataFrame(scadenze, columns=cols).sort_values(
        "data_scadenza", ascending=True
    )


def aggiorna_stato_scadenza(st, id_scadenza):
    conn = sqlite3.connect(Path(PATH, f"utente_{st.session_state['user']}.db"))
    c = conn.cursor()

    c.execute("UPDATE scadenze SET completata = 1 WHERE id = ?", (id_scadenza))
    c.execute(
        "UPDATE scadenze SET data_completamento = ? WHERE id = ?",
        (datetime.strftime(datetime.now(), "%Y-%m-%d"), id_scadenza),
    )

    conn.commit()
    conn.close()


def elimina_scadenza(st, id_scadenza):
    conn = sqlite3.connect(Path(PATH, f"utente_{st.session_state['user']}.db"))
    c = conn.cursor()

    c.execute("DELETE FROM scadenze WHERE id = ?;", (id_scadenza))

    conn.commit()
    conn.close()


def genera_body_scadenza(s):
    res_id = s["_id"]
    res_nome = s["nome"]
    res_data_inserimento = s["data_inserimento"]
    res_data_scadenza = s["data_scadenza"]
    res_data_completamento = s["data_completamento"]
    res_dettagli = s["dettagli"]
    res_importo = s["importo"]
    res_categoria = s["categoria"]
    res_frequenza = s["frequenza"]
    res_notifiche = s["notifiche"]
    res_completata = "Si" if s["completata"] == 1 else "No"
    return f"\
        ID: {res_id} - {res_nome}, \n\
        Categoria: {res_categoria},\n\
        Inserita il: {res_data_inserimento}\n\
        Scadenza: {res_data_scadenza},\n\
        Dettagli: {res_dettagli},\n\
        Importo: {res_importo},\n\
        Completata: {res_completata}\n\
        Data completamento: {res_data_completamento}\
        "


######### Mongo


def get_scadenze_mongo(st, mongo_uri):
    scadenze_col = get_collection(
        st.session_state["user"],
        "scadenze",
        mongo_uri,
        mongo_db="solexiv_db",
    )

    scadenze = list(scadenze_col.find().sort("data_scadenza", ASCENDING))
    cols = [
        "_id",
        "nome",
        "data_inserimento",
        "data_scadenza",
        "data_completamento",
        "dettagli",
        "importo",
        "categoria",
        "frequenza",
        "notifiche",
        "completata",
    ]

    return pd.DataFrame(scadenze, columns=cols).sort_values(
        "data_scadenza", ascending=True
    )


def inserisci_scadenza_mongo(
    st,
    nome,
    data_scadenza,
    dettagli,
    importo,
    stato,
    categoria,
    frequenza,
    notifiche=False,
):
    scadenze_col = get_collection(
        st.session_state["user"],
        "scadenze",
        st.session_state["mongo_uri"],
        mongo_db="solexiv_db",
    )

    data_inserimento = datetime.now().strftime("%Y-%m-%d")
    data_scadenza = data_scadenza.strftime("%Y-%m-%d")
    data_completamento = None
    completata = True if stato == "Completata" else False

    scadenza = {
        "nome": nome,
        "data_inserimento": data_inserimento,
        "data_scadenza": data_scadenza,
        "data_completamento": data_completamento,
        "dettagli": dettagli,
        "importo": importo,
        "categoria": categoria,
        "frequenza": frequenza,
        "notifiche": notifiche,
        "completata": completata,
    }

    res = scadenze_col.insert_one(scadenza)

    st.success("Scadenza inserita correttamente.")
    return True


def aggiorna_stato_scadenza_mongo(st, id_scadenza):
    scadenze_col = get_collection(
        st.session_state["user"],
        "scadenze",
        st.session_state["mongo_uri"],
        mongo_db="solexiv_db",
    )

    scadenza = scadenze_col.find_one({"_id": id_scadenza})

    if scadenza:
        scadenza["completata"] = True
        scadenza["data_completamento"] = datetime.now().strftime("%Y-%m-%d")

        scadenze_col.update_one({"_id": id_scadenza}, {"$set": scadenza})

        st.success("Stato della scadenza aggiornato correttamente.")
    else:
        st.error("Scadenza non trovata.")


def elimina_scadenza_mongo(st, id_scadenza):
    scadenze_col = get_collection(
        st.session_state["user"],
        "scadenze",
        st.session_state["mongo_uri"],
        mongo_db="solexiv_db",
    )

    # Elimina la scadenza corrispondente all'id fornito
    result = scadenze_col.delete_one({"_id": id_scadenza})

    if result.deleted_count > 0:
        st.success("Scadenza eliminata correttamente.")
    else:
        st.error("Scadenza non trovata.")
