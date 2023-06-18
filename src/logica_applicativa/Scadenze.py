from pathlib import Path
import sqlite3
from datetime import datetime

from utils.many_utils import PATH


def inserisci_scadenza(
    st, nome, data_scadenza, dettagli, importo, stato, categoria, frequenza, notifiche
):
    conn = sqlite3.connect(Path(PATH, f"utente_{st.session_state['user']}.db"))
    c = conn.cursor()

    data_inserimento = datetime.now().strftime("%Y-%m-%d")
    data_completamento = None
    completata = 0

    c.execute(
        """
        INSERT INTO scadenze (nome, data_inserimento, data_scadenza, data_completamento, dettagli, importo, categoria, frequenza, notifiche, completata)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            completata,  # completata
        ),
    )

    conn.commit()
    conn.close()


def get_scadenze(st):
    conn = sqlite3.connect(Path(PATH, f"utente_{st.session_state['user']}.db"))
    c = conn.cursor()

    c.execute("SELECT * FROM scadenze ORDER BY data_scadenza")
    scadenze = c.fetchall()

    conn.close()
    return scadenze


def inserisci_scadenza(
    nome, data_scadenza, dettagli, importo, stato, categoria, notifiche
):
    # Funzione per inserire una scadenza nel database
    pass


def aggiorna_stato_scadenza(id_scadenza, stato):
    # Funzione per aggiornare lo stato di una scadenza nel database
    pass
