import streamlit as st
from pylib.meta_llama2_cpp import chat_completion, Message

DEFAULT_SYSTEM_PROMPT = """You are a helpful, respectful and honest assistant. Always answer as helpfully as possible, while being safe.  Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. Please ensure that your responses are socially unbiased and positive in nature.\n\nIf a question does not make any sense, or is not factually coherent, explain why instead of answering something not correct. If you don't know the answer to a question, please don't share false information.\
"""

st.set_page_config(
    page_title=st.session_state.native_language.chatbot_label,
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 侧面菜单注释
st.sidebar.subheader(st.session_state.native_language.chatbot_label)

# 生成参数
temperature = st.sidebar.slider(
    "temperature", min_value=0.01, max_value=1.0, value=0.6, step=0.1
)
top_p = st.sidebar.slider("top_p", min_value=0.3, max_value=1.0, value=0.9, step=0.1)
max_new_tokens = st.sidebar.slider(
    "max_new_tokens", min_value=32, max_value=4096, value=2048, step=1
)

# Initialize chat history
if "cpp_chat_messages" not in st.session_state:
    st.session_state.cpp_chat_messages = []

system_prompt = st.sidebar.text_area(
    "system prompt",
    value=DEFAULT_SYSTEM_PROMPT,
    placeholder="Feel free to change the system instructions according to your needs",
    max_chars=2000,
)

clear_btn = st.sidebar.button(
    st.session_state.native_language.reset_chatbot_label,
    help=st.session_state.native_language.reset_chatbot_help_label,
)

if clear_btn:
    st.session_state.cpp_chat_messages = []

warning = """\
Llama 2 is a new technology that carries risks with use. Testing conducted to date has been in English, and has not covered, nor could it cover all scenarios. For these reasons, as with all LLMs, Llama 2’s potential outputs cannot be predicted in advance, and the model may in some instances produce inaccurate, biased or other objectionable responses to user prompts. Therefore, before deploying any applications of Llama 2, developers should perform safety testing and tuning tailored to their specific applications of the model.\
"""

# with st.expander("⚠️ Disclaimer"):
#     st.markdown(
#         """
#     Llama 2 is a new technology that carries risks with use. Testing conducted to date has been in English, and has not covered, nor could it cover all scenarios. For these reasons, as with all LLMs, Llama 2’s potential outputs cannot be predicted in advance, and the model may in some instances produce inaccurate, biased or other objectionable responses to user prompts. Therefore, before deploying any applications of Llama 2, developers should perform safety testing and tuning tailored to their specific applications of the model.
#     """
#     )

st.warning(warning, icon="⚠️")

for message in st.session_state.cpp_chat_messages:
    if message["role"] == "assistant":
        avatar = "🤖"
    else:
        avatar = "🧑‍🎓"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])


kwargs = {"temperature": temperature, "top_p": top_p, "max_new_tokens": max_new_tokens}

if prompt := st.chat_input(st.session_state.target_language.default_chat_input):
    st.session_state.cpp_chat_messages.append(Message(role="user", content=prompt))
    with st.chat_message("user", avatar="🧑‍🎓"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🤖"):
        message_placeholder = st.empty()
        full_response = ""
        for response in chat_completion(prompt, system_prompt, kwargs):
            full_response += response
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
        st.session_state.cpp_chat_messages.append(
            Message(role="assistant", content=full_response),
        )
