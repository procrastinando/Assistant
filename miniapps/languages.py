import requests
import subprocess
import torch
from faster_whisper import WhisperModel
import openai
import azure.cognitiveservices.speech as speechsdk
import difflib
import easyocr
from PIL import Image
import os
from gtts import gTTS
import random


def clean_text(string):
    string = string.lower()
    string = " ".join(string.split())
    string = string.strip()
    chars = '"\'“¿([{-"\'.。|,，!！?？:：”)]}、'
    for char in chars:
        string = string.replace(char, "")
    return string

def voice2text(BOT_TOKEN, resp_media, user_data):
    response_media = resp_media.json()
    url_media = f'https://api.telegram.org/file/bot{BOT_TOKEN}/' + response_media['result']["file_path"] # https://api.telegram.org/file/bot<token>/<file_path>
    response = requests.get(url_media)
    response.raise_for_status()

    with open('miniapps/languages/v2t.oga', 'wb') as f:
        f.write(response.content)

    try:
        if user_data['miniapps']['read-speak']['v2t-model'] == 'whisper':
            whisper_size = user_data['miniapps']['read-speak']['whisper-size'] # Choose model size
            if torch.cuda.is_available():
                model = WhisperModel(whisper_size, device="cuda", compute_type="float16")
            else:
                model = WhisperModel(whisper_size, device="cpu", compute_type="int8")
            segments, info = model.transcribe('miniapps/languages/v2t.oga')
            result = ''.join([segment.text for segment in segments])
        elif user_data['miniapps']['read-speak']['v2t-model'] == 'openai':
            openai.api_key = user_data['openai']
            model = 'whisper-1'
            audio_file = open("miniapps/languages/v2t.oga", 'rb')
            result = openai.Audio.transcribe(model=model, file=audio_file)["text"]
        return result
    except:
        return '#error'

def text2voice(config, user_data, type_hw):
    if type_hw == 'read-speak':
        cb_data = user_data['miniapps'][type_hw]['current_request'].split("$")
        text = user_data['miniapps'][type_hw]['homework'][cb_data[0]][int(cb_data[1])]['text'] # userdata[miniapps][languages][homework][hansel][6][text]
        lang = user_data['miniapps'][type_hw]['homework_lang'][cb_data[0]]['lang']
    elif type_hw == 'listen-write':
        cb_data = user_data['miniapps'][type_hw]['current_request'].split("%")
        options = user_data['miniapps'][type_hw]['homework'][cb_data[0]]
        option_names = list(options.keys())
        weights = [value ** 2 for value in options.values()]
        text = random.choices(option_names, weights=weights)[0]
        lang = user_data['miniapps'][type_hw]['homework_conf'][cb_data[0]]['lang']

        try:
            if user_data['miniapps'][type_hw]['chatgpt'] == True:
                openai.api_key = user_data['credentials']['openai']
                prompt = user_data['miniapps'][type_hw]['homework_conf'][cb_data[0]]['prompt'] # make a 4 words sentence with this word
                completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": f"{prompt} {text}"}])
                text = clean_text(completion.choices[0].message.content)
        except:
            pass

    if user_data['miniapps']['read-speak']['t2v-model'] == 'azure':
        speech_config = speechsdk.SpeechConfig(subscription=user_data['azure']['token'], region=user_data['azure']['region'])
        audio_config = speechsdk.AudioConfig(filename="miniapps/languages/t2v.mp3")
        synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
        result = synthesizer.speak_text_async(text).get()
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            print("Speech synthesized to speaker for text [{}]".format(text))
            subprocess.run(["ffmpeg", "-loglevel", "quiet", "-i", "miniapps/languages/t2v.mp3", "-filter:a", f"atempo={user_data['miniapps']['read-speak']['voice-speed']}", "-vn", "miniapps/languages/t2v_.mp3", "-y"])
            return text, 'miniapps/languages/t2v_.mp3'
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            print("Speech synthesis canceled: {}".format(cancellation_details.reason))
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                if cancellation_details.error_details:
                    print("Error details: {}".format(cancellation_details.error_details))
                    return text, '#error'

    elif user_data['miniapps']['read-speak']['t2v-model'] == 'google':
        try:
            tts = gTTS(text, lang=lang)
            tts.save('miniapps/languages/t2v.mp3')
            subprocess.run(["ffmpeg", "-loglevel", "quiet", "-i", "miniapps/languages/t2v.mp3", "-filter:a", f"atempo={user_data['miniapps']['read-speak']['voice-speed']}", "-vn", "miniapps/languages/t2v_.mp3", "-y"])
            return text, 'miniapps/languages/t2v_.mp3'
        except:
            return text, '#error'

def read_speak(BOT_TOKEN, user_data, file_id, idio, idi):
    resp_media = requests.get(f'https://api.telegram.org/bot{BOT_TOKEN}/getFile?file_id={file_id}') # File ID
    speech = voice2text(BOT_TOKEN, resp_media, user_data)
    
    if speech == '#error':
        return user_data, 'Error transcribing the audio'
    else:
        cb_data = user_data['miniapps']['read-speak']['current_request'].split("$")
        current_score = user_data['miniapps']['read-speak']['homework'][cb_data[0]][int(cb_data[1])]['score']

        if current_score > user_data['miniapps']['read-speak']['target_score']:
            message = f"{idio['Finished'][idi]}! 🎉 🎉 🎉 🎉 🎉"
        else:
            text = user_data['miniapps']['read-speak']['homework'][cb_data[0]][int(cb_data[1])]['text'] # userdata[miniapps][languages][homework][hansel][6][text]
            text_clean = clean_text(text)
            speech_clean = clean_text(speech)

            sequence = difflib.SequenceMatcher(isjunk=None, a=text_clean, b=speech_clean)
            score = ((sequence.ratio() ** user_data['miniapps']['read-speak']['difficulty']) * 13) - 3 # score from 1 to 10
            emoji = " 😍" if score > 6.6 else " 😐" if score > 3.3 else " 😭" if score > 0.0 else " ❗"

            if current_score + score > user_data['miniapps']['read-speak']['target_score']:
                user_data['miniapps']['read-speak']['homework'][cb_data[0]][int(cb_data[1])]['score'] = current_score + score
                message = f"{speech}\n\n{idio['Score'][idi]}: {round(score, 1)} {emoji}\n{idio['Finished'][idi]}! 🎉 🎉 🎉 🎉 🎉"
            else:
                user_data['miniapps']['read-speak']['homework'][cb_data[0]][int(cb_data[1])]['score'] = current_score + score
                message = f"{speech}\n\n{idio['Score'][idi]}: {round(score, 1)} {emoji}\n{idio['Total'][idi]}: {round(current_score + score, 1)}"
                user_data['coins'] = user_data['coins'] + score / user_data['miniapps']['read-speak']['ex_rate']
        
        return user_data, message
    
def listen_write(user_data, message_text, idio, idi):
    cb_data = user_data['miniapps']['listen-write']['current_request'].split("%")
    current_score = user_data['miniapps']['listen-write']['homework_conf'][cb_data[0]]['score']
    message_text = clean_text(message_text)

    if current_score >= user_data['miniapps']['listen-write']['target_score']:
        message = f"{idio['Finished'][idi]}! 🎉 🎉 🎉 🎉 🎉"
    else:
        if message_text == user_data['miniapps']['listen-write']['answer']:
            current_score = current_score + 1
            user_data['miniapps']['listen-write']['homework_conf'][cb_data[0]]['score'] = current_score
            user_data['miniapps']['listen-write']['homework'][cb_data[0]][user_data['miniapps']['listen-write']['answer']] = user_data['miniapps']['listen-write']['homework'][cb_data[0]][user_data['miniapps']['listen-write']['answer']]/2
            if current_score >= user_data['miniapps']['listen-write']['target_score']:
                message = f"{idio['Well done'][idi]}! 😀\n{idio['Finished'][idi]}! 🎉 🎉 🎉 🎉 🎉"
            else:
                message = f"{idio['Well done'][idi]}! 😀\n{idio['Progress'][idi]}: {round(current_score/user_data['miniapps']['listen-write']['target_score']*100, 1)}%"
        else:
            current_score = current_score + user_data['miniapps']['listen-write']['fault_penalty']
            user_data['miniapps']['listen-write']['homework_conf'][cb_data[0]]['score'] = current_score
            user_data['miniapps']['listen-write']['homework'][cb_data[0]][user_data['miniapps']['listen-write']['answer']] = (user_data['miniapps']['listen-write']['homework'][cb_data[0]][user_data['miniapps']['listen-write']['answer']]+1)/2
            message = f"{idio['That is not correct'][idi]} 😥\n➡️ {user_data['miniapps']['listen-write']['answer']}\n{idio['Progress'][idi]}: {round(current_score/user_data['miniapps']['listen-write']['target_score']*100, 1)}%"
            user_data['coins'] = user_data['coins'] + user_data['miniapps']['listen-write']['fault_penalty'] / user_data['miniapps']['listen-write']['ex_rate']
        user_data['coins'] = user_data['coins'] + 1 / user_data['miniapps']['listen-write']['ex_rate']

    return user_data, message

def rs_reply_markup(user_data):
    reply_markup = []
    for i in list(user_data['miniapps']['read-speak']['homework'].keys()): # e.g. hansel-gretel
        for j in list(user_data['miniapps']['read-speak']['homework'][i]):
            a = {}
            a['text'] = f"{i} {j}  ➡️  {round(user_data['miniapps']['read-speak']['homework'][i][j]['score'], 1)}/{user_data['miniapps']['read-speak']['target_score']}"
            a["callback_data"] = f"{i}${j}"
            reply_markup.append([a])
    return reply_markup

def lw_reply_markup(user_data):
    reply_markup = []
    for i in list(user_data['miniapps']['listen-write']['homework'].keys()): # e.g. hansel-gretel
        a = {}
        a['text'] = f"{i}  ➡️  {user_data['miniapps']['listen-write']['homework_conf'][i]['score']}/{user_data['miniapps']['listen-write']['target_score']}"
        a["callback_data"] = f"{i}%"
        b = {}
        b['text'] = '👁️'
        b["callback_data"] = f"{i}^"
        reply_markup.append([a, b])
    return reply_markup
 
def add_ocr(images_path, languages):

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

    lang_codes = []
    for i in languages:
        lang_codes.append(language_dict[i])
    reader = easyocr.Reader(lang_codes) # this needs to run only once to load the model into memory
    result = reader.readtext(images_path)

    text = ''
    for i in result:
        text = text + " " + i[1]

    return text
