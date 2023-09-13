"""具体来说，可以采用以下间隔设置策略：
⏳
**第一次复习：**20-30 分钟后
**第二次复习：**2-3 天后
**第三次复习：**7-10 天后
**第四次复习：**2-3 周后
**第五次复习：**1-2 月后"""

import json
import os
import random
import time
from pathlib import Path
import pygame
import streamlit as st
import streamlit.components.v1 as components

from pylib.bootstrap import HTML_HEAD

RESOURCE_PATH = (Path(__file__).parent.parent / "resource").absolute()
WORDS_PATH = RESOURCE_PATH / st.session_state.native_language.language_key / "words"


# 辅助函数
def word2fname(word: str):
    w = word.replace(" ", "_")
    w = w.replace("/", "-")
    w = w.replace("?", "问号")
    return w


def parse2header(fp):
    fn = fp.stem
    ns = fn.split("_")
    if len(ns) == 4:
        return f"{ns[1]}({ns[2]}-{ns[3]})【{ns[0]}】"
    elif len(ns) == 3:
        return f"{ns[1]}({ns[2]})【{ns[0]}】"
    elif len(ns) == 2:
        return f"{ns[0]}({ns[1]})"
    else:
        return fn


def gen_word_card(header, word_dict):
    return f"""
{HTML_HEAD}
<div class="card text-center border-light mb-3">
    <div class="card-header">{header}</div>
    <div class="card-body">
    <h3 class="card-title">{word_dict["name"]}</h5>
    <p class="card-text text-success">{",".join(word_dict["trans"])}</p>
    </div>
</div>
"""


pygame.init()

st.set_page_config(
    page_title=st.session_state.native_language.memorize_word_page_title,
    page_icon="📽️",
    layout="centered",
    initial_sidebar_state="expanded",
)

# 侧面菜单注释
st.sidebar.subheader(st.session_state.native_language.memorize_word_page_title)

# 文件名称
file_paths = sorted([file_name for file_name in WORDS_PATH.glob("*.json")])
# 词库
selected_file = st.sidebar.selectbox(
    st.session_state.native_language.selectbox_dialogue_word_books_label,
    file_paths,
    format_func=lambda x: x.stem,
)

word_num = st.sidebar.slider(
    st.session_state.native_language.word_number_label,
    min_value=5,
    max_value=30,
    value=10,
    step=1,
    help="记忆专家认为学习英语单词每次 5-10 个单词为宜",
)

intervals = st.sidebar.slider(
    st.session_state.native_language.presentation_interval_label,
    min_value=1.0,
    max_value=20.0,
    value=3.0,
    step=0.5,
    help="新单词间隔应该设置在 5-10 秒左右",
)

voice_on = st.sidebar.toggle(
    st.session_state.native_language.voice_toggle_label, value=True
)

header = parse2header(selected_file)
to_learn = []

# TODO:根据用户学习记录调整【掌握程度、学习间隔】
with open(selected_file, "r") as f:
    # 读取 JSON 文件
    words = json.load(f)
    to_learn = random.sample(words, word_num)

with st.empty():
    for w in to_learn:
        duration = 0
        start = time.time()
        components.html(gen_word_card(header, w), height=300)
        if voice_on:
            fn = word2fname(w["name"])
            mp3 = WORDS_PATH / "voice" / f"{fn}.mp3"
            sound = pygame.mixer.Sound(mp3)
            sound.play()
        duration = time.time() - start
        time.sleep(intervals - duration if intervals > duration else 0)

pygame.quit()
