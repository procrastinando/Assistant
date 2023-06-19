import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import os
import gc
import time

from run_telegram import open_data, add_to_data
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

    # List of languages
    language_dict = {
        "Abaza": "abq",
        "Adyghe": "ady",
        "Afrikaans": "af",
        "Angika": "ang",
        "Arabic": "ar",
        "Assamese": "as",
        "Avar": "ava",
        "Azerbaijani": "az",
        "Belarusian": "be",
        "Bulgarian": "bg",
        "Bihari": "bh",
        "Bhojpuri": "bho",
        "Bengali": "bn",
        "Bosnian": "bs",
        "Simplified Chinese": "ch_sim",
        "Traditional Chinese": "ch_tra",
        "Chechen": "che",
        "Czech": "cs",
        "Welsh": "cy",
        "Danish": "da",
        "Dargwa": "dar",
        "German": "de",
        "English": "en",
        "Spanish": "es",
        "Estonian": "et",
        "Persian (Farsi)": "fa",
        "French": "fr",
        "Irish": "ga",
        "Goan Konkani": "gom",
        "Hindi": "hi",
        "Croatian": "hr",
        "Hungarian": "hu",
        "Indonesian": "id",
        "Ingush": "inh",
        "Icelandic": "is",
        "Italian": "it",
        "Japanese": "ja",
        "Kabardian": "kbd",
        "Kannada": "kn",
        "Korean": "ko",
        "Kurdish": "ku",
        "Latin": "la",
        "Lak": "lbe",
        "Lezghian": "lez",
        "Lithuanian": "lt",
        "Latvian": "lv",
        "Magahi": "mah",
        "Maithili": "mai",
        "Maori": "mi",
        "Mongolian": "mn",
        "Marathi": "mr",
        "Malay": "ms",
        "Maltese": "mt",
        "Nepali": "ne",
        "Newari": "new",
        "Dutch": "nl",
        "Norwegian": "no",
        "Occitan": "oc",
        "Pali": "pi",
        "Polish": "pl",
        "Portuguese": "pt",
        "Romanian": "ro",
        "Russian": "ru",
        "Serbian (cyrillic)": "rs_cyrillic",
        "Serbian (latin)": "rs_latin",
        "Nagpuri": "sck",
        "Slovak": "sk",
        "Slovenian": "sl",
        "Albanian": "sq",
        "Swedish": "sv",
        "Swahili": "sw",
        "Tamil": "ta",
        "Tabassaran": "tab",
        "Telugu": "te",
        "Thai": "th",
        "Tajik": "tjk",
        "Tagalog": "tl",
        "Turkish": "tr",
        "Uyghur": "ug",
        "Ukrainian": "uk",
        "Urdu": "ur",
        "Uzbek": "uz",
        "Vietnamese": "vi"
    }
    languages = [
        "Abaza", "Adyghe", "Afrikaans", "Angika", "Arabic", "Assamese", "Avar", "Azerbaijani", "Belarusian", 
        "Bulgarian", "Bihari", "Bhojpuri", "Bengali", "Bosnian", "Simplified Chinese", "Traditional Chinese", 
        "Chechen", "Czech", "Welsh", "Danish", "Dargwa", "German", "English", "Spanish", "Estonian", "Persian (Farsi)", 
        "French", "Irish", "Goan Konkani", "Hindi", "Croatian", "Hungarian", "Indonesian", "Ingush", "Icelandic", 
        "Italian", "Japanese", "Kabardian", "Kannada", "Korean", "Kurdish", "Latin", "Lak", "Lezghian", "Lithuanian", 
        "Latvian", "Magahi", "Maithili", "Maori", "Mongolian", "Marathi", "Malay", "Maltese", "Nepali", "Newari", 
        "Dutch", "Norwegian", "Occitan", "Pali", "Polish", "Portuguese", "Romanian", "Russian", "Serbian (cyrillic)", 
        "Serbian (latin)", "Nagpuri", "Slovak", "Slovenian", "Albanian", "Swedish", "Swahili", "Tamil", "Tabassaran", 
        "Telugu", "Thai", "Tajik", "Tagalog", "Turkish", "Uyghur", "Ukrainian", "Urdu", "Uzbek", "Vietnamese"
    ]

    recog_lang = st.multiselect(idio['Select languages to recognize'][idi], languages, user_data['miniapps']['image2text'])
    if st.button(idio['Save'][idi]):
        user_data['miniapps']['image2text'] = recog_lang
        with open('users/'+st.session_state["username"]+'.yaml', 'w') as file:
            yaml.dump(user_data, file)

    uploaded_files = st.file_uploader(idio['Select images to process'][idi], accept_multiple_files=True)
    images_path = 'miniapps/languages/images/'
    if uploaded_files is not None:
        for file in uploaded_files:
            with open(os.path.join(images_path, file.name), "wb") as f:
                f.write(file.getbuffer())

    add_lang_hw = st.button(idio['Read images'][idi])
 
    if add_lang_hw:
        start_time = time.time()
        info_placeholder = st.empty()
        info_placeholder.info(idio['Running...'][idi])

        text = add_ocr(images_path)
        st.write(text)

        folder_path = 'miniapps/languages/images'
        for file_name in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file_name)
            if os.path.isfile(file_path):
                os.remove(file_path)

        info_placeholder.info(idio['Finished!'][idi])
        add_to_data(st.session_state["username"], '/image2text', start_time)
        gc.collect()

if __name__ == '__main__':
    st.set_page_config(
        page_title="Image to Text",
        page_icon="🅰",
    )

    main()