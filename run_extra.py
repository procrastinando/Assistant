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

from run_telegram import open_data
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
    for m in range(len(extra['short'])):
        extra_data = extra['short'][m].split('|')

        with open('idiom.yaml', 'r') as file:
            idio = yaml.safe_load(file)
        user_data = open_data(extra_data[0])
        idi = user_data['idiom']
        if idi not in list(idio['Add homework'].keys()):
            idi = 'en'

        if 'img2text' in extra_data: # user_id|img2text
            image_path = 'miniapps/languages/images/'+extra_data[0]
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image)
            os.remove(image_path)
            put_extra(f"{extra_data[0]}|message|{text}")
            take_extra('short', m)

        elif 'youtube' in extra_data:
            cb_data = extra_data[4].split("*") # cb_data => user_id*resolution*bitrate*fps
            size_exceeded = f"{idio['File size exceeded, download the file here'][idi]}:\n{admin_url}"
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
            take_extra('short', m)
        
        elif 'read_speak' in extra_data: # extra_data = user_id|read_speak|voice_file_id|reply
            user_data, message = read_speak(BOT_TOKEN, extra_data[0], extra_data[2], idio, idi)
            put_extra(f"{extra_data[0]}|message_reply|{message}|{extra_data[3]}")
            take_extra('short', m)


def run_large(BOT_TOKEN, extra, admin_url):
    for m in range(len(extra['large'])):
        extra_data = extra['large'][m].split('|') # user_id|voice2text|whisper|tiny

        with open('idiom.yaml', 'r') as file:
            idio = yaml.safe_load(file)
        user_data = open_data(extra_data[0])
        idi = user_data['idiom']
        if idi not in list(idio['Add homework'].keys()):
            idi = 'en'

        if 'voice2text' in extra_data: # user_id|voice2text|whisper|tiny
            media_file_path = f"miniapps/voice2text/{extra_data[0]}"
            text = generate_transcription(extra_data[3], media_file_path)
            os.remove(media_file_path)
            put_extra(f"{extra_data[0]}|message|{text}")
            take_extra('large', m)


def main(BOT_TOKEN, arg1, admin_url):
    while True:
        time.sleep(0.5) # to not overload the processor
        with open('extra.yaml', 'r') as file:
            extra = yaml.safe_load(file)

        if arg1 == 'short':
            try:
                run_short(BOT_TOKEN, extra, admin_url)
            except:
                pass

        elif arg1 == 'large':
            try:
                run_large(BOT_TOKEN, extra, admin_url)
                run_short(BOT_TOKEN, extra, admin_url)
            except:
                pass
        gc.collect()

if __name__ == '__main__':

    with open('config.yaml', 'r') as file:
        config = yaml.safe_load(file)
        BOT_TOKEN = config['telegram']['token']
        admin_url = config['admin']['url']

    arg1 = sys.argv[1]

    main(BOT_TOKEN, arg1, admin_url) # 'short' options: short, large. If short will try only short time required jobs. If large, will try to find large jobs first, if not, short jobs
