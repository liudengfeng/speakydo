from dataclasses import dataclass
from typing import List

REPO_URL: str = "https://github.com/liudengfeng/speakydo"
README_URL: str = f"{REPO_URL}#readme"
BUG_REPORT_URL: str = f"{REPO_URL}/issues"
STUDIO_URL: str = "https://speakydo.streamlit.app/"


# name, view name, description
TTS_VOICES = {
    "en-US": [
        ("en-US-ChristopherNeural", "Christopher 【male】", ""),
        ("en-US-RogerNeural", "Roger 【male】", ""),
        ("en-US-JennyNeural", "Jenny 【female】", ""),
        ("en-US-AnaNeural", "Ana 【female】", ""),
    ],
    "ja-JP": [
        ("ja-JP-DaichiNeural", "Daichi 【男】", ""),
        ("ja-JP-NaokiNeural", "Naoki 【男】", ""),
        ("ja-JP-NanamiNeural", "Nanami 【女】", ""),
        ("ja-JP-AoiNeural", "Aoi 【女】", ""),
    ],
    "zh-CN": [
        ("zh-CN-YunxiNeural", "云希 【男】", "活泼、阳光的声音，具有丰富的情感，可用于许多对话场景。"),
        ("zh-CN-YunyeNeural", "云野 【男】", "成熟、放松的声音，具有多种情感，适合音频书籍。"),
        ("zh-CN-YunyangNeural", "云扬 【男】", "专业、流利的声音，具有多种场景风格。"),
        ("zh-CN-XiaoxiaoNeural", "晓晓 【女】", "活泼、温暖的声音，具有多种场景风格和情感。"),
        ("zh-CN-XiaoyouNeural", "晓悠 【女】", "天使般的清晰声音，可以应用于许多儿童相关场景。"),
        ("zh-CN-XiaomoNeural", "晓墨 【女】", "清晰、放松的声音，具有丰富的角色扮演和情感，适合音频书籍。"),
    ],
    "fr-FR": [
        ("fr-FR-HenriNeural", "Henri 【mâle】", ""),
        ("fr-FR-ClaudeNeural", "Claude 【mâle】", ""),
        ("fr-FR-CelesteNeural", "Celeste 【femelle】", ""),
        ("fr-FR-EloiseNeural", "Eloise 【femelle】", ""),
    ],
}


LAN_LABELS = {
    "zh-CN": {
        "language_label": "简体中文",
        "app_introduce": """**沉浸式口语练习应用程序**""",
        "home_page_title": "主页",
        "native_language_label": "请选择您的母语",
        "target_language_label": "请选择您要学习的目标语言",
        "feedback_label": "反馈",
        "contact_me_label": "联系我们",
    },
    "en-US": {
        "language_label": "English",
        "app_introduce": """**The Immersive Spoken Language Practice App**""",
        "home_page_title": "Home",
        "native_language_label": "Please select your native language",
        "target_language_label": "Please select the target language you want to learn",
        "feedback_label": "feedback",
        "contact_me_label": "Contact me",
    },
    "ja-JP": {
        "language_label": "日本語",
        "app_introduce": """**没入型の話し言葉練習アプリ**""",
        "home_page_title": "家",
        "native_language_label": "あなたの母国語を選択してください",
        "target_language_label": "学びたい言語を選択してください",
        "feedback_label": "フィードバック",
        "contact_me_label": "私に連絡して",
    },
    "fr-FR": {
        "language_label": "Français",
        "app_introduce": """**L'application immersive de pratique de la langue parlée**""",
        "home_page_title": "maison",
        "native_language_label": "Veuillez sélectionner votre langue maternelle",
        "target_language_label": "Veuillez sélectionner la langue cible que vous souhaitez apprendre",
        "feedback_label": "le compte rendu",
        "contact_me_label": "Contactez moi",
    },
}


@dataclass
class Locale:
    language_key: str
    language_label: str
    app_introduce: str
    home_page_title: str
    native_language_label: str
    target_language_label: str
    feedback_label: str
    contact_me_label: str
    simulation_scene_label: str
    chatbot_label: str


zh_cn = Locale(
    language_key="zh-CN",
    language_label="简体中文",
    app_introduce="""**沉浸式口语练习应用程序**""",
    home_page_title="主页",
    native_language_label="请选择您的母语",
    target_language_label="要学习的目标语言",
    feedback_label="反馈",
    contact_me_label="联系我们",
    simulation_scene_label="模拟场景",
    chatbot_label="聊天机器人",
)

en_us = Locale(
    language_key="en-US",
    language_label="English",
    app_introduce="""**The Immersive Spoken Language Practice App**""",
    home_page_title="Home",
    native_language_label="Please select your native language",
    target_language_label="target language you want to learn",
    feedback_label="feedback",
    contact_me_label="Contact us",
    simulation_scene_label="simulation scene",
    chatbot_label="chatbot",
)

ja_jp = Locale(
    language_key="ja-JP",
    language_label="日本語",
    app_introduce="""**没入型の話し言葉練習アプリ**""",
    home_page_title="主页",
    native_language_label="あなたの母国語を選択してください",
    target_language_label="学びたい言語",
    feedback_label="フィードバック",
    contact_me_label="お問い合わせ",
    simulation_scene_label="シミュレーションシーン",
    chatbot_label="チャットボット",
)

fr_fr = Locale(
    language_key="fr-FR",
    language_label="Français",
    app_introduce="""**L'application immersive de pratique de la langue parlée**""",
    home_page_title="主页",
    native_language_label="Veuillez sélectionner votre langue maternelle",
    target_language_label="langue cible que vous souhaitez apprendre",
    feedback_label="retour",
    contact_me_label="Contactez-nous",
    simulation_scene_label="scène de simulation",
    chatbot_label="chatbot",
)

LAN_MAPS = {
    "zh-CN": zh_cn,
    "en-US": en_us,
    "ja-JP": ja_jp,
    "fr-FR": fr_fr,
}