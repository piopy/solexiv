from pathlib import Path
import sqlite3

from utils.many_utils import PATH


def rimuovi_transazioni(st, transazioni_selezionate, conto_corrente_selezionato):
    conn = sqlite3.connect(Path(PATH, f"utente_{st.session_state['user']}.db"))
    cursor = conn.cursor()

    for id_transazione in transazioni_selezionate:
        cursor.execute(
            "DELETE FROM transazioni_utente WHERE id = ? AND conto_corrente = ?",
            (id_transazione[0], conto_corrente_selezionato),
        )
    conn.commit()

    conn.close()


def select_all_transazioni(st, conto_corrente_selezionato):
    conn = sqlite3.connect(Path(PATH, f"utente_{st.session_state['user']}.db"))
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM transazioni_utente WHERE conto_corrente = ?",
        (conto_corrente_selezionato,),
    )
    transazioni = cursor.fetchall()
    conn.close()
    return transazioni
