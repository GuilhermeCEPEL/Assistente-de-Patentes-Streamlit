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
     for part in event.content.parts:
      if part.text is not None:
       final_response += part.text
       final_response += "\n"
  return final_response



##########################################
# --- Agente 2: Refinador de descrição de patentes existentes --- #
##########################################

def agente_resumidor(topico):
  buscador = Agent(
    name="agente_resumidor",
    model="gemini-2.5-flash-preview-05-20",
    description="Agente que analisa a descrição de patentes existentes e faz um resumo delas com as similaridades e diferenças em relação a patente que o usuário quer desenvolver",
    tools=[google_search],
    instruction="""
    Você é um especialista em descrição comparativa de patentes, sua função é analisar a patente alvo do usuário em 
    relação a um conjunto de patentes similares. Seu processo envolve:

    1. Reproduzir a descrição da patente fornecida pelo usuário.

    2. Elaborar resumos concisos das patentes similares, realçando de forma clara e objetiva as características 
    que se assemelham à invenção descrita pelo usuário.

    O resultado deve seguitar o seguinte formato:
    **1. Descrição da patente do usuário:**

    ...

    **2. Resumos das patentes similares e suas semelhanças:**

    ...

    Abaixo estão os resumos concisos das patentes identificadas, destacando as características similares à sua proposta:

    
    Identificador do documento:
    Título:
    Resumo da Similaridade:

    Além disso, quando fizer o resultado, não precisa se introduzir.
    """
  )

  entrada_do_agente_resumidor = f"Tópico: {topico}"
  # Executa o agente
  resultado_do_agente = call_agent(buscador, entrada_do_agente_resumidor)

  return resultado_do_agente 

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
    name="agente_buscador",
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
# --- Mock de funções Python (para simular o backend real) ---

##########################################
# --- Agente 1: Buscador de Patentes --- #
##########################################

def agente_revisor(topico):
  agente = Agent(
    name="agente_revisor",
    model="gemini-2.5-flash-preview-05-20",
    description="Agente que irá revisar a busca feita por outro agente e verificar se a busca foi completa",
    tools=[google_search],
    instruction="""
    O seu trabalho será revisar uma lista de propriedades intelectuais (PI) que foram buscadas por outro agente. O agente irá lhe informar uma lista de PIs que foram encontradas,
    e você deve analisar se os itens dessa lista realmente existem, se as informações descritas estão coerentes com a PI E, se necessário, atualizar elas informações da lista.
    
    Você deve verificar se as PIs estão completas, se os links estão corretos e se as informações estão em conformidade com a PI encontrada. Caso o link não esteja correto ou seja um
    link gerado como exemplo, você deve buscar o link correto e atualizar a PI na lista final. Caso encontre alguma PI que não esteja completa ou com informações
    incorretas, você deve corrigir as informações e adicionar a PI corrigida na lista final.

    Caso a PI analisada não possa ser encontrada, remova ela da lista final.

    A partir da nova lista final, reavalie as conclusões e análises feitas pelo agente buscador e reescreva-as.

    Além disso, quando fizer o resultado, não precisa se introduzir.
    """
  )

  entrada_do_agente = f"Tópico: {topico}"
  # Executa o agente
  lancamentos_buscados = call_agent(agente, entrada_do_agente)

  return lancamentos_buscados 


##########################################
# --- Agente 1: Buscador de Patentes --- #
##########################################

def agente_buscador(topico):
  buscador = Agent(
    name="agente_buscador",
    model="gemini-2.5-flash-preview-05-20",
    description="Agente que busca se ja existe alguma propriedade intelectual similar a ideia que o usuário quer desenvolver",
    tools=[google_search],
    instruction="""
    Atuando como um pesquisador de propriedade intelectual (PI), sua responsabilidade é investigar a existência de propriedade intelectual
    similares àquela que o usuário pretende desenvolver. O usuário irá providenciar uma descrição da ideia ou invenção e responderá as seguintes questões:

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
    patentes relevantes: (1) lista de propriedades intelectuais brasileiras e (2) lista de propriedades intelectuais internacionais. As listas irão
    conter os seguintes detalhes para cada item: identificador do documento (um número de identificação do documento 
    único em que o usuário possa se referir como o DOI no caso de um artigo), título da PI, um link para acessar essa PI (Não gere um link falso ou exemplo, 
    caso não consiga um link, justifique por que não conseguiu), resumo em português (descrição do que se trata essa PI), comparação (onde será feita uma 
    análise comparando a ideia descrita pelo usuário com essa PI) e outras informações que podem ser relevantes.

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


    Após listar as propriedades intelectuais, você deve fazer uma conclusão das pesquisas feitas, analisando se a ideia do usuário é original ou não,
    
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
    fazer uma avaliação detalhada dos pontos fortes e fracos da ideia, avaliando a possibilidade de tornar a ideia uma propriedade intelectual (PI),
    considerando as informações fornecidas.

    Você deverá gerar uma nota realista de 0 até 10 para o potencial da ideia utilizando a pesquisa de PIs realizada anteriormente seguindo os seguintes critérios:
    - Inovação: A ideia apresenta uma abordagem nova ou uma solução inovadora para um problema existente?
    - Originalidade: A ideia é única e não existem soluções similares disponíveis?
    - Potencial de Propriedade Intelectual: A ideia tem características que a tornam passível de proteção legal, como patenteabilidade ou registro de software?
    A nota deve ser uma escala de 0 a 10, onde cada critério deve ser avaliado de 0 a 10, e a nota final será a média aritmética dos critérios avaliados.

    Você deve fornecer um título que resuma a avaliação, as notas para cada critério e um breve justificativa da nota dada para cada critérito.

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

def exibir_resultado(titulo, conteudo):
  st.info(f"\n{titulo}")
  st.info("=" * 40)
  st.info(textwrap.indent(conteudo, '  '))
  st.info("=" * 40)

# def pesquisar_patentes(descricao: str):
#   """
#   Realiza a busca em bancos de dados de patentes e retorna os resultados dos agentes separadamente.
#   """
#   st.info("🔎 Realizando pesquisa em bancos de dados de patentes... Por favor, aguarde.")
#   # time.sleep(3) # Simula um atraso de rede/processamento

#   if not descricao.strip():
#     return ("⚠️ A descrição da patente não pode estar vazia para a pesquisa.", "", "")
#   else:
#     st.info("\n[1/3] Buscando patentes similares...")
#     patentes_identificadas = agente_buscador(descricao)

#     st.info("\n[2/3] Resumindo patentes encontradas...")
#     resumo_de_patentes = agente_resumidor(patentes_identificadas)

#     st.info("\n[3/3] Sugerindo inovações possíveis...")
#     sugestoes_identificadas = agente_sugestor(resumo_de_patentes)

#     return (patentes_identificadas, resumo_de_patentes, sugestoes_identificadas)

# def gerar_formulario_patente_inpi(descricao: str) -> str:
#   st.info("📄 Gerando formulário de patente no formato INPI... Por favor, aguarde.")

#   if not descricao.strip():
#     return "⚠️ A descrição da patente não pode estar vazia para gerar o formulário."
#   else:  
#     st.info("\nGerando formulário com base na descrição fornecida...")
#     descricao_formatada = agente_formatador(descricao)
#     return descricao_formatada

# Function to navigate to the next page
def next_page():
    st.session_state.currentPage += 1

# Function to navigate to the previous page
def prev_page():
    st.session_state.currentPage -= 1

# Function to save data to a CSV file
def save_data_to_csv(user_data, questions_data, idea_text):
    # Combine all data into a single dictionary
    combined_data = {
        'Nome': user_data['name'],
        'Matricula': user_data['matricula'],
        'Email': user_data['email'],
        'Ideia_Algoritmo_Matematico': 'Sim' if questions_data['q1'] else 'Não' if questions_data['q1'] is not None else '',
        'Ideia_Metodologia': 'Sim' if questions_data['q2'] else 'Não' if questions_data['q2'] is not None else '',
        'Ideia_Software_Puro': 'Sim' if questions_data['q3'] else 'Não' if questions_data['q3'] is not None else '',
        'Ideia_Resolve_Problema_Tecnico': 'Sim' if questions_data['q4'] else 'Não' if questions_data['q4'] is not None else '',
        'Solucao_Nova': 'Sim' if questions_data['q5'] else 'Não' if questions_data['q5'] is not None else '',
        'Solucao_Inventiva': 'Sim' if questions_data['q6'] else 'Não' if questions_data['q6'] is not None else '',
        'Tem_Aplicacao_Industrial': 'Sim' if questions_data['q7'] else 'Não' if questions_data['q7'] is not None else '',
        'Descricao_Ideia': idea_text
    }
    # Create a DataFrame from the combined data
    df = pd.DataFrame([combined_data])
    # Convert DataFrame to CSV string
    csv_string = df.to_csv(index=False, encoding='utf-8')
    return csv_string

def show_form(title, questions):
  st.write("**{}**".format(title))

  # Display each question with radio buttons
  for q in questions:
    # Determine the default index for the radio button based on current state
    if st.session_state.questionsData[q['id']] is True:
      default_index = 0 # 'Sim'
    elif st.session_state.questionsData[q['id']] is False:
      default_index = 1 # 'Não'
    else:
      default_index = None # No selection yet

    response = st.radio(
      q['text'],
      ('Sim', 'Não'),
      key=q['id'], # Unique key for each radio button
      index=default_index # Set initial selection
    )
    # Update session state based on user's selection
    if response == 'Sim':
      st.session_state.questionsData[q['id']] = True
    elif response == 'Não':
      st.session_state.questionsData[q['id']] = False

def analise_dos_resultados(repostas_descritivas, formulario):
  # Use a placeholder container for temporary info messages
  info_placeholder = st.empty()
  info_placeholder.info("🔎 Analisando as respostas ... Por favor, aguarde.")
  # time.sleep(3) # Simula um atraso de rede/processamento
  if not repostas_descritivas.strip() or not formulario.strip():
    info_placeholder.empty()  # Remove the info message
    return ("⚠️ A descrição da patente não pode estar vazia para a pesquisa.", "", "")
  else:
    info_placeholder.info("\n[1/3] Buscando patentes similares...")
    resultado_da_busca = agente_buscador(f"{repostas_descritivas}\n\n{formulario}")

    info_placeholder.info("\n[2/3] Revisando a lista de PIs encontradas...")
    resultado_da_revisao = agente_buscador(resultado_da_busca)

    info_placeholder.info("\n[3/3] Avaliando os resultados...")
    resultado_da_avaliacao = agente_avaliador(f"{resultado_da_revisao}\n\n{formulario}")

    info_placeholder.empty()  # Remove the info message after processing
    return (resultado_da_revisao, resultado_da_avaliacao)

st.set_page_config(
  page_title="InovaFacil",
  page_icon="💡",
  layout="wide",
  initial_sidebar_state="auto"
)

formulario = ""
initialize_session_state = False

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
    st.session_state.questionsData = {
        'q1': None, # A ideia é apenas um algoritmo isolado ou método matemático
        'q2': None, # A ideia é uma metodologia de ensino, gestão, negócios ou treinamento
        'q3': None, # A ideia é puramente software (sem aplicação técnica específica)
        'q4': None, # A ideia resolve um problema técnico com uma solução técnica (ex: dispositivo, sistema físico, mecanismo)?
        'q5': None, # A solução é nova? (Não existe algo igual já divulgado ou patenteado?)
        'q6': None, # A solução é inventiva? (Não é óbvia para um técnico no assunto?)
        'q7': None, # Tem aplicação industrial? (Pode ser fabricada, usada ou aplicada em algum setor produtivo?)
        'q8': None, # A ideia já foi divulgada publicamente? (ex: redes sociais, eventos, artigos)
        'q9': None, # Há intenção de comercializar ou licenciar essa ideia?
        'q10': None, # Tem aplicação industrial? (Pode ser fabricada, usada ou aplicada em algum setor produtivo?)
    }
if 'ideaText' not in st.session_state:
    st.session_state.ideaText = ''

# --- Page 1: User Information ---
if st.session_state.currentPage == 1:
  st.title("💡 InovaFacil - Guia de Ideias")
  st.markdown("Bem-vindo ao seu assistente pessoal para transformar ideias em inovações! Este guia irá ajudá-lo a estruturar sua ideia, responder perguntas importantes e gerar um formulário de patente no formato do INPI. Vamos começar?")


  st.title("Suas Informações")
  st.write("Por favor, preencha seus dados para continuar.")

  # Input fields for user data
  # Nome: não permitir números nem caracteres especiais
  def clean_name_input(name):
      # Permite apenas letras (incluindo acentos) e espaços
      return re.sub(r"[^A-Za-zÀ-ÿ\s]", "", name)

  raw_name = st.text_input("Nome:", value=st.session_state.userData['name'])
  cleaned_name = clean_name_input(raw_name)
  if raw_name != cleaned_name:
      st.warning("O nome deve conter apenas letras e espaços.")
  st.session_state.userData['name'] = cleaned_name

  st.session_state.userData['matricula'] = st.text_input(
      "Matrícula:",
      value=st.session_state.userData['matricula'],
      key="matricula_input"
  )
  # Permitir apenas números
  if st.session_state.userData['matricula'] and not st.session_state.userData['matricula'].isdigit():
      st.warning("A matrícula deve conter apenas números.")
      st.session_state.userData['matricula'] = ''.join(filter(str.isdigit, st.session_state.userData['matricula']))

  st.session_state.userData['email'] = st.text_input("Email:", value=st.session_state.userData['email'])

  # Check if all user data fields are filled
  is_user_data_complete = all(st.session_state.userData.values())

  # "Next Page" button
  if st.button("Próxima Página", key="prox_page_button_1", disabled=not is_user_data_complete):
    next_page()

# --- Page 2: Yes/No Questions ---
elif st.session_state.currentPage == 2:
  st.title("Perguntas de Sim ou Não")
  st.write("Por favor, responda às seguintes perguntas:")

  questions_1 = [
    {'id': 'q1', 'text': 'A ideia é apenas um algoritmo isolado ou método matemático?'},
    {'id': 'q2', 'text': 'A ideia é uma metodologia de ensino, gestão, negócios ou treinamento?'},
    {'id': 'q3', 'text': 'A ideia é puramente software (sem aplicação técnica específica)?'},
  ]

  questions_2 = [
    {'id': 'q4', 'text': 'A ideia resolve um problema técnico com uma solução técnica (ex: dispositivo, sistema físico, mecanismo)?'},
    {'id': 'q5', 'text': 'A solução é nova? (Não existe algo igual já divulgado ou patenteado?)'},
    {'id': 'q6', 'text': 'A solução é inventiva? (Não é óbvia para um técnico no assunto?)'},
    {'id': 'q7', 'text': 'Tem aplicação industrial? (Pode ser fabricada, usada ou aplicada em algum setor produtivo?)'},
  ]

  questions_3 = [
    {'id': 'q8', 'text': 'A ideia já foi divulgada publicamente? (ex: redes sociais, eventos, artigos)'},
    {'id': 'q9', 'text': 'Há intenção de comercializar ou licenciar essa ideia?'},
    {'id': 'q10', 'text': 'Você já desenvolveu um protótipo ou MVP da solução?'},
  ]

  show_form("Natureza da Ideia", questions_1)
  show_form("Critérios de Patenteabilidade", questions_2)
  show_form("Perguntas Adicionais", questions_3)
  
  # Check if all questions are answered
  are_questions_complete = all(value is not None for value in st.session_state.questionsData.values())

  col1, col2 = st.columns(2)
  with col1:
    if st.button("Voltar", key="prev_page_button_2"):
      prev_page()
  with col2:
    if st.button("Próxima Página", key="prox_page_button_2", disabled=not are_questions_complete):
      next_page()
      initialize_session_state = False  
      


# --- Page 3: Idea Description ---
elif st.session_state.currentPage == 3:
  if initialize_session_state == False:
    # Monta o formulário com as respostas do usuário
    formulario = f"""
    **Natureza da Ideia**
    A ideia é apenas um algoritmo isolado ou método matemático: {'Sim' if st.session_state.questionsData['q1'] else 'Não'}
    A ideia é uma metodologia de ensino, gestão, negócios ou treinamento: {'Sim' if st.session_state.questionsData['q2'] else 'Não'}
    A ideia é puramente software (sem aplicação técnica específica): {'Sim' if st.session_state.questionsData['q3'] else 'Não'}
    **Critérios de patenteabilidade**
    A ideia resolve um problema técnico com uma solução técnica (ex: dispositivo, sistema físico, mecanismo)?: {'Sim' if st.session_state.questionsData['q4'] else 'Não'}
    A solução é nova? (Não existe algo igual já divulgado ou patenteado?): {'Sim' if st.session_state.questionsData['q5'] else 'Não'}
    A solução é inventiva? (Não é óbvia para um técnico no assunto?): {'Sim' if st.session_state.questionsData['q6'] else 'Não'}
    Tem aplicação industrial? (Pode ser fabricada, usada ou aplicada em algum setor produtivo?): {'Sim' if st.session_state.questionsData['q7'] else 'Não'}
    A ideia já foi divulgada publicamente? (ex: redes sociais, eventos, artigos): {'Sim' if st.session_state.questionsData['q8'] else 'Não'}
    Há intenção de comercializar ou licenciar essa ideia? {'Sim' if st.session_state.questionsData['q9'] else 'Não'}
    Você já desenvolveu um protótipo ou MVP da solução? {'Sim' if st.session_state.questionsData['q10'] else 'Não'}
    """
    with st.spinner("Analisando as respostas do formulário..."):
        recomendacao = agente_recomendador(formulario)
    initialize_session_state = True

  with st.expander("🔔 Clique para ver a recomendação de protejer sua ideia 🔔", expanded=False):
    st.markdown("#### Recomendação do Assistente")
    st.write(recomendacao)

  st.title("Descreva Sua Ideia")
  st.write("Descreva sua ideia em detalhes para ser feita uma análise mais objetiva. Os campos marcados com * são obrigatórios.")

  # Campos obrigatórios
  st.session_state.ideaText_main = st.text_area(
      "Descreva a sua ideia ou invenção de forma clara e objetiva: *",
      value=st.session_state.get('ideaText_main', ''),
      height=250,
      help="Ex: o que é, para que serve, como funciona."
  )

  st.session_state.ideaText_differential = st.text_area(
      "Qual é o diferencial ou inovação da sua ideia? *",
      value=st.session_state.get('ideaText_differential', ''),
      height=250,
      help="Ex: por que ela é melhor ou diferente das soluções existentes."
  )

  st.session_state.ideaText_dev = st.text_area(
      "Você já desenvolveu algo relacionado a essa ideia?",
      value=st.session_state.get('ideaText_dev', ''),
      height=250,
      help="Ex: protótipo, código, apresentação, etc."
  )

  st.session_state.ideaText_sector = st.text_area(
      "Qual é o setor de aplicação? *",
      value=st.session_state.get('ideaText_sector', ''),
      height=250,
      help="Ex: energia, educação, tecnologia, etc."
  )

  are_questions_complete = st.session_state.ideaText_main.strip() and st.session_state.ideaText_sector.strip() and st.session_state.ideaText_differential.strip()
  
  col1, col2 = st.columns(2)
  with col1:
    if st.button("Voltar", key="prev_page_button_3"):
      prev_page()
  with col2:
    if st.button("Próxima Página", key="prox_page_button_3", disabled=not are_questions_complete):
      next_page()

# --- Page 4: Idea Description ---
elif st.session_state.currentPage == 4:

  repostas_descritivas = f"""
  **Descrição da Ideia**
  Descrição da ideia ou invenção: {st.session_state.ideaText_main}
  Qual é o diferencial ou inovação da sua ideia?: {st.session_state.ideaText_differential}
  Você já desenvolveu algo (protótipo, código, apresentação)?: {st.session_state.ideaText_dev}
  Qual é o setor de aplicação?: {st.session_state.ideaText_sector}
  """
  formulario = f"""
  **Natureza da Ideia**
  A ideia é apenas um algoritmo isolado ou método matemático: {'Sim' if st.session_state.questionsData['q1'] else 'Não'}
  A ideia é uma metodologia de ensino, gestão, negócios ou treinamento: {'Sim' if st.session_state.questionsData['q2'] else 'Não'}
  A ideia é puramente software (sem aplicação técnica específica): {'Sim' if st.session_state.questionsData['q3'] else 'Não'}
  **Critérios de patenteabilidade**
  A ideia resolve um problema técnico com uma solução técnica (ex: dispositivo, sistema físico, mecanismo)?: {'Sim' if st.session_state.questionsData['q4'] else 'Não'}
  A solução é nova? (Não existe algo igual já divulgado ou patenteado?): {'Sim' if st.session_state.questionsData['q5'] else 'Não'}
  A solução é inventiva? (Não é óbvia para um técnico no assunto?): {'Sim' if st.session_state.questionsData['q6'] else 'Não'}
  Tem aplicação industrial? (Pode ser fabricada, usada ou aplicada em algum setor produtivo?): {'Sim' if st.session_state.questionsData['q7'] else 'Não'}
  A ideia já foi divulgada publicamente? (ex: redes sociais, eventos, artigos): {'Sim' if st.session_state.questionsData['q8'] else 'Não'}
  Há intenção de comercializar ou licenciar essa ideia? {'Sim' if st.session_state.questionsData['q9'] else 'Não'}
  Você já desenvolveu um protótipo ou MVP da solução? {'Sim' if st.session_state.questionsData['q10'] else 'Não'}
  """

  # st.write(formulario)

  with st.spinner("Pesquisando..."):
    resultado_da_busca, resultado_da_avaliacao = analise_dos_resultados(repostas_descritivas, formulario)

  # Separa o resultado_da_avaliacao em título e texto usando o primeiro '\n'
  if resultado_da_avaliacao and isinstance(resultado_da_avaliacao, str) and '\n' in resultado_da_avaliacao:
      titulo, texto = resultado_da_avaliacao.split('\n', 1)
  else:
      titulo = resultado_da_avaliacao if resultado_da_avaliacao else "Resultado não disponível"
      texto = ""

  st.title(titulo)
  st.write(texto)
  
  # Exibe a recomendação de forma mais destacada e organizada
  with st.expander("❕ Análise de Propriedades Similares ❕", expanded=False):
    st.markdown("#### Análise de Propriedades Similares")
    st.write(resultado_da_busca)

    
  # st.title("Descreva Sua Ideia")
  # st.write("Por favor, descreva sua ideia em detalhes.")

  # Text area for idea description
  # st.session_state.ideaText = st.text_area(
  #     "Sua Ideia:",
  #     value=st.session_state.ideaText,
  #     height=250
  # )

  col1, col2 = st.columns(2)
  with col1:
      if st.button("Voltar", key="prev_page_button_3"):
          prev_page()
  with col2:
      if st.button("Finalizar Formulário", key="finish_form_button"):
          st.success("Formulário Finalizado! Seus dados e ideia foram submetidos (simulação).")


# st.title("💡 Assistente de Ideias")
# st.markdown("Bem-vindo ao seu assistente pessoal para gerenciar ideias.")

# # Inicializa 'pagina' se ainda não existir na sessão
# if 'pagina' not in st.session_state:
#   st.session_state['pagina'] = '0'

# if st.session_state['pagina'] == '0':
#   # Campos para nome, matrícula e email do usuário
#   st.subheader("👤 Dados do Usuário")
#   col_nome, col_matricula, col_email = st.columns(3)
#   with col_nome:
#       nome_usuario = st.text_input("Nome completo", key="nome_usuario")
#   with col_matricula:
#       matricula_usuario = st.text_input("Matrícula", key="matricula_usuario")
#   with col_email:
#       email_usuario = st.text_input("E-mail", key="email_usuario")
  
#   # Botão para avançar para a próxima página (disponível apenas se nome, matrícula e email estiverem preenchidos)
#   if nome_usuario.strip() and matricula_usuario.strip() and email_usuario.strip():
#     if st.button("➡️ Avançar para a próxima página", type="primary"):
#       st.session_state['pagina'] = '1'



          # st.experimental_rerun() # Normalmente não é necessário se a lógica de exibição estiver bem definida

# if st.session_state['pagina'] == '1':
#   # Adiciona 7 toggle switches no topo da interface
#   st.markdown("### Identificação inicial da ideia")
#   st.markdown(
#       "Responda **Sim** ou **Não** para cada pergunta abaixo, usando os botões deslizantes (toggle):"
#   )
#   col_tog1 = st.columns(1)
#   with col_tog1[0]:
#     toggle1 = st.toggle("A ideia é apenas um algoritmo isolado ou método matemático?", key="toggle1")
#     toggle2 = st.toggle("A ideia é uma metodologia de ensino, gestão, negócios ou treinamento?", key="toggle2")
#     toggle3 = st.toggle("A ideia é puramente software (sem aplicação técnica específica)?", key="toggle3")
#     toggle4 = st.toggle("A ideia resolve um problema técnico com uma solução técnica (ex: dispositivo, sistema físico, mecanismo)?", key="toggle4")
#     toggle5 = st.toggle("A solução é nova? (Não existe algo igual já divulgado ou patenteado?)", key="toggle5")
#     toggle6 = st.toggle("A solução é inventiva? (Não é óbvia para um técnico no assunto?)", key="toggle6")
#     toggle7 = st.toggle("Tem aplicação industrial? (Pode ser fabricada, usada ou aplicada em algum setor produtivo?)", key="toggle7")  

#     if st.button("➡️ Avançar para a próxima página", type="primary"):
#       st.session_state['pagina'] = '2'

#       formulario = """
#       A ideia é apenas um algoritmo isolado ou método matemático: {}
#       A ideia é uma metodologia de ensino, gestão, negócios ou treinamento: {}
#       A ideia é puramente software (sem aplicação técnica específica): {}
#       A ideia resolve um problema técnico com uma solução técnica (ex: dispositivo, sistema físico, mecanismo)?: {}
#       A solução é nova? (Não existe algo igual já divulgado ou patenteado?): {}
#       A solução é inventiva? (Não é óbvia para um técnico no assunto?): {}
#       Tem aplicação industrial? (Pode ser fabricada, usada ou aplicada em algum setor produtivo?): {}
#       """.format(toggle1, toggle2, toggle3, toggle4, toggle5, toggle6, toggle7)

#       recomendacao = agente_buscador(formulario)
    
#       # Exibe a recomendação de forma mais destacada e organizada
#       with st.expander("🔔 Clique para ver a recomendação sobre sua ideia", expanded=True):
#         st.markdown("#### Recomendação do Assistente")
#         st.write(recomendacao)



# # Lógica para navegação de páginas
# elif st.session_state.get('pagina') == '2':
#   st.markdown("## Página 2: Conteúdo Adicional")
  
#   if st.button("⬅️ Retornar para a página anterior", type="primary"):
#     st.session_state['pagina'] = '0'

#   # Campo de texto para a descrição da patente
#   st.subheader("📝 Descrição da Patente")
#   descricao_patente = st.text_area(
#     "Insira aqui a descrição detalhada da sua invenção ou modelo de utilidade:",
#     height=250,
#     help="Descreva sua ideia com o máximo de detalhes possível, incluindo o problema que ela resolve, como funciona, suas características e vantagens.",
#     key="descricao_patente_input" # Adicionado key para gerenciar o estado
#   )

#   # Inicializa as variáveis de resultado no session_state para persistência
#   if 'resultado_pesquisa' not in st.session_state:
#     st.session_state.resultado_pesquisa = ""
#   if 'resultado_resumo' not in st.session_state:
#     st.session_state.resultado_resumo = ""
#   if 'resultado_sugestoes' not in st.session_state:
#     st.session_state.resultado_sugestoes = ""
#   if 'formulario_patente' not in st.session_state:
#     st.session_state.formulario_patente = ""
#   if 'descricao_patente' not in st.session_state:
#     st.session_state.descricao_patente = "" # Para persistir a descrição entre as execuções
#   # if 'ultima_acao' not in st.session_state:
#   #   st.session_state.ultima_acao = None

#   # Atualiza a descrição no session_state quando o text_area muda
#   if descricao_patente != st.session_state.descricao_patente:
#     st.session_state.descricao_patente = descricao_patente
#     # Limpa resultados anteriores se a descrição mudar significativamente
#     st.session_state.resultado_pesquisa = ("", "", "")
#     st.session_state.formulario_patente = ""

#   st.markdown("---") # Divisor visual

#   # Botões de ação
#   col1, col2 = st.columns(2)

#   with col1:
#     if st.button("🔎 Pesquisar Patentes Similares", type="primary", use_container_width=True):
#       if st.session_state.descricao_patente.strip():
#         with st.spinner("Pesquisando..."):
#           patentes, resumo, sugestoes = pesquisar_patentes(st.session_state.descricao_patente)
#           st.session_state.resultado_pesquisa = patentes
#           st.session_state.resultado_resumo = resumo
#           st.session_state.resultado_sugestoes = sugestoes
#           # st.session_state.ultima_acao = "pesquisa"
#       else:
#         st.warning("Por favor, insira uma descrição da patente para pesquisar.")

#   with col2:
#     if st.button("📄 Gerar Formulário de Patente (INPI)", type="secondary", use_container_width=True):
#       if st.session_state.descricao_patente.strip():
#         with st.spinner("Gerando formulário..."):
#           st.session_state.formulario_patente = gerar_formulario_patente_inpi(st.session_state.descricao_patente)
#           # st.session_state.ultima_acao = "formulario" 
#       else:
#         st.warning("Por favor, insira uma descrição da patente para gerar o formulário.")

#   st.markdown("---") # Divisor visual

#   # Área para os outputs
#   st.subheader("Resultado")

#   # Botão para baixar o resultado completo da pesquisa (três agentes)
#   if (
#       st.session_state.resultado_pesquisa
#       and st.session_state.resultado_resumo
#       and st.session_state.resultado_sugestoes
#   ):
#       conteudo_download = (
#           "===== RESULTADO DA PESQUISA DE PATENTES =====\n\n"
#           f"{st.session_state.resultado_pesquisa}\n\n"
#           "===== RESUMO DAS PATENTES E SIMILARIDADES =====\n\n"
#           f"{st.session_state.resultado_resumo}\n\n"
#           "===== SUGESTÕES DE INOVAÇÕES =====\n\n"
#           f"{st.session_state.resultado_sugestoes}\n"
#       )
#       st.download_button(
#           label="Download Resultado Completo da Pesquisa (.txt)",
#           data=conteudo_download,
#           file_name="resultado_completo_pesquisa_patentes.txt",
#           mime="text/plain",
#           help="Clique para baixar todos os resultados dos agentes em um único arquivo.",
#           type="primary",
#           key="download_pesquisa_1"  # <-- Adicione um key único aqui
#       )
#       st.success("✅ Pesquisa Concluída!")

#   if st.session_state.resultado_pesquisa:
#     st.text_area("1️⃣ Resultado da Pesquisa de Patentes:",
#           value=st.session_state.resultado_pesquisa,
#           height=200,
#           key="output_pesquisa",
#           help="Resultados da busca por patentes similares à sua descrição.")

#   if st.session_state.resultado_resumo:
#     st.text_area("2️⃣ Resumo das Patentes e Similaridades:",
#           value=st.session_state.resultado_resumo,
#           height=200,
#           key="output_resumo",
#           help="Resumo das patentes similares encontradas.")

#   if st.session_state.resultado_sugestoes:
#     st.text_area("3️⃣ Sugestões de Inovações:",
#           value=st.session_state.resultado_sugestoes,
#           height=200,
#           key="output_sugestoes",
#           help="Sugestões de inovações possíveis para sua patente.")


#   # Output do Formulário
#   if st.session_state.formulario_patente:
#     st.success("✅ Formulário Gerado!")
#     st.download_button(
#       label="Download Formulário (.txt)",
#       data=st.session_state.formulario_patente,
#       file_name="formulario_patente_inpi.txt",
#       mime="text/plain",
#       help="Clique para baixar o formulário gerado em formato de texto.",
#       type="secondary"
#     )
#     st.text_area("Formulário de Patente INPI (Simulado):",
#           value=st.session_state.formulario_patente,
#           height=600,
#           key="output_formulario",
#           help="Formulário de patente gerado. Lembre-se que este é um modelo simulado.")

#   st.stop()


# st.markdown("""
# ---
# ### Como funciona?
# Este aplicativo ajuda você a:
# 1. **Pesquisar Patentes:** Insira uma descrição da sua invenção e o sistema simulará a busca por patentes já existentes.
# 2. **Gerar Formulário:** Com base na sua descrição, um modelo simplificado de formulário de patente no padrão INPI será gerado.

# **Importante:** Esta é uma aplicação demonstrativa. Para processos reais de patenteamento, consulte um advogado especializado e os guias oficiais do INPI.
# """)