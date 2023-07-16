from pathlib import Path
import sqlite3

from utils.many_utils import PATH, get_collection


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
    return True


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


################## Mongo


def rimuovi_transazioni_mongo(st, transazioni_selezionate, conto_corrente_selezionato):
    transazioni_col = get_collection(
        st.session_state["user"],
        "utente",
        st.session_state["mongo_uri"],
        mongo_db="solexiv_db",
    )
    st.write(transazioni_selezionate)
    for id_transazione in transazioni_selezionate:
        transazioni_col.delete_one(
            {
                "_id": id_transazione["_id"],
                "conto_corrente": conto_corrente_selezionato,
            }
        )

    return True


def select_all_transazioni_mongo(st, conto_corrente_selezionato):
    transazioni_col = get_collection(
        st.session_state["user"],
        "utente",
        st.session_state["mongo_uri"],
        mongo_db="solexiv_db",
    )

    transazioni = transazioni_col.find({"conto_corrente": conto_corrente_selezionato})

    return transazioni
