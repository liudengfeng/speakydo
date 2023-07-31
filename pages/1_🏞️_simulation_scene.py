import streamlit as st
from annotated_text import annotated_text
from pathlib import Path

current_dir: Path = (
    Path(__file__).parent.parent if "__file__" in locals() else Path.cwd()
)
video_path: Path = current_dir / "static/videos/chat.mp4"

st.set_page_config(
    page_title="模拟场景",
    page_icon="🏞️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# 侧面菜单注释
st.sidebar.subheader(st.session_state.native_language.simulation_scene_label)


with st.expander("🚨 如何与机器人聊天"):
    st.markdown(
        """
    - 多练习。要尽量多与机器人对话,通过大量练习提高流畅度和习惯
    - 明确表达。要尽量用简明清晰的语言表达自己的意思,避免语言过于简略或不够清晰,否则机器人可能无法准确理解你的意图
    - 针对性提问。如果需要机器人提供某方面的信息或回答某个具体问题,最好能够清晰地表达你的提问或疑问,避免过于笼统的提问,这有助于机器人提供更加准确和针对性的回复
    - 勇于纠错。如果发现机器人的回复中有任何错误或不妥之处,勇于纠正机器人,这有助于机器人继续学习和提高
    - [更多聊天模板](https://github.com/f/awesome-chatgpt-prompts)
    """
    )
    st.header("🦁 英语口语助手")
    annotated_text(
        "我希望您",
        ("扮演英语口语教师。", "角色"),
        ("我与您都用英语对话，", "对话语言"),
        ("您回答时尽量简洁，限制在100字以内。", "要求1"),
        ("另外，请您严格纠正我的语法错误、错别字和事实错误。", "要求2"),
        ("我希望你在回复中问我一个问题。", "互动方式"),
        ("现在让我们开始练习，你可以先问我一个问题。", "互动方式"),
        ("请记住，我希望您严格纠正我的语法错误、错别字和事实错误。", "可选强调"),
        ("假设我英语词汇量处于中级", "基准"),
        ("且只对旅游话题感兴趣。", "范围"),
    )
    st.divider()
    st.markdown(
        "I want you to act as a spoken English teacher and improver. I will speak to you in English and you will reply to me in English to practice my spoken English. I want you to keep your reply neat, limiting the reply to 100 words. I want you to strictly correct my grammar mistakes, typos, and factual errors. I want you to ask me a question in your reply. Now let's start practicing, you could ask me a question first. Remember, I want you to strictly correct my grammar mistakes, typos, and factual errors."
    )
    st.divider()
    st.video(str(video_path), format="video/mp4", start_time=0)
