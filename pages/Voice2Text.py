import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import os
import pandas as pd
import shutil
import torch
from faster_whisper import WhisperModel
from deep_translator import ChatGptTranslator

from run_telegram import open_data, update_config
from miniapps.voice2text import generate_srt_files, generate_transcription

def main():
    with open('config.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)

    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
        config['preauthorized']
    )
    authenticator.login('Login', 'main')

    if st.session_state["authentication_status"]:
        start(authenticator)
    elif st.session_state["authentication_status"] == False:
        st.error('User ID or password is incorrect')
    elif st.session_state["authentication_status"] == None:
        pass

def start(authenticator):
    authenticator.logout('Logout', 'sidebar')
    user_data = open_data(st.session_state["username"])

    with open('idiom.yaml') as file:
        idio = yaml.load(file, Loader=SafeLoader)
    idi = user_data['idiom']

    st.header(idio['Voice to Text'][idi])

    file_dir = 'miniapps/voice2text/' + st.session_state["username"] + '/'
    try:
        os.mkdir(file_dir)
    except:
        pass

    uploaded_files = st.file_uploader(idio['Select audio to process'][idi], accept_multiple_files=False)
    if uploaded_files is not None:
        files = os.listdir(file_dir)
        for media_file in files:
            os.remove(file_dir + media_file)

        with open(file_dir + uploaded_files.name, "wb") as f:
            f.write(uploaded_files.getvalue())

        whisper_size = st.selectbox(idio['Whisper size (the larger, the slower)'][idi], ['whisper-tiny', 'whisper-base', 'openai'])

        if whisper_size == 'openai': 
            st.write('Comming soon')
        else:
            lang_list = ['en', 'es', 'ru']
            languages = st.multiselect(idio['Select language to translate, no selection, no translation'][idi], lang_list)
            check_srt = st.checkbox(idio['Generate SRT subtitles file'][idi])
            if check_srt:
                beam_size = st.number_input(idio['Select beam size (in seconds) zero means no beam'][idi], min_value=0, value=5)

            if st.button(idio['Start'][idi]):
                if check_srt:
                    info_placeholder = st.empty()
                    info_placeholder.info(idio['Running...'][idi])
                    
                    file_path = file_dir + os.listdir(file_dir)[0]
                    original_srt, translated_srts = generate_srt_files(whisper_size.split("-")[1], file_path, languages, beam_size)

                    files = os.listdir(file_dir)
                    for media_file in files:
                        os.remove(file_dir + media_file)

                    with open(file_dir + 'original.srt', 'w') as f:
                        f.write(original_srt)

                    for i in range(len(translated_srts)):
                        with open(file_dir + f'{languages[i]}.srt', 'w') as f:
                            f.write(translated_srts[i])

                    info_placeholder.info(idio['Finished!'][idi])
                
                else:
                    info_placeholder = st.empty()
                    info_placeholder.info(idio['Running...'][idi])
                    
                    file_path = file_dir + os.listdir(file_dir)[0]
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
                        try:
                            translated.append([])
                            for text in original:
                                translated_text = ChatGptTranslator(api_key=user_data['credentials']['openai'], target=languages[l]).translate(text=text)
                                translated[l].append(translated_text)
                        except:
                            st.error(idio['Error using Openai API to translate the text'][idi])
                    
                    st.divider()
                    for o in original:
                        st.write(o)

                    for t in translated:
                        for tt in t:
                            st.divider()
                            st.write(tt)

    if os.listdir(file_dir):
        files = os.listdir(file_dir)
        for subtitle in files:
            if subtitle.split(".")[1] == 'srt':
                with open(file_dir + subtitle, 'rb') as f:
                    file_data = f.read()
                st.download_button(label='Download '+subtitle, data=file_data, file_name=subtitle, mime='application/x-subrip')

if __name__ == '__main__':
    st.set_page_config(
        page_title="Voice to text",
        page_icon="🎙",
    )

    main()