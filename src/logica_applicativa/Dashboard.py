from datetime import datetime, timedelta
import sqlite3

import pandas as pd


def ottieni_spese_ultimi_12_mesi(DB, conto_corrente):
    today = datetime.now()
    data_inizio = today - timedelta(days=365)
    data_inizio = data_inizio.strftime("%Y-%m-%d")

    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute(
        """SELECT strftime('%Y-%m', data), categoria, SUM(importo)
                    FROM transazioni_utente
                    WHERE data >= ? AND conto_corrente = ? AND data <= ? AND tipo = 'Uscita'
                    GROUP BY strftime('%Y-%m', data), categoria
                    ORDER BY strftime('%Y-%m', data) DESC""",
        (data_inizio, conto_corrente, datetime.now().strftime("%Y-%m-%d")),
    )
    results = c.fetchall()
    conn.close()

    mesi = []
    categorie = []
    importi = []

    for row in results:
        mese = row[0]
        categoria = row[1]
        importo = row[2]

        mesi.append(mese)
        categorie.append(categoria)
        importi.append(importo)

    return mesi, categorie, importi


def andamento_patrimonio(DB, conto_corrente):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute(
        """SELECT strftime('%Y-%m', data), categoria, SUM(importo), tipo
                    FROM transazioni_utente
                    WHERE conto_corrente = ? AND data <= ? 
                    GROUP BY strftime('%Y-%m', data), tipo
                    ORDER BY strftime('%Y-%m', data) DESC""",
        (conto_corrente, datetime.now().strftime("%Y-%m-%d")),
    )
    results = c.fetchall()
    conn.close()
    storico = (
        pd.DataFrame(results, columns=["data", "categoria", "importo", "tipo"])
        .groupby(["data", "tipo"])
        .agg(euri=("importo", "sum"))
        .reset_index()
    )
    storico.loc[storico["tipo"] == "Uscita", "euri"] *= -1
    storico["patrimonio"] = storico["euri"].cumsum()
    storico = storico.drop_duplicates(subset=["data"], keep="last").drop(
        columns=["tipo", "euri"]
    )
    return storico


def ottieni_spese_per_mese(DB, conto_corrente, mese_selezionato):
    if len(str(mese_selezionato)) == 1:
        mese_selezionato = "0" + str(mese_selezionato)
    mese_formato = f"{datetime.now().year}-{mese_selezionato}"

    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute(
        """SELECT data, categoria, SUM(importo)
                    FROM transazioni_utente
                    WHERE strftime('%Y-%m', data) = ? AND conto_corrente = ? AND tipo = 'Uscita'
                    GROUP BY data, categoria""",
        (mese_formato, conto_corrente),
    )
    results = c.fetchall()
    conn.close()

    giorni = []
    categorie = []
    importi = []

    for row in results:
        giorno = row[0]
        categoria = row[1]
        importo = row[2]

        giorni.append(giorno)
        categorie.append(categoria)
        importi.append(importo)

    return giorni, categorie, importi


def entrate_uscite(DB, conto_corrente, mese_selezionato):
    # Converte il mese selezionato nel formato "YYYY-MM"
    if len(str(mese_selezionato)) == 1:
        mese_selezionato = "0" + str(mese_selezionato)
    mese_formato = f"{datetime.now().year}-{mese_selezionato}"

    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute(
        """SELECT SUM(importo)
                    FROM transazioni_utente
                    WHERE strftime('%Y-%m', data) = ? AND conto_corrente = ? AND tipo = 'Uscita'
                    """,
        (mese_formato, conto_corrente),
    )
    results = c.fetchall()
    if results.__len__() == 0:
        results.append("0")
    if results[0] == (None,):
        results[0] = "0"
    uscite = results[0]

    c.execute(
        """SELECT SUM(importo)
                    FROM transazioni_utente
                    WHERE strftime('%Y-%m', data) = ? AND conto_corrente = ? AND tipo = 'Entrata'
                    """,
        (mese_formato, conto_corrente),
    )
    results = c.fetchall()
    if results.__len__() == 0:
        results.append("0")
    if results[0] == (None,):
        results[0] = "0"
    entr = results[0]

    conn.close()

    return entr, uscite
