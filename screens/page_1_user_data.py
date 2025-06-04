import streamlit as st
import os
import re
from PIL import Image

from functions.agents_functions import *
from functions.sheet_functions import *
from functions.auxiliar_functions import *

def render_page1():

    st.markdown("<h1 style='text-align: center;'>Bem-vindo à InovaFácil 💡</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 1.2rem;'>Sua plataforma inteligente para proteger e inovar ideias.</p>", unsafe_allow_html=True)

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    st.title("Suas Informações")
    st.write("Por favor, preencha seus dados para continuar.")

    raw_name = st.text_input("❓ Nome completo:", value=st.session_state.userData['name'], help="Apenas letras e espaços são permitidos.")
    cleaned_name = clean_name_input(raw_name)
    if raw_name and raw_name != cleaned_name:
        st.warning("O nome deve conter apenas letras e espaços. Caracteres inválidos foram removidos.")
    st.session_state.userData['name'] = cleaned_name

    matricula_input = st.text_input(
        label="❓ Matrícula (somente números):",
        value=st.session_state.userData['matricula'],
        key="matricula_input",
        help="Digite apenas números para sua matrícula."
    )
    # Ensure only digits are kept for matricula
    cleaned_matricula = ''.join(filter(str.isdigit, matricula_input or ""))
    if matricula_input and matricula_input != cleaned_matricula:
        st.warning("A matrícula deve conter apenas números. Caracteres inválidos foram removidos.")
    st.session_state.userData['matricula'] = cleaned_matricula

    # Check if matricula has exactly 7 digits
    if cleaned_matricula and len(cleaned_matricula) != 7:
        st.warning("A matrícula deve conter exatamente 7 dígitos.")

    st.session_state.userData['email'] = st.text_input("❓ Email:", value=st.session_state.userData['email'], help="Seu email para contato.")

    if st.session_state.userData['email']:
        if not is_valid_email(st.session_state.userData['email']):
            st.warning("Por favor, insira um e-mail válido.")

    # Check if all user data fields are filled and valid
    is_user_data_complete = (
        bool(st.session_state.userData['name'].strip()) and
        bool(st.session_state.userData['matricula']) and len(st.session_state.userData['matricula']) == 7 and
        bool(st.session_state.userData['email'].strip()) and is_valid_email(st.session_state.userData['email'])
    )

    st.markdown("---")
    # "Next Page" button, centered
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("Continuar", key="next_page_button_1", disabled=not is_user_data_complete):
            data_to_save_df = info_to_data_frame(st.session_state.userData, st.session_state.questionsData, st.session_state.ideaData)
            append_data_to_sheet("Dados InovaFacil", data_to_save_df)
            # next_page()
            return 1
        else:
            return 0