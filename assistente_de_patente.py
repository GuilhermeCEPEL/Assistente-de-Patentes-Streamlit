import streamlit as st
import time
import os
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import google_search
from google.genai import types # Para criar conteúdos (Content e Part)
from google import genai
from datetime import date
import textwrap # Para formatar melhor a saída de texto
from IPython.display import HTML, Markdown

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
# --- Agente 1: Buscador de Patentes --- #
##########################################

def agente_buscador(topico):
  buscador = Agent(
    name="agente_buscador",
    model="gemini-2.0-flash-thinking-exp",
    description="Agente que busca se ja existe alguma patente similar a patente que o usuário quer desenvolver",
    tools=[google_search],
    instruction="""
    Atuando como um pesquisador de patentes, sua responsabilidade é investigar a existência de tecnologias patenteadas
    similares àquela que o usuário pretende desenvolver. O usuário fornecerá uma descrição da patente que deseja
    criar, e você deverá analizar a descrição para realizar uma busca abrangente para identificar patentes 
    que possam ser similares e determinar se a patente do usuário é original ou não.
    
    Para isso, utilize as ferramentas de busca dos bancos de dados INPI, Espacenet, Google Patents e PATENTSCOPE. 
    A pesquisa deve abranger termos em português e inglês, explorando sinônimos e palavras relacionadas.

    O resultado da sua pesquisa deve conter a descrição da patente do usuário, seguida divida em duas listas de 
    patentes relevantes: (1) lista de patentes brasileiras e (2) lista de patentes internacionais. As listas irão
    conster os seguintes detalhes para cada item: identificador do documento um número de identificação do documento 
    único em que o usuário possa se referir), título, número do pedido, número do registro, data de depósito, data 
    de concessão, um link para visualização do documento, resumo (onde será descrito o que se trata essa patente em português) e 
    observações (onde será feita uma análise comparndo a patente descrita pelo usuário com essa patente).

    A lista deve seguir o seguinte formato:
    Identificador do documento:
    Título: 
    Número do pedido:
    Número do registro:
    Data de depósito:
    Data de concessão:
    Link para visualização:
    Observações:
    """
  )

  entrada_do_agente_buscador = f"Tópico: {topico}"
  # Executa o agente
  lancamentos_buscados = call_agent(buscador, entrada_do_agente_buscador)

  return lancamentos_buscados 

##########################################
# --- Agente 2: Refinador de descrição de patentes existentes --- #
##########################################

def agente_resumidor(topico):
  buscador = Agent(
    name="agente_resumidor",
    model="gemini-2.0-flash-thinking-exp",
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
    model="gemini-2.0-flash-thinking-exp",
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
    model="gemini-2.0-flash-thinking-exp",
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


def exibir_resultado(titulo, conteudo):
  st.info(f"\n{titulo}")
  st.info("=" * 40)
  st.info(textwrap.indent(conteudo, '  '))
  st.info("=" * 40)

def pesquisar_patentes(descricao: str):
  """
  Realiza a busca em bancos de dados de patentes e retorna os resultados dos agentes separadamente.
  """
  st.info("🔎 Realizando pesquisa em bancos de dados de patentes... Por favor, aguarde.")
  # time.sleep(3) # Simula um atraso de rede/processamento

  if not descricao.strip():
    return ("⚠️ A descrição da patente não pode estar vazia para a pesquisa.", "", "")
  else:
    st.info("\n[1/3] Buscando patentes similares...")
    patentes_identificadas = agente_buscador(descricao)

    st.info("\n[2/3] Resumindo patentes encontradas...")
    resumo_de_patentes = agente_resumidor(patentes_identificadas)

    st.info("\n[3/3] Sugerindo inovações possíveis...")
    sugestoes_identificadas = agente_sugestor(resumo_de_patentes)

    return (patentes_identificadas, resumo_de_patentes, sugestoes_identificadas)

def gerar_formulario_patente_inpi(descricao: str) -> str:
  st.info("📄 Gerando formulário de patente no formato INPI... Por favor, aguarde.")

  if not descricao.strip():
    return "⚠️ A descrição da patente não pode estar vazia para gerar o formulário."
  else:  
    st.info("\nGerando formulário com base na descrição fornecida...")
    descricao_formatada = agente_formatador(descricao)
    return descricao_formatada

# --- Interface Streamlit ---

st.set_page_config(
  page_title="Assistente de Patente",
  page_icon="💡",
  layout="wide",
  initial_sidebar_state="auto"
)

st.title("💡 Assistente de Patente INPI")
st.markdown("Bem-vindo ao seu assistente pessoal para gerenciar ideias de patentes.")

# Campo de texto para a descrição da patente
st.subheader("📝 Descrição da Patente")
descricao_patente = st.text_area(
  "Insira aqui a descrição detalhada da sua invenção ou modelo de utilidade:",
  height=250,
  help="Descreva sua ideia com o máximo de detalhes possível, incluindo o problema que ela resolve, como funciona, suas características e vantagens.",
  key="descricao_patente_input" # Adicionado key para gerenciar o estado
)

# Inicializa as variáveis de resultado no session_state para persistência
if 'resultado_pesquisa' not in st.session_state:
  st.session_state.resultado_pesquisa = ""
if 'resultado_resumo' not in st.session_state:
  st.session_state.resultado_resumo = ""
if 'resultado_sugestoes' not in st.session_state:
  st.session_state.resultado_sugestoes = ""
if 'formulario_patente' not in st.session_state:
  st.session_state.formulario_patente = ""
if 'descricao_patente' not in st.session_state:
  st.session_state.descricao_patente = "" # Para persistir a descrição entre as execuções
# if 'ultima_acao' not in st.session_state:
#   st.session_state.ultima_acao = None

# Atualiza a descrição no session_state quando o text_area muda
if descricao_patente != st.session_state.descricao_patente:
  st.session_state.descricao_patente = descricao_patente
  # Limpa resultados anteriores se a descrição mudar significativamente
  st.session_state.resultado_pesquisa = ("", "", "")
  st.session_state.formulario_patente = ""


st.markdown("---") # Divisor visual

# Botões de ação
col1, col2 = st.columns(2)

with col1:
  if st.button("🔎 Pesquisar Patentes Similares", type="primary", use_container_width=True):
    if st.session_state.descricao_patente.strip():
      with st.spinner("Pesquisando..."):
        patentes, resumo, sugestoes = pesquisar_patentes(st.session_state.descricao_patente)
        st.session_state.resultado_pesquisa = patentes
        st.session_state.resultado_resumo = resumo
        st.session_state.resultado_sugestoes = sugestoes
        # st.session_state.ultima_acao = "pesquisa"
    else:
      st.warning("Por favor, insira uma descrição da patente para pesquisar.")

with col2:
  if st.button("📄 Gerar Formulário de Patente (INPI)", type="secondary", use_container_width=True):
    if st.session_state.descricao_patente.strip():
      with st.spinner("Gerando formulário..."):
        st.session_state.formulario_patente = gerar_formulario_patente_inpi(st.session_state.descricao_patente)
        # st.session_state.ultima_acao = "formulario" 
    else:
      st.warning("Por favor, insira uma descrição da patente para gerar o formulário.")

st.markdown("---") # Divisor visual

# Área para os outputs
st.subheader("Resultado")

# Botão para baixar o resultado completo da pesquisa (três agentes)
if (
    st.session_state.resultado_pesquisa
    and st.session_state.resultado_resumo
    and st.session_state.resultado_sugestoes
):
    conteudo_download = (
        "===== RESULTADO DA PESQUISA DE PATENTES =====\n\n"
        f"{st.session_state.resultado_pesquisa}\n\n"
        "===== RESUMO DAS PATENTES E SIMILARIDADES =====\n\n"
        f"{st.session_state.resultado_resumo}\n\n"
        "===== SUGESTÕES DE INOVAÇÕES =====\n\n"
        f"{st.session_state.resultado_sugestoes}\n"
    )
    st.download_button(
        label="Download Resultado Completo da Pesquisa (.txt)",
        data=conteudo_download,
        file_name="resultado_completo_pesquisa_patentes.txt",
        mime="text/plain",
        help="Clique para baixar todos os resultados dos agentes em um único arquivo.",
        type="primary",
        key="download_pesquisa_1"  # <-- Adicione um key único aqui
    )
    st.success("✅ Pesquisa Concluída!")

if st.session_state.resultado_pesquisa:
  st.text_area("1️⃣ Resultado da Pesquisa de Patentes:",
        value=st.session_state.resultado_pesquisa,
        height=200,
        key="output_pesquisa",
        help="Resultados da busca por patentes similares à sua descrição.")

if st.session_state.resultado_resumo:
  st.text_area("2️⃣ Resumo das Patentes e Similaridades:",
        value=st.session_state.resultado_resumo,
        height=200,
        key="output_resumo",
        help="Resumo das patentes similares encontradas.")

if st.session_state.resultado_sugestoes:
  st.text_area("3️⃣ Sugestões de Inovações:",
        value=st.session_state.resultado_sugestoes,
        height=200,
        key="output_sugestoes",
        help="Sugestões de inovações possíveis para sua patente.")


# Output do Formulário
if st.session_state.formulario_patente:
  st.success("✅ Formulário Gerado!")
  st.download_button(
    label="Download Formulário (.txt)",
    data=st.session_state.formulario_patente,
    file_name="formulario_patente_inpi.txt",
    mime="text/plain",
    help="Clique para baixar o formulário gerado em formato de texto.",
    type="secondary"
  )
  st.text_area("Formulário de Patente INPI (Simulado):",
        value=st.session_state.formulario_patente,
        height=600,
        key="output_formulario",
        help="Formulário de patente gerado. Lembre-se que este é um modelo simulado.")


st.markdown("""
---
### Como funciona?
Este aplicativo ajuda você a:
1. **Pesquisar Patentes:** Insira uma descrição da sua invenção e o sistema simulará a busca por patentes já existentes.
2. **Gerar Formulário:** Com base na sua descrição, um modelo simplificado de formulário de patente no padrão INPI será gerado.

**Importante:** Esta é uma aplicação demonstrativa. Para processos reais de patenteamento, consulte um advogado especializado e os guias oficiais do INPI.
""")