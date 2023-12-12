import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from langchain.llms import OpenAI
from langchain.agents import create_csv_agent
import os

# Carregar os dados do CSV
@st.cache
def load_data():
    # Substitua pelo caminho correto do seu arquivo CSV
    return pd.read_csv('streamlit_agent/binder-data.csv')

# Funções para criar e exibir gráficos
def plot_results_by_type(df):
    result_counts = df['Tipo de resultado'].value_counts()
    plt.figure(figsize=(10, 6))
    result_counts.plot(kind='bar', color='skyblue')
    plt.title('Resultados por Tipo de Resultado')
    plt.xlabel('Tipo de Resultado')
    plt.ylabel('Frequência')
    st.pyplot()

def plot_clicks_over_time(df):
    df['Início dos relatórios'] = pd.to_datetime(df['Início dos relatórios'])
    clicks_over_time = df.groupby('Início dos relatórios')['Cliques no link'].sum()
    plt.figure(figsize=(10, 6))
    plt.plot(clicks_over_time.index, clicks_over_time.values, marker='o', color='orange')
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
    plt.gcf().autofmt_xdate()
    plt.title('Cliques no Link ao Longo do Tempo')
    plt.xlabel('Data')
    plt.ylabel('Total de Cliques no Link')
    st.pyplot()

# Configuração inicial do Streamlit
st.set_page_config(page_title="LangChain: Chat with Data", page_icon="🦜")
st.title("🦜 LangChain: Chat with Data")

# Configuração do agente OpenAI
openai_api_key = os.getenv('OPENAI_API_KEY')
llm = OpenAI(openai_api_key=openai_api_key, temperature=0)

# Carregar dados
df = load_data()

# Lógica de chat
if "messages" not in st.session_state:
    st.session_state.messages = []

if st.sidebar.button("Clear message history"):
    st.session_state.messages = []

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

user_query = st.chat_input(placeholder="Ask me anything!")
if user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})

    # Verificar se o usuário pediu para ver algum dos gráficos
    if user_query.lower() in ['mostrar gráfico 1', 'quero ver o primeiro gráfico']:
        plot_results_by_type(df)
    elif user_query.lower() in ['mostrar gráfico 2', 'quero ver o segundo gráfico']:
        plot_clicks_over_time(df)
    else:
        # Processar pergunta do usuário com o agente OpenAI
        response = llm.query(user_query)
        st.session_state.messages.append({"role": "assistant", "content": response})

st.sidebar.button("Clear message history")
