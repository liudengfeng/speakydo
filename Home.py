import streamlit as st
from pylib.constants import LAN_MAPS, BUG_REPORT_URL, REPO_URL
from pathlib import Path
from PIL import Image

# --- PATH SETTINGS ---
current_dir: Path = Path(__file__).parent if "__file__" in locals() else Path.cwd()
logo_path: Path = current_dir / "static/dfstudio.png"


if "native_language" not in st.session_state:
    st.session_state["native_language"] = LAN_MAPS["zh-CN"]

if "target_language" not in st.session_state:
    st.session_state["target_language"] = LAN_MAPS["en-US"]

st.set_page_config(
    page_title=st.session_state.native_language.home_page_title,
    page_icon="🎼",
    layout="centered",
    initial_sidebar_state="expanded",
)


# 口语文本
# if "scenario" not in st.session_state:
#     st.session_state["scenario"] = ""

# 练习口语历史记录
# if "spoken_list" not in st.session_state:
#     st.session_state["spoken_list"] = []

# 发音评估得分
# if "assessment_score" not in st.session_state:
#     st.session_state["assessment_score"] = [
#         {"pronunciation": 0, "accuracy": 0, "fluency": 0, "completeness": 0}
#     ]


def format_func(lan):
    return "{} {}".format(lan, LAN_MAPS[lan].language_label)


image = Image.open(logo_path)


t1, t2 = st.columns([1, 1], gap="large")

with t1:
    st.image(image, caption="", width=256)
with t2:
    st.markdown(
        """
        ## DF Studio
        {}
        """.format(
            st.session_state.native_language.app_introduce
        ),
        unsafe_allow_html=True,
    )

col1, col2 = st.columns(2)
options = list(LAN_MAPS.keys())


def on_native_language_changed():
    st.experimental_rerun()


with col1:
    native_language = st.selectbox(
        st.session_state.native_language.native_language_label,
        options=options,
        format_func=format_func,
        # on_change=on_native_language_changed,
        index=options.index(st.session_state.native_language.language_key),
        help=LAN_MAPS["en-US"].native_language_label,
    )
    st.session_state.native_language = LAN_MAPS[native_language]


with col2:
    target_language = st.selectbox(
        st.session_state.native_language.target_language_label,
        options=options,
        format_func=format_func,
        index=options.index(st.session_state.target_language.language_key),
        # key="selected_target_language",
        help=LAN_MAPS["en-US"].target_language_label,
    )
    st.session_state.target_language = LAN_MAPS[target_language]


st.divider()
st.header("沉浸式口语练习")
st.markdown(
    """
    - 使用meta-llama大型语言模型，提供丰富多样的模拟场景，增强趣味性，辅助记忆
    - 沉浸在语言环境中，可以不断体会到语言的乐趣，增强学习的动力和热情，达到事半功倍的效果
    - 使用微软AI语音评估技术，评估语音发音，就语音的准确性和流畅性提供反馈
    - 通过发音评估，语言学习者可以练习、获取即时反馈并改进其发音，使他们可以自信地说话和表达
    """,
    unsafe_allow_html=True,
)

st.divider()
st.markdown(
    f"""
### :page_with_curl: {LAN_MAPS[native_language].feedback_label}

- [{LAN_MAPS[native_language].contact_me_label} slack](https://join.slack.com/t/ldf-co/shared_invite/zt-1xidkytb8-7ePs_0wGOZPKRnUFMXshsA) 
- [report bug]({BUG_REPORT_URL})
"""
)
st.divider()
st.markdown(f"To view the project, please visit [github]({REPO_URL}).")


# 侧面菜单注释
st.sidebar.subheader(st.session_state.native_language.home_page_title)