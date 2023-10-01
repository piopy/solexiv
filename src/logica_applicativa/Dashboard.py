from datetime import datetime, timedelta
import sqlite3

import pandas as pd

from utils.many_utils import get_collection


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


def ottieni_spese_per_mese_descr(DB, conto_corrente, mese_selezionato):
    if len(str(mese_selezionato)) == 1:
        mese_selezionato = "0" + str(mese_selezionato)
    mese_formato = f"{datetime.now().year}-{mese_selezionato}"

    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute(
        """SELECT data, categoria, descrizione, SUM(importo)
                    FROM transazioni_utente
                    WHERE strftime('%Y-%m', data) = ? AND conto_corrente = ? AND tipo = 'Uscita'
                    GROUP BY data, categoria, descrizione""",
        (mese_formato, conto_corrente),
    )
    results = c.fetchall()
    conn.close()

    giorni = []
    categorie = []
    descrizioni = []
    importi = []

    for row in results:
        giorno = row[0]
        categoria = row[1]
        descrizione = row[2]
        importo = row[3]

        giorni.append(giorno)
        categorie.append(categoria)
        descrizioni.append(descrizione + " - " + giorno)
        importi.append(importo)

    return giorni, categorie, descrizioni, importi


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
    if float(entr[0]) > 0:
        entr = str(float(round(entr[0], 2)))
    if float(uscite[0]) > 0:
        uscite = str(float(round(uscite[0], 2)))

    return entr, uscite


######### MONGO


def andamento_patrimonio_mongo(username, conto_corrente, mongo_uri):
    transazioni_col = get_collection(
        username,
        "utente",
        mongo_uri,
        mongo_db="solexiv_db",
    )

    current_date = datetime.now()  # .strftime("%Y-%m-%d")
    # current_date = datetime.now().strftime("%Y-%m-%d")

    pipeline = [
        {
            "$addFields": {
                "data_datetime": {
                    "$dateFromString": {"dateString": "$data", "format": "%Y-%m-%d"}
                }
            }
        },
        {
            "$match": {
                "conto_corrente": conto_corrente,
                "data_datetime": {"$lte": current_date},
            }
        },
        {
            "$group": {
                "_id": {
                    "yearMonth": {
                        "$dateToString": {"format": "%Y-%m", "date": "$data_datetime"}
                    },
                    "tipo": "$tipo",
                },
                "categoria": {"$first": "$categoria"},
                "importo": {"$sum": "$importo"},
            }
        },
        {"$sort": {"_id.yearMonth": -1}},
        {
            "$project": {
                "_id": 0,
                "data": "$_id.yearMonth",
                "categoria": 1,
                "importo": 1,
                "tipo": "$_id.tipo",
            }
        },
    ]

    result = transazioni_col.aggregate(pipeline)
    results = list(result)

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


def entrate_uscite_mongo(username, mongo_uri, conto_corrente, mese_selezionato):
    # Converte il mese selezionato nel formato "YYYY-MM"
    if len(str(mese_selezionato)) == 1:
        mese_selezionato = "0" + str(mese_selezionato)
    mese_formato = f"{datetime.now().year}-{mese_selezionato}"

    transazioni_col = get_collection(
        username,
        "utente",
        mongo_uri,
        mongo_db="solexiv_db",
    )

    pipeline_uscite = [
        {
            "$match": {
                "data": {"$regex": f"^{mese_formato}.*"},
                "conto_corrente": conto_corrente,
                "tipo": "Uscita",
            }
        },
        {"$group": {"_id": None, "total": {"$sum": "$importo"}}},
    ]
    pipeline_entrate = [
        {
            "$match": {
                "data": {"$regex": f"^{mese_formato}.*"},
                "conto_corrente": conto_corrente,
                "tipo": "Entrata",
            }
        },
        {"$group": {"_id": None, "total": {"$sum": "$importo"}}},
    ]

    result_uscite = transazioni_col.aggregate(pipeline_uscite)
    result_entrate = transazioni_col.aggregate(pipeline_entrate)

    uscite = list(result_uscite)
    entr = list(result_entrate)

    if not uscite:
        uscite = 0  # [0]
    else:
        uscite = uscite[0]["total"]
        if float(uscite) > 0:
            uscite = str(float(round(uscite, 2)))

    if not entr:
        entr = 0  # [0]
    else:
        entr = entr[0]["total"]
        if float(entr) > 0:
            entr = str(float(round(entr, 2)))

    return entr, uscite


def ottieni_spese_per_mese_mongo(username, mongo_uri, conto_corrente, mese_selezionato):
    if len(str(mese_selezionato)) == 1:
        mese_selezionato = "0" + str(mese_selezionato)
    mese_formato = f"{datetime.now().year}-{mese_selezionato}"

    transazioni_col = get_collection(
        username,
        "utente",
        mongo_uri,
        mongo_db="solexiv_db",
    )

    pipeline = [
        {
            "$match": {
                "data": {"$regex": f"^{mese_formato}.*"},
                "conto_corrente": conto_corrente,
                "tipo": "Uscita",
            }
        },
        {
            "$group": {
                "_id": {"data": "$data", "categoria": "$categoria"},
                "importo": {"$sum": "$importo"},
            }
        },
        {
            "$project": {
                "_id": 0,
                "data": "$_id.data",
                "categoria": "$_id.categoria",
                "importo": 1,
            }
        },
    ]

    result = transazioni_col.aggregate(pipeline)
    results = list(result)

    giorni = []
    categorie = []
    importi = []

    for row in results:
        giorno = row["data"]
        categoria = row["categoria"]
        importo = row["importo"]

        giorni.append(giorno)
        categorie.append(categoria)
        importi.append(importo)

    return giorni, categorie, importi


def ottieni_spese_per_mese_descr_mongo(
    username, mongo_uri, conto_corrente, mese_selezionato
):
    if len(str(mese_selezionato)) == 1:
        mese_selezionato = "0" + str(mese_selezionato)
    mese_formato = f"{datetime.now().year}-{mese_selezionato}"

    transazioni_col = get_collection(
        username,
        "utente",
        mongo_uri,
        mongo_db="solexiv_db",
    )

    pipeline = [
        {
            "$match": {
                "data": {"$regex": f"^{mese_formato}.*"},
                "conto_corrente": conto_corrente,
                "tipo": "Uscita",
            }
        },
        {
            "$group": {
                "_id": {
                    "data": "$data",
                    "categoria": "$categoria",
                    "descrizione": "$descrizione",
                },
                "importo": {"$sum": "$importo"},
            }
        },
        {
            "$project": {
                "_id": 0,
                "data": "$_id.data",
                "categoria": "$_id.categoria",
                "descrizione": {
                    "$concat": [
                        {"$toString": "$_id.descrizione"},
                        # "$_id.data",  # "$_id.descrizione"
                        " - ",
                        "$_id.data",
                    ]
                },
                "importo": 1,
            }
        },
    ]

    result = transazioni_col.aggregate(pipeline)
    results = list(result)

    giorni = []
    categorie = []
    descrizioni = []
    importi = []

    for row in results:
        giorno = row["data"]
        categoria = row["categoria"]
        descrizione = row["descrizione"]
        importo = row["importo"]

        giorni.append(giorno)
        categorie.append(categoria)
        descrizioni.append(descrizione)
        importi.append(importo)

    return giorni, categorie, descrizioni, importi


def ottieni_spese_ultimi_12_mesi_mongo(username, mongo_uri, conto_corrente):
    today = datetime.now()
    data_inizio = today - timedelta(days=365)
    data_inizio = data_inizio.strftime("%Y-%m-%d")

    transazioni_col = get_collection(
        username,
        "utente",
        mongo_uri,
        mongo_db="solexiv_db",
    )

    pipeline = [
        {
            "$match": {
                "data": {
                    "$gte": data_inizio,
                    "$lte": datetime.now().strftime("%Y-%m-%d"),
                },
                "conto_corrente": conto_corrente,
                "tipo": "Uscita",
            }
        },
        {
            "$group": {
                "_id": {
                    "mese": {"$substr": ["$data", 0, 7]},
                    "categoria": "$categoria",
                },
                "importo": {"$sum": "$importo"},
            }
        },
        {
            "$project": {
                "_id": 0,
                "mese": "$_id.mese",
                "categoria": "$_id.categoria",
                "importo": 1,
            }
        },
        {"$sort": {"mese": -1}},
    ]

    result = transazioni_col.aggregate(pipeline)
    results = list(result)

    mesi = []
    categorie = []
    importi = []

    for row in results:
        mese = row["mese"]
        categoria = row["categoria"]
        importo = row["importo"]

        mesi.append(mese)
        categorie.append(categoria)
        importi.append(importo)

    return mesi, categorie, importi
