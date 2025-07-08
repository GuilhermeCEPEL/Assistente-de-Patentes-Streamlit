from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import google_search
from google.genai import types # Para criar conteúdos (Content e Part)

# Importações para Google Sheets

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

def agente_gerador_de_relatorio(topico):
  agente = Agent(
    name="agente_gerador_de_relatorio",
    model="gemini-2.5-flash-preview-05-20",
    description="Agente que irá gerara um relatório pa partir da descrição da patente no formato no INPI",
    tools=[google_search],
    instruction="""
    Você é um gerador de relatório para patentes no formato do INPI. Você deve analizar as informações da ideia fornecidas
    pelo usuário assim como a escolha de qual tipo de patente o usuário deseja desenvolver e gerar o Resumo e o Resumo descritivo 
    de acordo com os padrões do INPI. 
    
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
  entrada_do_agente = f"Tópico: {topico}"
  # Executa o agente
  resultado_do_agente = call_agent(agente, entrada_do_agente)

  return resultado_do_agente 

def agente_buscador_de_PI(topico):
  buscador = Agent(
    name="agente_buscador_de_PI",
    model="gemini-2.5-flash-preview-05-20",
    description="Agente responsável por investigar a existência de propriedade intelectual semelhante à ideia proposta pelo usuário.",
    tools=[google_search],
    instruction="""
    Como pesquisador especializado em Propriedade Intelectual (PI), sua missão é identificar registros existentes que possam ser semelhantes à ideia apresentada pelo usuário.

    O usuário responderá as seguintes perguntas:

    - Descrição da ideia ou invenção:
    - Qual é o diferencial ou inovação da sua ideia?:
    - Você já desenvolveu algo (protótipo, código, apresentação)?:
    - Qual é o setor de aplicação?:

    Com base nessas informações, conduza uma busca abrangente por possíveis registros de PI (como patentes, marcas, direitos autorais, softwares etc.) similares, com o objetivo de avaliar se a ideia apresentada é de fato original.

    Utilize ferramentas como INPI (Registro de Programa de Computador, Busca Web de Marca), Google Patents, PATENTSCOPE, Espacenet, TMView, GitHub, Creative Commons Search, Lens.org, Derwent Innovation, Wayback Machine, Google Scholar, entre outras. Pesquise termos tanto em português quanto em inglês, explorando sinônimos e expressões relacionadas.

    O resultado da sua busca deve incluir a descrição da ideia do usuário, seguida de **duas listas**:

    1. Propriedades Intelectuais Brasileiras  
    2. Propriedades Intelectuais Internacionais  

    Cada item listado deve conter:

    - Identificador do Documento  
    - Título da PI  
    - Link para Acessar a PI (não utilize links fictícios — se não for possível encontrá-lo, justifique)  
    - Resumo em Português  
    - Comparação com a ideia do usuário  
    - Outras informações relevantes

    **Formato obrigatório para os resultados:**

    1. Descrição da ideia do usuário:

    **Resuma a ideia do usuário em um parágrafo curto e objetivo**

    ------------------------------------------------------------------------------------
    
    2. Lista de Propriedades Intelectuais Brasileiras

      - Identificador do Documento:  
        - Título da PI:  
        - Link para Acessar a PI:  
        - Resumo em Português:  
        - Comparação:  
        - Outras informações relevantes:  

    ------------------------------------------------------------------------------------

    3. Lista de Propriedades Intelectuais Internacionais

      - Identificador do Documento:  
        - Título da PI:  
        - Link para Acessar a PI:  
        - Resumo em Português:  
        - Comparação:  
        - Outras informações relevantes:  

    Não se apresente no início do resultado.

    O conteúdo deve ser gerado em português do Brasil.
    """
  )

  entrada_do_agente = f"Tópico: {topico}"
  lancamentos_buscados = call_agent(buscador, entrada_do_agente)

  return lancamentos_buscados

def agente_revisor(topico):
  agente = Agent(
    name="agente_revisor",
    model="gemini-2.5-flash-preview-05-20",
    description="Agente responsável por revisar a busca realizada por outro agente, garantindo a precisão e completude das informações.",
    tools=[google_search],
    instruction="""
    Como Agente Revisor, sua função é validar a exatidão e integridade das informações de Propriedades Intelectuais
    (PIs) identificadas pelo Agente Buscador.

    Você receberá uma lista com os resultados encontrados e deverá avaliá-los cuidadosamente, com base nos
    seguintes critérios:

    - **Coerência das Informações**: Verifique se os dados (título, resumo, inventores etc.) refletem fielmente o 
    conteúdo da PI original.
    - **Validade e Funcionamento dos Links**: Confirme se os links estão corretos, acessíveis e levam diretamente 
    à PI em questão. Links falsos, quebrados ou genéricos devem ser substituídos ou devidamente justificados.
    - **Completude dos Dados**: Certifique-se de que todas as informações essenciais estejam presentes. Itens 
    incompletos devem ser corrigidos ou complementados.

    Ações a serem tomadas:

    - **Correção**: Atualize diretamente informações incorretas, links errados ou dados ausentes.
    - **Remoção**: Exclua PIs que não puderem ser verificadas, que não atendam aos critérios de relevância ou que sejam exemplos.

    Após revisar a lista, reavalie e reescreva as conclusões e comparações feitas pelo Agente Buscador,
    garantindo que reflitam apenas os dados corrigidos e validados.

    Se não conseguir validar o link, realize uma nova busca para encontrar o link correto.

    Não explique as alterações realizadas — apenas apresente a versão final corrigida.

    Utilize o mesmo formato estabelecido pelo Agente Buscador.

    Não se apresente no início do resultado.
    
    O conteúdo deve ser gerado em português do Brasil.
    """
  )

  entrada_do_agente = f"Tópico: {topico}"
  lancamentos_buscados = call_agent(agente, entrada_do_agente)

  return lancamentos_buscados

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
    description="Agente responsável por avaliar o potencial da ideia com base nas respostas do usuário e nas análises realizadas por outros agentes.",
    tools=[google_search],
    instruction="""
    Sua função é avaliar o potencial da ideia apresentada pelo usuário com base nas análises anteriores realizadas por outros agentes e nas informações fornecidas pelo próprio usuário.

    O usuário responderá às seguintes perguntas:
    
    - Descrição da ideia ou invenção:  
    - Qual é o diferencial ou inovação da sua ideia?  
    - Você já desenvolveu algo (protótipo, código, apresentação)?  
    - Qual é o setor de aplicação?

    Com base nessas informações, realize uma análise crítica destacando os **pontos fortes e fracos da ideia**, e avalie sua viabilidade como **Propriedade Intelectual (PI)**.

    A avaliação deve considerar os seguintes critérios, cada um com nota de 0 a 10:

    - **Inovação**: A ideia apresenta uma abordagem nova ou solução criativa para um problema real?  
    - **Originalidade**: A ideia é única e se diferencia de soluções existentes identificadas na pesquisa de PIs?  
    - **Potencial de Propriedade Intelectual**: A ideia possui características que permitem sua proteção legal, como patenteabilidade, registro de software ou marca?

    Calcule a **nota final** como a **média aritmética** das notas atribuídas a cada critério.

    Apresente o resultado no seguinte formato:

    X/10 - *Frase breve e objetiva que justifique a nota final geral (ex: "Boa inovação, mas já existem soluções similares.")*  
    x/10 - Inovação: *Justificativa breve da nota*  
    x/10 - Originalidade: *Justificativa breve da nota*  
    x/10 - Potencial de Propriedade Intelectual: *Justificativa breve da nota*

    Não se apresente no início do resultado.
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