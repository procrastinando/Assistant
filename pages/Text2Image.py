import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import random
import gc
import time

from miniapps.text2image import Lexica
from run_telegram import open_data, add_to_data

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

    st.header(idio['AI Image Generator'][idi])

    prompt = st.text_input(idio['Insert prompt in english'][idi])
    num_img = st.slider(idio['Select number or images'][idi], 1, 5, 3)

    lex = Lexica(query=prompt).images()
    image_urls = random.sample(lex, num_img)
    
    try:
        if st.button(idio['Generate images'][idi]):
            start_time = time.time()
            cols = st.columns(num_img)
            for i in range(num_img):
                with cols[i]:
                    st.image(image_urls[i])

            add_to_data(st.session_state["username"], '/text2image', start_time)
            gc.collect()

    except:
        st.error(idio['Error generating image'][idi])    

if __name__ == '__main__':
    st.set_page_config(
        page_title="Text to image",
        page_icon="📷",
    )

    main()