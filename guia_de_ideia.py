import streamlit as st
import pandas as pd
import io

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
    }
if 'ideaText' not in st.session_state:
    st.session_state.ideaText = ''

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

# --- Page 1: User Information ---
if st.session_state.currentPage == 1:
    st.title("Suas Informações")
    st.write("Por favor, preencha seus dados para continuar.")

    # Input fields for user data
    st.session_state.userData['name'] = st.text_input("Nome:", value=st.session_state.userData['name'])
    st.session_state.userData['matricula'] = st.text_input("Matrícula:", value=st.session_state.userData['matricula'])
    st.session_state.userData['email'] = st.text_input("Email:", value=st.session_state.userData['email'])

    # Check if all user data fields are filled
    is_user_data_complete = all(st.session_state.userData.values())

    # "Next Page" button
    if st.button("Próxima Página", disabled=not is_user_data_complete):
        next_page()

# --- Page 2: Yes/No Questions ---
elif st.session_state.currentPage == 2:
    st.title("Perguntas de Sim ou Não")
    st.write("Por favor, responda às seguintes perguntas:")

    # Adicione uma mensagem para o usuário
    st.info("💡 **Atenção:** Após responder a todas as perguntas, clique no botão 'Próxima Página' para continuar.")

    questions = [
        {'id': 'q1', 'text': 'A ideia é apenas um algoritmo isolado ou método matemático?'},
        {'id': 'q2', 'text': 'A ideia é uma metodologia de ensino, gestão, negócios ou treinamento?'},
        {'id': 'q3', 'text': 'A ideia é puramente software (sem aplicação técnica específica)?'},
        {'id': 'q4', 'text': 'A ideia resolve um problema técnico com uma solução técnica (ex: dispositivo, sistema físico, mecanismo)?'},
        {'id': 'q5', 'text': 'A solução é nova? (Não existe algo igual já divulgado ou patenteado?)'},
        {'id': 'q6', 'text': 'A solução é inventiva? (Não é óbvia para um técnico no assunto?)'},
        {'id': 'q7', 'text': 'Tem aplicação industrial? (Pode ser fabricada, usada ou aplicada em algum setor produtivo?)'},
    ]

    # Display each question with radio buttons
    for q in questions:
        # Determine the default index for the radio button based on current state
        default_index = None # Default to no selection
        if st.session_state.questionsData[q['id']] is True:
            default_index = 0 # 'Sim'
        elif st.session_state.questionsData[q['id']] is False:
            default_index = 1 # 'Não'
        elif st.session_state.questionsData[q['id']] is None:
            default_index = None

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


    # Check if all questions are answered
    are_questions_complete = all(value is not None for value in st.session_state.questionsData.values())

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Página Anterior"):
            prev_page()
    with col2:
        if st.button("Próxima Página 3", disabled=not are_questions_complete):
            next_page()

# --- Page 3: Idea Description ---
elif st.session_state.currentPage == 3:
    st.title("Descreva Sua Ideia")
    st.write("Por favor, descreva sua ideia em detalhes.")

    # Text area for idea description
    st.session_state.ideaText = st.text_area(
        "Sua Ideia:",
        value=st.session_state.ideaText,
        height=250
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Página Anterior"):
            prev_page()
    with col2:
        if st.button("Finalizar Formulário"):
            st.success("Formulário Finalizado! Seus dados e ideia foram submetidos (simulação).")
            st.write("---")
            st.subheader("Dados Coletados:")
            st.write("**Informações do Usuário:**")
            st.json(st.session_state.userData)
            st.write("**Respostas das Perguntas:**")
            st.json(st.session_state.questionsData)
            st.write("**Texto da Ideia:**")
            st.write(st.session_state.ideaText)

            # Generate CSV data
            csv_data = save_data_to_csv(
                st.session_state.userData,
                st.session_state.questionsData,
                st.session_state.ideaText
            )
            # Create a download button for the CSV file
            st.download_button(
                label="Baixar Dados do Formulário (CSV)",
                data=csv_data,
                file_name="dados_formulario_ideia.csv",
                mime="text/csv",
            )
