from dotenv import load_dotenv
from datetime import datetime
import winsound
import os
import time
import json

# Import namespaces
try:
    import azure.cognitiveservices.speech as speechsdk
except ImportError:
    print("""
    Importing the Speech SDK for Python failed.
    Refer to
    https://docs.microsoft.com/azure/cognitive-services/speech-service/quickstart-python for
    installation instructions.
    """)
    import sys
    sys.exit(1)

def main():
    try:
        global speech_config
        global translation_config

        # Get Configuration Settings
        load_dotenv()
        cog_key = os.getenv('COG_SERVICE_KEY')
        cog_region = os.getenv('COG_SERVICE_REGION')

        # Creates a SpeechConfig from your speech key and region
        speech_config = speechsdk.SpeechConfig(cog_key, cog_region)

        # Configure translation
        translation_config = speechsdk.translation.SpeechTranslationConfig(cog_key, cog_region)
        translation_config.speech_recognition_language = 'en-US'
        translation_config.add_target_language('fr')
        translation_config.add_target_language('es')
        translation_config.add_target_language('hi')
        translation_config.add_target_language('nb')
        translation_config.add_target_language('en')
        print('Ready to translate from',translation_config.speech_recognition_language)    

        
        # Get user input
        targetLanguage = ''
        targetLanguage = input('\nEnter a target language\n fr = French\n es = Spanish\n hi = Hindi\n nb = Norwegian\n Enter anything else to stop\n').lower()    
        while targetLanguage != 'quit':
            #targetLanguage = input('\nEnter a target language\n fr = French\n es = Spanish\n hi = Hindi\n Enter anything else to stop\n').lower()
            if targetLanguage in translation_config.target_languages:
                trnaslated_text = Translate(targetLanguage)
                print("here =============>>")
                print(str(trnaslated_text[1]).lower())
                if (str(trnaslated_text[1]).lower() != 'quit.'):
                    Speak(targetLanguage, trnaslated_text[0])
                else:
                    Speak("en", "finally! it's over!!!")
                    exit()

            else:
                targetLanguage = 'quit'
        
        #Translate(targetLanguage)

    except Exception as ex:
        print(ex)

def Translate(targetLanguage):
    translation = ''
    freq=1000
    dur=500

     # Translate speech
    audio_config = speechsdk.AudioConfig(use_default_microphone=True)
    translator = speechsdk.translation.TranslationRecognizer(translation_config, audio_config = audio_config)
    print("Speak now...")
    winsound.Beep(freq,dur)
    
    result = translator.recognize_once_async().get()
    print('Translating "{}"'.format(result.text))
    translation = result.translations[targetLanguage]
    print(translation)
    return (translation, result.text)


def Speak(targetLanguage, translation):

     # Synthesize translation
    voices = {
            "fr": "fr-FR-HenriNeural",
            "es": "es-ES-ElviraNeural",
            "hi": "hi-IN-MadhurNeural",
            "nb" : "nb-NO-FinnNeural",
            "en" : "en-IN-NeerjaNeural",
    }
    speech_config.speech_synthesis_voice_name = voices.get(targetLanguage)
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config)
    speak = speech_synthesizer.speak_text_async(translation).get()
    if speak.reason != speechsdk.ResultReason.SynthesizingAudioCompleted:
        print(speak.reason)


def speech_language_detection_once_from_mic():
    """performs one-shot speech language detection from the default microphone"""
    # <SpeechLanguageDetectionWithMicrophone>
    # Creates an AutoDetectSourceLanguageConfig, which defines a number of possible spoken languages
    auto_detect_source_language_config = speechsdk.languageconfig.AutoDetectSourceLanguageConfig(languages=["de-DE", "en-US"])

    audio_config = speechsdk.AudioConfig

    # Creates a source language recognizer using microphone as audio input.
    # The default language is "en-us".
    speech_language_detection = speechsdk.SourceLanguageRecognizer(
        speech_config=speech_config, auto_detect_source_language_config=auto_detect_source_language_config)

    print("Say something in English or German...")

    # Starts speech language detection, and returns after a single utterance is recognized. The end of a
    # single utterance is determined by listening for silence at the end or until a maximum of 15
    # seconds of audio is processed. It returns the recognition text as result.
    # Note: Since recognize_once() returns only a single utterance, it is suitable only for single
    # shot recognition like command or query.
    # For long-running multi-utterance recognition, use start_continuous_recognition() instead.
    result = speech_language_detection.recognize_once()

    # Check the result
    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        detected_src_lang = result.properties[
            speechsdk.PropertyId.SpeechServiceConnection_AutoDetectSourceLanguageResult]
        print("Detected Language: {}".format(detected_src_lang))
    elif result.reason == speechsdk.ResultReason.NoMatch:
        print("No speech could be recognized")
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        print("Speech Recognition canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print("Error details: {}".format(cancellation_details.error_details))
    # </SpeechLanguageDetectionWithMicrophone>



if __name__ == "__main__":
    main()