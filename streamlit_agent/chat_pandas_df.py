import streamlit as st
from langchain.agents import create_csv_agent
from langchain.llms import OpenAI
import tempfile
import io
import os

# Função para carregar dados
def load_data(file_path):
    with open(file_path, "rb") as f:
        return f.read()

# Função para salvar um arquivo CSV temporário
def save_temporary_csv(file_content):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as f:
        f.write(file_content)
        return f.name

# Caminho para o arquivo CSV pré-carregado
DEFAULT_CSV_PATH = "caminho/para/seu/arquivo.csv"

# Configuração inicial do Streamlit
st.set_page_config(page_title="LangChain: Chat with pandas DataFrame", page_icon="🦜")
st.title("🦜 LangChain: Chat with pandas DataFrame")

# Carregamento do arquivo
# uploaded_file = st.file_uploader("Upload a Data file", type="csv")
# Usando o arquivo pré-carregado diretamente
uploaded_file_content = load_data(DEFAULT_CSV_PATH)
temp_path = save_temporary_csv(uploaded_file_content)

# Inserir chave da API OpenAI
openai_api_key = st.sidebar.text_input("OpenAI API Key", type="password")

# Lógica de chat
if "messages" not in st.session_state or st.sidebar.button("Clear conversation history"):
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input(placeholder="What is this data about?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.")
        st.stop()

    agent = create_csv_agent(OpenAI(temperature=0, openai_api_key=openai_api_key), temp_path, verbose=True)
    with st.chat_message("assistant"):
        response = agent.run(prompt)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.write(response)
