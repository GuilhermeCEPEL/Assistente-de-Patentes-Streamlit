import streamlit as st

# Importações para Google Sheets
import gspread
from gspread_dataframe import set_with_dataframe
import json # Para carregar as credenciais do secrets

# --- Funções para Google Sheets ---
def get_sheets_client():
  # Carrega as credenciais da conta de serviço dos Streamlit Secrets
  # Converte o AttrDict para um dicionário Python antes de serializar para JSON
  credentials_dict = dict(st.secrets["google_sheets_credentials"])
  credentials_json = json.dumps(credentials_dict)
  gc = gspread.service_account_from_dict(json.loads(credentials_json))
  return gc

@st.cache_resource(ttl=3600) # Cache o cliente para evitar múltiplas autenticações
def get_spreadsheet(sheet_name):
  client = get_sheets_client()
  spreadsheet = client.open(sheet_name)
  return spreadsheet

def append_data_to_sheet(sheet_name, dataframe):
  # Use uma chave de sessão para controlar se já foi salvo antes
  if 'already_saved_to_sheet' not in st.session_state or st.session_state['already_saved_to_sheet'] == False:
    try:
      spreadsheet = get_spreadsheet(sheet_name)
      worksheet = spreadsheet.sheet1 # Ou use spreadsheet.worksheet("Nome da sua Aba")

      # Se a planilha estiver vazia, escreve o cabeçalho e os dados
      if not worksheet.get_all_values():
        set_with_dataframe(worksheet, dataframe)
      else:
        # Encontra a próxima linha vazia e anexa os dados
        # Convertendo DataFrame para lista de listas sem o cabeçalho para anexar
        list_of_lists = dataframe.values.tolist()
        worksheet.append_rows(list_of_lists)
      st.session_state['already_saved_to_sheet'] = True
    #   st.success("Dados salvos no Google Sheets com sucesso!")
    except Exception as e:
      st.error(f"Erro ao salvar dados no Google Sheets: {e}")
      st.info("Por favor, verifique se as credenciais estão corretas e a planilha está compartilhada com a conta de serviço.")
  else:
    try:
      spreadsheet = get_spreadsheet(sheet_name)
      worksheet = spreadsheet.sheet1
      # Remove apenas a última linha de dados (mantendo o cabeçalho)
      all_values = worksheet.get_all_values()
      if len(all_values) > 1:
        worksheet.delete_rows(len(all_values))
      # Adiciona a nova linha de dados
      list_of_lists = dataframe.values.tolist()
      worksheet.append_rows(list_of_lists)
      # st.success("Última linha sobrescrita no Google Sheets com sucesso!")
    except Exception as e:
      st.error(f"Erro ao sobrescrever dados no Google Sheets: {e}")
      st.info("Por favor, verifique se as credenciais estão corretas e a planilha está compartilhada com a conta de serviço.")

