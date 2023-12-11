from langchain.agents import create_csv_agent
from langchain.llms import OpenAI
from langchain.callbacks import StreamlitCallbackHandler
import streamlit as st
import pandas as pd
import os
import tempfile
import io
import re

def clear_submit():
    """
    Clear the Submit Button State
    """
    st.session_state["submit"] = False

@st.cache_data(ttl="2h")
def load_data(uploaded_file):
    try:
        ext = os.path.splitext(uploaded_file.name)[1][1:].lower()
    except:
        ext = uploaded_file.split(".")[-1]
    if ext in file_formats:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as f:
            f.write(uploaded_file.getvalue())
            return f.name
    else:
        st.error(f"Unsupported file format: {ext}")
        return None

st.set_page_config(page_title="LangChain: Chat with pandas DataFrame", page_icon="🦜")
st.title("🦜 LangChain: Chat with pandas DataFrame")

file_formats = {
    "csv": pd.read_csv,
    "xls": pd.read_excel,
    "xlsx": pd.read_excel,
    "xlsm": pd.read_excel,
    "xlsb": pd.read_excel,
}

uploaded_file = st.file_uploader(
    "Upload a Data file",
    type=list(file_formats.keys()),
    help="Various File formats are Support",
    on_change=clear_submit,
)

if not uploaded_file:
    st.warning(
        "This app uses LangChain's `PythonAstREPLTool` which is vulnerable to arbitrary code execution. Please use caution in deploying and sharing this app."
    )

openai_api_key = st.sidebar.text_input("OpenAI API Key", type="password")
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

    if uploaded_file:
        temp_path = load_data(uploaded_file)
        if temp_path:
            agent = create_csv_agent(OpenAI(temperature=0, model_kwargs={"api_key": openai_api_key}), temp_path, verbose=True)


            with st.chat_message("assistant"):
                st_cb = StreamlitCallbackHandler(st.container(), expand_new_thoughts=False)
                response = agent.run(prompt)
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.write(response)
