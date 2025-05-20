# 💡 Assistente de Patente INPI

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://assistente-de-patente.streamlit.app)

Um assistente de IA para a fase inicial de patenteamento, desenvolvido com **Streamlit** e **Agentes do Google ADK**.

---

## 🚀 Acesse a Aplicação

Experimente o Assistente de Patente online:
[assistente-de-patente.streamlit.app](https://assistente-de-patente.streamlit.app/)

---

## ✨ Funcionalidades

* **🔎 Pesquisa de Patentes Similares:** Analisa sua invenção e busca por patentes existentes para identificar o "estado da técnica".
* **📄 Geração de Formulário (Simulado):** Gera um modelo inicial de formulário de patente seguindo a estrutura do INPI, com base na sua descrição.

---

## 🧠 Como Funciona

A aplicação orquestra múltiplos agentes de IA (Google ADK com Gemini) para:

1.  **Buscar Patentes:** Pesquisa em bancos de dados (simulados) como INPI, Espacenet, Google Patents, PATENTSCOPE.
2.  **Resumir e Comparar:** Cria resumos concisos das patentes encontradas, destacando similaridades com sua invenção.
3.  **Sugerir Inovações:** Oferece ideias para aprimoramentos patenteáveis e novas invenções relacionadas.
4.  **Formatar INPI:** Estrutura sua descrição no formato de relatório descritivo e resumo do INPI.

---

## 🛠️ Configuração Local

Para rodar localmente:

1.  Clone o repositório: `git clone https://github.com/GuilhermeCEPEL/Assistente-de-Patentes-Streamlit.git`
2.  Crie e ative um ambiente virtual.
3.  Instale as dependências (do seu `requirements.txt`): `pip install -r requirements.txt`
    (Lembre-se de que `google-generativeai` deve cobrir `google.adk`.)
4.  Configure sua **API Key do Google AI** no `app_patentes.py`.
5.  Execute: `streamlit run app_patentes.py`

---

## ⚠️ Aviso Importante

Esta é uma **ferramenta demonstrativa e de prototipagem**. As análises e formulários são **simulados** e não substituem a consulta a um especialista. **Para processos reais de patenteamento, consulte um advogado especializado e os guias oficiais do INPI.**

---

## 🤝 Contribuição

Sinta-se à vontade para contribuir! Abra issues ou envie pull requests.
