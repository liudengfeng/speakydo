from pylib.meta_llama2 import get_model_tokenizer

model, tokenizer = get_model_tokenizer()
print(model.get_memory_footprint() / 1024**3, "GB")
