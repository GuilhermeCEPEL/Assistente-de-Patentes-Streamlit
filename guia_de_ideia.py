import streamlit as st

# Configuração da página
st.set_page_config(
    page_title="InovaFacil",
    page_icon="💡",
    layout="wide",
    initial_sidebar_state="auto"
)

# Estilo personalizado
st.markdown("""
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
""", unsafe_allow_html=True)

# Conteúdo principal
st.markdown("<h1 style='text-align: center;'>Bem-vindo à InovaFácil 💡</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 1.2rem;'>Transformando suas ideias em inovação real.</p>", unsafe_allow_html=True)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# Seção de serviços
st.markdown('<h2>Nossos Serviços</h2>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown('<div class="card"><h4>💼 Consultoria em Inovação</h4><p>Guiamos você em cada etapa com expertise e visão estratégica.</p></div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="card"><h4>🧪 Desenvolvimento de Produtos</h4><p>Transformamos ideias em soluções tangíveis, sob medida.</p></div>', unsafe_allow_html=True)
with col3:
    st.markdown('<div class="card"><h4>📚 Capacitação e Treinamento</h4><p>Empodere sua equipe com conhecimento prático e atual.</p></div>', unsafe_allow_html=True)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# Contato e Localização
contato_col, local_col = st.columns(2)

with contato_col:
    st.subheader("Fale Conosco")
    nome = st.text_input("Seu Nome")
    mensagem = st.text_area("Sua Mensagem")
    if st.button("Enviar"):
        if nome.strip() and mensagem.strip():
            st.success(f"✅ Obrigado, {nome}! Sua mensagem foi enviada com sucesso.")
        else:
            st.error("⚠️ Por favor, preencha todos os campos antes de enviar.")

with local_col:
    st.subheader("Localização")
    st.write("📍 Estamos em São José, Santa Catarina.")
    st.image("https://via.placeholder.com/400x250?text=Mapa+aqui", caption="Nosso Escritório")

