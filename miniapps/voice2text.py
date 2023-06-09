# import sys
# sys.path.insert(0, '/translator/lib/python3.9/site-packages')
# import argostranslate.package
# import argostranslate.translate
# sys.path.remove('/translator/lib/python3.9/site-packages')

import streamlit as st
from faster_whisper import WhisperModel
from deep_translator import GoogleTranslator
import srt
import torch
import gc

def format_timestamp(timestamp):
    hours = int(timestamp // 3600)
    minutes = int((timestamp % 3600) // 60)
    seconds = int(timestamp % 60)
    milliseconds = int((timestamp % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

# def argos_translate(text, from_code, to_code):
#     # Check if package is already installed
#     installed_packages = argostranslate.package.get_installed_packages()
#     installed_package = next(
#         (x for x in installed_packages if x.from_code == from_code and x.to_code == to_code), None
#     )
    
#     if not installed_package:
#         # Update package index and get available packages
#         argostranslate.package.update_package_index()
#         available_packages = argostranslate.package.get_available_packages()
        
#         # Find package to install
#         package_to_install = next(
#             (x for x in available_packages if x.from_code == from_code and x.to_code == to_code), None
#         )
        
#         # Check if package is available
#         if not package_to_install:
#             return "#There is no language package"
        
#         # Install package
#         else:
#             argostranslate.package.install_from_path(package_to_install.download())
#             return True

def generate_srt_files(whisper_size, file_path, translator_engine, languages, beam_size, user_data, idio, idi):
    # Transcribe audio to text
    model_size = whisper_size
    model = WhisperModel(model_size, device="cpu", compute_type="int8")
    
    if beam_size == 0:
        segments, info = model.transcribe(file_path)
    else:
        segments, info = model.transcribe(file_path, beam_size=beam_size)

    # Generate original .srt file
    original_subs = []
    for segment in segments:
        start = srt.srt_timestamp_to_timedelta(format_timestamp(segment.start))
        end = srt.srt_timestamp_to_timedelta(format_timestamp(segment.end))
        sub = srt.Subtitle(index=segment.id,
                           start=start,
                           end=end,
                           content=segment.text)
        original_subs.append(sub)
    original_srt = srt.compose(original_subs)

    # Translate text to specified
    translated_srts = []
    for language in languages:
        translated_subs = []

        try:
            for sub in original_subs:

                if translator_engine == 'ChatGPT translator':
                    try:
                        translated_text = ChatGptTranslator(api_key=user_data['credentials']['openai'], target=language).translate(text=sub.content)
                    except:
                        st.error(idio['Chatgpt API or network error'][idi])

                # elif translator_engine == 'Argostranslate':
                #     try:
                #         result = argos_translate(sub.content, info.language, language.split('-')[0])
                #         translated_text = argostranslate.translate.translate(sub.content, info.language, language.split('-')[0])
                #     except:
                #         st.error("Argostranslate cannot translate to this language")

                elif translator_engine == 'Google translator':
                    try:
                        translated_text = GoogleTranslator(source='auto', target=language).translate(sub.content)
                    except:
                        st.error(idio['Google translate network error'][idi])
                
                translated_sub = srt.Subtitle(index=sub.index,
                                            start=sub.start,
                                            end=sub.end,
                                            content=translated_text)
                translated_subs.append(translated_sub)

            # Generate .srt file for each language
            translated_srt = srt.compose(translated_subs)
            translated_srts.append(translated_srt)

        except:
            pass

        gc.collect()

    return original_srt, translated_srts

def generate_translation(whisper_size, file_path, translator_engine, languages, user_data, idio, idi):
    model_size = whisper_size.split("-")[1]
    if torch.cuda.is_available():
        model = WhisperModel(model_size, device="cuda", compute_type="float16")
    else:
        model = WhisperModel(model_size, device="cpu", compute_type="int8")
    segments, info = model.transcribe(file_path)

    original = []
    for segment in segments:
        original.append(segment.text)

    translated = []
    for l in range(len(languages)):
        if translator_engine == 'Google translator':
            try:
                translated.append([])
                for text in original:
                    translated_text = GoogleTranslator(source='auto', target=languages[l]).translate(text)
                    translated[l].append(translated_text)
            except:
                st.error(idio['Google translate network error'][idi])

        elif translator_engine == 'ChatGPT translator':
            try:
                translated.append([])
                for text in original:
                    translated_text = ChatGptTranslator(api_key=user_data['credentials']['openai'], target=languages[l]).translate(text=text)
                    translated[l].append(translated_text)
            except:
                st.error(idio['Chatgpt API or network error'][idi])

        # elif translator_engine == 'Argostranslate':
        #     translated.append([])
        #     for text in original:
        #         result = argos_translate(text, info.language, languages[l])
        #         if result == "#There is no language package":
        #             st.error(idio['Argostranslate cannot translate to this language'][idi])
        #             break
        #         else:
        #             translated_text = argostranslate.translate.translate(text, info.language, languages[l])
        #             translated[l].append(translated_text)
        #             gc.collect()
    
    return original, translated

def generate_transcription(whisper_size, file_path):
    # Transcribe audio to text
    model_size = whisper_size

    if torch.cuda.is_available():
        model = WhisperModel(model_size, device="cuda", compute_type="float16")
    else:
        model = WhisperModel(model_size, device="cpu", compute_type="int8")

    segments, info = model.transcribe(file_path)

    text = ''
    for segment in segments:
        text = text + segment.text

    return text

def transcribe(whisper_size, file_path, beam_size):
    # Transcribe audio to text
    model_size = whisper_size
    model = WhisperModel(model_size, device="cpu", compute_type="int8")
    
    if beam_size == 0:
        segments, info = model.transcribe(file_path)
    else:
        segments, info = model.transcribe(file_path, beam_size=beam_size)
    
    text = ''
    for segment in segments:
        text = text + segmnent

    return text