import requests
import yaml
import pytesseract
import time
from PIL import Image
import subprocess
import os
import gc
from pytube import YouTube
import sys
import torch
from gtts import gTTS
import datetime

from deep_translator import ChatGptTranslator, GoogleTranslator
from faster_whisper import WhisperModel

from run_telegram import open_data, add_to_data
from miniapps.languages import clean_text, read_speak
from miniapps.voice2text import generate_transcription

def take_extra(multi, position):
    with open('extra.yaml', 'r') as file:
        extra = yaml.safe_load(file)
    extra[multi].pop(position)
    with open('extra.yaml', 'w') as file:
        yaml.dump(extra, file)

def put_extra(job):
    with open('extra.yaml', 'r') as file:
        extra = yaml.safe_load(file)
    extra['answer'].append(job)
    with open('extra.yaml', 'w') as file:
        yaml.dump(extra, file)

def run_short(BOT_TOKEN, extra, admin_url):
    if len(extra['short']) != 0:
        short_tasks = extra['short']

        with open('extra.yaml', 'r') as file:
            extra = yaml.safe_load(file)
        extra['short'] = []
        with open('extra.yaml', 'w') as file:
            yaml.dump(extra, file)

        for m in range(len(short_tasks)):
            extra_data = short_tasks[m].split('|')

            with open('idiom.yaml', 'r') as file:
                idio = yaml.safe_load(file)
            user_data = open_data(extra_data[0])
            idi = user_data['idiom']
            if idi not in list(idio['Add homework'].keys()):
                idi = 'en'

            if 'img2text' in extra_data: # user_id|img2text
                start_time = time.time()
                image_path = 'miniapps/languages/images/'+extra_data[0]
                image = Image.open(image_path)
                text = pytesseract.image_to_string(image)
                os.remove(image_path)
                put_extra(f"{extra_data[0]}|message|{text}")
                add_to_data(extra_data[0], '/image2text', start_time)
            
            elif 'read_speak' in extra_data: # extra_data = user_id|read_speak|voice_file_id|reply
                start_time = time.time()
                user_data, message = read_speak(BOT_TOKEN, open_data(extra_data[0]), extra_data[2], idio, idi)
                with open('users/'+extra_data[0]+'.yaml', 'w') as file:
                    yaml.dump(user_data, file)
                put_extra(f"{extra_data[0]}|message_reply|{message}|{extra_data[3]}")
                add_to_data(extra_data[0], '/teacher', start_time)

            elif 'walkie_talkie' in extra_data: # user_id|walkie_talkie|file_id|message_id|contact
                # Get file
                start_time = time.time()
                try:
                    resp_media = requests.get(f'https://api.telegram.org/bot{BOT_TOKEN}/getFile?file_id={extra_data[2]}')
                    response_media = resp_media.json()
                    url_media = f'https://api.telegram.org/file/bot{BOT_TOKEN}/' + response_media['result']["file_path"]
                    response = requests.get(url_media)
                    response.raise_for_status()

                    try:
                        if not os.path.exists(f"miniapps/walkie_talkie/{extra_data[0]}"):
                            os.mkdir(f"miniapps/walkie_talkie/{extra_data[0]}")
                        with open(f"miniapps/walkie_talkie/{extra_data[0]}/{extra_data[0]}.oga", 'wb') as f:
                            f.write(response.content)

                        if user_data['miniapps']['walkie_talkie']['whisper-size'] == 'openai':
                            openai.api_key = user_data['openai']
                            model = 'whisper-1'
                            audio_file = open(f"miniapps/walkie_talkie/{extra_data[0]}/{extra_data[0]}.oga", 'rb')
                            result = openai.Audio.transcribe(model=model, file=audio_file)["text"]
                        else:
                            model_size = user_data['miniapps']['walkie_talkie']['whisper-size'].split("-")[1] # Choose model size
                            if torch.cuda.is_available():
                                model = WhisperModel(model_size, device="cuda", compute_type="float16")
                            else:
                                model = WhisperModel(model_size, device="cpu", compute_type="int8")
                            segments, info = model.transcribe(f"miniapps/walkie_talkie/{extra_data[0]}/{extra_data[0]}.oga")
                            result = ''.join([segment.text for segment in segments])

                        try:
                            target_lang = user_data['miniapps']['walkie_talkie']['contacts'][extra_data[4]]
                            if user_data['miniapps']['walkie_talkie']['translator_engine'] == 'Google translator':
                                translated_text = GoogleTranslator(source='auto', target=target_lang).translate(result)
                            elif user_data['miniapps']['walkie_talkie']['translator_engine'] == 'ChatGPT translator':
                                translated_text = ChatGptTranslator(api_key=user_data['credentials']['openai'], target=target_lang).translate(text=result)

                            try:
                                if user_data['miniapps']['walkie_talkie']['t2v-model'] == 'Azure':
                                    speech_config = speechsdk.SpeechConfig(subscription=user_data['azure']['token'], region=user_data['azure']['region'])
                                    file_name = time.time()
                                    audio_config = speechsdk.AudioConfig(filename=f"miniapps/walkie_talkie/{extra_data[0]}/{file_name}.mp3")
                                    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
                                    synthesizer.speak_text_async(text).get()

                                elif user_data['miniapps']['walkie_talkie']['t2v-model'] == 'Google TTS':
                                    tts = gTTS(translated_text, lang=target_lang)
                                    file_name = time.time()
                                    tts.save(f"miniapps/walkie_talkie/{extra_data[0]}/{file_name}.mp3")

                                put_extra(f"{extra_data[0]}|message_reply|{idio['You said'][idi]}:\n {result}|{extra_data[3]}")
                                put_extra(f"{user_data['miniapps']['walkie_talkie']['default']}|audio|{config['credentials']['usernames'][extra_data[0]]['name']}:\n{translated_text}|miniapps/walkie_talkie/{extra_data[0]}/{file_name}.mp3") # user_id|audio|message|audio_path

                            except:
                                put_extra(f"{extra_data[0]}|message|{idio['Error during text to voice generation'][idi]}")

                        except:
                            put_extra(f"{extra_data[0]}|message|{idio['Error during the translation'][idi]}")

                    except:
                        put_extra(f"{extra_data[0]}|message|{idio['Error during transcription'][idi]}")

                except:
                    put_extra(f"{extra_data[0]}|message|{idio['Network error'][idi]}")

                add_to_data(extra_data[0], '/walkie_talkie', start_time)

        gc.collect()

def run_large(BOT_TOKEN, extra, admin_url):
    if len(extra['large']) != 0:
        large_tasks = extra['large']

        with open('extra.yaml', 'r') as file:
            extra = yaml.safe_load(file)
        extra['large'] = []
        with open('extra.yaml', 'w') as file:
            yaml.dump(extra, file)

        for m in range(len(large_tasks)):
            extra_data = large_tasks[m].split('|') # user_id|voice2text|whisper|tiny

            with open('idiom.yaml', 'r') as file:
                idio = yaml.safe_load(file)
            user_data = open_data(extra_data[0])
            idi = user_data['idiom']
            if idi not in list(idio['Add homework'].keys()):
                idi = 'en'

            if 'voice2text' in extra_data: # user_id|voice2text|whisper|tiny
                start_tiem = time.time()
                media_file_path = f"miniapps/voice2text/{extra_data[0]}/{extra_data[0]}.oga"
                text = generate_transcription(extra_data[3], media_file_path)
                os.remove(media_file_path)
                put_extra(f"{extra_data[0]}|message|{text}")
                add_to_data(extra_data[0], '/voice2text', start_time)

            elif 'youtube' in extra_data: 
                start_time = time.time()

                cb_data = extra_data[4].split("*") # cb_data => user_id*resolution*bitrate*fps
                size_exceeded = f"{idio['File size exceeded, download the file here'][idi]}:\n{admin_url+'Youttube'}"
                del_list = ['miniapps/youtube/'+cb_data[0]+'a', 'miniapps/youtube/'+cb_data[0]+'v']

                if len(cb_data) == 4: # there is fps information
                    yt = YouTube(user_data['miniapps']['youtube']['request']['url']).streams
                    yt.filter(type="video", res=cb_data[1], fps=int(cb_data[3]))[0].download(output_path='miniapps/youtube/', filename=cb_data[0]+'v')
                    yt.filter(type="audio", abr=cb_data[2])[0].download(output_path='miniapps/youtube/', filename=cb_data[0]+'a')
                    subprocess.run(['ffmpeg', '-loglevel', 'quiet', '-i', 'miniapps/youtube/'+cb_data[0]+'v', '-i', 'miniapps/youtube/'+cb_data[0]+'a', '-c:v', 'copy', '-c:a', 'libmp3lame', '-b:a',  cb_data[2].split('b')[0], '-strict', '-2', 'miniapps/youtube/'+clean_text(extra_data[3])+'.mp4', '-y'])
                    del_list.append('miniapps/youtube/'+cb_data[0]+'.mp3')
                    put_extra(f"{extra_data[0]}|video|{extra_data[3]}|miniapps/youtube/{clean_text(extra_data[3])}.mp4|{size_exceeded}")

                elif 'audio' in cb_data: # is only audio
                    yt = YouTube(user_data['miniapps']['youtube']['request']['url']).streams
                    yt.filter(type="audio", abr=cb_data[2])[0].download(output_path='miniapps/youtube/', filename=cb_data[0]+'a')
                    subprocess.run(['ffmpeg', '-loglevel', 'quiet', '-i', 'miniapps/youtube/'+cb_data[0]+'a', '-c:a', 'libmp3lame', '-b:a',  cb_data[2].split('b')[0], '-strict', '-2', 'miniapps/youtube/'+clean_text(extra_data[3])+'.mp3', '-y'])
                    del_list.append('miniapps/youtube/'+cb_data[0]+'.mp4')
                    put_extra(f"{extra_data[0]}|audio|{extra_data[3]}|miniapps/youtube/{clean_text(extra_data[3])}.mp3|{size_exceeded}")

                else: # regular video
                    yt = YouTube(user_data['miniapps']['youtube']['request']['url']).streams
                    yt.filter(type="video", res=cb_data[1])[0].download(output_path='miniapps/youtube/', filename=cb_data[0]+'v')
                    yt.filter(type="audio", abr=cb_data[2])[0].download(output_path='miniapps/youtube/', filename=cb_data[0]+'a')
                    subprocess.run(['ffmpeg', '-loglevel', 'quiet', '-i', 'miniapps/youtube/'+cb_data[0]+'v', '-i', 'miniapps/youtube/'+cb_data[0]+'a', '-c:v', 'copy', '-c:a', 'libmp3lame', '-b:a',  cb_data[2].split('b')[0], '-strict', '-2', 'miniapps/youtube/'+clean_text(extra_data[3])+'.mp4', '-y'])
                    del_list.append('miniapps/youtube/'+cb_data[0]+'.mp3')
                    put_extra(f"{extra_data[0]}|video|{extra_data[3]}|miniapps/youtube/{clean_text(extra_data[3])}.mp4|{size_exceeded}")

                for del_file in del_list:
                    try:
                        os.remove(del_file)
                    except:
                        pass

                add_to_data(extra_data[0], '/youtube', start_time)

        gc.collect()

def main(BOT_TOKEN, arg1, admin_url):
    while True:
        try:
            time.sleep(1) # to not overload the processor
            with open('extra.yaml', 'r') as file:
                extra = yaml.safe_load(file)

            if arg1 == 'short':
                run_short(BOT_TOKEN, extra, admin_url)

            elif arg1 == 'large':
                run_large(BOT_TOKEN, extra, admin_url)
                run_short(BOT_TOKEN, extra, admin_url)

        except Exception as e:
            with open('log.txt', 'a') as f:
                f.write(f"{datetime.datetime.now()}: {e}\n")

if __name__ == '__main__':

    with open('config.yaml', 'r') as file:
        config = yaml.safe_load(file)
        BOT_TOKEN = config['telegram']['token']
        admin_url = config['admin']['url']

    arg1 = sys.argv[1]

    main(BOT_TOKEN, arg1, admin_url) # 'short' options: short, large. If short will try only short time required jobs. If large, will try to find large jobs first, if not, short jobs
