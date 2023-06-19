import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

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

    st.header(idio['Text to voice'][idi])

    v2t_model = st.selectbox(idio['Text to voice model'][idi], [])

    if st.button(idio['Generate voice'][idi]):
        if user_data['miniapps']['read-speak']['t2v-model'] == 'azure':
            speech_config = speechsdk.SpeechConfig(subscription=user_data['azure']['token'], region=user_data['azure']['region'])
            audio_config = speechsdk.AudioConfig(filename="miniapps/languages/t2v.mp3")
            synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
            result = synthesizer.speak_text_async(text).get()
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                print("Speech synthesized to speaker for text [{}]".format(text))
                subprocess.run(["ffmpeg", "-loglevel", "quiet", "-i", "miniapps/languages/t2v.mp3", "-filter:a", f"atempo={user_data['miniapps']['read-speak']['voice-speed']}", "-vn", "miniapps/languages/t2v_.mp3", "-y"])
                audio_file = 'miniapps/languages/t2v_.mp3'

        elif user_data['miniapps']['read-speak']['t2v-model'] == 'google':
            try:
                tts = gTTS(text, lang=lang)
                tts.save('miniapps/languages/t2v.mp3')
                subprocess.run(["ffmpeg", "-loglevel", "quiet", "-i", "miniapps/languages/t2v.mp3", "-filter:a", f"atempo={user_data['miniapps']['read-speak']['voice-speed']}", "-vn", "miniapps/languages/t2v_.mp3", "-y"])
                audio_file = 'miniapps/languages/t2v_.mp3'
            except:
                st.error("Error")

        ###### Not finished yet....


if __name__ == '__main__':
    st.set_page_config(
        page_title="Voice to text",
        page_icon="👄",
    )

    main()