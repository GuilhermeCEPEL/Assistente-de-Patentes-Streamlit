import streamlit as st
import os
import re

from datetime import date
from functions.agents_functions import *
from functions.sheet_functions import *
from functions.auxiliar_functions import *
from screens.page_1_user_data import render_page1
from screens.page_2_questions import render_page2, get_initial_questions_data
from screens.page_3_idea_description import render_page3
from screens.page_4_results import render_page4

# Importações para Google Sheets
from PIL import Image

# Function to navigate to the next page
def next_page():
    st.session_state.currentPage += 1
    st.rerun()
    
# Function to navigate to the previous page
def prev_page():
    st.session_state.currentPage -= 1
    st.rerun()

# Acessa a API Key de forma segura através dos Streamlit Secrets
# O nome da chave 'GOOGLE_API_KEY' deve corresponder ao que você definirá no Streamlit Cloud
api_key = st.secrets["GOOGLE_API_KEY"]

# Configura a variável de ambiente para as bibliotecas Google
os.environ["GOOGLE_API_KEY"] = api_key


# Load the custom icon image
icon_path = os.path.join(os.path.dirname(__file__), "image", "cepel.png")
icon_image = Image.open(icon_path)

logo_path = os.path.join(os.path.dirname(__file__), "image", "eletrobras_cortado.png")
logo_image = Image.open(logo_path)

st.set_page_config(
  page_title="InovaFacil",
  page_icon=icon_image,
  layout="wide",
  initial_sidebar_state="auto"
)

# CSS para aplicar o degradê ao plano de fundo e o overlay
st.markdown(
  """
  <style>
  @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;500;700&display=swap');

  html, body, [class*="css"] {
    font-family: 'Poppins', sans-serif;
  }

  .stApp {
    background: linear-gradient(to bottom, #009E49, #00AEEF);
    background-attachment: fixed;
    color: white;
  }

  h1, h2, h3, h4, .st-emotion-cache-10qzy2j { /* Targets header elements and some Streamlit text elements */
    color: white !important;
  }

  .stAlert { /* Styling for info/warning messages */
    background-color: rgba(255, 255, 255, 0.15);
    color: white;
    border-radius: 8px;
  }

  .stButton button, .stDownloadButton button {
    background-color: #ffffff;
    color: #009E49;
    border-radius: 8px;
    padding: 0.5em 2em;
    font-weight: bold;
    border: none;
    transition: background-color 0.3s ease;
    width: 100%; /* Make buttons full width */
  }

  .stButton button:hover, .stDownloadButton button:hover {
    background-color: #00AEEF;
    color: white;
  }

  .divider {
    height: 1px;
    background-color: rgba(255,255,255,0.3);
    margin: 30px 0;
  }

  .stTextArea textarea {
    background-color: rgba(255, 255, 255, 0.1);
    color: black;
    border-radius: 8px;
    border: 1px solid rgba(255, 255, 255, 0.3);
  }

  .stTextInput input {
    background-color: rgba(255, 255, 255, 0.1);
    color: black;
    border-radius: 8px;
    border: 1px solid rgba(255, 255, 255, 0.3);
  }

  /* Style for radio buttons */
  .stRadio div[role="radiogroup"] label {
    color: white;
  }
  .stRadio div[role="radiogroup"] label div {
    color: white; /* Ensures the 'Sim' / 'Não' text is white */
  }

  /* Expander styling */
  .stExpander details {
    background-color: rgba(255, 255, 255, 0.1);
    border-radius: 10px;
    padding: 10px 20px;
    margin-bottom: 15px;
    border: 1px solid rgba(255, 255, 255, 0.2);
  }

  .stExpander details summary {
    color: white;
    font-weight: bold;
  }

  .stExpander details div {
    color: white;
  }

  </style>
  """,
  unsafe_allow_html=True
)


# Initialize session state variables if they don't exist
if 'currentPage' not in st.session_state:
  st.session_state.currentPage = 0

if 'userData' not in st.session_state:
  st.session_state.userData = {
      'name': '',
      'matricula': '',
      'email': '',
  }

if 'questionsData' not in st.session_state:
    # Use a função do módulo da página 2 para obter a estrutura inicial
    st.session_state.questionsData = get_initial_questions_data()

if 'ideaData' not in st.session_state:
  st.session_state.ideaData = {
      'main': '',
      'differential': '',
      'dev': '',
      'sector': '',
  }
# Display the logo image centered at the top of the page

col_logo, col_title, col_empty = st.columns([1, 2, 1])
with col_logo:
  st.image(logo_image, width=200)

# --- Lógica de Navegação Principal ---
def navigate_pages():
    page_functions = {
        0: render_page1,
        1: render_page2,
        2: render_page3,
        3: render_page4,
    }

    current_page_renderer = page_functions.get(st.session_state.currentPage)

    if current_page_renderer:
        navigation_action = current_page_renderer()

        if navigation_action == 1:
            st.session_state.currentPage += 1
            st.rerun()
        elif navigation_action == -1:
            st.session_state.currentPage -= 1
            st.rerun()
    else:
        st.session_state.currentPage = 0
        st.rerun()

navigate_pages()
