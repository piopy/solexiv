from pathlib import Path
import sqlite3
import pandas as pd

from utils.many_utils import PATH


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
