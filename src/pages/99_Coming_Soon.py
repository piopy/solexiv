import streamlit as st
from pathlib import Path


from PIL import Image

from utils.many_utils import PATH

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


def main():
    st.title("SoleXIV")
    st.markdown("By [piopy](https://github.com/piopy/)")
    st.write("")
    st.markdown(
        '<img src="https://pngimg.com/uploads/github/github_PNG83.png" width=25%>',
        unsafe_allow_html=True,
    )
    st.markdown("### [Visita il repository](https://github.com/piopy/solexiv)")

    st.markdown(" ## Coming Soon")

    st.markdown(
        """
    - [ ] Panoramica conti
    - [ ] Previsione del bilancio futuro
    - [ ] Ricerca delle transazioni per data, descrizione o importo
    - [ ] Notifiche per scadenze, pagamenti o obiettivi di risparmio
    """
    )


main()
