import streamlit as st
from langchain.agents import create_csv_agent
from langchain.llms import OpenAI
import tempfile
import os

# Função para carregar dados do arquivo CSV pré-carregado
def load_data(file_path):
    with open(file_path, "rb") as f:
        return f.read()

# Função para salvar um arquivo CSV temporário
def save_temporary_csv(file_content):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as f:
        f.write(file_content)
        return f.name

# Configuração inicial do Streamlit
st.set_page_config(page_title="Campaign Wizard MVP - Binder", page_icon="")
st.title("Campaign Wizard MVP - Binder")

# Adicionando o link na barra lateral
st.sidebar.markdown("[Chat with Data Viz](https://agent-viz-zor6g7kbzrzyzbe7der6k7.streamlit.app/)")

# Caminho para o arquivo CSV pré-carregado
DEFAULT_CSV_PATH = "streamlit_agent/binder-data.csv"

# Carregando o arquivo CSV pré-carregado
uploaded_file_content = load_data(DEFAULT_CSV_PATH)
temp_path = save_temporary_csv(uploaded_file_content)

# Obtendo a chave da API do OpenAI da variável de ambiente
openai_api_key = os.getenv('OPENAI_API_KEY')

# Verificando se a chave da API está disponível
if not openai_api_key:
    st.error("Chave da API do OpenAI não encontrada. Configure a variável de ambiente OPENAI_API_KEY.")
    st.stop()

# Lógica de chat
if "messages" not in st.session_state or st.sidebar.button("Limpar Histórico"):
    st.session_state["messages"] = [{"role": "assistant", "content": "Como posso te ajudar?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input(placeholder="Me pergunte sobre campanhas de marketing"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # Criação do agente CSV com a chave da API fornecida
    agent = create_csv_agent(OpenAI(temperature=0, openai_api_key=openai_api_key), temp_path, verbose=True)
    
    with st.chat_message("assistant"):
        response = agent.run(prompt)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.write(response)



# Inserir a frase no final da barra lateral usando Markdown e HTML
st.sidebar.markdown(
    """
    <div style="position: absolute; bottom: 10px; left: 0; width: 100%; text-align: center; color: white; font-weight: bold;">
        <p>Powered by On-Chain Labs</p>
    </div>
    """,
    unsafe_allow_html=True
)

# Rodapé com logo e texto
st.markdown("""
    <style>
    .reportview-container .main footer {visibility: hidden;}
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: transparent;
        color: white;
        text-align: center;
        padding: 10px;
    }
    .footer img {
        vertical-align: middle;
        height: 30px;  # Ajuste a altura conforme necessário
        margin: 5px;
    }
    .footer span {
        display: inline-block;
        vertical-align: middle;
    }
    </style>
    <footer class="footer">
        <img src='NEW-LOGO-2.png' alt='Logo On-Chain Labs'>
        <span>Powered by On-Chain Labs</span>
    </footer>
    """, unsafe_allow_html=True)
