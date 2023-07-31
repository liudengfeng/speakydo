import streamlit as st
import streamlit.components.v1 as components
from pylib.cognitive import (
    # speech_recognize_once_from_mic,
    speech_synthesis_to_file,
    # record_audio,
    pronunciation_assessment_from_microphone,
)
from pylib.constants import TTS_VOICES
from pathlib import Path
from annotated_text import annotated_text, annotation

# --- PATH SETTINGS ---
current_dir: Path = Path(__file__).parent.parent

voice_path: Path = current_dir / "static/audio"

st.set_page_config(
    page_title="口语练习",
    page_icon="🗣️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 练习口语历史记录
if "spoken_list" not in st.session_state:
    st.session_state["spoken_list"] = []

# 侧面菜单注释
st.sidebar.subheader(st.session_state.native_language.oral_practice_label)

voice_options = [
    item[0] for item in TTS_VOICES[st.session_state.target_language.language_key]
]


def get_index(voice):
    names = [
        item[0] for item in TTS_VOICES[st.session_state.target_language.language_key]
    ]
    return names.index(voice)


def voice_format_func(voice):
    i = get_index(voice)
    return TTS_VOICES[st.session_state.target_language.language_key][i][1]


st.sidebar.selectbox(
    st.session_state.native_language.selectbox_voice_name_label,
    voice_options,
    format_func=voice_format_func,
    key="voice_name",
    # label_visibility="hidden",
)


voice_file = voice_path / "{}.wav".format(st.session_state["voice_name"])
st.sidebar.audio(str(voice_file))

# 指定录制音频时长
max_duration = st.sidebar.slider(
    st.session_state.native_language.voice_duration_label,
    min_value=3,
    max_value=30,
    value=15,
)  # Duration of recording


@st.cache_data(show_spinner="Speech synthesis from Azure AI...")
def tts_mav_file(text):
    return speech_synthesis_to_file(
        text,
        st.session_state["voice_name"],
        st.secrets.Microsoft.SPEECH_KEY,
        st.secrets.Microsoft.SPEECH_REGION,
    )


@st.cache_data(
    show_spinner="Performs one-shot pronunciation assessment asynchronously with input from microphone with Azure AI..."
)
def pafm(text):
    return pronunciation_assessment_from_microphone(
        text,
        st.secrets.Microsoft.SPEECH_KEY,
        st.secrets.Microsoft.SPEECH_REGION,
        st.session_state.target_language.language_key,
    )


def gen_badge(mispronunciation, omission, insertion):
    return f"""
    <button type="button" class="btn btn-warning" data-bs-toggle="tooltip" data-bs-placement="top" data-bs-title="说得不正确的字词。此类型来自 SDK 返回的参数: "ErrorType"。">
    发音错误
    <span class="badge text-bg-warning">{mispronunciation}</span>
    </button>
    <button type="button" class="btn btn-secondary" data-bs-toggle="tooltip" data-bs-placement="top" data-bs-title="脚本中提供的但未说出的字词。此类型来自 SDK 返回的参数: "ErrorType"。">
    遗漏
    <span class="badge text-bg-secondary">{omission}</span>
    </button>
    <button type="button" class="btn btn-danger" data-bs-toggle="tooltip" data-bs-placement="top" data-bs-title="不在脚本中但在录制中检测到的字词。此类型来自 SDK 返回的参数: "ErrorType"。">
    插入内容
    <span class="badge text-bg-danger">{insertion}</span>
    </button>
    """


def practice(i, text):
    col1, col2, col3, col4, _ = st.columns([1, 1, 1, 1, 8])
    s_col1, _ = st.columns([4, 8])
    with col1:
        listen_btn = st.button("👂聆听", key="listen_{}".format(i), help="点击聆听文本")
    with col2:
        speak_btn = st.button(
            "🔊朗读", key="speak_{}".format(i), help="点击跟读文本，👈左侧菜单滑块可设定录制时长"
        )
        # if speak_btn:
        #     wav = record_audio(max_duration)
        #     if len(st.session_state["spoken_list"]) == i + 1:
        #         # 替代
        #         st.session_state["spoken_list"][i] = wav
        #     else:
        #         st.session_state["spoken_list"].append(wav)
    with col3:
        replay_btn = st.button("🎧回放", key="replay_{}".format(i), help="回放跟读音频")
    with col4:
        evaluation_btn = st.button("🎼评估", key="evaluation_{}".format(i), help="语音评估")

    st.markdown(text)

    with s_col1:
        if listen_btn:
            st.audio(tts_mav_file(text))
        if replay_btn:
            if len(st.session_state["spoken_list"]) >= i + 1:
                st.audio(st.session_state["spoken_list"][i])
            else:
                st.warning("录制音频后才能回放", icon="⚠️")

    st.divider()
    container = st.container()
    if evaluation_btn:
        result = pafm(text)
        # st.write(result)
        with container:
            if result["warning"]:
                st.warning(result["warning"], icon="⚠️")
            elif result["error"]:
                st.error(result["error"], icon="🚨")
            else:
                info = result["final_words"]["counter_info"]
                components.html(
                    """
                    <head>
                    <meta charset="utf-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1">
                    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-9ndCyUaIbzAi2FUVXJi0CjmCapSmO7SnpJef0486qhLnuZ2cdeRhO02iuK6FUUVM" crossorigin="anonymous">
                    </head>{}""".format(
                        gen_badge(
                            info["mispronunciation"],
                            info["omission"],
                            info["insertion"],
                        )
                    ),
                    height=50,
                )
                annotated_text(
                    *[annotation(**tag) for tag in result["final_words"]["tags"]]
                )

                col1, col2, col3, col4 = st.columns(4)
                last_score = st.session_state["assessment_score"][-1]
                col1.metric(
                    "发音分数",
                    "{:.2f}".format(result["scores"]["pronunciation"]),
                    "{:.2f}".format(
                        result["scores"]["pronunciation"] - last_score["pronunciation"]
                    ),
                    help="表示给定语音发音质量的总体分数。它是从 AccuracyScore、FluencyScore、CompletenessScore、Weight 按权重聚合的。",
                )
                col2.metric(
                    "准确性评分",
                    "{:.2f}".format(result["scores"]["accuracy"]),
                    "{:.2f}".format(
                        result["scores"]["accuracy"] - last_score["accuracy"]
                    ),
                    help="语音的发音准确性。准确性表示音素与母语说话人的发音的匹配程度。字词和全文的准确性得分是由音素级的准确度得分汇总而来。",
                )
                col3.metric(
                    "流畅性评分",
                    "{:.2f}".format(result["scores"]["fluency"]),
                    "{:.2f}".format(
                        result["scores"]["fluency"] - last_score["fluency"]
                    ),
                    help="给定语音的流畅性。流畅性表示语音与母语说话人在单词间的停顿上有多接近。",
                )
                col4.metric(
                    "完整性评分",
                    "{:.2f}".format(result["scores"]["completeness"]),
                    "{:.2f}".format(
                        result["scores"]["completeness"] - last_score["completeness"]
                    ),
                    help="语音的完整性，按发音单词与输入引用文本的比率计算。",
                )
        # 记录得分
        st.session_state["assessment_score"].append(result["scores"])
    st.divider()


# 临时测试
if "scenario" not in st.session_state:
    st.session_state[
        "scenario"
    ] = """For users who have already developed prompts and flows using the open-source library, such as LangChain, prompt flow provides a seamless integration pathway. 
    This compatibility enables you to lift and shift your existing assets to prompt flow, facilitating Prompt Engineering, evaluation, and collaboration efforts to prepare your flow for production. 
    This smooth transition ensures that your previous work is not lost and can be further enhanced within the prompt flow environment for evaluation, optimization and production."""

if st.session_state["scenario"]:
    sentences = [l for l in st.session_state["scenario"].splitlines() if l]
    # 按行分割，去除空行
    for i, line in enumerate(sentences):
        practice(i, line)
