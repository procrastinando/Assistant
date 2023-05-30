import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import os
import pandas as pd
import shutil

from run_telegram import open_data, update_config
from miniapps.voice2text import generate_srt_files

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
        for file in uploaded_files:
            with open(file_dir + file.name, "wb") as f:
                f.write(file.getbuffer())

        whisper_size = st.selectbox(idio['Whisper size (the larger, the slower)'][idi], ['whisper-tiny', 'whisper-base', 'openai'])

        if whisper_size == 'openai':
            st.write('Comming soon')
        else:
            beam_size = st.number_input(idio['Select beam size (in seconds) zero means no beam'][idi], min_value=0, value=5)
            lang_list = ['en', 'es', 'ru']
            languages = st.multiselect(idio['Select language to translate, no selection, no translation'][idi], lang_list)

            if st.button(idio['Start'][idi]):
                file_path = file_dir + os.listdir(file_dir)[0]
                original_srt, translated_srts = generate_srt_files(whisper_size.split("-")[1], file_path, languages, beam_size)

                files = os.listdir(file_dir)
                for file in files:
                    os.remove(os.path.join(path, file))

                with open('original.srt', 'w') as f:
                    f.write(original_srt)
                for i in range(len(translated_srts)):
                    with open(f'{lang_list[i]}.srt', 'w') as f:
                        f.write(translated_srts[i])


if __name__ == '__main__':
    main()