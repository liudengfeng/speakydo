import streamlit as st
from pylib.meta_llama2 import get_model_tokenizer


@st.cache_resource
def load_model_tokenizer():
    return get_model_tokenizer()


# 侧面菜单注释
st.sidebar.subheader(st.session_state.native_language.chatbot_label)


model, tokenizer = load_model_tokenizer()


with st.chat_message("user"):
    st.write("Hello 👋")
