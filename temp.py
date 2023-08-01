from pylib.meta_llama2 import *


model, tokenizer = get_model_tokenizer()
# print(model.get_memory_footprint() / 1024**3, "GB")
text = "Hamburg is in which country?\n"

res = chat_stream_completion(model, tokenizer, text, [], None)
for r in res:
    print(r)
