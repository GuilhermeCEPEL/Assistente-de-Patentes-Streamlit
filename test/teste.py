from crewai import Agent, Task, Crew, Process # Assumindo que você está usando CrewAI
from crewai_tools import SerperDevTool # Exemplo de ferramenta para busca web, pode ser substituída por Google Search
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import google_search
from google.genai import types # Para criar conteúdos (Content e Part)
import streamlit as st
import os
import re

from datetime import date
from functions.agents_functions import *
from functions.sheet_functions import *
from functions.auxiliar_functions import *

# Importações para Google Sheets
# Instancie a ferramenta de busca. Se você estiver usando Google Search diretamente,
# pode ser necessário configurá-lo de forma similar ou importá-lo do seu ambiente.
# Por exemplo: Google Search = GoogleSearchTool() se você tiver essa ferramenta.
# Para este exemplo, estou usando SerperDevTool como um placeholder.
# Google Search = SerperDevTool()

# Acessa a API Key de forma segura através dos Streamlit Secrets
# O nome da chave 'GOOGLE_API_KEY' deve corresponder ao que você definirá no Streamlit Cloud
api_key = st.secrets["GOOGLE_API_KEY"]

# Configura a variável de ambiente para as bibliotecas Google
os.environ["GOOGLE_API_KEY"] = api_key


# Função auxiliar que envia uma mensagem para um agente via Runner e retorna a resposta final
def call_agent(agent: Agent, message_text: str) -> str:
  # Cria um serviço de sessão em memória
  session_service = InMemorySessionService()
  # Cria uma nova sessão (você pode personalizar os IDs conforme necessário)
  session = session_service.create_session(app_name=agent.name, user_id="user1", session_id="session1")
  # Cria um Runner para o agente
  runner = Runner(agent=agent, app_name=agent.name, session_service=session_service)
  # Cria o conteúdo da mensagem de entrada
  content = types.Content(role="user", parts=[types.Part(text=message_text)])

  final_response = ""
  # Itera assincronamente pelos eventos retornados durante a execução do agente
  for event in runner.run(user_id="user1", session_id="session1", new_message=content):
    if event.is_final_response():
     for part in event.content.parts: # type: ignore
      if part.text is not None:
       final_response += part.text
       final_response += "\n"
  return final_response


def agente_pesquisa_pdi_aneel(topico):    
  agente = Agent(
        name="agente_pesquisa_pdi_aneel",
        model="gemini-2.5-flash-preview-05-20", # Mantendo o mesmo modelo do seu exemplo
        description="Agente especializado em pesquisar e identificar projetos de Pesquisa, Desenvolvimento e Inovação (PDI) regulados ou financiados pela ANEEL, com base em um tópico de interesse.",
        tools=[google_search], # Usaremos Google Search para rastrear diversas fontes
        instruction="""
        Seu papel é atuar como um especialista em identificação de projetos de PDI da ANEEL.
        Sua principal tarefa é vasculhar a internet utilizando as ferramentas de busca disponíveis
        para encontrar **projetos de PDI, artigos, relatórios ou publicações que mencionem a ANEEL**
        e que estejam diretamente relacionados ao tópico fornecido pelo usuário.

        Ao realizar a pesquisa, concentre-se em:
        1. **Fontes oficiais e acadêmicas:** Priorize buscas em sites da ANEEL, empresas do setor elétrico
           que desenvolvem PDI (ex: Eletrobras, CPFL, Light, Neoenergia, etc.), universidades, centros de pesquisa,
           bases de dados de artigos científicos (como Scielo, Google Scholar) e repositórios de teses e dissertações.
        2. **Termos-chave:** Use o tópico fornecido e sinônimos relevantes, além de termos como
           "PDI ANEEL", "projeto de pesquisa ANEEL", "inovação energética ANEEL" para refinar a busca.
        3. **Extração de informações:** Para cada projeto relevante encontrado, tente extrair o máximo de informações possível,
           como:
           - **Nome do Projeto:** (se disponível)
           - **Empresa/Instituição Executora:**
           - **Ano/Período de Execução:** (se disponível)
           - **Breve descrição:** (o que o projeto aborda)
           - **Link/Fonte:** (onde a informação foi encontrada)

        **Seu resultado final deve ser uma lista concisa dos projetos de PDI da ANEEL encontrados que se relacionam com o tópico,
        apresentando as informações extraídas de forma clara e organizada (pode ser em formato de lista ou tabela).
        Se não encontrar projetos diretos, você pode listar artigos ou iniciativas que abordem o tema sob o guarda-chuva da ANEEL.**

        Não se introduza no início da resposta. Vá direto ao ponto com os resultados da pesquisa.
        """
    )
  
  entrada_do_agente= f"Tópico: {topico}"
  # Executa o agente

  resultado_do_agente = call_agent(agente, entrada_do_agente)

  return resultado_do_agente 

# --- Exemplo de como usar a função ---
if __name__ == "__main__":
    # Exemplo de uso:
    topico_desejado = "armazenamento de energia em baterias"
    print(f"Buscando projetos de PDI da ANEEL sobre: '{topico_desejado}'...\n")
    projetos_encontrados = agente_pesquisa_pdi_aneel(topico_desejado)
    print("--- Projetos de PDI ANEEL encontrados ---")
    print(projetos_encontrados)

    print("\n----------------------------------------\n")

    topico_desejado_2 = "redes elétricas inteligentes"
    print(f"Buscando projetos de PDI da ANEEL sobre: '{topico_desejado_2}'...\n")
    projetos_encontrados_2 = agente_pesquisa_pdi_aneel(topico_desejado_2)
    print("--- Projetos de PDI ANEEL encontrados ---")
    print(projetos_encontrados_2)