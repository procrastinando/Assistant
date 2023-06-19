import os
import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

from miniapps.languages import clean_text
from run_telegram import open_data
from run_telegram import update_config

from run_telegram import send_message

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

    with open('config.yaml', 'r') as file:
        usernames = yaml.safe_load(file)['credentials']['usernames']

    with open('idiom.yaml') as file:
        idio = yaml.load(file, Loader=SafeLoader)
    idi = user_data['idiom']
    if idi not in list(idio['Add homework'].keys()):
        idi = 'en'

    st.header(idio['AI Teacher assistant'][idi])

    #if True:
    try:
        if user_data['childs'] != []:

            col1, col2 = st.columns([1, 1])
            with col1:
                i = st.selectbox(f"{idio['Child'][idi]}:", user_data['childs'])
                child_data = open_data(i)
            child_name = usernames[i]['name']
            st.subheader(f'✔️ {child_name}')

            # --- Languages settings
            st.header(idio['Language settings'][idi])
            t2v_models = ['google', 'azure']
            v2t_models = ['whisper', 'openai']
            whisper_sizes = ['tiny', 'base']

            voice_speed = child_data['miniapps']['read-speak']['voice-speed']
            voice_speed_n = float(st.text_input(idio['Voice speed'][idi], voice_speed))

            t2v_model = st.selectbox(idio['Text to voice model'][idi], t2v_models, index=t2v_models.index(child_data['miniapps']['read-speak']['t2v-model']))
            v2t_model = st.selectbox(idio['Voice to text model'][idi], v2t_models)
            if v2t_model == 'whisper':
                whisper_size = st.selectbox(idio['Whisper size (the larger, the slower)'][idi], whisper_sizes, index=whisper_sizes.index(child_data['miniapps']['read-speak']['whisper-size']))

                # speech_key, service_region = user_data['credentials']['azure']['token'], user_data['credentials']['azure']['region']
                # speech_config = SpeechConfig(subscription=speech_key, region=service_region)
                # audio_config = AudioOutputConfig(filename="t2v.mp3")
                # synthesizer = SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

            if st.button(idio['Save'][idi], key=2):
                child_data['miniapps']['read-speak']['voice-speed'] = voice_speed_n
                child_data['miniapps']['read-speak']['t2v-model'] = t2v_model
                child_data['miniapps']['read-speak']['v2t-model'] = v2t_model
                if v2t_model == 'whisper':
                    child_data['miniapps']['read-speak']['whisper-size'] = whisper_size
                update_config(child_data, 'users/'+i+'.yaml')

            # --- READ-SPEAKING
            st.divider()
            st.header(f"1. {idio['Read and speak'][idi]}")

            ex_rate_l = child_data['miniapps']['read-speak']['ex_rate']
            ex_rate_l_n = float(st.text_input(idio['Exchange rate'][idi], ex_rate_l, key=3))

            difficulty = child_data['miniapps']['read-speak']['difficulty']
            difficulty_n = float(st.text_input(idio['Difficulty'][idi], difficulty))

            target_score_l = child_data['miniapps']['read-speak']['target_score']
            target_score_l_n = float(st.text_input(idio['Target score'][idi], target_score_l, key=17))

            languages_save = st.button(idio['Save'][idi], key=4)
            if languages_save:
                child_data['miniapps']['read-speak']['ex_rate'] = ex_rate_l_n
                child_data['miniapps']['read-speak']['difficulty'] = difficulty_n
                child_data['miniapps']['read-speak']['target_score'] = target_score_l_n
                update_config(child_data, 'users/'+i+'.yaml')

            # --- List homeworks
            langs = [    'af: Afrikaans',     'ar: Arabic',     'bg: Bulgarian',     'bn: Bengali',     'bs: Bosnian',     'ca: Catalan',     'cs: Czech',     'da: Danish',     'de: German',     'el: Greek',     'en: English',     'es: Spanish',     'et: Estonian',     'fi: Finnish',     'fr: French',     'gu: Gujarati',     'hi: Hindi',     'hr: Croatian',     'hu: Hungarian',     'id: Indonesian',     'is: Icelandic',     'it: Italian',     'iw: Hebrew',     'ja: Japanese',     'jw: Javanese',     'km: Khmer',     'kn: Kannada',     'ko: Korean',     'la: Latin',     'lv: Latvian',     'ml: Malayalam',     'mr: Marathi',     'ms: Malay',     'my: Myanmar (Burmese)',     'ne: Nepali',     'nl: Dutch',     'no: Norwegian',     'pl: Polish',     'pt: Portuguese',     'ro: Romanian',     'ru: Russian',     'si: Sinhala',     'sk: Slovak',     'sq: Albanian',     'sr: Serbian',     'su: Sundanese',     'sv: Swedish',     'sw: Swahili',     'ta: Tamil',     'te: Telugu',     'th: Thai',     'tl: Filipino',     'tr: Turkish',     'uk: Ukrainian',     'ur: Urdu',     'vi: Vietnamese',     'zh-CN: Chinese (Simplified)',     'zh-TW: Chinese (Mandarin/Taiwan)',     'zh: Chinese (Mandarin)']
            st.subheader(f"1.1. {idio['Read and Speak homeworks'][idi]}")

            # --- Create new homework
            new_read_speak_hw_name = st.text_input(idio['Enter new homework name'][idi])

            if st.button(idio['Create homework'][idi]):
                child_data['miniapps']['read-speak']['homework_lang'][new_read_speak_hw_name] = {}
                child_data['miniapps']['read-speak']['homework_lang'][new_read_speak_hw_name]['lang'] = 'en'
                new_read_speak_hw = "This is an example. Write some sentences here."
                child_data['miniapps']['read-speak']['homework'][new_read_speak_hw_name] = {}

                for j in range(len(new_read_speak_hw)):
                    child_data['miniapps']['read-speak']['homework'][new_read_speak_hw_name][j] = {}
                    child_data['miniapps']['read-speak']['homework'][new_read_speak_hw_name][j]['score'] = 0.0
                    child_data['miniapps']['read-speak']['homework'][new_read_speak_hw_name][j]['text'] = new_read_speak_hw[j]

                coins = round(len(new_read_speak_hw) * child_data['miniapps']['read-speak']['target_score'] / child_data['miniapps']['read-speak']['ex_rate'], 2)
                st.write(f'Done! Expected coins: {coins}')
                update_config(child_data, 'users/'+i+'.yaml')

            # --- Show current homeworks
            read_speak_hws = list(child_data['miniapps']['read-speak']['homework'].keys())
            if read_speak_hws:
                read_speak_hw = st.selectbox(idio['Select a homework to update or delete'][idi], read_speak_hws, key=11)

                read_speak_hw_content = ''
                for n in child_data['miniapps']['read-speak']['homework'][read_speak_hw]:
                    read_speak_hw_content = read_speak_hw_content + child_data['miniapps']['read-speak']['homework'][read_speak_hw][n]['text'] + '.'

                read_speak_hw_concat = st.text_area(idio['Homework, separate sentences by dots'][idi], read_speak_hw_content)
                lang = st.selectbox(idio['Select language'][idi], langs, key=14, index=langs.index(idio['Language code'][user_data['idiom']]))

                col1, col2, col3 = st.columns(3)
                with col1:
                    button_del_hw = st.button(f"{idio['Delete homework'][idi]} ⚠️", key=5)
                with col2:
                    button_update_hw = st.button(idio['Update homework'][idi], key=13)

                if button_del_hw:
                    try:
                        child_data['miniapps']['read-speak']['homework'].pop(read_speak_hw)
                        child_data['miniapps']['read-speak']['homework_lang'].pop(read_speak_hw)
                        update_config(child_data, 'users/'+i+'.yaml')
                        st.write(f'Done!  {read_speak_hw} deleted')
                    except:
                        pass

                if button_update_hw:
                    child_data['miniapps']['read-speak']['homework_lang'][read_speak_hw] = {}
                    child_data['miniapps']['read-speak']['homework_lang'][read_speak_hw]['lang'] = lang.split(':')[0]
                    read_speak_hw_concat = read_speak_hw_concat.split('.')
                    child_data['miniapps']['read-speak']['homework'][read_speak_hw] = {}

                    for j in range(len(read_speak_hw_concat)):
                        child_data['miniapps']['read-speak']['homework'][read_speak_hw][j] = {}
                        child_data['miniapps']['read-speak']['homework'][read_speak_hw][j]['score'] = 0.0
                        child_data['miniapps']['read-speak']['homework'][read_speak_hw][j]['text'] = read_speak_hw_concat[j]

                    coins = round(len(read_speak_hw_concat) * child_data['miniapps']['read-speak']['target_score'] / child_data['miniapps']['read-speak']['ex_rate'], 2)
                    st.write(f'Done! Expected coins: {coins}')
                    update_config(child_data, 'users/'+i+'.yaml')

            else:
                st.write(idio['There are no homeworks to show'][idi])

            # --- LISTEN-WRITE
            st.divider()
            st.header(f"2. {idio['Listen and Write'][idi]}")

            use_chatgpt = st.checkbox(idio['Use ChatGPT to make a sentence'][idi], child_data['miniapps']['listen-write']['chatgpt'])
            if use_chatgpt:
                try:
                    child_data['miniapps']['listen-write']['chatgpt'] = True
                except:
                    st.error(f"{idio['Insert a valid OpenAI API here'][idi]}: https://assistant.ibarcena.net/")
                    child_data['miniapps']['listen-write']['chatgpt'] = False
            else:
                child_data['miniapps']['listen-write']['chatgpt'] = False

            ex_rate_lw = child_data['miniapps']['listen-write']['ex_rate']
            ex_rate_lw_n = float(st.text_input(idio['Exchange rate'][idi], ex_rate_lw, key=6))

            fault_penalty_lw = child_data['miniapps']['listen-write']['fault_penalty']
            fault_penalty_lw_n = float(st.text_input(idio['Fault penalty'][idi], fault_penalty_lw, key=7))

            target_score_lw = child_data['miniapps']['listen-write']['target_score']
            target_score_lw_n = float(st.text_input(idio['Target score'][idi], target_score_lw, key=8))

            languages_save = st.button(idio['Save'][idi], key=9)
            if languages_save:
                child_data['miniapps']['listen-write']['ex_rate'] = ex_rate_lw_n
                child_data['miniapps']['listen-write']['fault_penalty'] = fault_penalty_lw_n
                child_data['miniapps']['listen-write']['target_score'] = target_score_lw_n
                update_config(child_data, 'users/'+i+'.yaml')

            # --- List homeworks
            st.subheader(f"2.1. {idio['Listen and Write homeworks'][idi]}")

            if list(child_data['miniapps']['listen-write']['homework'].keys()):
                vocabulary_name_new = st.text_input(idio['Choose a vocabulary name'][idi], key=20)
                create_vocabulary = st.button(idio['Create vocabulary'][idi], key=22)

                vocabulary_names = list(child_data['miniapps']['listen-write']['homework'].keys())
                vocabulary_name = st.selectbox(idio['List of homeworks'][idi], vocabulary_names, key=12)

                vocabulary_list = child_data['miniapps']['listen-write']['homework'][vocabulary_name]
                vocabulary = st.text_area(idio['Vocabulary (separate by commas)'][idi], ', '.join(vocabulary_list.keys()))
                lang_voc = st.selectbox(idio['Select vocabulary language'][idi], langs, key=16, index=langs.index(idio['Language code'][user_data['idiom']]))
                
                if use_chatgpt:
                    chatgpt_prompt = st.text_input(idio['Insert ChatGPT prompt to create write a sentence'][idi], child_data['miniapps']['listen-write']['homework_conf'][vocabulary_name]['prompt'])
                
                scol1, scol2, scol3 = st.columns(3)
                with scol1:
                    button_del_lwhw = st.button(f"{idio['Delete vocabulary'][idi]} ⚠️", key=10)
                with scol2:
                    update_vocabulary = st.button(idio['Update vocabulary'][idi])

                # delete vocabulary
                if button_del_lwhw:
                    child_data['miniapps']['listen-write']['homework'].pop(vocabulary_name)
                    child_data['miniapps']['listen-write']['homework_conf'].pop(vocabulary_name)
                    update_config(child_data, 'users/'+i+'.yaml')
                    st.write(f'{vocabulary_name} deleted')

            else:
                vocabulary_name_new = st.text_input(idio['Choose a vocabulary name'][idi], key=21)
                create_vocabulary = st.button(idio['Create vocabulary'][idi])

                st.write(idio['There are no vocabularies to show'][idi])

            # create new vocabulary
            if create_vocabulary:
                child_data['miniapps']['listen-write']['homework'][vocabulary_name_new] = {}
                child_data['miniapps']['listen-write']['homework_conf'][vocabulary_name_new] = {}
                child_data['miniapps']['listen-write']['homework_conf'][vocabulary_name_new]['lang'] = 'en'
                child_data['miniapps']['listen-write']['homework_conf'][vocabulary_name_new]['score'] = 0
                child_data['miniapps']['listen-write']['homework_conf'][vocabulary_name_new]['prompt'] = idio['write a four words sentence with this word'][idi]
                child_data['miniapps']['listen-write']['homework'][vocabulary_name_new]['hello'] = 1.0
                update_config(child_data, 'users/'+i+'.yaml')

            # update existing vocabulary
            if update_vocabulary:
                try:
                    child_data['miniapps']['listen-write']['homework_conf'][vocabulary_name]['prompt'] = chatgpt_prompt
                except:
                    pass

                child_data['miniapps']['listen-write']['homework_conf'][vocabulary_name]['lang'] = lang_voc.split(':')[0]
                vocabulary = vocabulary.replace('，', ',')
                vocabulary = vocabulary.strip(', ')
                vocabulary = vocabulary.replace(', ', ',')
                vocabulary = vocabulary.split(',')
                vocabulary = [word.lower() for word in vocabulary]

                st.write(vocabulary)

                for l in vocabulary:
                    if l not in vocabulary_list:
                        child_data['miniapps']['listen-write']['homework'][vocabulary_name][clean_text(l)] = 1.0

                for m in list(vocabulary_list.keys()):
                    if m not in vocabulary:
                        child_data['miniapps']['listen-write']['homework'][vocabulary_name].pop(m)

                update_config(child_data, 'users/'+i+'.yaml')

            # --- Mathematics
            st.divider()
            st.header(f"3. {idio['Mathematics'][idi]}")

            mathematics_restart = st.button(f"{idio['Restart homework'][idi]} ⚠️")
            if mathematics_restart:
                child_data['miniapps']['mathematics']['current_score'] = 0.0
                update_config(child_data, 'users/'+i+'.yaml')

            target_score_m = child_data['miniapps']['mathematics']['target_score']
            target_score_m_n = float(st.text_input(idio['Target score'][idi], target_score_m))

            fault_penalty = child_data['miniapps']['mathematics']['fault_penalty']
            fault_penalty_n = float(st.text_input(idio['Fault penalty'][idi], fault_penalty))

            ex_rate_m = child_data['miniapps']['mathematics']['ex_rate']
            ex_rate_m_n = float(st.text_input(idio['Exchange rate'][idi], ex_rate_m, key=1))

            operations_n = st.multiselect(idio['Mathematic homeworks'][idi], ['sum', 'rest', 'multiplication', 'division'], child_data['miniapps']['mathematics']['operations'])

            mathematics_save2 = st.button(f"{idio['Save'][idi]}", key=18)
            if mathematics_save2:
                child_data['miniapps']['mathematics']['operations'] = operations_n
                child_data['miniapps']['mathematics']['ex_rate'] = ex_rate_m_n
                child_data['miniapps']['mathematics']['fault_penalty'] = fault_penalty_n
                child_data['miniapps']['mathematics']['target_score'] = target_score_m_n
                update_config(child_data, 'users/'+i+'.yaml')

            st.subheader(f"3.1. {idio['Basic operations'][idi]}:")

            sum_range = st.slider(idio['Sums range'][idi], 0, 1024, (child_data['miniapps']['mathematics']['homework']['sum']['lower_num'], child_data['miniapps']['mathematics']['homework']['sum']['upper_num']))
            rest_range = st.slider(idio['Rests range'][idi], 0, 1024, (child_data['miniapps']['mathematics']['homework']['rest']['lower_num'], child_data['miniapps']['mathematics']['homework']['rest']['upper_num']))
            multiplication_range = st.slider(idio['Multiplications range'][idi], 0, 32, (child_data['miniapps']['mathematics']['homework']['multiplication']['lower_num'], child_data['miniapps']['mathematics']['homework']['multiplication']['upper_num']))
            division_range = st.slider(idio['Divisions range'][idi], 0, 32, (child_data['miniapps']['mathematics']['homework']['division']['lower_num'], child_data['miniapps']['mathematics']['homework']['division']['upper_num']))

            mathematics_save = st.button(idio['Save'][idi], key=19)

            if mathematics_save:
                child_data['miniapps']['mathematics']['homework']['division']['lower_num'] = division_range[0]
                child_data['miniapps']['mathematics']['homework']['division']['upper_num'] = division_range[1]
                child_data['miniapps']['mathematics']['homework']['multiplication']['lower_num'] = multiplication_range[0]
                child_data['miniapps']['mathematics']['homework']['multiplication']['upper_num'] = multiplication_range[1]
                child_data['miniapps']['mathematics']['homework']['sum']['lower_num'] = sum_range[0]
                child_data['miniapps']['mathematics']['homework']['sum']['upper_num'] = sum_range[1]
                child_data['miniapps']['mathematics']['homework']['rest']['lower_num'] = rest_range[0]
                child_data['miniapps']['mathematics']['homework']['rest']['upper_num'] = rest_range[1]
                update_config(child_data, 'users/'+i+'.yaml')

        else:
            st.write(idio['You have no childs, to add a child send /add_child using telegram'][idi])


    except ValueError as e:
        with open('config.yaml', 'r') as file:
            BOT_TOKEN = yaml.safe_load(file)['telegram']['token']
        send_message(BOT_TOKEN, '649792299', e)

if __name__ == '__main__':
    st.set_page_config(
        page_title="AI teacher assistant",
        page_icon="📚",
    )

    main()
