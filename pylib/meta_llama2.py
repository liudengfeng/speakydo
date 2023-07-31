import json
import requests


LAN_MODEL_MAPS = {
    "zh-en": "Helsinki-NLP/opus-mt-zh-en",
    "en-zh": "Helsinki-NLP/opus-mt-en-zh",
    "en-ja": "Helsinki-NLP/opus-tatoeba-en-ja",
    "en-fr": "Helsinki-NLP/opus-mt-en-fr",
}


TEXT_GENERATION_MODELS = ["gpt2", "mosaicml/mpt-7b-instruct"]


def get_endpoint(src, tgt):
    URL_FMT = "https://api-inference.huggingface.co/models/{}"
    m = "{}-{}".format(src, tgt)
    if m in LAN_MODEL_MAPS.keys():
        return URL_FMT.format(LAN_MODEL_MAPS[m])
    else:
        raise ValueError("暂不支持`{}`翻译".format(m))


def lan2lan(txt: str, src: str, tgt: str, token: str):
    data = json.dumps({"inputs": txt})
    headers = {"Authorization": f"Bearer {token}"}
    url = get_endpoint(src, tgt)
    response = requests.request("POST", url, headers=headers, data=data)
    return json.loads(response.content.decode("utf-8"))


def chat_generate(msg: str, model: str, token: str):
    # 生成的文本主要用于情景模拟，不需要修改设置 top_k top_p temperature 等参数
    # There is a cache layer on the inference API to speedup requests we have already seen.
    # mosaicml/mpt-7b-instruct dolly-15k format
    data = json.dumps({"inputs": msg, "use_cache": True})
    headers = {"Authorization": f"Bearer {token}"}
    url = "https://api-inference.huggingface.co/models/{}".format(model)
    response = requests.request("POST", url, headers=headers, data=data)
    return json.loads(response.content.decode("utf-8"))
