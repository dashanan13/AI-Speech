import azure.cognitiveservices.speech as speechsdk
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
        global audio_config
        global auto_detect_source_language_config

        # Get Configuration Settings
        load_dotenv()
        cog_key = os.getenv('COG_SERVICE_KEY')
        cog_region = os.getenv('COG_SERVICE_REGION')
        
        
        # Creates a SpeechConfig from your speech key and region
        speech_config = speechsdk.SpeechConfig(cog_key, cog_region)

        # set up translation parameters: source language and target languages
        # Currently the v2 endpoint is required. In a future SDK release you won't need to set it. 
        endpoint_string = "wss://{}.stt.speech.microsoft.com/speech/universal/v2".format(cog_region)
        translation_config = speechsdk.translation.SpeechTranslationConfig(
            subscription=cog_key,
            endpoint=endpoint_string,
            speech_recognition_language='en-US',
            target_languages=('nb', 'fr'))
        audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)

        # Specify the AutoDetectSourceLanguageConfig, which defines the number of possible languages
        auto_detect_source_language_config = speechsdk.languageconfig.AutoDetectSourceLanguageConfig(languages=["en-US", "hi-IN"])
        
        # Get user input
        targetLanguage = ''
        targetLanguage = input('\nEnter a target language\n nb = Norwegian\n fr = French \n Enter anything else to stop\n').lower()    
        while targetLanguage != 'quit':
            #targetLanguage = input('\nEnter a target language\n fr = French\n es = Spanish\n hi = Hindi\n Enter anything else to stop\n').lower()
            if targetLanguage in translation_config.target_languages:

                trnaslated_text = RecognizeLang(targetLanguage)
                print(trnaslated_text[0].lower())
                print((str(trnaslated_text[0]).lower() != 'quit.'))
                print((str(trnaslated_text[0]).lower() != 'quit'))
                
                if ((str(trnaslated_text[0]).lower() != 'quit.')):
                    Speak(targetLanguage, trnaslated_text[1])
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

def RecognizeLang(targetLanguage):
    print('Recognizing...')
    freq=500
    dur=500

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
    # Translate speech
    print("Speak now...")
    winsound.Beep(freq,dur)

    result = recognizer.recognize_once()

    # Check the result
    if result.reason == speechsdk.ResultReason.TranslatedSpeech:
        print("""Recognized: {}
        Norwegian translation: {}
        French translation: {}""".format(
            result.text, result.translations['nb'], result.translations['fr']))
        if (targetLanguage == 'nb'):
            return([result.text, result.translations['nb']])
        else:
            return([result.text, result.translations['fr']])
    elif result.reason == speechsdk.ResultReason.RecognizedSpeech:
        print("Recognized: {}".format(result.text))
        detectedSrcLang = result.properties[speechsdk.PropertyId.SpeechServiceConnection_AutoDetectSourceLanguageResult]
        print("Detected Language: {}".format(detectedSrcLang))
        return(['quit.', 'quit.'])
    elif result.reason == speechsdk.ResultReason.NoMatch:
        print("No speech could be recognized: {}".format(result.no_match_details))
        return(['quit.', 'quit.'])
    elif result.reason == speechsdk.ResultReason.Canceled:
        print("Translation canceled: {}".format(result.cancellation_details.reason))
        if result.cancellation_details.reason == speechsdk.CancellationReason.Error:
            print("Error details: {}".format(result.cancellation_details.error_details))
        return(['quit.', 'quit.'])
    


if __name__ == "__main__":
    main()