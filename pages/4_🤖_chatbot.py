import streamlit as st
from pylib.meta_llama2 import get_model_tokenizer, chat_stream_completion, Message


@st.cache_resource
def load_model_tokenizer():
    return get_model_tokenizer()


# 侧面菜单注释
st.sidebar.subheader(st.session_state.native_language.chatbot_label)

# 生成参数
temperature = st.sidebar.slider("temperature", min_value=0.01, max_value=1.0, value=0.6)
top_p = st.sidebar.slider("top_p", min_value=0.33, max_value=1.0, value=0.9)
max_new_tokens = st.sidebar.slider(
    "max_new_tokens", min_value=64, max_value=4096, value=256
)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

clear_btn = st.sidebar.button("重置会话", help="清除会话历史，开始一个新的话题")

if clear_btn:
    st.session_state.messages = []

model, tokenizer = load_model_tokenizer()


with st.expander("ℹ️ Disclaimer"):
    st.markdown(
        """
    Llama 2 is a new technology that carries risks with use. Testing conducted to date has been in English, and has not covered, nor could it cover all scenarios. For these reasons, as with all LLMs, Llama 2’s potential outputs cannot be predicted in advance, and the model may in some instances produce inaccurate, biased or other objectionable responses to user prompts. Therefore, before deploying any applications of Llama 2, developers should perform safety testing and tuning tailored to their specific applications of the model.
    """
    )

# with st.chat_message(name="user", avatar="🙎‍♂️"):
#     st.write("Hello 👋")

# with st.chat_message("assistant", avatar="🤖"):
#     st.write("Hello human")


for message_tuple in st.session_state.messages:
    with st.chat_message(message_tuple[0]["role"], avatar="🙎‍♂️"):
        st.markdown(message_tuple[0]["content"])
    with st.chat_message(message_tuple[1]["role"], avatar="🤖"):
        st.markdown(message_tuple[1]["content"])

if prompt := st.chat_input("What is up?"):
    # st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🙎‍♂️"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        for response in chat_stream_completion(
            model,
            tokenizer,
            prompt,
            st.session_state.messages,
            temperature=temperature,
            top_p=top_p,
            max_new_tokens=max_new_tokens,
        ):
            full_response += response
            message_placeholder.markdown(full_response + "▌")

        message_placeholder.markdown(full_response)
    # st.session_state.messages.append({"role": "assistant", "content": full_response})
    st.session_state.messages.append(
        (
            Message(role="user", content=prompt),
            Message(role="assistant", content=full_response),
        )
    )
