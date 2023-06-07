import streamlit as st
from pathlib import Path
from utils.many_utils import PATH
import json
import os


from PIL import Image

im = Image.open(Path(PATH, "favicon.ico"))
st.set_page_config(
    page_title="SOLEXIV",
    page_icon=im,
    layout="wide",
)

hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

if os.path.exists(Path(PATH, "_active_session")):
    with open(Path(PATH, "_active_session"), "r") as f:
        dizi = json.load(f)
        st.session_state["user"] = dizi["username"]
        st.session_state["password"] = dizi["hash_pw"]
        st.session_state["encrypted"] = dizi["encrypted"]

if st.session_state.user:
    if st.session_state.encrypted:
        st.error(
            "Il tuo archivio è crittografato, sbloccalo nella pagina di sicurezza."
        )
        st.stop()
    st.title(f"Ciao, {st.session_state.user.title()}")
    st.markdown(f"### Qui puoi importare ed esportare il database")
else:
    st.error("Non sei autenticato, torna alla pagina di login")
    st.stop()


# Funzione per il download del database
def download_database():
    # Percorso del file del database
    db_file = Path(PATH, f"utente_{st.session_state['user']}.db")

    # Nome del file per il download
    download_file_name = f"utente_{st.session_state['user']}.db"

    # Effettua il download del file
    try:
        if os.path.exists(db_file):
            with open(db_file, "rb") as file:
                data = file.read()
            if st.download_button(
                "Clicca qui per scaricare il database",
                data,
                file_name=download_file_name,
            ):
                st.success("Database scaricato")
        else:
            st.warning("Database non trovato")
    except:
        st.error("Qualcosa è andato storto")


# Pagina principale
def main():
    st.header("Download del Database")

    # Form per il download del database
    download_database()

    # Form per il ripristino del database
    st.header("Ripristino del Database")
    st.write("Seleziona il file di backup del database per il ripristino")
    backup_file = st.file_uploader(
        "Carica il file di backup", type=["db"], accept_multiple_files=False
    )
    if backup_file is not None:
        if st.button("Ripristina"):
            # Salvataggio del file di backup nel percorso desiderato
            try:
                with open(
                    Path(PATH, f"utente_{st.session_state['user']}.db"), "wb"
                ) as file:
                    file.write(backup_file.getvalue())
                    st.success("Database ripristinato con successo!")
            except:
                st.error("Qualcosa è andato storto")


# Esecuzione dell'applicazione principale
main()
