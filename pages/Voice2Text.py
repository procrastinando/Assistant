# import sys
# sys.path.insert(0, '/translator/lib/python3.9/site-packages')
# import argostranslate.package
# import argostranslate.translate
# sys.path.remove('/translator/lib/python3.9/site-packages')

import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import os
import pandas as pd
import shutil
import torch
import gc
import time
from faster_whisper import WhisperModel

from run_telegram import open_data, update_config, add_to_data
from miniapps.voice2text import generate_srt_files, generate_translation


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
            if not media_file.endswith(".srt"):
                os.remove(file_dir + media_file)

        with open(file_dir + uploaded_files.name, "wb") as f:
            f.write(uploaded_files.getvalue())

        whisper_size = st.selectbox(idio['Whisper size (the larger, the slower)'][idi], ['whisper-tiny', 'whisper-base', 'openai'])

        if whisper_size == 'openai': 
            st.write('Comming soon')
        else:
            lang_list = ['ar', 'az', 'ca', 'zh-CN', 'cs', 'da', 'nl', 'en', 'eo', 'fi', 'fr', 'de', 'el', 'he', 'hi', 'hu', 'id', 'ga', 'it', 'ja', 'ko', 'fa', 'pl', 'pt', 'ru', 'sk', 'es', 'sv', 'tr', 'uk']
            languages = st.multiselect(idio['Select language to translate, no selection, no translation'][idi], lang_list)

            if languages:
                translator_engine = st.selectbox(idio['Select translator engine'][idi], ['Google translator', 'ChatGPT translator'])
            else:
                translator_engine = None

            check_srt = st.checkbox(idio['Generate SRT subtitles file'][idi])
            if check_srt:
                beam_size = st.number_input(idio['Select beam size (in seconds) zero means no beam'][idi], min_value=0, value=5)

            if st.button(idio['Start'][idi]):
                start_time = time.time()

                for media_file in files:
                    if media_file.endswith(".srt"):
                        os.remove(file_dir + media_file)

                if check_srt:
                    info_placeholder = st.empty()
                    info_placeholder.info(idio['Transcribing'][idi]) 
                    
                    file_path = file_dir + os.listdir(file_dir)[0]
                    original_srt, translated_srts = generate_srt_files(whisper_size.split("-")[1], file_path, translator_engine, languages, beam_size, user_data, idio, idi)

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
                    info_placeholder.info(idio['Transcribing'][idi])
                    
                    file_path = file_dir + os.listdir(file_dir)[0]

                    original, translated = generate_translation(whisper_size, file_path, translator_engine, languages, user_data, idio, idi)

                    st.divider()
                    for o in original:
                        st.write(o)

                    for t in translated:
                        st.divider()
                        for tt in t:
                            st.write(tt)
                    
                    info_placeholder.info(idio['Finished!'][idi])

                add_to_data(st.session_state["username"], '/voice2text', start_time)
                gc.collect()

    if os.listdir('miniapps/voice2text/' + st.session_state["username"] + '/'):
        files = os.listdir('miniapps/voice2text/' + st.session_state["username"] + '/')
        for subtitle in files:
            if subtitle.split(".")[1] == 'srt':
                with open('miniapps/voice2text/' + st.session_state["username"] + '/' + subtitle, 'rb') as f:
                    file_data = f.read()
                st.download_button(label='Download '+subtitle, data=file_data, file_name=subtitle, mime='application/x-subrip')

if __name__ == '__main__':
    st.set_page_config(
        page_title="Voice to text",
        page_icon="🎙",
    )

    main()
