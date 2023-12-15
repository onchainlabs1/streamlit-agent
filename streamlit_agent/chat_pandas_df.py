import streamlit as st
from langchain.agents import create_csv_agent
from langchain.llms import OpenAI
import tempfile
import os
import pandas as pd
import openai

# Função para gerar embeddings usando o GPT da OpenAI
def generate_gpt_embeddings(text, openai_api_key):
    try:
        response = openai.Embedding.create(input=[text], engine="text-similarity-babbage-001", api_key=openai_api_key)
        return response['data'][0]['embedding']
    except Exception as e:
        st.error(f"Erro ao gerar embeddings: {e}")
        return None

# Configuração inicial do Streamlit
st.set_page_config(page_title="Campaign Wizard MVP - Binder", page_icon="")
st.title("Campaign Wizard MVP - Binder")

# Adicionando o link na barra lateral
st.sidebar.markdown("[Chat with Data Viz](https://agent-viz-zor6g7kbzrzyzbe7der6k7.streamlit.app/)")

# Caminho para o arquivo CSV pré-carregado
DEFAULT_CSV_PATH = "streamlit_agent/binder-data2.csv"

# Carregando o arquivo CSV pré-carregado
def load_data(file_path):
    with open(file_path, "rb") as f:
        return f.read()

def save_temporary_csv(file_content):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as f:
        f.write(file_content)
        return f.name

uploaded_file_content = load_data(DEFAULT_CSV_PATH)
temp_path = save_temporary_csv(uploaded_file_content)

# Carrega o DataFrame
df = pd.read_csv(temp_path)

# Obtendo a chave da API do OpenAI da variável de ambiente
openai_api_key = os.getenv('OPENAI_API_KEY')

# Verificando se a chave da API está disponível
if not openai_api_key:
    st.error("Chave da API do OpenAI não encontrada. Configure a variável de ambiente OPENAI_API_KEY.")
    st.stop()

# Lógica de chat
if "messages" not in st.session_state or st.sidebar.button("Limpar Histórico"):
    st.session_state["messages"] = [{"role": "assistant", "content": "Como posso te ajudar com suas campanhas de marketing e análise de dados?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input(placeholder="Me pergunte sobre campanhas de marketing"):
    # Gerando embeddings para o resumo do dataframe
    summary = df.describe().to_string()
    embeddings = generate_gpt_embeddings(summary, openai_api_key)

    if embeddings is not None:
        # Construindo um prompt usando embeddings
        expert_prompt = f"""
        [Em Português 🇧🇷]
        Aqui estão os embeddings das métricas de marketing: 
        {embeddings}
        Com base nisso, {prompt}
        """
        
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)

        agent = create_csv_agent(OpenAI(temperature=0, openai_api_key=openai_api_key), temp_path, verbose=True)
        
        with st.chat_message("assistant"):
            response = agent.run(expert_prompt)
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.write(response)

# Adicionando a visualização do CSV colapsável após a lógica de chat
with st.expander("Ver dados do CSV", expanded=False):
    st.dataframe(df)

# Estilização da barra lateral e rodapé
st.sidebar.markdown("""
    <style>
        .sidebar .sidebar-content {
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            height: calc(100vh - 96px);
        }
        .sidebar-footer {
            text-align: center;
            font-weight: bold;
            color: white;
            padding: 10px 0;
        }
    </style>
    <footer class="sidebar-footer">
        Powered by On-Chain Labs
    </footer>
""", unsafe_allow_html=True)

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
        height: 30px;
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
