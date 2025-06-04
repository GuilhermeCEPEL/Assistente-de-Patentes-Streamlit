import streamlit as st
import os
import re
from PIL import Image

from datetime import date
from functions.agents_functions import *
from functions.sheet_functions import *
from functions.auxiliar_functions import *

def render_page5():
    st.title("Obrigado por participar do InovaFacil!")
    st.write("Esperamos que tenha encontrado informações úteis para proteger e desenvolver sua ideia.")
    
    image_path = os.path.join("image", "imagem_final.jpg")
    if os.path.exists(image_path):
        image = Image.open(image_path)
        # Centralize the image using columns
        col_img1, col_img2, col_img3 = st.columns([1, 2, 1])
        with col_img2:
            st.image(image, width=600)
    
    st.markdown("---")
    st.write("Você pode baixar um arquivo CSV com todas as suas respostas e os resultados da análise.")
    
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Voltar para a página anterior"):
            return -1
    
    with col2:
        csv_data = info_to_data_frame(st.session_state.userData, st.session_state.questionsData, st.session_state.ideaData)
            # Convert DataFrame to CSV string with BOM for Excel compatibility
        csv_string = csv_data.to_csv(index=False, encoding='utf-8-sig')

        st.download_button(
            label="💾 Baixar Formulário Completo (CSV)",
            key="download_button",
            data=csv_string,
            file_name=f"formulario_inovafacil_{date.today()}.csv",
            mime="text/csv",
            help="Baixe um arquivo CSV com todas as suas respostas e os resultados da análise.",
            use_container_width=True
        )    

    with col3:
        # Button to go back to the first page
        if st.button("Recomeçar o Questionário"):
            st.session_state['already_saved_to_sheet'] = False
            return 1