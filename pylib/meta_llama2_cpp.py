import os
from typing import Any, List, Literal, Mapping, Optional, Tuple, TypedDict
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.llms import LlamaCpp
from langchain.chains import LLMChain

Role = Literal["system", "user", "assistant"]


class Message(TypedDict):
    role: Role
    content: str


def get_llm(kwargs):
    user_path = os.path.expanduser("~")
    cpp_model_root = os.path.join(user_path, "llm-models", "cpp", "llama-2-13b-chat")
    model_path = os.path.join(cpp_model_root, "ggml-model-q4_0.gguf")
    if not os.path.exists(model_path):
        raise FileNotFoundError(
            f"Not found File: {model_path}\nrefer to https://github.com/ggerganov/llama.cpp"
        )
    return LlamaCpp(
        model_path=model_path,
        n_gpu_layers=40,
        # n_batch=256,
        # n_ctx=2048,
        # f16_kv=True,
        # max_tokens=4096,
        **kwargs,
    )


def chat_completion(user_prompt, system_prompt, kwargs):
    llm = get_llm(kwargs)
    system_message_prompt = SystemMessagePromptTemplate.from_template(system_prompt)
    human_template = "{user_prompt}"
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
    chat_prompt = ChatPromptTemplate.from_messages(
        [system_message_prompt, human_message_prompt]
    )
    chain = LLMChain(
        llm=llm,
        prompt=chat_prompt,
        verbose=True,
    )
    return chain.run(user_prompt)
