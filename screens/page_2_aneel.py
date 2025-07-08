import streamlit as st
from functions.agents_functions import *


def render_page2_aneel():
    st.title("Pesquisa de PDI ANEEL")

    st.write("Informe o tópico de interesse para pesquisar projetos de Pesquisa, Desenvolvimento e Inovação (PDI) regulados ou financiados pela ANEEL.")

    topico = st.text_area("Tópico:", height=150)

    if st.button("Pesquisar"):
        with st.spinner("Pesquisando..."):
            resultado_da_busca_pdi_aneel = agente_pesquisa_pdi_aneel(f"{topico}")
            st.session_state['resultado_da_busca_pdi_aneel'] = resultado_da_busca_pdi_aneel

    if 'resultado_da_busca_pdi_aneel' in st.session_state and st.session_state['resultado_da_busca_pdi_aneel']:        
        with st.expander("📃 Veja o resultado da busca por PDIs sobre esse tópico 📃", expanded=False):
            st.markdown("### Resultados da Pesquisa:")
            st.write(st.session_state['resultado_da_busca_pdi_aneel'])

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Voltar", key="prev_page_button_3"):
            return -1  # Go back to the previous page
