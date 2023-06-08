import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import os
import gc

from run_telegram import open_data
from miniapps.languages import add_ocr

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
        st.error('Username/password is incorrect')
    elif st.session_state["authentication_status"] == None:
        pass

def start(authenticator):
    authenticator.logout('Logout', 'sidebar')
    user_data = open_data(st.session_state["username"])

    with open('idiom.yaml') as file:
        idio = yaml.load(file, Loader=SafeLoader)
    idi = user_data['idiom']

    st.header(idio['Image to text (OCR)'][idi])

    uploaded_files = st.file_uploader(idio['Select images to process'][idi], accept_multiple_files=True)
    images_path = 'miniapps/languages/images/'
    if uploaded_files is not None:
        for file in uploaded_files:
            with open(os.path.join(images_path, file.name), "wb") as f:
                f.write(file.getbuffer())

    add_lang_hw = st.button(idio['Read images'][idi])

    if add_lang_hw:
        info_placeholder = st.empty()
        info_placeholder.info(idio['Running...'][idi])

        text = add_ocr(images_path)
        st.write(text)

        folder_path = 'miniapps/languages/images'
        for file_name in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file_name)
            if os.path.isfile(file_path):
                os.remove(file_path)

        gc.collect()
        info_placeholder.info(idio['Finished!'][idi])

if __name__ == '__main__':
    st.set_page_config(
        page_title="Image to Text",
        page_icon="🅰",
    )

    main()