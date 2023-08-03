import os

import streamlit as st
from langchain.llms import LlamaCpp
from langchain.tools import Tool
from langchain.utilities import BingSearchAPIWrapper
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.agents import AgentType, initialize_agent
from langchain import PromptTemplate, LLMChain
from langchain.callbacks import StreamlitCallbackHandler

user_path = os.path.expanduser("~")
cpp_model_root = os.path.join(user_path, "llm-models", "llama-2-7b-chat-cpp")
cpp_model_names = [f for f in os.listdir(cpp_model_root) if f.endswith(".bin")]


bing_web_search = BingSearchAPIWrapper(
    bing_subscription_key=st.secrets["Microsoft"].BING_SUBSCRIPTION_KEY,
    bing_search_url="{}/v7.0/search".format(
        st.secrets["Microsoft"].BING_SEARCH_V7_ENDPOINT
    ),
    k=1,
)


tools = [
    Tool.from_function(
        func=bing_web_search.run,
        name="Bing web search",
        description="useful for when you need to answer questions about current events"
        # coroutine= ... <- you can specify an async method if desired as well
    ),
]

st.set_page_config(
    page_title=st.session_state.native_language.langchain_label,
    page_icon="🦜",
    layout="wide",
    initial_sidebar_state="expanded",
)


st.title("🦜🔗 LangChain: Chat with search")

# 侧面菜单注释
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

# Callbacks support token-wise streaming
# Verbose is required to pass to the callback manager
callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])

# Make sure the model path is correct for your system!
llm = LlamaCpp(
    model_path=model_path,
    n_gpu_layers=n_gpu_layers,
    n_batch=n_batch,
    callback_manager=callback_manager,
    verbose=True,
)

if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "How can I help you?"}
    ]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])


if prompt := st.chat_input(placeholder="Who won the Women's U.S. Open in 2018?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # Construct the agent. We will use the default agent type here.
    # See documentation for a full list of options.
    search_agent = initialize_agent(
        tools,
        llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        handle_parsing_errors=True,
    )

    with st.chat_message("assistant"):
        st_cb = StreamlitCallbackHandler(st.container(), expand_new_thoughts=False)
        response = search_agent.run(st.session_state.messages, callbacks=[st_cb])
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.write(response)

# template = """Question: {question}

# Answer: Let's work this out in a step by step way to be sure we have the right answer."""

# prompt = PromptTemplate(template=template, input_variables=["question"])
