import streamlit as st
import os
import re
from PIL import Image

from datetime import date
from functions.agents_functions import *
from functions.sheet_functions import *
from functions.auxiliar_functions import *

def render_page4():

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

    if not st.session_state.get("analise_realizada", False):
        with st.spinner("⌛ Analisando as respostas... Por favor, aguarde."):
            resultado_da_busca, resultado_da_avaliacao, resultado_da_analise = analise_dos_resultados(repostas_descritivas, formulario_respostas)
        st.session_state['resultado_da_busca'] = resultado_da_busca
        st.session_state['resultado_da_avaliacao'] = resultado_da_avaliacao
        st.session_state['resultado_da_analise'] = resultado_da_analise
        
        st.session_state['analise_realizada'] = True 

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
            st.info("Ocrreu algum erro durante a busca por propriedade intelectual similares, favor rodar a análise novamente.")

    with st.expander("💡 Análise Final e Recomendações Estratégicas"):
        st.markdown("#### Conclusão e Próximos Passos Sugeridos")
        if resultado_da_analise:
            st.write(resultado_da_analise)
        else:
            st.info("Ocrreu algum erro durante a análise final está sendo processada, favor rodar a análise novamente.")

    # Button to regenerate the analysis
    if st.button("🔄 Reprocessar Análise", key="regenerate_analysis_button"):
        with st.spinner("Reprocessando análise..."):
            resultado_da_busca, resultado_da_avaliacao, resultado_da_analise = analise_dos_resultados(repostas_descritivas, formulario_respostas)
        st.session_state['resultado_da_busca'] = resultado_da_busca
        st.session_state['resultado_da_avaliacao'] = resultado_da_avaliacao
        st.session_state['resultado_da_analise'] = resultado_da_analise
        st.success("Análise reprocessada com sucesso!")
        st.rerun()

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
        st.session_state['opcao_selecionada'] = opcao  # Store the selected option in session state
        if st.button("Gerar Próximos Passos Detalhados", key="prox_passos_button"):
            with st.spinner(f"Gerando os próximos passos para {opcao}..."):
                proximos_passos = agente_de_próximos_passos(f"Opção selecionada: {opcao}\n\nAnálise Detalhada:\n{resultado_da_analise}")
            st.session_state['proximos_passos_texto'] = proximos_passos
            st.success("Próximos passos gerados com sucesso!")

        # Always display the generated "proximos_passos_texto" if it exists in session_state
        if 'proximos_passos_texto' in st.session_state and st.session_state['proximos_passos_texto']:
            with st.expander("📝 Guia Detalhado para Proteção", expanded=True):
                st.markdown("### Guia Detalhado para Proteção:")
                st.write(st.session_state['proximos_passos_texto'])
    else:
        st.info("Por favor, selecione uma opção para gerar os próximos passos.")

    st.markdown("---")

    st.subheader("📄 Relatório INPI Provisório")
    st.write("Clique no botão abaixo para gerar um relatório provisório com as informações coletadas e análises realizadas. Este relatório pode ser usado como base para o envio ao INPI.")

    button_enabled = st.session_state.get('proximos_passos_texto')

    if st.button(
        "Gerar Relatório INPI Agora",
        key="trigger_report_generation",
        disabled=not button_enabled,
        use_container_width=True
    ):
        # Este bloco SÓ é executado quando o botão 'Gerar Relatório INPI Agora' é clicado
        with st.spinner("Gerando relatório... Isso pode levar alguns segundos."):
            # Recupere as variáveis necessárias do session_state
            # É fundamental que essas variáveis estejam armazenadas no session_state
            # pelas páginas anteriores ou em um passo anterior desta página.
            # opcao_selecionada = st.session_state.get('opcao_de_protecao', "Patente de Invenção") # Exemplo: nome da sua variável no session_state
            # respostas_descritivas_salvas = st.session_state.get('respostas_descritivas_geradas', "") # Exemplo
            # formulario_respostas_salvas = st.session_state.get('formulario_respostas_para_relatorio', "") # Exemplo

            # Chame a função do agente de geração
            try:
                relatorio_gerado = generate_relatorio(opcao, repostas_descritivas, formulario_respostas)
                st.session_state.relatorio_texto_final = relatorio_gerado
                st.success("Relatório gerado com sucesso! Agora você pode baixá-lo.")
                # Se desejar, force um rerun para habilitar o botão de download imediatamente
                st.rerun()
            except Exception as e:
                st.error(f"Ocorreu um erro ao gerar o relatório: {e}")
                st.session_state.relatorio_texto_final = "" # Limpa para tentar novamente
    
    # Display the generated report in an expander if it exists
    if 'relatorio_texto_final' in st.session_state and st.session_state['relatorio_texto_final']:
        with st.expander("📄 Visualizar Relatório INPI Gerado", expanded=False):
            st.markdown("### Relatório INPI Gerado:")
            st.write(st.session_state['relatorio_texto_final'])

    relatorio_para_download = st.session_state.get('relatorio_texto_final', '').encode('utf-8')
    download_disabled = not bool(relatorio_para_download)

    if st.download_button(
        label="💾 Baixar Relatório INPI (TXT)",
        key="final_download_report_button", # Mudei a chave para evitar conflito com a anterior
        data=relatorio_para_download,
        file_name=f"relatorio_inovafacil_{date.today()}.txt",
        mime="text/plain", # Use text/plain para arquivos .txt
        help="Baixe o relatório provisório gerado para o INPI.",
        use_container_width=True,
        disabled=download_disabled # Desabilita se não houver relatório gerado
    ):
    # Este bloco é executado DEPOIS que o download é iniciado no navegador.
    # Nenhuma lógica de geração deve estar aqui.
        pass

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Voltar para Descrição da Ideia", key="prev_page_button_4"):
            return -1
        
    with col2:
        # # Always generate a new report when the button is pressed
        # if st.download_button(
        #     label="📃 Gerar Relatório INPI",
        #     key="download_report_button",
        #     data=generate_relatorio(opcao, repostas_descritivas, formulario_respostas),
        #     file_name=f"relatorio_inovafacil_{date.today()}.txt",
        #     mime="text/txt",
        #     help="Baixe um relatório no formato requisitado pelo INPI.",
        #     use_container_width=True,
        #     disabled=button_disabled
        # ):
        #     pass
        
        if st.button("➡️ Finalizar e Enviar Respostas", key="finalize_button"):
            return 1