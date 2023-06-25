import streamlit as st


from utils.many_utils import logo_and_page_title

logo_and_page_title(st)


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
    - [ ] Previsione del bilancio futuro
    - [ ] Notifiche per scadenze, pagamenti o obiettivi di risparmio
    """
    )


main()
