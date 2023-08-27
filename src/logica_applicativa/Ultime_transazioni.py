from pathlib import Path
import sqlite3
import pandas as pd
from io import BytesIO
from utils.many_utils import PATH, get_collection


def ottieni_ultime_transazioni(st, conto_corrente, n_transazioni=20):
    conn = sqlite3.connect(Path(PATH, "utente_" + st.session_state["user"] + ".db"))
    c = conn.cursor()

    c.execute(
        f"""
    SELECT data as data ,tipo , printf("%.2f", importo) ,categoria , descrizione, note
    FROM transazioni_utente 
    WHERE conto_corrente=? ORDER BY data DESC 
    LIMIT {n_transazioni}""",
        (conto_corrente,),
    )
    transazioni = c.fetchall()

    conn.close()

    return transazioni


def ottieni_ultime_transazioni_mongo(st, conto_corrente, mongo_uri, n_transazioni=20):
    transazioni_col = get_collection(
        st.session_state["user"],
        "utente",
        mongo_uri,
        mongo_db="solexiv_db",
    )

    pipeline = [
        {"$match": {"conto_corrente": conto_corrente}},
        {"$sort": {"data": -1}},
        {"$limit": int(n_transazioni)},
        {
            "$project": {
                "_id": 0,
                "data": "$data",
                "tipo": "$tipo",
                "importo": {"$round": ["$importo", 2]},
                "categoria": "$categoria",
                "descrizione": "$descrizione",
                "note": "$note",
            }
        },
    ]

    if n_transazioni == "0":
        pipeline.remove({"$limit": int(n_transazioni)})

    result = transazioni_col.aggregate(pipeline)
    transazioni = list(result)

    return transazioni


def download_excel(df, name) -> bytes:
    buffer = BytesIO()
    with pd.ExcelWriter(path=buffer, engine="xlsxwriter") as w:
        df.to_excel(excel_writer=w, index=False, sheet_name=name)
    return buffer.getvalue()
