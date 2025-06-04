import streamlit as st
import pandas as pd
import re

from .agents_functions import *
from .sheet_functions import *

# Importações para Google Sheets
from datetime import datetime

# Extract scores and justifications for each category
def extract_score_and_justification(text, category):
    # Pattern: x/10 - Categoria: justificativa
    pattern = rf"(\d+(?:\.\d+)?)/10\s*-?\s*\b{re.escape(category)}\b:\s*(.*)"
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        score = float(match.group(1)) if match is not None else 0
        return score, match.group(2).strip()
    return 0, ""


# Função auxiliar para renderizar a pontuação com emoji e justificativa
def display_score(label, score, justification):
    color = "green" if score >= 7 else ("orange" if score >= 4 else "red")
    emoji = "✅" if score >= 7 else ("⚠️" if score >= 4 else "❌")
    st.markdown(f"**{label}:** {emoji} <span style='color:{color}'>**{score}/10**</span>", unsafe_allow_html=True)
    if justification:
        # st.markdown(f"<span style='font-size:0.95em;color:#222;'>{justification}</span>", unsafe_allow_html=True)
        st.markdown(f"{justification}", unsafe_allow_html=True)

# Function to save data to a CSV file
def info_to_data_frame(user_data, questions_data, idea_data):
  # Add current date and time
  now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  # Combine all data into a single dictionary
  combined_data = {
    'Data_Hora': now,
    'Nome': user_data['name'],
    'Matricula': user_data['matricula'],
    'Email': user_data['email'],
    # Page 2: All formulary questions
    'Ideia_Algoritmo_Matematico': 'Sim' if questions_data['q1'] else 'Não' if questions_data['q1'] is not None else '',
    'Ideia_Metodologia': 'Sim' if questions_data['q2'] else 'Não' if questions_data['q2'] is not None else '',
    'Ideia_Software_Puro': 'Sim' if questions_data['q3'] else 'Não' if questions_data['q3'] is not None else '',
    'Ideia_Resolve_Problema_Tecnico': 'Sim' if questions_data['q4'] else 'Não' if questions_data['q4'] is not None else '',
    'Solucao_Nova': 'Sim' if questions_data['q5'] else 'Não' if questions_data['q5'] is not None else '',
    'Solucao_Inventiva': 'Sim' if questions_data['q6'] else 'Não' if questions_data['q6'] is not None else '',
    'Tem_Aplicacao_Industrial': 'Sim' if questions_data['q7'] else 'Não' if questions_data['q7'] is not None else '',
    'Ideia_Divulgada_Publicamente': 'Sim' if questions_data['q8'] else 'Não' if questions_data['q8'] is not None else '',
    'Intencao_Comercializar': 'Sim' if questions_data['q9'] else 'Não' if questions_data['q9'] is not None else '',
    'Protótipo_Ou_MVP': 'Sim' if questions_data['q10'] else 'Não' if questions_data['q10'] is not None else '',
    # Page 3: All descriptions
    'Descricao_Ideia': idea_data.get('main', ''),
    'Diferencial_Ideia': idea_data.get('differential', ''),
    'Desenvolvimento_Relacionado': idea_data.get('dev', ''),
    'Setor_Aplicacao': idea_data.get('sector', ''),
    # Page 3: Recommendation generated
    'Recomendacao_Protecao': st.session_state.get('recomendacao_texto', ''),
    # Page 4: Results
    'Resultado_Analise_PI': st.session_state.get('resultado_da_busca', ''),
    'Resultado_Avaliacao': st.session_state.get('resultado_da_avaliacao', ''),
    'Resultado_Analise_Final': st.session_state.get('resultado_da_analise', ''),
    'Relatorio_INPI': st.session_state.get('relatorio_texto', ''),
  }
  # Create a DataFrame from the combined data
  df = pd.DataFrame([combined_data])
  return df

def display_questionnaire_section(title, questions_list):
  st.subheader(f"**{title}**")
  for q in questions_list:
    default_index = None
    if st.session_state.questionsData[q['id']] is True:
      default_index = 0 # 'Sim'
    elif st.session_state.questionsData[q['id']] is False:
      default_index = 1 # 'Não'

    response = st.radio(
      f"❓ {q['text']}",
      ('Sim', 'Não'),
      key=f"radio_{q['id']}", # Unique key for each radio button
      index=default_index
    )
    if response == 'Sim':
      st.session_state.questionsData[q['id']] = True
    elif response == 'Não':
      st.session_state.questionsData[q['id']] = False
  st.markdown("---") # Divider for visual separation

def analise_dos_resultados(repostas_descritivas, formulario):
  # Set a session state flag to indicate analysis is running
  st.session_state['analysis_running'] = True

  info_placeholder = st.empty()
  info_placeholder.info("🔎 Analisando as respostas... Por favor, aguarde.")

  if not repostas_descritivas.strip() or not formulario.strip():
    info_placeholder.error("⚠️ A descrição da patente não pode estar vazia para a pesquisa.")
    st.session_state['analysis_running'] = False
    return ("", "", "")
  else:
    progress_bar = st.progress(0, text="Iniciando análise...")

    info_placeholder.info("Buscando patentes similares...")
    progress_bar.progress(0.15)
    resultado_da_busca = agente_buscador_de_PI(f"{repostas_descritivas}\n\n{formulario}")

    info_placeholder.info("Revisando a lista de propriedades intelectuais encontradas...")
    progress_bar.progress(0.5)
    resultado_da_revisao = agente_revisor(resultado_da_busca)

    info_placeholder.info("Avaliando o potencial da ideia...")
    progress_bar.progress(0.75)
    resultado_da_avaliacao = agente_avaliador(f"{resultado_da_revisao}\n\n{formulario}")

    info_placeholder.info("Finalizando a análise e gerando conclusões...")
    progress_bar.progress(0.95)
    resultado_da_analise = agente_analista(f"{resultado_da_revisao}\n\n{resultado_da_avaliacao}")

    info_placeholder.empty()  # Remove the info message after processing
    progress_bar.empty()      # Remove the progress bar
    st.session_state['analysis_running'] = False
    return (resultado_da_revisao, resultado_da_avaliacao, resultado_da_analise)

# Email validation
def is_valid_email(email):
    # Simple regex for email validation
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(pattern, email) is not None


def clean_name_input(name):
    # Permite apenas letras (incluindo acentos) e espaços
    return re.sub(r"[^A-Za-zÀ-ÿ\s]", "", name)

# Only generate the report when the download button is pressed
def generate_relatorio(opcao, repostas_descritivas, formulario_respostas):
    relatorio = agente_gerador_de_relatorio(f"Opção de patente: {opcao}\n\n{repostas_descritivas}\n\n{formulario_respostas}")       
    st.session_state['relatorio_texto'] = relatorio
    data_to_save_df = info_to_data_frame(st.session_state.userData, st.session_state.questionsData, st.session_state.ideaData)
    append_data_to_sheet("Dados InovaFacil", data_to_save_df)
    return relatorio
