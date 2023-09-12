import streamlit as st
from pylib.meta_llama2 import (
    get_model_tokenizer,
    chat_stream_completion,
    Message,
    DEFAULT_SYSTEM_PROMPT,
)
import time


@st.cache_resource
def load_model_tokenizer():
    return get_model_tokenizer()


st.set_page_config(
    page_title=st.session_state.native_language.chatbot_label,
    page_icon="🗨️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 侧面菜单注释
st.sidebar.subheader(st.session_state.native_language.chatbot_label)

# 生成参数
temperature = st.sidebar.slider("temperature", min_value=0.01, max_value=1.0, value=0.6)
top_p = st.sidebar.slider("top_p", min_value=0.33, max_value=1.0, value=0.9)
max_new_tokens = st.sidebar.slider(
    "max_new_tokens", min_value=32, max_value=2048, value=512
)

# Initialize chat history
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

system_prompt = st.sidebar.text_area(
    "system prompt", placeholder="Please enter system instructions", max_chars=2000
)

clear_btn = st.sidebar.button(
    st.session_state.native_language.reset_chatbot_label,
    help=st.session_state.native_language.reset_chatbot_help_label,
)

if clear_btn:
    st.session_state.chat_messages = []

model, tokenizer = load_model_tokenizer()


with st.expander("ℹ️ Disclaimer"):
    st.markdown(
        """
    Llama 2 is a new technology that carries risks with use. Testing conducted to date has been in English, and has not covered, nor could it cover all scenarios. For these reasons, as with all LLMs, Llama 2’s potential outputs cannot be predicted in advance, and the model may in some instances produce inaccurate, biased or other objectionable responses to user prompts. Therefore, before deploying any applications of Llama 2, developers should perform safety testing and tuning tailored to their specific applications of the model.
    """
    )


for message in st.session_state.chat_messages:
    if message["role"] == "assistant":
        avatar = "🤖"
    else:
        avatar = "🧑‍🎓"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])


if prompt := st.chat_input("What is up?"):
    start = time.time()
    st.session_state.chat_messages.append(Message(role="user", content=prompt))
    with st.chat_message("user", avatar="🧑‍🎓"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🤖"):
        message_placeholder = st.empty()
        full_response = ""
        for response in chat_stream_completion(
            model,
            tokenizer,
            prompt,
            st.session_state.chat_messages,
            system_prompt=system_prompt if system_prompt else DEFAULT_SYSTEM_PROMPT,
            temperature=temperature,
            top_p=top_p,
            max_new_tokens=max_new_tokens,
        ):
            full_response += response
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
        print(f"duration = {time.time()- start:.2f}s")
        st.session_state.chat_messages.append(
            Message(role="assistant", content=full_response),
        )
