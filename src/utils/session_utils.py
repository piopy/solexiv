import os
import json
from pathlib import Path
from utils.many_utils import PATH


def recupera_sessione_attiva(st):
    with open(Path(PATH, "_active_session"), "r") as f:
        dizi = json.load(f)
        st.session_state["user"] = dizi["username"]
        st.session_state["password"] = dizi["hash_pw"]
        st.session_state["encrypted"] = dizi["encrypted"]


def salva_sessione_attiva(st):
    with open(Path(PATH, "_active_session"), "w") as f:
        dizi = {
            "username": st.session_state["user"],
            "hash_pw": st.session_state["password"],
            "encrypted": st.session_state["encrypted"],
        }
        f.write(json.dumps(dizi))


def rimuovi_sessione_attiva(st):
    try:
        os.remove(Path(PATH, "_active_session"))
    except:
        return False
    return True
