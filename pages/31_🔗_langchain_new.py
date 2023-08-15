import os

import streamlit as st
from langchain.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.callbacks import StreamlitCallbackHandler
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.chains import ConversationChain
from langchain.llms import LlamaCpp
from langchain.memory import ConversationBufferMemory

user_path = os.path.expanduser("~")
cpp_model_root = os.path.join(user_path, "llm-models", "cpp")
# cpp_model_names = [f for f in os.listdir(cpp_model_root) if f.endswith(".bin")]


st.set_page_config(
    page_title=st.session_state.native_language.langchain_label,
    page_icon="🦜",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 左侧菜单

st.sidebar.subheader(st.session_state.native_language.langchain_label)

model_path = os.path.join(cpp_model_root, "llama-2-13b-chat-ggml-q4_0.bin")

# Change this value based on your model and your GPU VRAM pool.
n_gpu_layers = st.sidebar.slider("n_gpu_layers", min_value=20, max_value=100, value=128)
# Should be between 1 and n_ctx, consider the amount of VRAM in your GPU.
n_batch = st.sidebar.slider("n_batch", min_value=64, max_value=1024, value=512)

# 页面
st.title("🦜🔗 LangChain Chat")
# Callbacks support token-wise streaming
# Verbose is required to pass to the callback manager
callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])


# Make sure the model path is correct for your system!
llm = LlamaCpp(
    model_path=model_path,
    n_gpu_layers=n_gpu_layers,
    n_batch=n_batch,
    top_p=0.9,
    temperature=0.6,
    callback_manager=callback_manager,
    verbose=True,
)

# Prompt
prompt = ChatPromptTemplate(
    messages=[
        SystemMessagePromptTemplate.from_template(
            "You are a helpful, respectful and honest assistant. Always answer as helpfully as possible, while being safe. Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. Please ensure that your responses are socially unbiased and positive in nature. If a question does not make any sense, or is not factually coherent, explain why instead of answering something not correct. If you don't know the answer to a question, please don't share false information."
        ),
        # The `variable_name` here is what must align with memory
        MessagesPlaceholder(variable_name="chat_history"),
        HumanMessagePromptTemplate.from_template("{question}"),
    ]
)

memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

conversation = ConversationChain(
    llm=llm,
    prompt=prompt,
    memory=memory,
    input_key="question",
    verbose=True,
)

if "lc_messages" not in st.session_state:
    st.session_state.lc_messages = [
        {"role": "assistant", "content": "How can I help you?"}
    ]

for msg in st.session_state.lc_messages:
    if msg["role"] == "assistant":
        avatar = "🤖"
    else:
        avatar = "🧑‍🎓"
    st.chat_message(msg["role"], avatar=avatar).write(msg["content"])


if question := st.chat_input(placeholder="Please input your query here."):
    st.session_state.lc_messages.append({"role": "user", "content": question})
    with st.chat_message("assistant", avatar="🧑‍🎓"):
        st.markdown(question)

    with st.chat_message("assistant", avatar="🤖"):
        st_cb = StreamlitCallbackHandler(st.container(), expand_new_thoughts=False)
        response = conversation.predict(question=question, callbacks=[st_cb])
        st.session_state.lc_messages.append({"role": "assistant", "content": response})
        st.markdown(response)
