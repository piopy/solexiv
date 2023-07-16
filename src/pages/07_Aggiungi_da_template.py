from pathlib import Path
import streamlit as st
from logica_applicativa.Aggiungi_da_template import injection, injection_mongo

from utils.many_utils import check_active_session, logo_and_page_title


logo_and_page_title(st)
check_active_session(st, "Qui puoi aggiungere transazioni a partire da un template")


def aggiungi_da_template():
    st.markdown("### Template:")
    try:
        with open(Path("..", "data", "Template.xlsx"), "rb") as file:
            data = file.read()
        if st.download_button(
            "Scarica il template", data=data, file_name="Template.xlsx"
        ):
            st.success("Template scaricato")
    except:
        st.error("Template non disponibile")
    st.write("Una volta compilato, carica qui il template")
    template_file = st.file_uploader(
        "Carica il template", type=["xlsx"], accept_multiple_files=False
    )
    if template_file is not None:
        if st.button("Inserisci le transazioni"):
            try:
                injection_mongo(st, template_file.getvalue())
                st.success("Transazioni aggiunte con successo")
            except:
                st.error("Qualcosa è andato storto")


#################

aggiungi_da_template()
