import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

from run_telegram import open_data, update_config

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

    with open('config.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)

    user_data = open_data(st.session_state["username"])

    with open('idiom.yaml') as file:
        idio = yaml.load(file, Loader=SafeLoader)
    idi = user_data['idiom']

    lang_list = ['ar', 'az', 'ca', 'zh-CN', 'cs', 'da', 'nl', 'en', 'eo', 'fi', 'fr', 'de', 'el', 'he', 'hi', 'hu', 'id', 'ga', 'it', 'ja', 'ko', 'fa', 'pl', 'pt', 'ru', 'sk', 'es', 'sv', 'tr', 'uk']
    lang_names = ['Arabic','Azerbaijani','Catalan','Chinese (Simplified)','Czech','Danish','Dutch','English','Esperanto','Finnish','French','German','Greek','Hebrew','Hindi','Hungarian','Indonesian','Irish','Italian','Japanese','Korean','Persian','Polish','Portuguese','Russian','Slovak','Spanish','Swedish','Turkish','Ukrainian']
    lang_dict = dict(zip(lang_names, lang_list))

    st.header('Walkie Talkie')

    # Settings
    st.subheader(f"1. {idio['Language and models settings'][idi]}")
    t2v_model = st.selectbox(f"{idio['Text to voice model'][idi]}:", ['Google TTS', 'Azure'])
    Translator_engine = st.selectbox(f"{idio['Text to voice model'][idi]}:", ['Google translator', 'ChatGPT translator'])
    v2t_model = st.selectbox(f"{idio['Text to voice model'][idi]}:", ['whisper-tiny', 'whisper-base', 'openai'])

    if st.button(idio['Save'][idi]):
        user_data['miniapps']['walkie_talkie']['t2v-model'] = t2v_model
        user_data['miniapps']['walkie_talkie']['translator_engine'] = Translator_engine
        user_data['miniapps']['walkie_talkie']['whisper-size'] = v2t_model
        update_config(user_data, 'users/'+st.session_state["username"]+'.yaml')

    # Add new contact
    st.divider()
    st.subheader(f"2. {idio['Language and models settings'][idi]}")
    new_contact = st.text_input(idio['Add new contact, insert ID'][idi])

    if new_contact in list(config['credentials']['usernames'].keys()):
        language = st.selectbox(idio['Select language to translate your voice messages to'][idi], lang_names)
        if st.button(idio['Add contact'][idi]):
            user_data['miniapps']['walkie_talkie']['contacts'][new_contact] = language
    else:
        st.write(idio['This user has not registered yet, ask her/him to register'][idi])

    # Edit or delete contact
    st.divider()
    st.subheader(f"3. {idio['Edit or delete contact'][idi]}")
    if user_data['miniapps']['walkie_talkie']['contacts'] != {}:
        contact_id = st.selectbox(f"{idio['Contact'][idi]}:", list(user_data['miniapps']['walkie_talkie']['contacts'].keys()))
        contact_lang = st.selectbox(idio['Contact translation language'][idi], lang_names, index=lang_list.index(user_data['miniapps']['walkie_talkie']['contacts'][contact_id]))

        col1, col2 = st.columns(2)
        with col1:
            if st.button(idio['Remove contact'][idi]):
                user_data['miniapps']['walkie_talkie']['contacts'].pop(contact_id)
                update_config(user_data, 'users/'+st.session_state["username"]+'.yaml')
        with col2:
            if st.button(idio['Update contact'][idi]):
                user_data['miniapps']['walkie_talkie']['contacts'][contact_id] = lang_dict[contact_lang]
                update_config(user_data, 'users/'+st.session_state["username"]+'.yaml')
    else:
        st.write(idio['You do not have contacts'][idi])


    st.divider()
    
if __name__ == '__main__':
    # st.set_page_config(
    #     page_title="Image to Text",
    #     page_icon="📲",
    # )

    main()