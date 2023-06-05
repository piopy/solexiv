import sqlite3
from pathlib import Path 
from datetime import datetime, timedelta

PATH = '../data/'

# Funzione per creare la tabella "transazioni_utente" se non esiste
def crea_tabella_utente(username):
    conn = sqlite3.connect(Path(PATH,f"utente_{username}.db"))
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS transazioni_utente (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    data TEXT,
                    descrizione TEXT,
                    tipo TEXT,
                    importo REAL,
                    categoria TEXT,
                    conto_corrente TEXT,
                    note TEXT)''')
    conn.commit()
    conn.close()



# Funzione per ottenere i conti correnti distinti
def ottieni_conti_correnti(username):
    conn = sqlite3.connect(Path(PATH,f"utente_{username}.db"))
    c = conn.cursor()
    c.execute(f"SELECT DISTINCT conto_corrente FROM transazioni_utente")
    results = c.fetchall()
    conn.close()

    conti_correnti = [row[0] for row in results]
    return conti_correnti


def risali_sei_mesi_prima(mese):
    # Ottieni l'oggetto datetime per la data corrente
    data_corrente = datetime.now()
    
    # Calcola l'anno corrente
    anno_corrente = data_corrente.year
    
    # Calcola l'anno e il mese sei mesi prima
    anno_sei_mesi_prima = anno_corrente
    mese_sei_mesi_prima = mese - 6
    
    # Verifica se il mese sei mesi prima è negativo
    if mese_sei_mesi_prima <= 0:
        # Sottrai l'anno e il mese necessari per ottenere sei mesi prima
        anno_sei_mesi_prima -= 1
        mese_sei_mesi_prima += 12
    
    # Formatta l'anno e il mese come stringa "YYYY-MM"
    mese_sei_mesi_prima_str = f"{anno_sei_mesi_prima:04d}-{mese_sei_mesi_prima:02d}"
    
    return mese_sei_mesi_prima_str