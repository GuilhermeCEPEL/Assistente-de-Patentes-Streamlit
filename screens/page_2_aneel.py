import streamlit as st
from functions.agents_functions import *
from functions.auxiliar_functions import *


def render_page2_aneel():
    st.title("Pesquisa de PDI ANEEL")

    st.write("Informe o tópico de interesse para pesquisar projetos de Pesquisa, Desenvolvimento e Inovação (PDI) regulados ou financiados pela ANEEL.")

    if 'topico_pdi_aneel' not in st.session_state:
        st.session_state['topico_pdi_aneel'] = ""

    topico_input = st.text_area(
        "Tópico:", 
        value=st.session_state['topico_pdi_aneel'], 
        height=150
    )
    if topico_input != st.session_state['topico_pdi_aneel']:
        st.session_state['topico_pdi_aneel'] = topico_input
    # topico = st.session_state['topico_pdi_aneel']

    if st.button("Pesquisar", disabled= not st.session_state['topico_pdi_aneel'].strip()):
        with st.spinner("Pesquisando..."):
            resultado_da_busca_pdi_aneel, resultado_da_sugestao = analise_de_projetos_aneel(f"{st.session_state['topico_pdi_aneel']}")
            st.session_state['resultado_da_busca_pdi_aneel'] = resultado_da_busca_pdi_aneel
            st.session_state['resultado_da_sugestao_pdi_aneel'] = resultado_da_sugestao

    if 'resultado_da_busca_pdi_aneel' in st.session_state and st.session_state['resultado_da_busca_pdi_aneel']:        
        with st.expander("📃 Veja o resultado da busca por PDIs sobre esse tópico 📃", expanded=False):
            st.markdown("### Resultados da Pesquisa:")
            st.write(st.session_state['resultado_da_busca_pdi_aneel'])

    if 'resultado_da_sugestao_pdi_aneel' in st.session_state and st.session_state['resultado_da_sugestao_pdi_aneel']:
        with st.expander("💡 Veja a sugestão de projetos relacionados 💡", expanded=False):
            st.markdown("### Sugestão de Projetos Relacionados:")
            st.write(st.session_state['resultado_da_sugestao_pdi_aneel'])

    if (
        st.session_state['topico_pdi_aneel'].strip()
        and 'resultado_da_busca_pdi_aneel' in st.session_state
        and 'resultado_da_sugestao_pdi_aneel' in st.session_state
        and st.session_state['resultado_da_busca_pdi_aneel']
        and st.session_state['resultado_da_sugestao_pdi_aneel']
    ):
        download_content = (
            "Tópico de Interesse:\n"
            f"{st.session_state['topico_pdi_aneel']}\n\n"
            "Resultados da Pesquisa:\n"
            f"{st.session_state['resultado_da_busca_pdi_aneel']}\n\n"
            "Sugestão de Projetos Relacionados:\n"
            f"{st.session_state['resultado_da_sugestao_pdi_aneel']}\n"
        )
        st.download_button(
            label="📥 Baixar resultados (.txt)",
            data=download_content,
            file_name="resultado_pesquisa_aneel.txt",
            mime="text/plain"
        )

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Voltar", key="prev_page_button_6"):            
            st.session_state.currentPage = 0
