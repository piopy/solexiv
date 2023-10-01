import json
import sqlite3
from pathlib import Path
from datetime import datetime
from PIL import Image
import os
from pymongo import MongoClient

from utils.many_utils import PATH, get_collection


def aggiungi_transazione(
    st,
    data_transazione,
    conto_corrente,
    tipo_transazione,
    descrizione,
    importo,
    categoria,
    note,
):
    conn = sqlite3.connect(Path(PATH, f"utente_{st.session_state['user']}.db"))
    c = conn.cursor()
    c.execute(
        """INSERT INTO transazioni_utente (data, conto_corrente, tipo, descrizione, importo, categoria, note) 
    VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (
            data_transazione,
            conto_corrente,
            tipo_transazione,
            descrizione,
            importo,
            categoria,
            note,
        ),
    )
    conn.commit()
    conn.close()
    return True


################## Mongo


def aggiungi_transazione_mongo(
    st,
    data_transazione,
    conto_corrente,
    tipo_transazione,
    descrizione,
    importo,
    categoria,
    note,
):
    transazioni_col = get_collection(
        st.session_state["user"],
        "utente",
        st.session_state["mongo_uri"],
        mongo_db="solexiv_db",
    )
    data_transazione = data_transazione.strftime("%Y-%m-%d")
    transazione = {
        "data": data_transazione,
        "conto_corrente": conto_corrente,
        "tipo": tipo_transazione,
        "descrizione": descrizione,
        "importo": importo,
        "categoria": categoria,
        "note": note,
    }

    transazioni_col.insert_one(transazione)

    return True
