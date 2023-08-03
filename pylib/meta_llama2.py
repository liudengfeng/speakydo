from threading import Thread
from typing import Any, List, Literal, Mapping, Optional, Tuple, TypedDict

import torch
import transformers
from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain.llms.base import LLM

model_id = "meta-llama/Llama-2-7b-chat-hf"

Role = Literal["system", "user", "assistant"]


class Message(TypedDict):
    role: Role
    content: str


class CompletionPrediction(TypedDict, total=False):
    generation: str
    tokens: List[str]  # not required
    logprobs: List[float]  # not required


class ChatPrediction(TypedDict, total=False):
    generation: Message
    tokens: List[str]  # not required
    logprobs: List[float]  # not required


# Dialog = List[tuple[Message, Message]]
Dialog = List[Message]
DialogPairHistory = List[Tuple[Message, Message]]

DEFAULT_SYSTEM_PROMPT = """\
You are a helpful, respectful and honest assistant. Always answer as helpfully as possible, while being safe. Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. Please ensure that your responses are socially unbiased and positive in nature.

If a question does not make any sense, or is not factually coherent, explain why instead of answering something not correct. If you don't know the answer to a question, please don't share false information."""


def get_model_tokenizer():
    model = transformers.AutoModelForCausalLM.from_pretrained(
        model_id,
        device_map="auto",
        load_in_8bit=True,
        # 由于精度限制,torch.bfloat16主要用于训练过程中,很少在推理部署中使用。
        torch_dtype=torch.float16,
        trust_remote_code=True,
    )
    tokenizer = transformers.AutoTokenizer.from_pretrained(model_id)
    model.eval()
    return model, tokenizer


def get_prompt(
    message: str, chat_pair_history: DialogPairHistory, system_prompt: str
) -> str:
    s_prompt, e_prompt = "<s>[INST]", "[/INST]"
    conversation = [f"<<SYS>>\n{system_prompt}\n<</SYS>>\n\n"]
    for user_input, response in chat_pair_history:
        conversation.append(
            "{} {} {}</s><s>[INST] ".format(
                user_input["content"].strip(), e_prompt, response["content"]
            )
        )
    conversation.append(f"{message}")
    return s_prompt + "".join(conversation) + e_prompt


def chat_stream_completion(
    model,
    tokenizer,
    message: str,
    chat_history: List[Dialog],
    system_prompt: Optional[str] = None,
    temperature: float = 0.6,
    top_p: float = 0.9,
    max_new_tokens: Optional[int] = None,
):
    max_len = max_new_tokens if max_new_tokens else 4096
    generation_config = transformers.GenerationConfig.from_pretrained(
        model_id,
        do_sample=True,
        temperature=temperature,
        top_p=top_p,
        # max_length=None,
        max_new_tokens=max_len,
        repetition_penalty=1.1,
        # early_stopping=True,
    )
    assert (
        len(chat_history) % 2 != 0
    ), "Chat history must appear in pairs, i.e. user input, ai response"
    chat_pairs = [(u, r) for u, r in zip(chat_history[::2], chat_history[1::2])]
    prompt = get_prompt(
        message, chat_pairs, system_prompt if system_prompt else DEFAULT_SYSTEM_PROMPT
    )
    inputs = tokenizer([prompt], return_tensors="pt").input_ids.to(model.device)
    # Although inference is possible with the pipeline() function, it is not optimized for mixed-8bit models,
    # and will be slower than using the generate() method
    streamer = transformers.TextIteratorStreamer(
        tokenizer, timeout=15.0, skip_prompt=True, skip_special_tokens=True
    )
    generation_kwargs = dict(
        inputs=inputs,
        streamer=streamer,
        generation_config=generation_config,
    )
    thread = Thread(target=model.generate, kwargs=generation_kwargs)
    thread.start()

    for text in streamer:
        yield text


def chat_completion(
    model,
    tokenizer,
    message: str,
    chat_history: List[Dialog],
    system_prompt: Optional[str] = None,
    temperature: float = 0.6,
    top_p: float = 0.9,
    max_new_tokens: Optional[int] = None,
):
    res = []
    for s in chat_stream_completion(
        model,
        tokenizer,
        message,
        chat_history,
        system_prompt,
        temperature,
        top_p,
        max_new_tokens,
    ):
        res.append(s)
    return "".join(res)


# class MetaLlaMa2(LLM):
#     model_meta: dict

#     @property
#     def _llm_type(self) -> str:
#         return "MetaLlaMa2"

#     def _call(
#         self,
#         prompt: str,
#         stop: Optional[List[str]] = None,
#         run_manager: Optional[CallbackManagerForLLMRun] = None,
#     ) -> str:
#         if stop is not None:
#             raise ValueError("stop kwargs are not permitted.")
#         return chat_completion(
#             self.model_meta.model,
#             self.model_meta.tokenizer,
#             prompt,
#             [],
#             temperature=self.model_meta.temperature,
#             top_p=self.model_meta.top_p,
#         )

#     @property
#     def _identifying_params(self) -> Mapping[str, Any]:
#         """Get the identifying parameters."""
#         return {
#             "model_id": model_id,
#             "temperature": self.model_meta.temperature,
#             "top_p": self.model_meta.top_p,
#         }
