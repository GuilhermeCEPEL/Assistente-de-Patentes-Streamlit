import streamlit as st
import os
import re
from PIL import Image

from functions.agents_functions import *
from functions.sheet_functions import *
from functions.auxiliar_functions import *

# Centralized questionnaire questions
QUESTIONNAIRE_SECTIONS = [
    {
        'title': 'Natureza da Ideia',
        'questions': [
            {'id': 'q1', 'text': 'Sua ideia é apenas um algoritmo isolado ou método matemático?'},
            {'id': 'q2', 'text': 'Sua ideia consiste em uma metodologia (de ensino, gestão, negócios ou treinamento)?'},
            {'id': 'q3', 'text': 'Sua ideia é puramente software (sem aplicação técnica ou física específica)?'},
        ]
    },
    {
        'title': 'Critérios de Patenteabilidade',
        'questions': [
            {'id': 'q4', 'text': 'A ideia resolve um problema técnico com uma solução técnica (ex: dispositivo, sistema físico, mecanismo)?'},
            {'id': 'q5', 'text': 'A solução é nova (não existe algo igual já divulgado ou patenteado)?'},
            {'id': 'q6', 'text': 'A solução é inventiva (não é óbvia para um técnico no assunto)?'},
            {'id': 'q7', 'text': 'Tem aplicação industrial (pode ser fabricada, usada ou aplicada em algum setor produtivo)?'},
        ]
    },
    {
        'title': 'Perguntas Adicionais',
        'questions': [
            {'id': 'q8', 'text': 'A ideia já foi divulgada publicamente? (ex: redes sociais, eventos, artigos)'},
            {'id': 'q9', 'text': 'Há intenção de comercializar ou licenciar essa ideia?'},
            {'id': 'q10', 'text': 'Você já desenvolveu um protótipo ou MVP da solução?'},
        ]
    }
]

def get_initial_questions_data():
    initial_data = {}
    for section_info in QUESTIONNAIRE_SECTIONS:
        for question in section_info["questions"]:
            # Inicializa checkboxes como None (não respondido) ou False
            if question.get("type", "checkbox") == "checkbox":
                initial_data[question["id"]] = None # Ou False, dependendo da sua preferência para não respondido
            # Adicione outros tipos de perguntas aqui se tiver (ex: text_input = "")
    return initial_data

def render_page2():
    st.header("Questionário Rápido")
    st.write("Por favor, responda às perguntas abaixo para nos ajudar a entender melhor sua ideia. Suas respostas são cruciais para a análise.")

    for section in QUESTIONNAIRE_SECTIONS:
        display_questionnaire_section(section['title'], section['questions'])

    # Check if all questions are answered
    are_questions_complete = all(value is not None for value in st.session_state.questionsData.values())

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Voltar", key="prev_page_button_2"):
            return -1
    with col2:
        if st.button("➡️ Próxima Página", key="next_page_button_2", disabled=not are_questions_complete):
            # Clear recommendation related session state when moving back to description page
            # for key in ['recomendacao_gerada', 'recomendacao_texto']:
            #     if key in st.session_state:
            #         del st.session_state[key]  
            return 1
        else:
            return 0