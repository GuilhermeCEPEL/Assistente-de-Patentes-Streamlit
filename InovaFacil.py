import streamlit as st
import os
import re

from datetime import date
from functions.agents_functions import *
from functions.sheet_functions import *
from functions.auxiliar_functions import *
from screens.page_1_user_data import render_page1

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

# Centralized questionnaire questions
QUESTIONNAIRE_SECTIONS = [
    {
        'title': 'Natureza da Ideia',
        'questions': [
            {'id': 'q1', 'text': 'A ideia é apenas um algoritmo isolado ou método matemático?'},
            {'id': 'q2', 'text': 'A ideia é uma metodologia de ensino, gestão, negócios ou treinamento?'},
            {'id': 'q3', 'text': 'A ideia é puramente software (sem aplicação técnica específica)?'},
        ]
    },
    {
        'title': 'Critérios de Patenteabilidade',
        'questions': [
            {'id': 'q4', 'text': 'A ideia resolve um problema técnico com uma solução técnica (ex: dispositivo, sistema físico, mecanismo)?'},
            {'id': 'q5', 'text': 'A solução é nova? (Não existe algo igual já divulgado ou patenteado?)'},
            {'id': 'q6', 'text': 'A solução é inventiva? (Não é óbvia para um técnico no assunto?)'},
            {'id': 'q7', 'text': 'Tem aplicação industrial? (Pode ser fabricada, usada ou aplicada em algum setor produtivo?)'},
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
  st.session_state.currentPage = 1
if 'userData' not in st.session_state:
  st.session_state.userData = {
      'name': '',
      'matricula': '',
      'email': '',
  }
if 'questionsData' not in st.session_state:
  st.session_state.questionsData = {q['id']: None for section in QUESTIONNAIRE_SECTIONS for q in section['questions']}
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

###################################################################################
# --- Page 1: User Information ---
if st.session_state.currentPage == 1:
  if render_page1(): # Chama a função da página 1
    st.session_state.currentPage = 2
    st.rerun() 


###################################################################################
# --- Page 2: Yes/No Questions ---
elif st.session_state.currentPage == 2:
  st.header("Questionário Rápido")
  st.write("Por favor, responda às perguntas abaixo para nos ajudar a entender melhor sua ideia. Suas respostas são cruciais para a análise.")

  for section in QUESTIONNAIRE_SECTIONS:
      display_questionnaire_section(section['title'], section['questions'])

  # Check if all questions are answered
  are_questions_complete = all(value is not None for value in st.session_state.questionsData.values())

  col1, col2 = st.columns(2)
  with col1:
    if st.button("Voltar", key="prev_page_button_2"):
      prev_page()
  with col2:
    if st.button("Próxima Página", key="next_page_button_2", disabled=not are_questions_complete):
      next_page()
      # Clear recommendation related session state when moving back to description page
      for key in ['recomendacao_gerada', 'recomendacao_texto']:
        if key in st.session_state:
          del st.session_state[key]  

###################################################################################
# --- Page 3: Idea Description ---
elif st.session_state.currentPage == 3:
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
      "Descrição da sua ideia ou invenção (o que é, para que serve, como funciona): *",
      value=st.session_state.ideaData['main'],
      height=180,
      help="Ex: 'É um sistema de irrigação inteligente que utiliza sensores de umidade para otimizar o uso da água em plantações agrícolas, reduzindo o desperdício em até 30%.'"
  )

  st.session_state.ideaData['differential'] = st.text_area(
      "Qual é o diferencial ou inovação da sua ideia? *",
      value=st.session_state.ideaData['differential'],
      height=150,
      help="Ex: 'Seu diferencial está no algoritmo preditivo que antecipa as necessidades hídricas da planta com base em dados climáticos e do solo, algo que as soluções atuais não oferecem.'"
  )

  st.session_state.ideaData['dev'] = st.text_area(
      "Você já desenvolveu algo relacionado a essa ideia? (protótipo, código, apresentação, etc.)",
      value=st.session_state.ideaData['dev'],
      height=120,
      help="Ex: 'Sim, desenvolvi um protótipo em escala reduzida e um software de controle em Python.'"
  )

  st.session_state.ideaData['sector'] = st.text_area(
      "Qual é o setor de aplicação da sua ideia? *",
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
    if st.button("Voltar", key="prev_page_button_3"):
      prev_page()
  with col2:
    if st.button("Analisar Ideia", key="next_page_button_3", disabled=not are_description_fields_complete):
      next_page()
      # Clear analysis related session state when moving to analysis page to ensure fresh run
      for key in ['resultado_da_avaliacao', 'resultado_da_busca', 'resultado_da_analise', 'proximos_passos_texto']:
        if key in st.session_state:
          del st.session_state[key]


# # --- Page 4: Idea Description ---
# elif st.session_state.currentPage == 4:
#   next_page()

###################################################################################
# --- Page 4: Idea Description ---
elif st.session_state.currentPage == 4:

  repostas_descritivas = f"""
  **Descrição da Ideia**
  Descrição da ideia ou invenção: {st.session_state.ideaData['main']}
  Qual é o diferencial ou inovação da sua ideia?: {st.session_state.ideaData['differential']}
  Você já desenvolveu algo (protótipo, código, apresentação)?: {st.session_state.ideaData['dev']}
  Qual é o setor de aplicação?: {st.session_state.ideaData['sector']}
  """
  formulario_respostas = "\n".join([
      f"A ideia é apenas um algoritmo isolado ou método matemático: {'Sim' if st.session_state.questionsData['q1'] else 'Não'}",
      f"A ideia é uma metodologia de ensino, gestão, negócios ou treinamento: {'Sim' if st.session_state.questionsData['q2'] else 'Não'}",
      f"A ideia é puramente software (sem aplicação técnica específica): {'Sim' if st.session_state.questionsData['q3'] else 'Não'}",
      f"A ideia resolve um problema técnico com uma solução técnica (ex: dispositivo, sistema físico, mecanismo)?: {'Sim' if st.session_state.questionsData['q4'] else 'Não'}",
      f"A solução é nova? (Não existe algo igual já divulgado ou patenteado?): {'Sim' if st.session_state.questionsData['q5'] else 'Não'}",
      f"A solução é inventiva? (Não é óbvia para um técnico no assunto?): {'Sim' if st.session_state.questionsData['q6'] else 'Não'}",
      f"Tem aplicação industrial? (Pode ser fabricada, usada ou aplicada em algum setor produtivo?): {'Sim' if st.session_state.questionsData['q7'] else 'Não'}",
      f"A ideia já foi divulgada publicamente? (ex: redes sociais, eventos, artigos): {'Sim' if st.session_state.questionsData['q8'] else 'Não'}",
      f"Há intenção de comercializar ou licenciar essa ideia? {'Sim' if st.session_state.questionsData['q9'] else 'Não'}",
      f"Você já desenvolveu um protótipo ou MVP da solução? {'Sim' if st.session_state.questionsData['q10'] else 'Não'}",
  ])

  if 'resultado_da_busca' not in st.session_state or 'resultado_da_avaliacao' not in st.session_state or 'resultado_da_analise' not in st.session_state:
    with st.spinner("⌛ Analisando as respostas... Por favor, aguarde."):
      resultado_da_busca, resultado_da_avaliacao, resultado_da_analise = analise_dos_resultados(repostas_descritivas, formulario_respostas)
    st.session_state['resultado_da_busca'] = resultado_da_busca
    st.session_state['resultado_da_avaliacao'] = resultado_da_avaliacao
    st.session_state['resultado_da_analise'] = resultado_da_analise
    
    data_to_save_df = info_to_data_frame(st.session_state.userData, st.session_state.questionsData, st.session_state.ideaData)
    append_data_to_sheet("Dados InovaFacil", data_to_save_df)
  else:
    resultado_da_busca = st.session_state['resultado_da_busca']
    resultado_da_avaliacao = st.session_state['resultado_da_avaliacao']
    resultado_da_analise = st.session_state['resultado_da_analise']

  # Parse and display the evaluation result with scores and emojis
  if resultado_da_avaliacao and isinstance(resultado_da_avaliacao, str):
    # Try to split the first line as title, rest as text
    lines = resultado_da_avaliacao.strip().split('\n')
    titulo_avaliacao = lines[0] if lines else "Avaliação não disponível"
    texto_avaliacao = "\n".join(lines[1:]) if len(lines) > 1 else ""

    # Extract score and text from the title if present (e.g., "8/10 - Avaliação do Potencial de Proteção")
    title_score_match = re.match(r"(\d+(?:\.\d+)?)/10\s*-?\s*(.*)", titulo_avaliacao)
    if title_score_match:
      titulo_score = float(title_score_match.group(1))
      titulo_text = title_score_match.group(2).strip()
      titulo_avaliacao = titulo_text
    else:
      titulo_score = None
      
    score_inovacao, just_inovacao = extract_score_and_justification(resultado_da_avaliacao, "Inovação")
    score_originalidade, just_originalidade = extract_score_and_justification(resultado_da_avaliacao, "Originalidade")
    score_potencial, just_potencial = extract_score_and_justification(resultado_da_avaliacao, "Potencial de Propriedade Intelectual")
  else:
    titulo_avaliacao = "Avaliação não disponível"
    texto_avaliacao = ""
    score_inovacao = score_originalidade = score_potencial = 0
    just_inovacao = just_originalidade = just_potencial = ""

  st.header("📊 Avaliação do Potencial de Proteção")
  # Display the score and text from the title in the subheader, with emoji and color
  if titulo_score is not None:
      color = "green" if titulo_score >= 7 else ("orange" if titulo_score >= 4 else "red")
      emoji = "✅" if titulo_score >= 7 else ("⚠️" if titulo_score >= 4 else "❌")
      st.markdown(f"<h3>{emoji} <span style='color:{color}'>{titulo_score}/10</span> — {titulo_avaliacao}</h3>", unsafe_allow_html=True)
  else:
      st.subheader(titulo_avaliacao)

  display_score("Inovação", score_inovacao, just_inovacao)
  display_score("Originalidade", score_originalidade, just_originalidade)
  display_score("Potencial de Propriedade Intelectual", score_potencial, just_potencial)

  st.markdown("---")

  # Display the detailed results in expanders
  with st.expander("🔍 Propriedades Intelectuais Similares Encontradas"):
    st.markdown("#### Lista Detalhada de PIs Similares")
    if resultado_da_busca:
      st.write(resultado_da_busca)
    else:
      st.info("Nenhuma propriedade intelectual similar foi encontrada na sua busca inicial ou a busca está em andamento.")

  with st.expander("💡 Análise Final e Recomendações Estratégicas"):
    st.markdown("#### Conclusão e Próximos Passos Sugeridos")
    if resultado_da_analise:
      st.write(resultado_da_analise)
    else:
      st.info("A análise final está sendo processada ou não há dados suficientes para uma conclusão.")

  st.markdown("---")
  st.subheader("O que você deseja proteger?")
  st.write("Com base na análise, selecione a categoria de proteção mais adequada para sua ideia.")

  opcao = st.selectbox(
    "Escolha o tipo de proteção para sua Propriedade Intelectual:",
    ("Selecione uma opção", "Patente de Invenção (PI)", "Modelo de Utilidade (MU)", "Programa de Computador (Software)"),
    key="combobox_proximos_passos"
  )

  # Only show "Próximos passos" button if an option is selected
  if opcao != "Selecione uma opção":
    if st.button("Gerar Próximos Passos Detalhados", key="prox_passos_button"):
      with st.spinner(f"Gerando os próximos passos para {opcao}..."):
        proximos_passos = agente_de_próximos_passos(f"Opção selecionada: {opcao}\n\nAnálise Detalhada:\n{resultado_da_analise}")
      st.session_state['proximos_passos_texto'] = proximos_passos
      st.success("Próximos passos gerados com sucesso!")
      st.markdown("### 📝 Guia Detalhado para Proteção:")
      st.write(st.session_state['proximos_passos_texto'])
  else:
      st.info("Por favor, selecione uma opção para gerar os próximos passos.")


  st.markdown("---")
  col1, col2, col3 = st.columns(3)
  with col1:
    if st.button("Voltar para Descrição da Ideia", key="prev_page_button_4"):
      prev_page()

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

    # Only generate the report when the download button is pressed
    def generate_relatorio():
      relatorio = agente_gerador_de_relatorio(f"Opção de patente: {opcao}\n\n{repostas_descritivas}\n\n{formulario_respostas}")
      st.session_state['relatorio_texto'] = relatorio
      data_to_save_df = info_to_data_frame(st.session_state.userData, st.session_state.questionsData, st.session_state.ideaData)
      append_data_to_sheet("Dados InovaFacil", data_to_save_df)
      return relatorio

    relatorio = st.session_state.get('relatorio_texto', '')

    if st.download_button(
      label="📃 Gerar Relatório INPI",
      key="download_report_button",
      data=relatorio if relatorio else "",
      file_name=f"relatorio_inovafacil_{date.today()}.txt",
      mime="text/txt",
      help="Baixe um relatório no formato requisitado pelo INPI.",
      use_container_width=True,
      on_click=lambda: generate_relatorio() if not relatorio else None # type: ignore
    ):
      if not relatorio:
        relatorio = generate_relatorio()
