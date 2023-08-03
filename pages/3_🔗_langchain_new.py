import os

import streamlit as st
from langchain.prompts import ChatPromptTemplate
from langchain.callbacks import StreamlitCallbackHandler
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.chains import ConversationChain
from langchain.llms import LlamaCpp
from langchain.memory import ConversationBufferMemory

user_path = os.path.expanduser("~")
cpp_model_root = os.path.join(user_path, "llm-models", "llama-2-7b-chat-cpp")
cpp_model_names = [f for f in os.listdir(cpp_model_root) if f.endswith(".bin")]


st.set_page_config(
    page_title=st.session_state.native_language.langchain_label,
    page_icon="🦜",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 左侧菜单

st.sidebar.subheader(st.session_state.native_language.langchain_label)
cpp_model_name = st.sidebar.selectbox(
    st.session_state.native_language.cpp_model_selectbox_label,
    cpp_model_names,
    key="voice_name",
    # label_visibility="hidden",
)

st.sidebar.markdown(
    "[ℹ️ download model from here](https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGML)",
    unsafe_allow_html=True,
    help="Make sure save model in `~/llm-models/llama-2-7b-chat-cpp/`",
)

model_path = os.path.join(cpp_model_root, cpp_model_name)

# Change this value based on your model and your GPU VRAM pool.
n_gpu_layers = st.sidebar.slider("n_gpu_layers", min_value=20, max_value=100, value=40)
# Should be between 1 and n_ctx, consider the amount of VRAM in your GPU.
n_batch = st.sidebar.slider("n_batch", min_value=64, max_value=1024, value=512)

# 页面
st.title("🦜🔗 LangChain: Chat with search")
# Callbacks support token-wise streaming
# Verbose is required to pass to the callback manager
callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])



# Make sure the model path is correct for your system!
llm = LlamaCpp(
    model_path=model_path,
    n_gpu_layers=n_gpu_layers,
    # n_batch=n_batch,
    top_p=0.9,
    callback_manager=callback_manager,
    verbose=True,
)

prompt_template = ChatPromptTemplate.from_role_strings(
    [
        (
            "system",
            "You are a helpful, respectful and honest assistant. Always answer as helpfully as possible, while being safe. Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. Please ensure that your responses are socially unbiased and positive in nature. If a question does not make any sense, or is not factually coherent, explain why instead of answering something not correct. If you don't know the answer to a question, please don't share false information. Chat history is ```{history}```.",
        ),
        ("human", "{user_input}"),
    ]
)
memory = ConversationBufferMemory()
conversation = ConversationChain(
    llm=llm,
    # prompt=prompt_template,
    # memory=memory,
    verbose=True
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


if prompt := st.chat_input(placeholder="Please input your query here."):
    st.session_state.lc_messages.append({"role": "user", "content": prompt})
    with st.chat_message("assistant",avatar="🧑‍🎓"):
        st.markdown(prompt)

    with st.chat_message("assistant",avatar="🤖"):
        st_cb = StreamlitCallbackHandler(st.container(), expand_new_thoughts=False)
        response = conversation.predict(user_input=prompt, callbacks=[st_cb])
        st.session_state.lc_messages.append({"role": "assistant", "content": response})
        st.markdown(response)

    # st.write("memory.buffer=",memory.buffer)

# template = """Question: {question}

# Answer: Let's work this out in a step by step way to be sure we have the right answer."""

# prompt = PromptTemplate(template=template, input_variables=["question"])
