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
# --- Mock de funções Python (para simular o backend real) ---

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
def save_data_to_csv(user_data, questions_data, idea_text):
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
    'Descricao_Ideia': st.session_state.get('ideaText_main', ''),
    'Diferencial_Ideia': st.session_state.get('ideaText_differential', ''),
    'Desenvolvimento_Relacionado': st.session_state.get('ideaText_dev', ''),
    'Setor_Aplicacao': st.session_state.get('ideaText_sector', ''),
    # Page 3: Recommendation generated
    'Recomendacao_Protecao': st.session_state.get('recomendacao_texto', ''),
    # Page 4: Results
    'Resultado_Analise_PI': st.session_state.get('resultado_da_busca', ''),
    'Resultado_Avaliacao': st.session_state.get('resultado_da_avaliacao', ''),
  }
  # Create a DataFrame from the combined data
  df = pd.DataFrame([combined_data])
  # Convert DataFrame to CSV string with BOM for Excel compatibility
  csv_string = df.to_csv(index=False, encoding='utf-8-sig')
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

  # Add a divider line after the section
  st.markdown("---")

def analise_dos_resultados(repostas_descritivas, formulario):
  # Use a placeholder container for temporary info messages
  info_placeholder = st.empty()
  info_placeholder.info("🔎 Analisando as respostas ... Por favor, aguarde.")
  # time.sleep(3) # Simula um atraso de rede/processamento
  if not repostas_descritivas.strip() or not formulario.strip():
    info_placeholder.empty()  # Remove the info message
    return ("⚠️ A descrição da patente não pode estar vazia para a pesquisa.", "", "")
  else:
    info_placeholder.info("\n[1/4] Buscando patentes similares...")
    resultado_da_busca = agente_buscador_de_PI(f"{repostas_descritivas}\n\n{formulario}")

    info_placeholder.info("\n[2/4] Revisando a lista de propriedades intelectuais encontradas...")
    resultado_da_revisao = agente_revisor(resultado_da_busca)

    info_placeholder.info("\n[3/4] Avaliando os resultados...")
    resultado_da_avaliacao = agente_avaliador(f"{resultado_da_revisao}\n\n{formulario}")

    info_placeholder.info("\n[4/4] Analisando a lisa e a avaliação...")
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

    h1, h2, h3, h4 {
        color: white !important;
    }

    .card {
        background-color: rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        margin-bottom: 20px;
    }

    .stButton button {
        background-color: #ffffff;
        color: #009E49;
        border-radius: 8px;
        padding: 0.5em 2em;
        font-weight: bold;
        border: none;
        transition: background-color 0.3s ease;
    }

    .stButton download_button {
        background-color: #ffffff;
        color: #009E49;
        border-radius: 8px;
        padding: 0.5em 2em;
        font-weight: bold;
        border: none;
        transition: background-color 0.3s ease;
    }
    .stButton button:hover {
        background-color: #00AEEF;
        color: white;
    }

    .divider {
        height: 1px;
        background-color: rgba(255,255,255,0.3);
        margin: 30px 0;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# Adicionando o overlay e o contêiner de conteúdo


formulario = ""
# initialize_session_state = None

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

###################################################################################
# --- Page 1: User Information ---
if st.session_state.currentPage == 1:
  # st.title("💡 InovaFacil - Guia de Ideias")
  # st.markdown("Bem-vindo ao seu assistente pessoal para transformar ideias em inovações! Este guia irá ajudá-lo a estruturar sua ideia, responder perguntas importantes e gerar um formulário de patente no formato do INPI. Vamos começar?")

  st.markdown("<h1 style='text-align: center;'>Bem-vindo à InovaFácil 💡</h1>", unsafe_allow_html=True)
  st.markdown("<p style='text-align: center; font-size: 1.2rem;'>Transformando suas ideias em inovação real.</p>", unsafe_allow_html=True)
  
  st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

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

###################################################################################
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
      if 'recomendacao_gerada' in st.session_state:
        del st.session_state['recomendacao_gerada'] 
      if 'recomendacao_texto' in st.session_state:
        del st.session_state['recomendacao_texto']
      

###################################################################################
# --- Page 3: Idea Description ---
elif st.session_state.currentPage == 3:
  if 'recomendacao_gerada' not in st.session_state:
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
    
    st.session_state['recomendacao_texto'] = recomendacao
    st.session_state['recomendacao_gerada'] = True

  with st.expander("🔔 Clique para ver a recomendação de protejer sua ideia 🔔", expanded=False):
    st.markdown("#### Recomendação do Assistente")
    st.write(st.session_state['recomendacao_texto'])

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
      if 'resultado_da_avaliacao' in st.session_state:
        del st.session_state['resultado_da_avaliacao'] 
      if 'resultado_da_busca' in st.session_state:
        del st.session_state['resultado_da_busca']
      if 'resultado_da_analise' in st.session_state:
        del st.session_state['resultado_da_analise']
      

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

  # Só executa a análise se ainda não estiver salva no session_state
  if 'resultado_da_busca' not in st.session_state or 'resultado_da_avaliacao' not in st.session_state:
    with st.spinner("Pesquisando..."):
      resultado_da_busca, resultado_da_avaliacao, resultado_da_analise = analise_dos_resultados(repostas_descritivas, formulario)
    st.session_state['resultado_da_busca'] = resultado_da_busca
    st.session_state['resultado_da_avaliacao'] = resultado_da_avaliacao
    st.session_state['resultado_da_analise'] = resultado_da_analise
  else:
    resultado_da_busca = st.session_state['resultado_da_busca']
    resultado_da_avaliacao = st.session_state['resultado_da_avaliacao']
    resultado_da_analise = st.session_state['resultado_da_analise']

  # Separa o resultado_da_avaliacao em título e texto usando o primeiro '\n'
  if resultado_da_avaliacao and isinstance(resultado_da_avaliacao, str) and '\n' in resultado_da_avaliacao:
    titulo, texto = resultado_da_avaliacao.split('\n', 1)
  else:
    titulo = resultado_da_avaliacao if resultado_da_avaliacao else "Resultado não disponível"
    texto = ""

  st.title(titulo)
  st.write(texto)
  
  # Exibe a recomendação de forma mais destacada e organizada
  with st.expander("📃 Lista de Propriedades Similares 📃", expanded=False):
    st.markdown("#### Lista de Propriedades Similares")
    st.write(resultado_da_busca)

  # Exibe a recomendação de forma mais destacada e organizada
  with st.expander("❕Análise Final ❕", expanded=False):
    st.markdown("#### Análise Final")
    st.write(resultado_da_analise)

  col1, col2 = st.columns(2)
  with col1:
    if st.button("Voltar", key="prev_page_button_4"):
      prev_page()

  with col2:
    csv_string = save_data_to_csv(st.session_state.userData, st.session_state.questionsData, st.session_state.ideaText)
    st.download_button(
  label="Clique aqui para baixar o CSV",
  key="download_button",
  data=csv_string,
  file_name="respostas_inovafacil.csv",
  mime="text/csv"
    )
    st.success("Formulário Finalizado! Seus dados e ideia foram submetidos (simulação).")

st.markdown('</div>', unsafe_allow_html=True) # Fecha a div de conteúdo