import streamlit as st


from utils.many_utils import logo_and_page_title

logo_and_page_title(st)


def main():
    st.title("SoleXIV")
    st.markdown("By [piopy](https://github.com/piopy/)")
    col1, col2 = st.columns([0.4, 0.6])

    with col1:
        st.write("")
        st.write("")
        st.markdown(
            '<img src="https://pngimg.com/uploads/github/github_PNG83.png" width=25%>',
            unsafe_allow_html=True,
        )
        st.markdown("### [Visita il repository](https://github.com/piopy/solexiv)")

    with col2:
        st.markdown(" ## Coming Soon")
        st.markdown(
            """
        - [x] Total MongoDB Application
        - [x] Export transazioni in Excel
        - [ ] Previsione del bilancio futuro
        - [ ] Notifiche per scadenze, pagamenti o obiettivi di risparmio
        - [ ] Export mensile in PDF
        """
        )


main()
