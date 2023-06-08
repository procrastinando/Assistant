import sys
sys.path.insert(0, '/translator/lib/python3.9/site-packages')
import argostranslate
sys.path.remove('/translator/lib/python3.9/site-packages')

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

import argostranslate.package
import argostranslate.translate

from run_telegram import open_data, update_config
from miniapps.voice2text import generate_srt_files, generate_translation


def argos_translate(text, from_code, to_code):
    # Check if package is already installed
    installed_packages = argostranslate.package.get_installed_packages()
    installed_package = next(
        (x for x in installed_packages if x.from_code == from_code and x.to_code == to_code), None
    )
    
    if not installed_package:
        # Update package index and get available packages
        argostranslate.package.update_package_index()
        available_packages = argostranslate.package.get_available_packages()
        
        # Find package to install
        package_to_install = next(
            (x for x in available_packages if x.from_code == from_code and x.to_code == to_code), None
        )
        
        # Check if package is available
        if not package_to_install:
            return "#There is no language package"
        
        # Install package
        argostranslate.package.install_from_path(package_to_install.download())
    
    # Translate text
    return argostranslate.translate.translate(text, from_code, to_code)

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
            lang_list = ['en', 'es', 'ru']
            languages = st.multiselect(idio['Select language to translate, no selection, no translation'][idi], lang_list)

            if languages:
                translator_engine = st.selectbox(idio['Select translator engine'][idi], ['Argostranslate', '', 'ChatGPT translator'])

            check_srt = st.checkbox(idio['Generate SRT subtitles file'][idi])
            if check_srt:
                beam_size = st.number_input(idio['Select beam size (in seconds) zero means no beam'][idi], min_value=0, value=5)

            if st.button(idio['Start'][idi]):
                for media_file in files:
                    if media_file.endswith(".srt"):
                        os.remove(file_dir + media_file)

                if check_srt:
                    info_placeholder = st.empty()
                    info_placeholder.info(idio['Transcribing'][idi]) 
                    
                    file_path = file_dir + os.listdir(file_dir)[0]
                    original_srt, translated_srts = generate_srt_files(whisper_size.split("-")[1], file_path, translator_engine, languages, beam_size, user_data)

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

                    original, translated = generate_translation(whisper_size, file_path, translator_engine, languages, user_data)

                    st.divider()
                    for o in original:
                        st.write(o)

                    for t in translated:
                        st.divider()
                        for tt in t:
                            st.write(tt)
                    
                    info_placeholder.info(idio['Finished!'][idi])

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
