import transformers
import torch
from threading import Thread
from typing import List, Literal, Optional, Tuple, TypedDict

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


HistoryDialog = List[tuple[Message, Message]]

B_INST, E_INST = "[INST]", "[/INST]"
B_SYS, E_SYS = "<<SYS>>\n", "\n<</SYS>>\n\n"
DEFAULT_SYSTEM_PROMPT = """\
You are a helpful, respectful and honest assistant. Always answer as helpfully as possible, while being safe. Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. Please ensure that your responses are socially unbiased and positive in nature.

If a question does not make any sense, or is not factually coherent, explain why instead of answering something not correct. If you don't know the answer to a question, please don't share false information."""


def get_model_tokenizer():
    model = transformers.AutoModelForCausalLM.from_pretrained(
        model_id,
        device_map="auto",
        load_in_8bit=True,
        trust_remote_code=True,
    )
    tokenizer = transformers.AutoTokenizer.from_pretrained(model_id)
    return model, tokenizer


def get_prompt(
    message: str, chat_history: HistoryDialog, system_prompt: Optional[str]
) -> str:
    if system_prompt:
        texts = [f"{B_INST} {B_SYS}\n{system_prompt}\n{E_SYS}\n\n"]
    else:
        texts = [f"{B_INST} {B_SYS}\n{DEFAULT_SYSTEM_PROMPT}\n{E_SYS}\n\n"]
    for user_input, response in chat_history:
        texts.append(
            f"{user_input['content'].strip()} {E_INST} {response['content'].strip()} </s><s> {B_INST} "
        )
    texts.append(f"{message.strip()} {E_INST}")
    return "".join(texts)


def chat_stream_completion(
    model,
    tokenizer,
    message: str,
    chat_history: HistoryDialog,
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
        early_stopping=True,
    )
    prompt = get_prompt(message, chat_history, system_prompt)
    inputs = tokenizer([prompt], return_tensors="pt").input_ids.to(model.device)
    # Although inference is possible with the pipeline() function, it is not optimized for mixed-8bit models,
    # and will be slower than using the generate() method
    streamer = transformers.TextIteratorStreamer(
        tokenizer, timeout=10.0, skip_prompt=True, skip_special_tokens=True
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
