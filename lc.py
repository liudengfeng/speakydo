from pylib.meta_llama2 import (
    get_prompt,
    Message,
    get_model_tokenizer,
)

# m, t = get_model_tokenizer()

dialogs = [
    Message(role="user", content="user 指示1"),
    Message(role="assistant", content="assistant 回复1"),
    Message(role="user", content="user 指示2"),
    Message(role="assistant", content="assistant 回复2"),
]

chat_pairs = [(u, r) for u, r in zip(dialogs[::2], dialogs[1::2])]

print(
    get_prompt(
        "最新查询",
        chat_pairs,
        "系统指示",
    )
)
