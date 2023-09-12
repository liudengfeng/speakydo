import streamlit as st
import random
import os
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.llms import LlamaCpp
from langchain import PromptTemplate, LLMChain
from langchain.chains import SimpleSequentialChain
from copy import copy

st.set_page_config(
    page_title=st.session_state.native_language.simulation_scene_label,
    page_icon="🎞",
    layout="wide",
    initial_sidebar_state="expanded",
)


# 侧面菜单注释
st.sidebar.subheader(st.session_state.native_language.simulation_scene_label)
# 语言水平
language_level = st.sidebar.selectbox(
    st.session_state.native_language.selectbox_dialogue_language_level,
    st.session_state.target_language.language_level,
)
# 场景主题
selected_dialogue_topic = st.sidebar.selectbox(
    st.session_state.native_language.selectbox_dialogue_topic_label,
    list(st.session_state.native_language.dialogue_topic.keys()),
)
st.sidebar.info(
    st.session_state.native_language.dialogue_topic_help[selected_dialogue_topic]
)

# 角色1性别
first_person_gender = st.sidebar.selectbox(
    st.session_state.native_language.role_1_gender_label,
    st.session_state.target_language.names.keys(),
)
# 角色2性别
second_person_gender = st.sidebar.selectbox(
    st.session_state.native_language.role_2_gender_label,
    st.session_state.target_language.names.keys(),
)

first_name = random.sample(
    st.session_state.target_language.names[first_person_gender], 1
)[0]

# 确保不重名
candidates = copy(st.session_state.target_language.names[second_person_gender])
if first_person_gender == second_person_gender:
    # candidates = st.session_state.target_language.names[first_person_gender]
    candidates.remove(first_name)

second_name = random.sample(candidates, 1)[0]

st.sidebar.subheader(st.session_state.native_language.model_arg_label)
# Should be between 1 and n_ctx, consider the amount of VRAM in your GPU.
n_gpu_layers = st.sidebar.slider("n_gpu_layers", min_value=1, max_value=100, value=40)
temperature = st.sidebar.slider(
    "temperature", min_value=0.01, max_value=5.00, value=0.10
)
top_p = st.sidebar.slider("top_p", min_value=0.01, max_value=1.00, value=0.75)


st.markdown(
    """\
## {}
{}
""".format(
        st.session_state.native_language.simulation_scene_label,
        st.session_state.native_language.dialogue_topic_tip,
    )
)


user_path = os.path.expanduser("~")
cpp_model_root = os.path.join(user_path, "llm-models", "cpp", "llama-2-13b-chat")
model_path = os.path.join(cpp_model_root, "ggml-model-q4_0.gguf")

# Callbacks support token-wise streaming
callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])


llm = LlamaCpp(
    model_path=model_path,
    n_gpu_layers=n_gpu_layers,
    temperature=temperature,
    max_tokens=4096,
    top_p=top_p,
    callback_manager=callback_manager,
    verbose=True,  # Verbose is required to pass to the callback manager
)


if st.button("Submit"):
    topic_template = """
    List 10 topics related to the following topic and randomly select one as the output:

    topic:{topic}
    """

    topic_prompt_template = PromptTemplate(
        input_variables=["topic"], template=topic_template
    )
    topic_chain = LLMChain(llm=llm, prompt=topic_prompt_template)

    dialogue_content = f"""Regarding the topic:XXX, please simulate a conversation between {first_name} and {second_name}.

    Require:
    The conversation should be realistic and natural
    Both parties spoke in {st.session_state.target_language.language_label}
    Fully consider that the language level of both parties in the conversation is {language_level}
    The number of words per conversation per person should not exceed 120
    no more than 10 dialogue rounds
    """

    dialogue_template = dialogue_content.replace("XXX", "{detail_topic}")

    dialogue_prompt_template = PromptTemplate(
        input_variables=["detail_topic"], template=dialogue_template
    )
    dialogue_chain = LLMChain(llm=llm, prompt=dialogue_prompt_template)

    # overall_chain = SimpleSequentialChain(
    #     chains=[topic_chain, dialogue_chain], verbose=True
    # )

    overall_chain = SimpleSequentialChain(chains=[topic_chain], verbose=True)

    dialogue = overall_chain.run(selected_dialogue_topic)

    st.text(dialogue)
