import streamlit as st
import os
import re
from PIL import Image
from time import sleep
import streamlit.components.v1 as components

from functions.agents_functions import *
from functions.sheet_functions import *
from functions.auxiliar_functions import *


def render_page3():

    # Construct the full form input for the recommender agent
    formulario = "\n".join([
        f"**Natureza da Ideia**",
        f"A ideia é apenas um algoritmo isolado ou método matemático: {'Sim' if st.session_state.questionsData['q1'] else 'Não'}",
        f"A ideia é uma metodologia de ensino, gestão, negócios ou treinamento: {'Sim' if st.session_state.questionsData['q2'] else 'Não'}",
        f"A ideia é puramente software (sem aplicação técnica específica): {'Sim' if st.session_state.questionsData['q3'] else 'Não'}",
        f"**Critérios de patenteabilidade**",
        f"A ideia resolve um problema técnico com uma solução técnica (ex: dispositivo, sistema físico, mecanismo)?: {'Sim' if st.session_state.questionsData['q4'] else 'Não'}",
        f"A solução é nova? (Não existe algo igual já divulgado ou patenteado?): {'Sim' if st.session_state.questionsData['q5'] else 'Não'}",
        f"A solução é inventiva? (Não é óbvia para um técnico no assunto?): {'Sim' if st.session_state.questionsData['q6'] else 'Não'}",
        f"Tem aplicação industrial? (Pode ser fabricada, usada ou aplicada em algum setor produtivo?): {'Sim' if st.session_state.questionsData['q7'] else 'Não'}",
        f"A ideia já foi divulgada publicamente? (ex: redes sociais, eventos, artigos): {'Sim' if st.session_state.questionsData['q8'] else 'Não'}",
        f"Há intenção de comercializar ou licenciar essa ideia? {'Sim' if st.session_state.questionsData['q9'] else 'Não'}",
        f"Você já desenvolveu um protótipo ou MVP da solução? {'Sim' if st.session_state.questionsData['q10'] else 'Não'}",
    ])

    if 'recomendacao_gerada' not in st.session_state:
        with st.spinner("Gerando recomendação inicial com base no questionário..."):
            recomendacao = agente_recomendador(formulario)

            st.session_state['recomendacao_texto'] = recomendacao
            st.session_state['recomendacao_gerada'] = True

            data_to_save_df = info_to_data_frame(st.session_state.userData, st.session_state.questionsData, st.session_state.ideaData)
            append_data_to_sheet("Dados InovaFacil", data_to_save_df)

        with st.expander("💡 Veja a Recomendação Inicial sobre sua Ideia 💡", expanded=False):
            st.markdown("### Recomendação do Assistente")
            st.write(st.session_state['recomendacao_texto'])

    st.header("Descreva Detalhadamente Sua Ideia")
    st.write("Forneça o máximo de detalhes possível nos campos abaixo para uma análise mais precisa. Campos com * são obrigatórios.")

    st.session_state.ideaData['main'] = st.text_area(
        "❓ Descrição da sua ideia ou invenção (o que é, para que serve, como funciona): *",
        value=st.session_state.ideaData['main'],
        height=180,
        help="Ex: 'É um sistema de irrigação inteligente que utiliza sensores de umidade para otimizar o uso da água em plantações agrícolas, reduzindo o desperdício em até 30%.'"
    )

    st.session_state.ideaData['differential'] = st.text_area(
        "❓ Qual é o diferencial ou inovação da sua ideia? *",
        value=st.session_state.ideaData['differential'],
        height=150,
        help="Ex: 'Seu diferencial está no algoritmo preditivo que antecipa as necessidades hídricas da planta com base em dados climáticos e do solo, algo que as soluções atuais não oferecem.'"
    )

    st.session_state.ideaData['dev'] = st.text_area(
        "❓ Você já desenvolveu algo relacionado a essa ideia? (protótipo, código, apresentação, etc.)",
        value=st.session_state.ideaData['dev'],
        height=120,
        help="Ex: 'Sim, desenvolvi um protótipo em escala reduzida e um software de controle em Python.'"
    )

    st.session_state.ideaData['sector'] = st.text_area(
        "❓ Qual é o setor de aplicação da sua ideia? *",
        value=st.session_state.ideaData['sector'],
        height=100,
        help="Ex: 'Agricultura, automação, energia renovável.'"
    )

    are_description_fields_complete = (
        st.session_state.ideaData['main'].strip() and
        st.session_state.ideaData['differential'].strip() and
        st.session_state.ideaData['sector'].strip()
    )

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Voltar", key="prev_page_button_3"):
            return -1  # Go back to the previous page
    with col2:
        if st.button("➡️ Analisar Ideia", key="next_page_button_3", disabled=not are_description_fields_complete):
            # Clear analysis related session state when moving to analysis page to ensure fresh run
            for key in ['resultado_da_avaliacao', 'resultado_da_busca', 'resultado_da_analise', 'proximos_passos_texto']:
                if key in st.session_state:
                    del st.session_state[key]
            return 1  # Indicate to move to the next page for analysis
