import os
import streamlit as st
from pathlib import Path
from logica_applicativa.Proteggi_DB import (
    check_active_session_proteggi_db,
    crittografa_database,
    decrittografa_database,
    gen_fernet_key,
    modifica_session_encrypted,
)
from utils.many_utils import PATH, logo_and_page_title


logo_and_page_title(st)
check_active_session_proteggi_db(st)


DB = Path(PATH, f"utente_{st.session_state.user}.db")


password = st.session_state["password"]
if st.session_state["encrypted"] == False:
    if st.button("Crittografa database"):
        chiave = gen_fernet_key(password.encode("utf-8"))

        # Crittografa il database
        crittografa_database(chiave, str(DB))
        st.toast("Il database è stato crittografato con successo!")
        st.session_state["encrypted"] = True
        os.remove(DB)
        modifica_session_encrypted(st, True)
        st.experimental_rerun()
else:
    if st.button("Decrittografa database"):
        chiave = gen_fernet_key(password.encode("utf-8"))

        # Decrittografa il database
        decrittografa_database(chiave, str(DB))
        st.toast("Il database è stato decrittografato con successo!")
        st.session_state["encrypted"] = False
        modifica_session_encrypted(st, False)

        os.remove(str(DB) + "_")

        st.experimental_rerun()
