from pathlib import Path
import sqlite3
import pandas as pd

from utils.many_utils import PATH, get_collection


def injection(st, file):
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
    return True


########### Mongo


def injection_mongo(st, file):
    df = (
        pd.read_excel(file, sheet_name="Template")
        .dropna(subset=["Data", "Tipo", "Importo", "Categoria", "Conto corrente"])
        .fillna("")
    )

    transazioni_col = get_collection(
        st.session_state["user"],
        "utente",
        st.session_state["mongo_uri"],
        mongo_db="solexiv_db",
    )

    for _, row in df.iterrows():
        transazione = {
            "data": str(row["Data"]),
            "descrizione": row["Descrizione"],
            "tipo": row["Tipo"],
            "importo": row["Importo"],
            "categoria": row["Categoria"],
            "conto_corrente": row["Conto corrente"],
            "note": row["Note"],
        }

        transazioni_col.insert_one(transazione)

    return True
