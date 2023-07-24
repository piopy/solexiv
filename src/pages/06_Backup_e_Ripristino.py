import streamlit as st

# from pathlib import Path
from logica_applicativa.Backup_e_ripristino import (
    # backup_su_mongo,
    # download_database,
    download_database_mongo,
    download_database_scadenze_mongo,
    # get_collection_scadenze,
    # get_collection_transazioni,
    # get_scadenze,
    # get_transazioni,
    # ripristina_da_file,
    ripristina_da_file_mongo,
    ripristina_scadenze_da_file_mongo,
    # ripristina_scadenze_da_mongo,
    # ripristina_transazioni_da_mongo,
)
from utils.many_utils import (
    check_active_session,
    # db_isempty,
    logo_and_page_title,
)

# import json
# import os
from logica_applicativa.Creazioni_tabelle import (
    # crea_tabella_utente,
    crea_tabella_utente_mongo,
)


logo_and_page_title(st)
check_active_session(
    st, "Qui puoi importare ed esportare il database in locale o su MongoDB"
)


# def main_():
#     # st.markdown("### Da file")
#     col1, col2 = st.columns(2)
#     crea_tabella_utente(st.session_state["user"])

#     with col1:
#         st.markdown("Download del Database")
#         download_database(st)
#     with col2:
#         st.markdown("Ripristino del Database")
#         backup_file = st.file_uploader(
#             "Seleziona il file di backup del database per il ripristino",
#             type=["db"],
#             accept_multiple_files=False,
#         )
#         if backup_file is not None:
#             st.warning("Attenzione! Questo sovrascriverà l'attuale database locale!")
#             if st.button("Ripristina"):
#                 ripristina_da_file(st, backup_file)


# ####################### MONGODB


# def main():
#     uri = ""
#     data = {}
#     # st.markdown("### MongoDB")
#     crea_tabella_utente(st.session_state["user"])
#     empty = db_isempty(st.session_state["user"])
#     if os.path.exists(Path("..", "creds", "creds.json")):
#         with open(Path("..", "creds", "creds.json"), "r") as f:
#             data = json.load(f)

#         uri = st.text_input("URI MongoDB", value=data["uri"])
#         if not uri.endswith("/?retryWrites=true&w=majority"):
#             uri += "/?retryWrites=true&w=majority"

#     else:
#         uri = st.text_input("URI MongoDB")
#         if not uri.endswith("/?retryWrites=true&w=majority"):
#             uri += "/?retryWrites=true&w=majority"
#     col3, col4 = st.columns(2)
#     with col3:
#         st.warning("Attenzione! Questo sovrascriverà l'attuale database su MongoDB!")
#         if st.button("Backup", disabled=empty):
#             # backup transazioni
#             coll = get_collection_transazioni(st, uri)
#             transazioni = get_transazioni(st)
#             a = backup_su_mongo(coll, transazioni)

#             st.success(f"Effettuato il backup di {len(a)} transazioni")

#             # backup scadenze
#             coll_scad = get_collection_scadenze(st, uri)
#             scadenze = get_scadenze(st)
#             b = backup_su_mongo(coll_scad, scadenze)
#             st.success(f"Effettuato il backup di {len(b)} scadenze")

#     with col4:
#         st.warning("Attenzione! Questo sovrascriverà l'attuale database locale!")
#         if st.button("Ripristina"):
#             # ripristino transazioni
#             coll = get_collection_transazioni(st, uri)
#             transazioni = ripristina_transazioni_da_mongo(st, coll)
#             st.success(f"Effettuato il ripristino di {len(transazioni)} transazioni")

#             # ripristino scadenze
#             coll_scad = get_collection_scadenze(st, uri)
#             scadenze = ripristina_scadenze_da_mongo(st, coll_scad)
#             st.success(f"Effettuato il ripristino di {len(scadenze)} scadenze")


######################### Mongo v2


def main_v2(mongouri):
    col1, col2 = st.columns(2)
    crea_tabella_utente_mongo(st.session_state["user"], mongouri)

    with col1:
        st.markdown("Download del Database")
        download_database_mongo(st)
    with col2:
        st.markdown("Ripristino del Database")
        backup_file = st.file_uploader(
            "Seleziona il file di backup TRANSAZIONI del database per il ripristino",
            type=["solexiv"],
            accept_multiple_files=False,
        )
        if backup_file is not None:
            st.warning("Attenzione! Questo sovrascriverà l'attuale database locale!")
            if st.button("Ripristina"):
                ripristina_da_file_mongo(st, backup_file)


def main_scadenze_v2(mongouri):
    col3, col4 = st.columns(2)
    crea_tabella_utente_mongo(st.session_state["user"], mongouri)

    with col3:
        st.markdown("Download del Database")
        download_database_scadenze_mongo(st)
    with col4:
        st.markdown("Ripristino del Database")
        backup_file_s = st.file_uploader(
            "Seleziona il file di backup SCADENZE del database per il ripristino",
            type=["solexiv"],
            accept_multiple_files=False,
        )
        if backup_file_s is not None:
            st.warning("Attenzione! Questo sovrascriverà l'attuale database locale!")
            if st.button("Ripristina"):
                ripristina_scadenze_da_file_mongo(st, backup_file_s)


########################


# with st.expander("Operazioni su file"):
#     main_()
# with st.expander("Operazioni su MongoDB"):
#     main()
def pagina_bella():
    mongouri = st.text_input("Mongo URI", value=st.session_state["mongo_uri"])
    st.write("")
    with st.expander("Operazioni su Transazioni MongoDB", True):
        main_v2(mongouri)
    with st.expander("Operazioni su Scadenze MongoDB", True):
        main_scadenze_v2(mongouri)


pagina_bella()
