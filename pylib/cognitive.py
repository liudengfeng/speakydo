"""认知服务辅助函数"""

import azure.cognitiveservices.speech as speechsdk
import requests, uuid
from pathlib import Path
import tempfile

# import sounddevice as sd
# import soundfile as sf
import string
import difflib


current_dir: Path = Path(__file__).parent


# def record_audio(max_duration):
#     """录音

#     Args:
#         max_duration (int): 音频长度

#     Returns:
#         str: 音频临时文件路径
#     """
#     fs = 44100  # Sample rate
#     myrecording = sd.rec(int(max_duration * fs), samplerate=fs, channels=2)
#     sd.wait()  # Wait until recording is finished
#     filename = tempfile.mktemp(prefix="rec_", suffix=".wav")
#     sf.write(filename, myrecording, fs)
#     return filename


def translate(text: str, src: str, tgt: str, key: str, location: str):
    """翻译文本

    Args:
        text (str): 翻译文本
        src (str): 源语言
        tgt (str): 目标语言
        key (str): 微软云 key
        location (str): 微软云 location

    Returns:
        list of dict:

    [
        {
            "translations": [
                {
                    "text": "我很高兴尝试文本到语音转换",
                    "to": "zh-Hans"
                }
            ]
        }
    ]
    """
    endpoint = "https://api.cognitive.microsofttranslator.com"
    path = "/translate"
    constructed_url = endpoint + path

    params = {"api-version": "3.0", "from": src, "to": [tgt]}

    headers = {
        "Ocp-Apim-Subscription-Key": key,
        # location required if you're using a multi-service or regional (not global) resource.
        "Ocp-Apim-Subscription-Region": location,
        "Content-type": "application/json",
        "X-ClientTraceId": str(uuid.uuid4()),
    }

    # You can pass more than one object in body.
    body = [{"text": text}]
    request = requests.post(constructed_url, params=params, headers=headers, json=body)
    response = request.json()
    return response


def speech_synthesis_to_file(
    text: str, voice_name: str, subscription: str, region: str, filename=None
):
    """语音合成

    Args:
        text (str): 文本
        voice_name (str): 语音名称
        subscription (str): 订阅key
        region (str): 订阅region

    Returns:
        file path: 存储音频文件的路径
    """
    speech_config = speechsdk.SpeechConfig(subscription=subscription, region=region)
    # The language of the voice that speaks.
    speech_config.speech_synthesis_voice_name = voice_name
    if filename is None:
        filename = tempfile.mktemp(prefix="rec_", suffix=".wav")
    audio_config = speechsdk.audio.AudioOutputConfig(filename=str(filename))
    speech_synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=speech_config, audio_config=audio_config
    )
    # 获取结果
    speech_synthesizer.speak_text_async(text).get()
    return filename


def speech_recognize_once_from_mic(speech_key, service_region, language="zh-cn"):
    """performs one-shot speech recognition from the default microphone"""
    speech_config = speechsdk.SpeechConfig(
        subscription=speech_key,
        region=service_region,
        speech_recognition_language=language,
    )
    # audio_config = speechsdk.AudioConfig(use_default_microphone=True)
    # Creates a recognizer with the given settings
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)

    # Starts speech recognition, and returns after a single utterance is recognized. The end of a
    # single utterance is determined by listening for silence at the end or until a maximum of 15
    # seconds of audio is processed.  The task returns the recognition text as result.
    # Note: Since recognize_once() returns only a single utterance, it is suitable only for single
    # shot recognition like command or query.
    # For long-running multi-utterance recognition, use start_continuous_recognition() instead.
    return speech_recognizer.recognize_once()


def speech_recognize_once_from_file(
    wav_file, speech_key, service_region, language="en-US"
):
    """performs one-shot speech recognition with input from an audio file"""
    # <SpeechRecognitionWithFile>
    speech_config = speechsdk.SpeechConfig(
        subscription=speech_key, region=service_region
    )
    audio_config = speechsdk.audio.AudioConfig(filename=wav_file)
    # Creates a speech recognizer using a file as audio input, also specify the speech language
    speech_recognizer = speechsdk.SpeechRecognizer(
        speech_config=speech_config, language=language, audio_config=audio_config
    )

    # Starts speech recognition, and returns after a single utterance is recognized. The end of a
    # single utterance is determined by listening for silence at the end or until a maximum of 15
    # seconds of audio is processed. It returns the recognition text as result.
    # Note: Since recognize_once() returns only a single utterance, it is suitable only for single
    # shot recognition like command or query.
    # For long-running multi-utterance recognition, use start_continuous_recognition() instead.
    return speech_recognizer.recognize_once()


def speech_recognize_once_compressed_input(
    mp3_file, speech_key, service_region, language="en-US"
):
    """performs one-shot speech recognition with compressed input from an audio file [mp3]"""

    # <SpeechRecognitionWithCompressedFile>
    class BinaryFileReaderCallback(speechsdk.audio.PullAudioInputStreamCallback):
        def __init__(self, filename: str):
            super().__init__()
            self._file_h = open(filename, "rb")

        def read(self, buffer: memoryview) -> int:
            try:
                size = buffer.nbytes
                frames = self._file_h.read(size)

                buffer[: len(frames)] = frames

                return len(frames)
            except Exception as ex:
                print("Exception in `read`: {}".format(ex))
                raise

        def close(self) -> None:
            print("closing file")
            try:
                self._file_h.close()
            except Exception as ex:
                print("Exception in `close`: {}".format(ex))
                raise

    # Creates an audio stream format. For an example we are using MP3 compressed file here
    compressed_format = speechsdk.audio.AudioStreamFormat(
        compressed_stream_format=speechsdk.AudioStreamContainerFormat.MP3
    )
    callback = BinaryFileReaderCallback(filename=mp3_file)
    stream = speechsdk.audio.PullAudioInputStream(
        stream_format=compressed_format, pull_stream_callback=callback
    )

    speech_config = speechsdk.SpeechConfig(
        subscription=speech_key, region=service_region
    )
    audio_config = speechsdk.audio.AudioConfig(stream=stream)

    # Creates a speech recognizer using a file as audio input, also specify the speech language
    speech_recognizer = speechsdk.SpeechRecognizer(
        speech_config, audio_config, language=language
    )

    # Starts speech recognition, and returns after a single utterance is recognized. The end of a
    # single utterance is determined by listening for silence at the end or until a maximum of 15
    # seconds of audio is processed. It returns the recognition text as result.
    # Note: Since recognize_once() returns only a single utterance, it is suitable only for single
    # shot recognition like command or query.
    # For long-running multi-utterance recognition, use start_continuous_recognition() instead.
    return speech_recognizer.recognize_once()

    # # Check the result
    # if result.reason == speechsdk.ResultReason.RecognizedSpeech:
    #     print("Recognized: {}".format(result.text))
    # elif result.reason == speechsdk.ResultReason.NoMatch:
    #     print("No speech could be recognized: {}".format(result.no_match_details))
    # elif result.reason == speechsdk.ResultReason.Canceled:
    #     cancellation_details = result.cancellation_details
    #     print("Speech Recognition canceled: {}".format(cancellation_details.reason))
    #     if cancellation_details.reason == speechsdk.CancellationReason.Error:
    #         print("Error details: {}".format(cancellation_details.error_details))


def gen_word_tags(final_words, accuracy_upper=85):
    """生成词语标识

    Args:
        final_words (list): word对象列表
        accuracy_upper (int, optional): 精确度. Defaults to 85.

    Returns:
        dict: 供文字标注的字典信息
    """
    mispronunciation, omission, insertion = 0, 0, 0
    tags = []
    for word in final_words:
        tag = {"body": word.word}
        match word.error_type:
            case "Mispronunciation":
                tag["background"] = "#DAA520"
            case "Omission":
                tag["background"] = "#808080"
            case "Insertion":
                # 删除线
                tag["background"] = "#DC143C"
                tag["text_decoration"] = "line-through"
            case _:
                if word.accuracy_score >= accuracy_upper:
                    tag["background"] = "#32CD32"
        tags.append(tag)
    return {
        "counter_info": {
            "mispronunciation": mispronunciation,
            "omission": omission,
            "insertion": insertion,
        },
        "tags": tags,
    }


def recognizer_normalizated(reference_text, result, language):
    output = {
        "warning": "",
        "error": "",
        "scores": {
            "pronunciation": 0,
            "accuracy": 0,
            "completeness": 0,
            "fluency": 0,
        },
        "final_words": [],
    }
    if result.reason == speechsdk.ResultReason.NoMatch:
        output["warning"] = "No speech could be recognized"
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        error = "Speech Recognition canceled: {}".format(cancellation_details.reason)
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            error += "Error details: {}".format(cancellation_details.error_details)
        output["error"] = error
    else:
        pronunciation_result = speechsdk.PronunciationAssessmentResult(result)
        output["scores"] = {
            "accuracy": pronunciation_result.accuracy_score,
            "pronunciation": pronunciation_result.pronunciation_score,
            "completeness": pronunciation_result.completeness_score,
            "fluency": pronunciation_result.fluency_score,
        }

        # we need to convert the reference text to lower case, and split to words, then remove the punctuations.
        recognized_words = pronunciation_result.words
        if language == "zh-CN":
            # Use jieba package to split words for Chinese
            import jieba
            import zhon.hanzi

            jieba.suggest_freq([x.word for x in recognized_words], True)
            reference_words = [
                w for w in jieba.cut(reference_text) if w not in zhon.hanzi.punctuation
            ]
        else:
            reference_words = [
                w.strip(string.punctuation) for w in reference_text.lower().split()
            ]

        # For continuous pronunciation assessment mode, the service won't return the words with `Insertion` or `Omission`
        # even if miscue is enabled.
        # We need to compare with the reference text after received all recognized words to get these error words.
        normed_words = [x.word.lower() for x in recognized_words]
        diff = difflib.SequenceMatcher(None, reference_words, normed_words)
        final_words = []
        for tag, i1, i2, j1, j2 in diff.get_opcodes():
            # print(
            #     "{:7}   a[{}:{}] --> b[{}:{}] {!r:>8} --> {!r}".format(
            #         tag, i1, i2, j1, j2, reference_words[i1:i2], normed_words[j1:j2]
            #     )
            # )
            if tag in ["insert", "replace"]:
                for word in recognized_words[j1:j2]:
                    if word.error_type == "None":
                        word._error_type = "Insertion"
                    final_words.append(word)
            if tag in ["delete", "replace"]:
                for word_text in reference_words[i1:i2]:
                    word = speechsdk.PronunciationAssessmentWordResult(
                        {
                            "Word": word_text,
                            "PronunciationAssessment": {
                                "ErrorType": "Omission",
                            },
                        }
                    )
                    final_words.append(word)
            if tag == "equal":
                final_words += recognized_words[j1:j2]
        output["final_words"] = gen_word_tags(final_words)
    return output


def pronunciation_assessment_from_microphone(
    reference_text, speech_key, service_region, language="en-US"
):
    """Performs one-shot pronunciation assessment asynchronously with input from microphone.
    See more information at https://aka.ms/csspeech/pa"""

    # Creates an instance of a speech config with specified subscription key and service region.
    # Replace with your own subscription key and service region (e.g., "westus").
    config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)

    # The pronunciation assessment service has a longer default end silence timeout (5 seconds) than normal STT
    # as the pronunciation assessment is widely used in education scenario where kids have longer break in reading.
    # You can adjust the end silence timeout based on your real scenario.
    config.set_property(
        speechsdk.PropertyId.SpeechServiceConnection_EndSilenceTimeoutMs, "2000"
    )

    # create pronunciation assessment config, set grading system, granularity and if enable miscue based on your requirement.
    pronunciation_config = speechsdk.PronunciationAssessmentConfig(
        # json_string=json_config
        # 用来对发音进行评估的文本
        reference_text=reference_text,
        # HundredMark 系统给出 0-100 的浮点分数
        grading_system=speechsdk.PronunciationAssessmentGradingSystem.HundredMark,
        # 确定评估粒度的最低级别。 Word（显示全文和单词级别的分数
        granularity=speechsdk.PronunciationAssessmentGranularity.Word,
        # 将发音的字与引用文本进行比较时，启用误读计算。
        enable_miscue=True,
    )

    # Creates a speech recognizer, also specify the speech language
    recognizer = speechsdk.SpeechRecognizer(speech_config=config, language=language)

    pronunciation_config.reference_text = reference_text
    pronunciation_config.apply_to(recognizer)

    # Starts recognizing.
    # print('Read out "{}" for pronunciation assessment ...'.format(reference_text))

    # Note: Since recognize_once() returns only a single utterance, it is suitable only for single
    # shot evaluation.
    # For long-running multi-utterance pronunciation evaluation, use start_continuous_recognition() instead.
    result = recognizer.recognize_once_async().get()

    return recognizer_normalizated(reference_text, result, language)


def pronunciation_assessment_continuous_from_file(
    audio_filename, reference_text, language, speech_key, service_region
):
    """Performs continuous pronunciation assessment asynchronously with input from an audio file.
    See more information at https://aka.ms/csspeech/pa"""

    import difflib
    import json, time, string

    # Creates an instance of a speech config with specified subscription key and service region.
    # Replace with your own subscription key and service region (e.g., "westus").
    # Note: The sample is for en-US language.
    speech_config = speechsdk.SpeechConfig(
        subscription=speech_key, region=service_region
    )
    audio_config = speechsdk.audio.AudioConfig(filename=audio_filename)

    # reference_text = "What's the weather like?"
    # create pronunciation assessment config, set grading system, granularity and if enable miscue based on your requirement.
    enable_miscue = True
    json_config = (
        "{"
        + f'"ReferenceText": "{reference_text}",\
          "GradingSystem": "HundredMark", \
          "Granularity": "Phoneme", \
          "EnableMiscue": "{enable_miscue}", \
          "ScenarioId": ""'
        + "}"
    )
    pronunciation_config = speechsdk.PronunciationAssessmentConfig(
        json_string=json_config
    )

    # Creates a speech recognizer using a file as audio input.
    # language = "en-US"
    speech_recognizer = speechsdk.SpeechRecognizer(
        speech_config=speech_config, language=language, audio_config=audio_config
    )
    # apply pronunciation assessment config to speech recognizer
    pronunciation_config.apply_to(speech_recognizer)

    done = False
    recognized_words = []
    fluency_scores = []
    durations = []

    def stop_cb(evt: speechsdk.SessionEventArgs):
        """callback that signals to stop continuous recognition upon receiving an event `evt`"""
        print("CLOSING on {}".format(evt))
        nonlocal done
        done = True

    def recognized(evt: speechsdk.SpeechRecognitionEventArgs):
        print("pronunciation assessment for: {}".format(evt.result.text))
        pronunciation_result = speechsdk.PronunciationAssessmentResult(evt.result)
        print(
            "    Accuracy score: {}, pronunciation score: {}, completeness score : {}, fluency score: {}".format(
                pronunciation_result.accuracy_score,
                pronunciation_result.pronunciation_score,
                pronunciation_result.completeness_score,
                pronunciation_result.fluency_score,
            )
        )
        nonlocal recognized_words, fluency_scores, durations
        recognized_words += pronunciation_result.words
        fluency_scores.append(pronunciation_result.fluency_score)
        json_result = evt.result.properties.get(
            speechsdk.PropertyId.SpeechServiceResponse_JsonResult
        )
        jo = json.loads(json_result)
        nb = jo["NBest"][0]
        durations.append(sum([int(w["Duration"]) for w in nb["Words"]]))

    # Connect callbacks to the events fired by the speech recognizer
    speech_recognizer.recognized.connect(recognized)
    speech_recognizer.session_started.connect(
        lambda evt: print("SESSION STARTED: {}".format(evt))
    )
    speech_recognizer.session_stopped.connect(
        lambda evt: print("SESSION STOPPED {}".format(evt))
    )
    speech_recognizer.canceled.connect(lambda evt: print("CANCELED {}".format(evt)))
    # stop continuous recognition on either session stopped or canceled events
    speech_recognizer.session_stopped.connect(stop_cb)
    speech_recognizer.canceled.connect(stop_cb)

    # Start continuous pronunciation assessment
    speech_recognizer.start_continuous_recognition()
    while not done:
        time.sleep(0.5)

    speech_recognizer.stop_continuous_recognition()

    # we need to convert the reference text to lower case, and split to words, then remove the punctuations.
    if language == "zh-CN":
        # Use jieba package to split words for Chinese
        import jieba
        import zhon.hanzi

        jieba.suggest_freq([x.word for x in recognized_words], True)
        reference_words = [
            w for w in jieba.cut(reference_text) if w not in zhon.hanzi.punctuation
        ]
    else:
        reference_words = [
            w.strip(string.punctuation) for w in reference_text.lower().split()
        ]

    # For continuous pronunciation assessment mode, the service won't return the words with `Insertion` or `Omission`
    # even if miscue is enabled.
    # We need to compare with the reference text after received all recognized words to get these error words.
    if enable_miscue:
        normed_words = [x.word.lower() for x in recognized_words]
        diff = difflib.SequenceMatcher(None, reference_words, normed_words)
        final_words = []
        for tag, i1, i2, j1, j2 in diff.get_opcodes():
            print(
                "{:7}   a[{}:{}] --> b[{}:{}] {!r:>8} --> {!r}".format(
                    tag, i1, i2, j1, j2, reference_words[i1:i2], normed_words[j1:j2]
                )
            )
            if tag in ["insert", "replace"]:
                for word in recognized_words[j1:j2]:
                    if word.error_type == "None":
                        word._error_type = "Insertion"
                    final_words.append(word)
            if tag in ["delete", "replace"]:
                for word_text in reference_words[i1:i2]:
                    word = speechsdk.PronunciationAssessmentWordResult(
                        {
                            "Word": word_text,
                            "PronunciationAssessment": {
                                "ErrorType": "Omission",
                            },
                        }
                    )
                    final_words.append(word)
            if tag == "equal":
                final_words += recognized_words[j1:j2]
    else:
        final_words = recognized_words

    # We can calculate whole accuracy by averaging
    final_accuracy_scores = []
    for word in final_words:
        if word.error_type == "Insertion":
            continue
        else:
            final_accuracy_scores.append(word.accuracy_score)

    accuracy_score = (
        sum(final_accuracy_scores) / len(final_accuracy_scores)
        if final_accuracy_scores
        else 0.0
    )
    # Re-calculate fluency score
    fluency_score = sum([x * y for (x, y) in zip(fluency_scores, durations)]) / sum(
        durations
    )
    # Calculate whole completeness score
    completeness_score = (
        len([w for w in recognized_words if w.error_type == "None"])
        / len(reference_words)
        * 100
    )
    completeness_score = completeness_score if completeness_score <= 100 else 100

    print(
        "    Paragraph accuracy score: {}, completeness score: {}, fluency score: {}".format(
            accuracy_score, completeness_score, fluency_score
        )
    )

    for idx, word in enumerate(final_words):
        print(
            "    {}: word: {}\taccuracy score: {}\terror type: {};".format(
                idx + 1, word.word, word.accuracy_score, word.error_type
            )
        )

    return {
        "scores": {
            "accuracy": accuracy_score,
            "completeness": completeness_score,
            "fluency": fluency_score,
        },
        "final_words": final_words,
    }
