import streamlit as st
import time
import os
import pandas as pd
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import google_search
from google.genai import types # Para criar conteúdos (Content e Part)
from google import genai
from datetime import date
import textwrap # Para formatar melhor a saída de texto
from IPython.display import HTML, Markdown
import re

# Importações para Google Sheets
import gspread
from gspread_dataframe import set_with_dataframe
import json # Para carregar as credenciais do secrets

# Acessa a API Key de forma segura através dos Streamlit Secrets
# O nome da chave 'GOOGLE_API_KEY' deve corresponder ao que você definirá no Streamlit Cloud
api_key = st.secrets["GOOGLE_API_KEY"]

# Configura a variável de ambiente para as bibliotecas Google
os.environ["GOOGLE_API_KEY"] = api_key

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
  if 'already_saved_to_sheet' not in st.session_state:
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
      st.success("Dados salvos no Google Sheets com sucesso!")
    except Exception as e:
      st.error(f"Erro ao salvar dados no Google Sheets: {e}")
      st.info("Por favor, verifique se as credenciais estão corretas e a planilha está compartilhada com a conta de serviço.")
  else:
    try:
      spreadsheet = get_spreadsheet(sheet_name)
      worksheet = spreadsheet.sheet1
      # Limpa a planilha e sobrescreve com o novo DataFrame
      worksheet.clear()
      set_with_dataframe(worksheet, dataframe)
      st.success("Dados sobrescritos no Google Sheets com sucesso!")
    except Exception as e:
      st.error(f"Erro ao sobrescrever dados no Google Sheets: {e}")
      st.info("Por favor, verifique se as credenciais estão corretas e a planilha está compartilhada com a conta de serviço.")


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
     for part in event.content.parts:
      if part.text is not None:
       final_response += part.text
       final_response += "\n"
  return final_response


##########################################
# --- Agente 3: Sugestor de inovações --- #
##########################################

def agente_sugestor(topico):
  buscador = Agent(
    name="agente_sugestor",
    model="gemini-2.5-flash-preview-05-20",
    description="Agente que analisa a patente de usuário e as patentes existentes para sugerir inovações que podem ser patenteadas",
    tools=[google_search],
    instruction="""
    Seu papel é o de um catalisador de inovação em propriedade intelectual. Diante da patente do usuário 
    e de um conjunto de patentes similares, seu objetivo é gerar duas categorias de sugestões:
    

    1. dentificar áreas de melhoria: Analisar a patente do usuário em busca de pontos fracos, 
    limitações ou funcionalidades que poderiam ser aprimoradas.
    
    2. Aprimoramentos patenteáveis: Inovações específicas que podem ser incorporadas à patente do usuário, 
    conferindo-lhe originalidade e distinguindo-a do estado da técnica.

    3. Novas invenções relacionadas: Ideias inéditas e com potencial de patenteamento que emergem da análise
    do contexto tecnológico apresentado.

    Além disso, quando fizer o resultado, não precisa se introduzir.
    """
  )

  entrada_do_agente_sugestor = f"Tópico: {topico}"
  # Executa o agente
  resultado_do_agente = call_agent(buscador, entrada_do_agente_sugestor)

  return resultado_do_agente 

##########################################
# --- Agente 4: Buscador Formatador --- #
##########################################

def agente_formatador(topico):
  buscador = Agent(
    name="agente_buscador_de_PI",
    model="gemini-2.5-flash-preview-05-20",
    description="Agente que irá formatar a descrição da patente no formato no INPI",
    tools=[google_search],
    instruction="""
    Você é um formatador e gerador de documentos para patentes no formato do INPI. Você deve analizar a descrição da 
    patente fornecida pelo usuário e gerar o Resumo e o Resumo descritivo de acordo com os padrões do INPI. 
    
    Além disso, quando fizer o resultado, não precisa se introduzir.
    
    Siga as diretrizes a seguir:

    RESUMO
        TÍTULO DO SEU PEDIDO DE PATENTE (deve ser idêntico ao informado no formulário de depósito)

        Escreva um resumo da sua invenção aqui em um único parágrafo de no máximo 25 linhas. Indique o setor técnico 
        da sua invenção e faça uma breve descrição dela dando informações essenciais sobre o que a caracteriza e o que 
        a diferencia do estado da técnica. Esta seção do pedido de patente é muito utilizada nas buscas feitas pelos 
        examinadores e também por outros interessados.

    RELATÓRIO DESCRITIVO

        TÍTULO DO SEU PEDIDO DE PATENTE (deve ser idêntico ao informado no formulário de depósito)

    Campo da invenção
    [001]	Descreva aqui o setor técnico ao qual se refere sua invenção. O setor técnico pode ser 
    composições de tintura capilar, máquinas para semeadura ou comunicações de rede sem fio, por exemplo.
    Se sua invenção puder ser aplicada em mais de um campo técnico cite todos eles.

    Fundamentos da invenção
    [002]	Escreva aqui o estado da técnica relacionado à sua invenção, ou seja, aquilo que já se conhece sobre 
    inventos parecidos com o seu. Procure apresentar as características mais importantes desses inventos. É isso 
    o que pede o artigo 2°, inciso IV, da Instrução Normativa n° 30/2013. Use quantos parágrafos forem necessários.
    [003]	Em seguida, você deve apresentar o problema técnico que ainda não foi solucionado pelo estado da técnica 
    e mostrar como sua invenção resolve esse problema. Ou seja, você deve mostrar as diferenças da sua invenção em 
    relação às invenções do estado da técnica e apresentar as vantagens da sua. É muito importante destacar o benefício 
    ou efeito técnico da sua invenção (mais eficiente, mais barata, ocupa menos espaço, não contém elementos tóxicos 
    para o meio ambiente etc), pois o examinador de patentes levará isso em consideração durante o exame do seu pedido
    de patente.

    Breve descrição dos desenhos
    [004]	Se o seu pedido de patente tiver desenhos (podem ser figuras, gráficos ou desenhos propriamente ditos) 
    descreva de forma breve as informações apresentadas em cada um dos desenhos. Uma a duas linhas são suficientes 
    para essa descrição. As linhas que contêm as descrições dos desenhos não precisam conter numeração sequencial 
    dos parágrafos. Por exemplo:
        A Figura 1 apresenta os resultados do teste de absorção da amostra X.
        A Figura 2 ilustra a vista frontal do objeto Y.
        A Figura 3 apresenta o efeito sinérgico da associação dos ingredientes A e B na inibição do crescimento de bactérias.
        A Figura 4 apresenta a vista de uma seção transversal de uma modalidade do instrumento cirúrgico.

    Descrição da invenção
    [005]	Essa é a maior seção do relatório descritivo, que pode ter de poucas até centenas de páginas. Apresente de 
    forma detalhada sua invenção nessa seção e inclua todas as suas possibilidades de concretização. Você pode iniciar 
    por uma ideia geral da invenção para detalhá-la melhor nos parágrafos seguintes. Mais importante do que escrever muitas 
    páginas sobre sua invenção é descrevê-la de forma clara e precisa, de forma que o examinador de patentes possa entender 
    o que você inventou e como sua invenção funciona.
    [006]	Lembre-se de que todas as informações importantes para que alguém possa reproduzir sua invenção devem estar descritas
    nessa seção (essa pessoa é chamada de forma genérica na lei de “técnico no assunto”). Essas mesmas informações serão utilizadas
    pelo examinador de patentes para poder avaliar sua invenção e decidir se seu pedido pode ser deferido ou não. É isso o que 
    exige o artigo 24 da LPI (Lei da Propriedade Industrial - Lei n° 9.279/1996).
    [007]	Lembre-se de que sua invenção só pode se referir a um único conceito inventivo, ou seja, ela só pode resolver 
    um único problema técnico ou problemas técnicos inter-relacionados. Isso significa que se você inventou um novo motor
    Para carros e também um novo sistema de freios para carros, por exemplo, por mais que ambas as invenções sejam 
    destinadas para uso em carros, elas resolvem problemas técnicos diferentes e, portanto, não possuem o mesmo conceito
    inventivo. É isso o que exige o artigo 22 da LPI e o artigo 2°, inciso II, da Instrução Normativa n° 30/2013.

    Exemplos de concretizações da invenção
    [008]	Nesta seção do relatório descritivo você deve apresentar exemplos de concretizações da sua invenção, seja 
    ela um composto, uma composição, um equipamento, um processo etc. Se for o caso, você deve também indicar qual é 
    a forma preferida de concretizar sua invenção. Por exemplo, se sua invenção for uma composição, você deve indicar
    qual composição (ou tipo de composição) é preferida dentre as várias possíveis composições que sua invenção representa.
    [009]	Dependendo das características da sua invenção, pode ser essencial que você apresente os resultados de testes 
    comparativos da sua invenção com outros inventos para demonstrar as vantagens da sua invenção, por exemplo. Se esse 
    for o seu caso, não deixe de colocar essas informações aqui para aumentar as chances de ter seu pedido deferido. 
    Lembre-se de que tabelas devem ser colocadas nessa seção do pedido, enquanto gráficos, desenhos ou outras figuras 
    devem ser colocados na seção Desenhos.
    [0010]	Outro importante ponto de atenção é: qualquer informação essencial ao exame e à patenteabilidade do seu 
    pedido não poderá ser inserida depois que você solicitar o exame do pedido (por meio dos códigos de serviço 203 ou 284)! 
    Isso significa que seu pedido pode ser indeferido pelo INPI caso essa informação não esteja no pedido até o requerimento 
    de exame, mesmo que sua invenção seja considerada nova e inventiva, sem chance de recurso contra essa decisão. É isso 
    o que exigem o artigo 32 da LPI e a Resolução n° 93/2013.        

    """
  )
  entrada_do_agente_formatador = f"Tópico: {topico}"
  # Executa o agente
  resultado_do_agente = call_agent(buscador, entrada_do_agente_formatador)

  return resultado_do_agente 

##########################################
# --- Agente 1: Buscador de Patentes --- #
##########################################

def agente_revisor(topico):
  agente = Agent(
    name="agente_revisor",
    model="gemini-2.5-flash-preview-05-20",
    description="Agente que irá revisar a busca feita por outro agente e verificar se as informações da busca estão corretas",
    tools=[google_search],
    instruction="""
      Como Agente Revisor, sua função é garantir a precisão e integridade dos dados de Propriedades Intelectuais (PIs) coletados
      pelo Agente Buscador.

      Você receberá uma lista de PIs encontradas e deverá realizar uma verificação minuciosa de cada item, com os seguintes critérios:

      - Coerência da Informação: Analise se os dados descritos para cada PI (título, resumo, inventores, etc.) 
      correspondem de forma exata e completa ao conteúdo da própria PI.
      - Validade e Correção dos Links: Confirme se os links fornecidos são válidos, funcionais e direcionam diretamente para a PI 
      correspondente. Links incorretos, quebrados ou gerados como exemplo devem ser substituídos pelo link oficial e correto da PI ou 
      uma justificativa de porque não foi possível obter o link.
      - Completude dos Dados: Verifique se todas as informações essenciais da PI estão presentes na lista. PIs incompletas devem 
      ser corrigidas e complementadas com os dados ausentes.

      Reescreva a lista seguindo as seguintes ações a serem tomadas:

      - Correção: Inconsistências, links errados e informações incompletas devem ser corrigidos e atualizados diretamente na lista 
      de PIs.
      - Remoção: PIs que não puderem ser encontradas ou verificadas através dos links fornecidos devem ser removidas da lista final.
      Após a revisão e correção da lista de PIs, sua tarefa final será reavaliar e reescrever as conclusões e análises previamente 
      elaboradas pelo Agente Buscador, assegurando que elas reflitam precisamente a nova lista de PIs validada e corrigida.
    """
  )

  entrada_do_agente = f"Tópico: {topico}"
  # Executa o agente
  lancamentos_buscados = call_agent(agente, entrada_do_agente)

  return lancamentos_buscados 


##########################################
# --- Agente 1: Buscador de Patentes --- #
##########################################

def agente_buscador_de_PI(topico):
  buscador = Agent(
    name="agente_buscador_de_PI",
    model="gemini-2.5-flash-preview-05-20",
    description="Agente que busca se ja existe alguma propriedade intelectual similar a ideia que o usuário quer desenvolver",
    tools=[google_search],
    instruction="""
    Atuando como um pesquisador de propriedade intelectual (PI), sua responsabilidade é investigar a existência de propriedade 
    intelectual similares àquela que o usuário pretende desenvolver. O usuário irá providenciar uma descrição da ideia ou invenção
    e responderá as seguintes questões:

    - Você já desenvolveu algo (protótipo, código, apresentação)?:
    - Qual é o setor de aplicação?:
    
    A partir disso, você deverá analizar as informações fornecidas para realizar uma busca abrangente para identificar 
    possíveis propiedades intelectuais (patentes, marcas, direitos autorais, softwares, etc.) que possam ser similares 
    e determinar se a patente do usuário é original ou não.
    
    Para isso, utilize as ferramentas de busca de propriedades intelectuais como INPI (Registro de programa de computador,
    Busca de Marca Busca Web), Google Patents, PATENTSCOPE, Espacenet, TMView, GitHub, Creative Commons Search, Lens.org,
    Dewent Innovation, Wayback Machine, Google Scholar, entre outras. A pesquisa deve abranger termos em português e inglês, explorando
    sinônimos e palavras relacionadas.

    O resultado da sua pesquisa deve conter a descrição da ideia do usuário, seguida divida em duas listas de 
    patentes relevantes: (1) lista de propriedades intelectuais brasileiras e (2) lista de propriedades intelectuais internacionais.
    As listas irão conter os seguintes detalhes para cada item: identificador do documento (um número de identificação do documento 
    único em que o usuário possa se referir como o DOI no caso de um artigo), título da PI, um link para acessar essa PI (Não gere um 
    link falso ou exemplo, caso não consiga um link, justifique por que não conseguiu), resumo em português (descrição do que se trata
    essa PI), comparação (onde será feita uma análise comparando a ideia descrita pelo usuário com essa PI) e outras informações que 
    podem ser relevantes.

    Siga o seguinte formato para a listagem no resultado:

    1. Lista de Propriedades Intelectuais Brasileiras

      - Identificador do Documento:

        - Título da PI: Plantas sob controle: 
        - Link para Acessar a PI: 
        - Resumo em Português: 
        - Comparação:
        - Outras informações relevantes: 
        \n\n

        ...

    ------------------------------------------------------------------------------------
        
    2. Lista de Propriedades Intelectuais Internacionais

      - Identificador do Documento:

        - Título da PI: Plantas sob controle: 
        - Link para Acessar a PI: 
        ...
    
    Além disso, quando fizer o resultado, não precisa se introduzir.
    """
  )

  entrada_do_agente = f"Tópico: {topico}"
  # Executa o agente
  lancamentos_buscados = call_agent(buscador, entrada_do_agente)

  return lancamentos_buscados 

##########################################
# --- Agente 5: Agente Recomendador --- #
##########################################

def agente_recomendador(topico):
  agente = Agent(
    name="agente_recomendador",
    model="gemini-2.5-flash-preview-05-20",
    description="Agente que analisa o formulário preenchido pelo usuário e faz uma recomendação de como proceder",
    tools=[google_search],
    instruction="""
    Seu papel é instruir o usuário sobre se é possível criar uma propriedade intelectual baseado no formulário preenchido. O usuário 
    respondeu as seguintes perguntas:
    A ideia é apenas um algoritmo isolado ou método matemático
    A ideia é uma metodologia de ensino, gestão, negócios ou treinamento
    A ideia é puramente software (sem aplicação técnica específica)
    A ideia resolve um problema técnico com uma solução técnica (ex: dispositivo, sistema físico, mecanismo)?
    A solução é nova? (Não existe algo igual já divulgado ou patenteado?
    A solução é inventiva? (Não é óbvia para um técnico no assunto?
    Tem aplicação industrial? (Pode ser fabricada, usada ou aplicada em algum setor produtivo?)

    Além disso, será providenciada uma descrição da ideia ou invenção a partir das seguintes perguntas:
    Descrição da ideia ou invenção:
    Qual é o diferencial ou inovação da sua ideia?:
    Você já desenvolveu algo (protótipo, código, apresentação)?:
    Qual é o setor de aplicação?:

    Baseado nas respostas avalie se é possível tornar essa ideia uma propriedade intelectual. Caso seja possível,
    direcione para o usuário como é possível fazer isso (tornar uma patente, registro de software, etc). Caso não seja possível,
    explique o porquê e o que pode ser feito para tornar essa ideia uma propriedade intelectual.

    Além disso, quando fizer o resultado, não precisa se introduzir.
    """
  )

  entrada_do_agente= f"Tópico: {topico}"
  # Executa o agente
  resultado_do_agente = call_agent(agente, entrada_do_agente)

  return resultado_do_agente 

def agente_avaliador(topico):
  agente = Agent(
    name="agente_recomendador",
    model="gemini-2.5-flash-preview-05-20",
    description="Agente que avalia o potencial da ideia baseado nas análises feitas pelos outros agentes",
    tools=[google_search],
    instruction="""
    Seu papel será avaliar o potencial da ideia do usuário baseado nas análises feitas pelos outros agentes. Seu objetivo será
    fazer uma avaliação detalhada dos pontos fortes e fracos da ideia, avaliando a possibilidade de tornar a ideia uma propriedade
    intelectual (PI), considerando as informações fornecidas.

    Você deverá gerar uma nota realista de 0 até 10 para o potencial da ideia utilizando a pesquisa de PIs realizada anteriormente
    seguindo os seguintes critérios:
    - Inovação: A ideia apresenta uma abordagem nova ou uma solução inovadora para um problema existente?
    - Originalidade: A ideia é única e não existem soluções similares disponíveis?
    - Potencial de Propriedade Intelectual: A ideia tem características que a tornam passível de proteção legal, como patenteabilidade 
    ou registro de software?
    A nota deve ser uma escala de 0 a 10, onde cada critério deve ser avaliado de 0 a 10, e a nota final será a média aritmética dos
    critérios avaliados.

    Você deve fornecer um título que resuma a avaliação, as notas para cada critério e um breve justificativa da nota dada para cada
    critérito.

    O resultado deve seguir o seguinte formato:

    X/10 - 'titulo que resuma a avaliação'\n
    x/10 - Inovação: 'justificativa breve da nota'\n
    x/10 - Originalidade: 'justificativa breve da nota'\n
    x/10 - Potencial de Propriedade Intelectual: 'justificativa breve da nota'

    Além disso, quando fizer o resultado, não precisa se introduzir.
    """
  )

  entrada_do_agente= f"Tópico: {topico}"
  # Executa o agente

  resultado_do_agente = call_agent(agente, entrada_do_agente)

  return resultado_do_agente 

def agente_analista(topico):
  agente = Agent(
    name="agente_analista",
    model="gemini-2.5-flash-preview-05-20",
    description="Agente que analisa a lista de propriedades intelectuais e as recomendações feitas pelos outros agentes para fazer uma conclusão final",
    tools=[google_search],
    instruction="""
    Como Agente Analista, sua responsabilidade é sintetizar e interpretar as informações fornecidas pelo Agente Buscador (lista de
    Propriedades Intelectuais - PIs) e as recomendações do Agente Recomendador. Seu objetivo final é gerar uma conclusão definitiva
    sobre o potencial de patenteabilidade/proteção da ideia do usuário como Propriedade Intelectual.

    Sua análise deve abranger:

    Originalidade e Novidade: Avaliar a originalidade da ideia do usuário em relação às PIs existentes, determinando se ela é 
    nova e não óbvia.
    Viabilidade de Proteção: Concluir se a ideia pode ser efetivamente protegida como Propriedade Intelectual (patente, registro,
    etc.), justificando a viabilidade ou não.
    Caminhos e Estratégias: Caso a proteção seja viável, delinear os possíveis caminhos e estratégias para formalizar a ideia como
    uma PI, incluindo tipos de proteção aplicáveis e etapas iniciais.
    Adicionalmente, forneça recomendações estratégicas para aprimoramento da ideia, com base em todas as informações e análises 
    dos agentes anteriores, visando fortalecer seu potencial de proteção ou comercialização.

    Além disso, quando fizer o resultado, não precisa se introduzir.
    """
  )

  entrada_do_agente= f"Tópico: {topico}"
  # Executa o agente

  resultado_do_agente = call_agent(agente, entrada_do_agente)

  return resultado_do_agente 

def agente_de_próximos_passos(topico):
  agente = Agent(
    name="agente_de_próximos_passos",
    model="gemini-2.5-flash-preview-05-20",
    description="Orienta os próximos passos para proteger sua Propriedade Intelectual com base nas suas escolhas.",
    tools=[google_search],
    instruction="""
    Você irá orientar o usuário sobre os próximos passos para proteger sua Propriedade Intelectual (PI) com base na escolha indicada.
    Você receberá uma dentre as seguintes opções: (i) Patente de Invenção, (ii) Modelo de Utilidade ou (iii) Programa de Computador.
    Com base nessa escolha, e em uma análise fornecida que foi reproduzida por um agente analisador você deve fornecer um passo a passo
    detalhado e claro sobre como o usuário pode proceder para proteger sua PI. 

    Além disso, quando fizer o resultado, não precisa se introduzir.
    """
  )

  entrada_do_agente= f"Tópico: {topico}"
  # Executa o agente

  resultado_do_agente = call_agent(agente, entrada_do_agente)

  return resultado_do_agente 

# Function to navigate to the next page
def next_page():
    st.session_state.currentPage += 1

# Function to navigate to the previous page
def prev_page():
    st.session_state.currentPage -= 1

# Function to save data to a CSV file
def info_to_data_frame(user_data, questions_data, idea_data):
  # Combine all data into a single dictionary
  combined_data = {
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
  }
  # Create a DataFrame from the combined data
  df = pd.DataFrame([combined_data])
  return df
  # # Convert DataFrame to CSV string with BOM for Excel compatibility
  # csv_string = df.to_csv(index=False, encoding='utf-8-sig')
  # return csv_string

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

def display_questionnaire_section(title, questions_list):
  st.subheader(f"**{title}**")
  for q in questions_list:
    default_index = None
    if st.session_state.questionsData[q['id']] is True:
      default_index = 0 # 'Sim'
    elif st.session_state.questionsData[q['id']] is False:
      default_index = 1 # 'Não'

    response = st.radio(
      q['text'],
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
  info_placeholder = st.empty()
  info_placeholder.info("🔎 Analisando as respostas... Por favor, aguarde.")

  if not repostas_descritivas.strip() or not formulario.strip():
    info_placeholder.error("⚠️ A descrição da patente não pode estar vazia para a pesquisa.")
    return ("", "", "")
  else:
    info_placeholder.info("⏳ [1/4] Buscando patentes similares...")
    resultado_da_busca = agente_buscador_de_PI(f"{repostas_descritivas}\n\n{formulario}")

    info_placeholder.info("⏳ [2/4] Revisando a lista de propriedades intelectuais encontradas...")
    resultado_da_revisao = agente_revisor(resultado_da_busca)

    info_placeholder.info("⏳ [3/4] Avaliando o potencial da ideia...")
    resultado_da_avaliacao = agente_avaliador(f"{resultado_da_revisao}\n\n{formulario}")

    info_placeholder.info("⏳ [4/4] Finalizando a análise e gerando conclusões...")
    resultado_da_analise = agente_analista(f"{resultado_da_revisao}\n\n{resultado_da_avaliacao}")

    info_placeholder.empty()  # Remove the info message after processing
    return (resultado_da_revisao, resultado_da_avaliacao, resultado_da_analise)

###################################################################################

st.set_page_config(
  page_title="InovaFacil",
  page_icon="💡",
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

# --- Page 1: User Information ---
if st.session_state.currentPage == 1:
  st.markdown("<h1 style='text-align: center;'>Bem-vindo à InovaFácil 💡</h1>", unsafe_allow_html=True)
  st.markdown("<p style='text-align: center; font-size: 1.2rem;'>Sua plataforma inteligente para proteger e inovar ideias.</p>", unsafe_allow_html=True)

  st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

  st.title("Suas Informações")
  st.write("Por favor, preencha seus dados para continuar.")

  def clean_name_input(name):
      # Permite apenas letras (incluindo acentos) e espaços
      return re.sub(r"[^A-Za-zÀ-ÿ\s]", "", name)
  
  raw_name = st.text_input("Nome completo:", value=st.session_state.userData['name'], help="Apenas letras e espaços são permitidos.")
  cleaned_name = clean_name_input(raw_name)
  if raw_name and raw_name != cleaned_name:
      st.warning("O nome deve conter apenas letras e espaços. Caracteres inválidos foram removidos.")
  st.session_state.userData['name'] = cleaned_name

  matricula_input = st.text_input(
      "Matrícula (somente números):",
      value=st.session_state.userData['matricula'],
      key="matricula_input",
      help="Digite apenas números para sua matrícula."
  )
  # Ensure only digits are kept for matricula
  cleaned_matricula = ''.join(filter(str.isdigit, matricula_input))
  if matricula_input and matricula_input != cleaned_matricula:
      st.warning("A matrícula deve conter apenas números. Caracteres inválidos foram removidos.")
  st.session_state.userData['matricula'] = cleaned_matricula


  st.session_state.userData['email'] = st.text_input("Email:", value=st.session_state.userData['email'], help="Seu email para contato.")

  # Check if all user data fields are filled
  is_user_data_complete = all(st.session_state.userData.values())

  st.markdown("---")
  # "Next Page" button, centered
  col1, col2, col3 = st.columns([1, 1, 1])
  with col2:
    if st.button("Continuar", key="prox_page_button_1", disabled=not is_user_data_complete):
      data_to_save_df = info_to_data_frame(st.session_state.userData, st.session_state.questionsData, st.session_state.ideaData)
      append_data_to_sheet("Dados InovaFacil", data_to_save_df)

      next_page()


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
    if st.button("Próxima Página", key="prox_page_button_2", disabled=not are_questions_complete):
      data_to_save_df = info_to_data_frame(st.session_state.userData, st.session_state.questionsData, st.session_state.ideaData)
      append_data_to_sheet("Dados InovaFacil", data_to_save_df)
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
    if st.button("Analisar Ideia", key="prox_page_button_3", disabled=not are_description_fields_complete):
      data_to_save_df = info_to_data_frame(st.session_state.userData, st.session_state.questionsData, st.session_state.ideaData)
      append_data_to_sheet("Dados InovaFacil", data_to_save_df)
      next_page()
      # Clear analysis related session state when moving to analysis page to ensure fresh run
      for key in ['resultado_da_avaliacao', 'resultado_da_busca', 'resultado_da_analise', 'proximos_passos_texto']:
        if key in st.session_state:
          del st.session_state[key]

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


  # Only run analysis if not already in session_state
  if 'resultado_da_busca' not in st.session_state or 'resultado_da_avaliacao' not in st.session_state or 'resultado_da_analise' not in st.session_state:
    with st.spinner("Realizando análise aprofundada da sua ideia..."):
      resultado_da_busca, resultado_da_avaliacao, resultado_da_analise = analise_dos_resultados(repostas_descritivas, formulario_respostas)
    st.session_state['resultado_da_busca'] = resultado_da_busca
    st.session_state['resultado_da_avaliacao'] = resultado_da_avaliacao
    st.session_state['resultado_da_analise'] = resultado_da_analise
  else:
    resultado_da_busca = st.session_state['resultado_da_busca']
    resultado_da_avaliacao = st.session_state['resultado_da_avaliacao']
    resultado_da_analise = st.session_state['resultado_da_analise']

  # Parse the evaluation result for better display
  if resultado_da_avaliacao and isinstance(resultado_da_avaliacao, str) and '\n' in resultado_da_avaliacao:
    titulo_avaliacao, texto_avaliacao = resultado_da_avaliacao.split('\n', 1)
  else:
    titulo_avaliacao = resultado_da_avaliacao if resultado_da_avaliacao else "Avaliação não disponível"
    texto_avaliacao = ""

  st.header("Resultados da Análise da Sua Ideia")
  st.subheader(titulo_avaliacao)
  st.write(texto_avaliacao)

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
    ("Selecione uma opção", "Patente de Invenção", "Modelo de Utilidade", "Programa de Computador"),
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
  col1, col2 = st.columns(2)
  with col1:
    if st.button("Voltar para Descrição da Ideia", key="prev_page_button_4"):
      prev_page()

  with col2:
    
    csv_data = info_to_data_frame(st.session_state.userData, st.session_state.questionsData, st.session_state.ideaData)
      # Convert DataFrame to CSV string with BOM for Excel compatibility
    csv_string = csv_data.to_csv(index=False, encoding='utf-8-sig')

    st.download_button(
      label="💾 Baixar Relatório Completo (CSV)",
      key="download_button",
      data=csv_string,
      file_name=f"relatorio_inovafacil_{date.today()}.csv",
      mime="text/csv",
      help="Baixe um arquivo CSV com todas as suas respostas e os resultados da análise."
    )