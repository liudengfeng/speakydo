import transformers
import torch


model_id = "meta-llama/Llama-2-7b-chat-hf"


def get_model_tokenizer():
    model = transformers.AutoModelForCausalLM.from_pretrained(
        model_id,
        device_map="auto",
        # load_in_8bit=True,
    )
    tokenizer = transformers.AutoTokenizer.from_pretrained(model_id)
    return model, tokenizer
