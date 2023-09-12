"""具体来说，可以采用以下间隔设置策略：

**第一次复习：**20-30 分钟后
**第二次复习：**2-3 天后
**第三次复习：**7-10 天后
**第四次复习：**2-3 周后
**第五次复习：**1-2 月后"""

import streamlit as st
import time
from pathlib import Path
import os
import json
import random


WORDS_PATH = (Path(__file__).parent.parent / "resource/words").absolute()

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

to_learn = []

with open(selected_file, "r") as f:
    # 读取 JSON 文件
    words = json.load(f)
    to_learn = random.sample(words, word_num)

with st.empty():
    for w in to_learn:
        st.write(f"⏳ {w['name']} {w['trans']}")
        time.sleep(intervals)
# st.stop()
