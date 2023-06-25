from pathlib import Path
import sqlite3

from utils.many_utils import PATH


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
