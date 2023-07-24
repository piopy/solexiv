import json
import os
from time import sleep

import streamlit as st
from pathlib import Path
from logica_applicativa.Creazioni_tabelle import (
    # crea_tabella_scadenze,
    crea_tabella_scadenze_mongo,
    # crea_tabella_utente,
    crea_tabella_utente_mongo,
    crea_tabella_utenti,
)
from logica_applicativa.Dashboard import (
    # andamento_patrimonio,
    andamento_patrimonio_mongo,
)
from logica_applicativa.Mainpage import autenticazione, crea_utente
from logica_applicativa.Scadenze import (
    genera_body_scadenza,
    # get_scadenze,
    get_scadenze_mongo,
)
from utils.many_utils import (
    cancella_account,
    logo_and_page_title,
    # ottieni_conti_correnti,
    ottieni_conti_correnti_mongo,
)
from utils.many_utils import PATH
from utils.session_utils import (
    recupera_sessione_attiva,
    rimuovi_sessione_attiva,
)
from streamlit_card import card

logo_and_page_title(st)


# Pagina di accesso e registrazione
def login():
    st.markdown(
        "<h1 style='text-align: center; color:#8B0000;'>👑 SOLEXIV 👑</h1>",
        unsafe_allow_html=True,
    )
    try:
        temp = st.session_state["user"]
    except:
        st.session_state["user"] = None
    if os.path.exists(Path(PATH, "_active_session")):
        recupera_sessione_attiva(st)

    # Utente loggato
    if st.session_state["user"]:
        uri = st.session_state["mongo_uri"]
        st.title(f"Ciao, {st.session_state.user.title()}!")
        st.success("<- Ora puoi navigare tra le pagine")
        crea_tabella_utente_mongo(st.session_state["user"], uri)
        crea_tabella_scadenze_mongo(st, uri)

        #### CARDS

        if len(ottieni_conti_correnti_mongo(st.session_state["user"], uri)) > 0:
            # Cards
            st.markdown("---")
            with st.expander("Situazione finanziaria", True):
                # st.markdown("## Situazione finanziaria")
                card_cols = st.columns(2)
                conti = ottieni_conti_correnti_mongo(st.session_state["user"], uri)
                i = 0
                for conto_corrente in conti:
                    with card_cols[i % 2]:
                        # DB = Path(PATH, f"utente_{st.session_state.user}.db")
                        # storico = andamento_patrimonio(DB, conto_corrente)
                        storico = andamento_patrimonio_mongo(
                            st.session_state["user"], conto_corrente, uri
                        )
                        value = storico.tail(1)["patrimonio"].values[0].round(2)
                        card(
                            title=conto_corrente,
                            text=f"{value} €",
                            on_click=lambda: 1,
                        )
                        if value < 50:
                            st.warning(
                                f"{conto_corrente} - Attenzione: il saldo di questo conto inizia ad essere basso!"
                            )
                        i += 1

        # Scadenze
        with st.expander("Scadenze", True):
            # st.markdown("## Scadenze")
            scadenze = get_scadenze_mongo(st, uri)
            scadenze_non_completate = scadenze[scadenze["completata"].lt(1)]
            if scadenze_non_completate.shape[0] > 0:
                st.warning("Scadenze in avvicinamento")
                for i, s in scadenze_non_completate.iterrows():
                    body = genera_body_scadenza(s)
                    st.code(
                        body,
                        language="json",
                    )

                    st.markdown("---")
            else:
                st.success("Non hai scadenze in elenco")
                st.markdown("---")
        with st.expander("Scadenze completate"):
            if scadenze[scadenze["completata"].gt(0)].shape[0] > 0:
                # st.markdown("### Scadenze completate")
                for i, s in scadenze[scadenze["completata"].gt(0)].iterrows():
                    body = genera_body_scadenza(s)
                    st.code(
                        body,
                        language="json",
                    )

                st.markdown("---")

        st.image(
            "https://media.giphy.com/media/Zhpvn5KvGEvJu/giphy.gif",
            use_column_width=True,
        )
        with st.expander("Cancella account"):
            # cancella account
            if st.button(
                "Cancella account - Attenzione! Verrà eliminato anche il database!"
            ):
                cancella_account(st.session_state["user"])
                st.session_state["user"] = None
                st.session_state["password"] = None
                rimuovi_sessione_attiva(st)
                st.image(
                    "https://media.giphy.com/media/o0eOCNkn7cSD6/giphy.gif",
                    use_column_width=False,
                )
                st.success(
                    "Hai eliminato l'account. Verrai rispedito alla pagina di login a breve."
                )
                sleep(4)
                st.experimental_rerun()
        # logout
        if st.button("Logout"):
            st.session_state["user"] = None
            st.session_state["password"] = None
            st.success("Hai effettuato il logout")
            rimuovi_sessione_attiva(st)
            st.experimental_rerun()
        st.stop()

    crea_tabella_utenti()

    with st.expander("**ACCESSO**", True):
        # st.title("ACCESSO")
        username = st.text_input("Nome utente")
        password = st.text_input("Password", type="password")
        if os.getenv("SAFEBOX", 0) == 0:
            persistenza = st.checkbox("Ricordami")
        else:
            persistenza = False

        # Controllo dell'autenticazione
        if st.button("Accedi"):
            # Input del nome utente
            try:
                if autenticazione(st, username, password, persistenza):
                    st.success("Accesso effettuato con successo.")
                    st.experimental_rerun()
                else:
                    st.error("Nome utente o password non validi.")
            except Exception as e:
                st.error("Errore nel recupero dell'utente")
                st.write(e)

    with st.expander("**REGISTRAZIONE**"):
        # st.title("Registrazione")
        data = "mongodb+srv://<USER>:<Password>@.........mongodb.net"
        if os.path.exists(Path("..", "creds", "creds.json")):
            with open(Path("..", "creds", "creds.json"), "r") as f:
                data = json.load(f)["uri"]

        new_username = st.text_input("Nuovo nome utente")
        new_password = st.text_input("Nuova password", type="password")
        mongo_uri = st.text_input("Mongo URI", value=data)

        if not mongo_uri.endswith("/?retryWrites=true&w=majority"):
            mongo_uri = mongo_uri + "/?retryWrites=true&w=majority"
        if st.button("Registra"):
            if (
                new_username != ""
                and new_password != ""
                and mongo_uri != "mongodb+srv://<USER>:<Password>@.........mongodb.net"
                and mongo_uri != ""
            ):
                esito = crea_utente(st, new_username, new_password, mongo_uri)
                if esito:
                    st.success(
                        "Registrazione effettuata con successo. Ora puoi effettuare l'accesso."
                    )
                    st.warning(
                        "Attenzione! Su questo server gli utenti potrebbero cancellarsi in seguito a rilasci o a pulizia del dominio del server.\nCi dispiace per l'inconveniente."
                    )
                    st.toast("Registrazione completata con successo")
            else:
                st.error("Verifica i campi inseriti e riprova")


login()
