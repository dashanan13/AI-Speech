import azure.cognitiveservices.speech as speechsdk
import time
import json

speech_key, service_region = "cda77e21d1ea443fa2fe0f83d66c51c1","westeurope"
weatherfilename="en-us_zh-cn.wav"


# set up translation parameters: source language and target languages
# Currently the v2 endpoint is required. In a future SDK release you won't need to set it. 
endpoint_string = "wss://{}.stt.speech.microsoft.com/speech/universal/v2".format(service_region)
translation_config = speechsdk.translation.SpeechTranslationConfig(
    subscription=speech_key,
    endpoint=endpoint_string,
    speech_recognition_language='en-US',
    target_languages=('de', 'fr'))
audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)

# Specify the AutoDetectSourceLanguageConfig, which defines the number of possible languages
auto_detect_source_language_config = speechsdk.languageconfig.AutoDetectSourceLanguageConfig(languages=["en-US", "hi-IN"])

# Creates a translation recognizer using and audio file as input.
recognizer = speechsdk.translation.TranslationRecognizer(
    translation_config=translation_config, 
    audio_config=audio_config,
    auto_detect_source_language_config=auto_detect_source_language_config)

# Starts translation, and returns after a single utterance is recognized. The end of a
# single utterance is determined by listening for silence at the end or until a maximum of 15
# seconds of audio is processed. The task returns the recognition text as result.
# Note: Since recognize_once() returns only a single utterance, it is suitable only for single
# shot recognition like command or query.
# For long-running multi-utterance recognition, use start_continuous_recognition() instead.
result = recognizer.recognize_once()

# Check the result
if result.reason == speechsdk.ResultReason.TranslatedSpeech:
    print("""Recognized: {}
    German translation: {}
    French translation: {}""".format(
        result.text, result.translations['de'], result.translations['fr']))
elif result.reason == speechsdk.ResultReason.RecognizedSpeech:
    print("Recognized: {}".format(result.text))
    detectedSrcLang = result.properties[speechsdk.PropertyId.SpeechServiceConnection_AutoDetectSourceLanguageResult]
    print("Detected Language: {}".format(detectedSrcLang))
elif result.reason == speechsdk.ResultReason.NoMatch:
    print("No speech could be recognized: {}".format(result.no_match_details))
elif result.reason == speechsdk.ResultReason.Canceled:
    print("Translation canceled: {}".format(result.cancellation_details.reason))
    if result.cancellation_details.reason == speechsdk.CancellationReason.Error:
        print("Error details: {}".format(result.cancellation_details.error_details))