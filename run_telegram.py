import requests
import json
import yaml
import time
import datetime
import pandas as pd
import os
import gc
import streamlit_authenticator as stauth
from pytube import YouTube
import random
import pytz

from miniapps.text2image import Lexica
from miniapps.mathematics import mathematics, random_question
from miniapps.languages import listen_write, rs_reply_markup, lw_reply_markup, clean_text, text2voice

def get_user_id(i):
    try:
        user_id = i['message']['from']['id']
    except:
        try:
            user_id = i['callback_query']['from']['id']
        except:
            user_id = 'None'
    return str(user_id)

def create_new_user(config, BOT_TOKEN, user_id, i):
    user_data = {
        'idiom': i['message']['from']['language_code'],
        'credentials': {
            'share': [],
            'azure': {}
        },
        'blocked': [],
        'coins': 0.0,
        'childs': [],
        'location': '0',
        'azure': {},
        'miniapps': {
            'image2text': ['English'],
            'walkie_talkie': {
                'whisper-size': 'whisper-tiny',
                'default': '0',
                'contacts': {},
                'translator_engine': 'Google translator',
                't2v-model': 'Google TTS',
            },
            'mathematics': {
                'current_score': 0.0,
                'answer': 0,
                'ex_rate': 20.0,
                'fault_penalty': -1,
                'target_score': 50.0,
                'operations': [],
                'homework': {
                    'division': {
                        'lower_num': 2,
                        'upper_num': 10
                    },
                    'multiplication': {
                        'lower_num': 2,
                        'upper_num': 10
                    },
                    'rest': {
                        'lower_num': 4,
                        'upper_num': 32
                    },
                    'sum': {
                        'lower_num': 4,
                        'upper_num': 32
                    }
                }
            },
            'listen-write': {
                'answer': 0,
                'chatgpt': False,
                'current_request': 0,
                'ex_rate': 10.0,
                'fault_penalty': -1,
                'target_score': 50.0,
                'homework': {},
                'homework_conf': {}
            },
            'read-speak': {
                'current_request': '0',
                'difficulty': 2.0,
                'ex_rate': 500.0,
                'homework': {},
                'homework_lang': {},
                't2v-model': 'google',
                'target_score': 50.0,
                'v2t-model': 'whisper',
                'voice-speed': 0.75,
                'whisper-size': 'base'
            },
            'youtube': {
                'file': {},
                'request': {
                    'url': 'https://www.youtube.com/shorts/WAWQluwU0yM'
                }
            }
        }
    }
    with open(f'users/{user_id}.yaml', 'w') as file:
        yaml.dump(user_data, file)

    try:
        complete_name = i['message']['from']['first_name']
    except:
        complete_name = i['callback_query']['from']['first_name']

    config['credentials']['usernames'][user_id] = {}
    config['credentials']['usernames'][user_id]['name'] = complete_name
    config['credentials']['usernames'][user_id]['password'] = '0'
    welcome_message = f"Welcome {complete_name}!\nYour user ID is: {user_id}\nYou can set a /password to access to your console\n{config['admin']['url']}"

    update_config(config, 'config.yaml')

    send_message(BOT_TOKEN, user_id, welcome_message)

def update_config(data, data_path):
    with open(data_path, 'w') as file:
        yaml.dump(data, file)

def open_data(user_id):
    with open('users/'+user_id+'.yaml', 'r') as file:
        user_config = yaml.safe_load(file)
    return user_config

def set_commands(BOT_TOKEN):
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/setMyCommands'
    headers = {"Content-Type": "application/json"}
    data = {
        "commands": [{"command": "settings", "description": "Manage your account ⚙️"}, {"command": "image2text", "description": "Image to text (OCR) 🅰"}, {"command": "teacher", "description": "AI Teacher assistant 📚"}, {"command": "text2image", "description": "AI image generator 📷"}, {"command": "voice2text", "description": "AI voice to text 🎙"}, {"command": "walkie_talkie", "description": "AI walkie talkie 📲"}, {"command": "youtube", "description": "Youtube downloader 📺"}]
        }
    data = json.dumps(data)
    resp = requests.post(url, data=data, headers=headers)

def send_teacher_keyboard(BOT_TOKEN, chat_id, text):
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
    headers = {"Content-Type": "application/json"}

    keyboard = {
        'keyboard': [['/wallet'], ['/mathematics'], ['/read_speak'], ['/listen_write']],
        'one_time_keyboard': True,
        'resize_keyboard': True
    }

    data = {
        "chat_id": chat_id,
        "text": text,
        "reply_markup": keyboard,
        }
    data = json.dumps(data)
    resp = requests.post(url, data=data, headers=headers)

def send_settings_keyboard(BOT_TOKEN, chat_id, text):
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
    headers = {"Content-Type": "application/json"}

    keyboard = {
        'keyboard': [['/console'], ['/get_id'], ['/language'], ['/password'], ['/change_name'], ['/add_member'], ['/remove_member']],
        'one_time_keyboard': True,
        'resize_keyboard': True
    }

    data = {
        "chat_id": chat_id,
        "text": text,
        "reply_markup": keyboard,
        }
    data = json.dumps(data)
    resp = requests.post(url, data=data, headers=headers)

def send_message(BOT_TOKEN, chat_id, text):
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
    data = {'chat_id': chat_id, 'text': text}
    response = requests.post(url, data=data)
    return response.json()

def send_message_reply(BOT_TOKEN, chat_id, text, reply):
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
    data = {'chat_id': chat_id, 'text': text, 'reply_to_message_id': reply}
    response = requests.post(url, data=data)
    return response.json()

def send_inline(BOT_TOKEN, chat_id, text, reply_markup):
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
    headers = {"Content-Type": "application/json"}
    data = {
        "chat_id": chat_id,
        "text": text,
        "reply_markup": {
            "inline_keyboard": reply_markup,
            },
        }
    data = json.dumps(data)
    resp = requests.post(url, data=data, headers=headers)

def send_audio(BOT_TOKEN, chat_id, message, audio_file):
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendAudio'
    data = {
        "chat_id": chat_id,
        "caption": message
    }
    files = {
        "audio": open(audio_file, "rb")
    }
    response = requests.post(url, data=data, files=files)

def send_video(BOT_TOKEN, chat_id, message, video_file):
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendVideo'
    data = {
        "chat_id": chat_id,
        "caption": message
    }
    files = {
        "video": open(video_file, "rb")
    }
    response = requests.post(url, data=data, files=files)

def send_mediagroup(bot_token, chat_id, image_urls):
    url = f'https://api.telegram.org/bot{bot_token}/sendMediaGroup'
    media = [{'type': 'photo', 'media': image_url} for image_url in image_urls]
    data = {'chat_id': chat_id, 'media': json.dumps(media)}
    response = requests.post(url, data=data)

def delete_old_files(directory_path, time_threshold):
    current_time = time.time()
    for foldername, subfolders, filenames in os.walk(directory_path):
        for filename in filenames:
            file_path = os.path.join(foldername, filename)
            file_time = os.path.getmtime(file_path)
            if current_time - file_time > time_threshold:
                os.remove(file_path)

def process_extra(BOT_TOKEN):
    with open('extra.yaml', 'r') as file:
        extra = yaml.safe_load(file)

    for a in extra['answer']:
        start_time = time.time()

        cb_data = a.split("|")

        if "message" in cb_data:
            send_message(BOT_TOKEN, cb_data[0], cb_data[2])
        
        elif "message_reply" in cb_data:
            send_message_reply(BOT_TOKEN, cb_data[0], cb_data[2], cb_data[3])

        elif "audio" in cb_data:
            try:
                send_audio(BOT_TOKEN, cb_data[0], cb_data[2], cb_data[3])
            except:
                send_message(BOT_TOKEN, cb_data[0], cb_data[4])

        elif "video" in cb_data:
            if os.path.getsize(cb_data[3]) < 50*1024*1024:
                send_video(BOT_TOKEN, cb_data[0], cb_data[2], cb_data[3])
            else:
                send_message(BOT_TOKEN, cb_data[0], cb_data[4])

        add_to_data(cb_data[0], 'others', start_time)

    extra['answer'] = []
    with open('extra.yaml', 'w') as file:
        yaml.dump(extra, file)

def add_to_data(user, job_type, start_time):
    if not os.path.exists('data.csv'): 
         with open('data.csv', 'w') as file: 
             yaml.dump('date,User,job_type,time', file)
    data = pd.read_csv('data.csv')
    current_date_time = datetime.datetime.now(pytz.utc).strftime('%Y-%m-%d-%H:%M:%S')
    total_time = (time.time() - start_time) / 60
    new_row = pd.DataFrame({'date': [current_date_time], 'User': [user], 'job_type': [job_type], 'time': [total_time]})
    data = pd.concat([data, new_row], ignore_index=True)
    data.to_csv('data.csv', index=False)

def main():

    try:
        # Load basic conf
        with open('config.yaml', 'r') as file:
            config = yaml.safe_load(file)
        BOT_TOKEN = config['telegram']['token']
        streamlit_url = config['admin']['url']
        url = config['telegram']['offset']

        # Delete old files and send extra jobs
        delete_old_files('miniapps/youtube/', 1800)
        delete_old_files('miniapps/voice2text/', 1800)
        delete_old_files('miniapps/walkie_talkie/', 1800)
        process_extra(BOT_TOKEN)
        add_to_data(config['admin']['id'], 'none', time.time())

        # Set everything to start
        response = requests.get(url)
        resp = response.json()

        # check if there are any new messages
        if resp['result']:

            for i in resp['result']:
                user_id = get_user_id(i)
                users = list(config['credentials']['usernames'].keys())

                if user_id != 'None':
                    if user_id not in users:
                        create_new_user(config, BOT_TOKEN, user_id, i)
                        update_config(config, 'config.yaml')

                    else:
                        with open('idiom.yaml', 'r') as file:
                            idio = yaml.safe_load(file)
                        user_data = open_data(user_id)

                        idi = user_data['idiom']
                        if idi not in list(idio['Add homework'].keys()):
                            idi = 'en'

                        if 'message' in i: # ['message']['entities'] in i:
                            if 'entities' in i['message'] and i['message']['text'] not in user_data['blocked']:

                                if i['message']['text'] == '/console':
                                    user_data['location'] = i['message']['text']
                                    send_message(BOT_TOKEN, user_id, idio['Access to your console here'][idi]+f":\n{streamlit_url}\n\n{idio['User'][idi]}: {user_id}")

                                elif i['message']['text'] == '/get_id':
                                    user_data['location'] = i['message']['text']
                                    send_message(BOT_TOKEN, user_id, f'{user_id}')

                                elif i['message']['text'] == '/language':
                                    user_data['location'] = i['message']['text']
                                    reply_markup = []
                                    for k in list(idio['Add homework'].keys()):
                                        a = {}
                                        a['text'] = k
                                        a["callback_data"] = f"{k}!"
                                        reply_markup.append([a])
                                    send_inline(BOT_TOKEN, user_id, f"{idio['Current language'][idi]}: {user_data['idiom']}", reply_markup)

                                elif i['message']['text'] == '/change_name':
                                    user_data['location'] = i['message']['text']
                                    send_message(BOT_TOKEN, user_id, f"{idio['Current'][idi]}: {config['credentials']['usernames'][user_id]['name']}. "+idio['Choose a new name'][idi])

                                elif i['message']['text'] == '/password':
                                    user_data['location'] = i['message']['text']
                                    send_message(BOT_TOKEN, user_id, idio['Type a new password'][idi])

                                elif i['message']['text'] == '/add_member':
                                    user_data['location'] = i['message']['text']
                                    send_message(BOT_TOKEN, user_id, idio["Insert the child's ID"][idi])

                                elif i['message']['text'] == '/remove_member':
                                    user_data['location'] = i['message']['text']
                                    reply_markup = []
                                    for a in user_data['childs']:
                                        b = {}
                                        b['text'] = a
                                        b["callback_data"] = f"{a}&{0}"
                                        reply_markup.append([b])

                                    send_inline(BOT_TOKEN, user_id, idio['Select child to remove'][idi], reply_markup)

                                elif i['message']['text'] == '/wallet':
                                    user_data['location'] = i['message']['text']
                                    reply_markup = [[{'text': '-0.1', 'callback_data': f'{user_id}@0.1'}, {'text': '-0.5', 'callback_data': f'{user_id}@0.5'}, {'text': '-1', 'callback_data': f'{user_id}@1'}, {'text': '-2', 'callback_data': f'{user_id}@2'}, {'text': '-5', 'callback_data': f'{user_id}@5'}, {'text': '-10', 'callback_data': f'{user_id}@10'}]]
                                    send_inline(BOT_TOKEN, user_id, f"{idio['Balance'][idi]}:  $ " + str(round(user_data['coins'], 2)), reply_markup)
                                    if user_data['childs'] != None:
                                        for s in user_data['childs']:
                                            child_data = open_data(s)
                                            reply_markup = [[{'text':  '+0.1', 'callback_data': f'{s}#0.1'}, {'text':  '+0.5', 'callback_data': f'{s}#0.5'}, {'text': '+1', 'callback_data': f'{s}#1'}, {'text': '+2', 'callback_data': f'{s}#2'}, {'text': '+5', 'callback_data': f'{s}#5'}, {'text': '+10', 'callback_data': f'{s}#10'}]]
                                            send_inline(BOT_TOKEN, user_id, config['credentials']['usernames'][s]['name'] + " (" + str(s) + f")\n{idio['Balance'][idi]} :  $ " + str(round(child_data['coins'], 2)), reply_markup) # sends user balance

                                elif i['message']['text'] == '/mathematics': # <<====
                                    target_score = user_data['miniapps']['mathematics']['target_score']
                                    if user_data['miniapps']['mathematics']['current_score'] >= target_score:
                                        send_message(BOT_TOKEN, user_id, '🎉 🎉 🎉 🎉 🎉')
                                    else:
                                        try:
                                            user_data, question = random_question(user_data, idio, idi)
                                        except:
                                            question = idio['No mathematic operations selected'][idi]
                                        user_data['location'] = i['message']['text']
                                        send_message(BOT_TOKEN, user_id, question)

                                elif i['message']['text'] == '/listen_write': # <<====
                                    reply_markup = lw_reply_markup(user_data)
                                    user_data['location'] = i['message']['text']
                                    send_inline(BOT_TOKEN, user_id, f"=====> {idio['List of listen-write'][idi]} <=====", reply_markup)

                                elif i['message']['text'] == '/read_speak': # <<====
                                    reply_markup = rs_reply_markup(user_data)
                                    user_data['location'] = i['message']['text']
                                    send_inline(BOT_TOKEN, user_id, f"=====> {idio['List of read-speak'][idi]} <=====", reply_markup)

                                elif i['message']['text'] == '/settings': # <<====
                                    send_settings_keyboard(BOT_TOKEN, user_id, idio['Settings'][idi])
                                
                                elif i['message']['text'] == '/teacher': # <<====
                                    send_teacher_keyboard(BOT_TOKEN, user_id, idio['Select homework'][idi])
                                
                                elif i['message']['text'] == '/text2image': # <<====
                                    user_data['location'] = i['message']['text']
                                    send_message(BOT_TOKEN, user_id, idio['Insert prompt in english'][idi])

                                elif i['message']['text'] == '/image2text': # <<====
                                    user_data['location'] = i['message']['text']
                                    send_message(BOT_TOKEN, user_id, idio['Select images to process'][idi])

                                elif i['message']['text'] == '/voice2text': # <<====
                                    user_data['location'] = i['message']['text']
                                    send_message(BOT_TOKEN, user_id, idio['Send audio/video to transcribe or generate subtitles (25Mb limit)'][idi])
                                
                                elif i['message']['text'] == '/walkie_talkie': # <<====
                                    user_data['location'] = i['message']['text']

                                    if user_data['miniapps']['walkie_talkie']['contacts'] == {}:
                                        send_message(BOT_TOKEN, user_id, idio['Insert a new user ID to add to your contacts'][idi])

                                    else:
                                        reply_markup = [[{'text': idio['Add contact'][idi], 'callback_data': "add#"}, {'text': idio['Remove contact'][idi], 'callback_data': "remove#"}]]
                                        for l in list(user_data['miniapps']['walkie_talkie']['contacts'].keys()):
                                            reply_markup.append([{'text': f"{l} - {config['credentials']['usernames'][l]['name']}", 'callback_data': f"{l}#"}]) # 123456 - carl

                                        text = f"{idio['Send voice to'][idi]}\n {l} - {config['credentials']['usernames'][l]['name']}\n {idio['or select other contact'][idi]}"
                                        send_inline(BOT_TOKEN, user_id, text, reply_markup)

                                elif i['message']['text'] == '/youtube': # <<====
                                    user_data['location'] = i['message']['text']
                                    send_message(BOT_TOKEN, user_id, idio['Send the YouTube Link'][idi])

                                # If there is an entity (url), try to request youtube
                                elif user_data['location'] == '/youtube': # <<====
                                    start_time = time.time()

                                    try:
                                        yt = YouTube(i['message']['text'])
                                        user_data['miniapps']['youtube']['request']['fname'] = yt.title

                                        video = {}
                                        audio = []
                                        for stream in yt.streams:
                                            if stream.type == 'video':
                                                res = stream.resolution
                                                fps = stream.fps
                                                if res not in video:
                                                    video[res] = []
                                                video[res].append(fps)
                                            elif stream.type == 'audio':
                                                abr = stream.abr
                                                audio.append(abr)

                                        # Remove duplicates from video dictionary values
                                        for key in video:
                                            video[key] = list(set(video[key]))

                                        video['audio'] = audio

                                        user_data['miniapps']['youtube']['file']['task'] = video
                                        user_data['miniapps']['youtube']['request']['url'] = i['message']['text']
                                        
                                        reply_markup = []
                                        for l in sorted(list(user_data['miniapps']['youtube']['file']['task'].keys())):
                                            reply_markup.append([{'text': l, 'callback_data': f"{user_id}*{l}"}])

                                        send_inline(BOT_TOKEN, user_id, idio['Select the file type'][idi], reply_markup)
                                    except:
                                        user_data['location'] = 0
                                        send_message(BOT_TOKEN, user_id, idio["The video/audio can not be downloaded"][idi])

                                    add_to_data(user_id, '/youtube', start_time)

                            elif 'voice' in i['message']:

                                if user_data['location'] == '/read_speak':
                                    if user_data['miniapps']['read-speak']['homework'] != None: # <<====
                                        if not 'forward_from' in i['message']:
                                            if i['message']['voice']['duration'] < 16:
                                                with open('extra.yaml', 'r') as file:
                                                    extra = yaml.safe_load(file)
                                                    extra['short'].append(f"{user_id}|read_speak|{i['message']['voice']['file_id']}|{i['message']['message_id']}") # send also reply
                                                with open('extra.yaml', 'w') as file:
                                                    yaml.dump(extra, file)
                                            else:
                                                send_message(BOT_TOKEN, user_id, idio['Audio lenght limit is 15 seconds'][idi])

                                elif user_data['location'] == '/voice2text':
                                    if i['message']['voice']['file_size'] < 25*1024*1024:
                                        resp_media = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getFile?file_id={i['message']['voice']['file_id']}")
                                        response_media = resp_media.json()
                                        url_media = f'https://api.telegram.org/file/bot{BOT_TOKEN}/' + response_media['result']["file_path"] # https://api.telegram.org/file/bot<token>/<file_path>
                                        response = requests.get(url_media)
                                        response.raise_for_status()

                                        if not os.path.exists(f"miniapps/voice2text/{user_id}"):
                                            os.mkdir(f"miniapps/voice2text/{user_id}")

                                        with open(f"miniapps/voice2text/{user_id}/{user_id}.oga", 'wb') as f:
                                            f.write(response.content)
                                    
                                        reply_markup = [[]]
                                        reply_markup[0].append({'text': 'Whisper-tiny', 'callback_data': 'whisper-tiny'})
                                        reply_markup[0].append({'text': 'Whisper-base', 'callback_data': 'whisper-base'})
                                        reply_markup[0].append({'text': 'Openai', 'callback_data': 'openai-large'})
                                        send_inline(BOT_TOKEN, user_id, idio['Whisper size (the larger, the slower)'][idi], reply_markup)

                                elif user_data['location'] == '/walkie_talkie':
                                    if i['message']['voice']['duration'] < 31:
                                        with open('extra.yaml', 'r') as file:
                                            extra = yaml.safe_load(file)
                                            extra['short'].append(f"{user_id}|walkie_talkie|{i['message']['voice']['file_id']}|{i['message']['message_id']}|{user_data['miniapps']['walkie_talkie']['default']}") # user_id|walkie_talkie|file_id|message_id|contact
                                        with open('extra.yaml', 'w') as file:
                                            yaml.dump(extra, file)
                                    else:
                                        send_message(BOT_TOKEN, user_id, idio['Audio lenght limit is 15 seconds'][idi])

                            elif 'photo' in i['message']:

                                if user_data['location'] == '/image2text':
                                    with open('extra.yaml', 'r') as file:
                                        file_id = i['message']['photo'][-1]['file_id']
                                        resp_media = requests.get(f'https://api.telegram.org/bot{BOT_TOKEN}/getFile?file_id={file_id}') # File ID
                                        response_media = resp_media.json()
                                        url_media = f'https://api.telegram.org/file/bot{BOT_TOKEN}/' + response_media['result']["file_path"]
                                        response = requests.get(url_media)
                                        with open('miniapps/languages/images/'+user_id, 'wb') as file:
                                            file.write(response.content)

                                        with open('extra.yaml', 'r') as extra_file:
                                            extra = yaml.safe_load(extra_file)
                                        extra['short'].append(f"{user_id}|img2text")

                                    with open('extra.yaml', 'w') as file:
                                        yaml.dump(extra, file)

                            elif 'text' in i['message']:

                                if user_data['location'] == '/walkie_talkie':
                                    if i['message']['text'] in config['credentials']['usernames']:
                                        # select language
                                        lang_list = ['ar', 'az', 'ca', 'zh-CN', 'cs', 'da', 'nl', 'en', 'eo', 'fi', 'fr', 'de', 'el', 'he', 'hi', 'hu', 'id', 'ga', 'it', 'ja', 'ko', 'fa', 'pl', 'pt', 'ru', 'sk', 'es', 'sv', 'tr', 'uk']
                                        lang_names = ['Arabic','Azerbaijani','Catalan','Chinese (Simplified)','Czech','Danish','Dutch','English','Esperanto','Finnish','French','German','Greek','Hebrew','Hindi','Hungarian','Indonesian','Irish','Italian','Japanese','Korean','Persian','Polish','Portuguese','Russian','Slovak','Spanish','Swedish','Turkish','Ukrainian']

                                        reply_markup = []
                                        row = []
                                        for j in range(len(lang_list)):
                                            row.append({'text': lang_names[j], 'callback_data': f"lang#{lang_list[j]}#{i['message']['text']}"})
                                            if (j+1) % 5 == 0:
                                                reply_markup.append(row)
                                                row = []
                                        if row:
                                            reply_markup.append(row)

                                        text = f"{idio['Select language to translate your voice messages to'][idi]}:\n {config['credentials']['usernames'][i['message']['text']]['name']} - {i['message']['text']}"
                                        send_inline(BOT_TOKEN, user_id, text, reply_markup)

                                    else:
                                        text = idio['This user has not registered yet, ask her/him to register'][idi]
                                        send_message(BOT_TOKEN, user_id, text)

                                elif user_data['location'] == '/text2image': # <<====
                                    reply_markup = [[]]
                                    for m in range(5):
                                        reply_markup[0].append({'text': str(m+1), 'callback_data': f"{i['message']['text']}+{m+1}"})
                                    send_inline(BOT_TOKEN, user_id, idio['Select number or images'][idi], reply_markup)

                                elif user_data['location'] == '/mathematics': # <<====
                                    try: # try to make a calculation
                                        user_data, message = mathematics(user_data, float(i['message']['text']), idio, idi)
                                        send_message(BOT_TOKEN, user_id, message)
                                    except:
                                        pass
                                
                                elif user_data['location'] == '/listen_write': # <<====
                                    user_data, message = listen_write(user_data, i['message']['text'], idio, idi)
                                    if '🎉' in message:
                                        send_message(BOT_TOKEN, user_id, message)
                                    else:
                                        answer, audio_file = text2voice(config, user_data, 'listen-write')
                                        user_data['miniapps']['listen-write']['answer'] = clean_text(answer)
                                        if audio_file == '#error':
                                            send_message(BOT_TOKEN, user_id, idio['Error synthesizing audio'][idi]+" ❌\n\n")
                                        else:
                                            send_audio(BOT_TOKEN, user_id, message, audio_file)

                                elif user_data['location'] == '/change_name':
                                    config['credentials']['usernames'][user_id]['name'] = i['message']['text']
                                    update_config(config, 'config.yaml')
                                    send_message(BOT_TOKEN, user_id, idio['Name changed!'][idi])

                                elif user_data['location'] == '/password':
                                    config['credentials']['usernames'][user_id]['password'] = stauth.Hasher([i['message']['text']]).generate()[0]
                                    update_config(config, 'config.yaml')
                                    send_message(BOT_TOKEN, user_id, f"{idio['Password changed!'][idi]}\n{idio['Your ID'][idi]}: {user_id}\n{idio['Access to your console here'][idi]}: {config['admin']['url']}")

                                elif user_data['location'] == '/add_member':
                                    send_message(BOT_TOKEN, user_id, idio["Request sent. Accept from the other device"][idi])
                                    reply_markup = [[{'text': '✔️', 'callback_data': f"{user_id}&{1}"}]]
                                    send_inline(BOT_TOKEN, i['message']['text'], f"{idio['Request from'][idi]} {user_id} {idio['to manage your account, Respond yes to accept'][idi]}", reply_markup)

                        elif 'callback_query' in i:

                            # Walkie talkie
                            if "#" in i['callback_query']['data']: # add# or 123456# 
                                cb_data = i['callback_query']['data'].split("#")

                                if 'lang' in cb_data: # lang#lang_code#contact
                                    user_data['miniapps']['walkie_talkie']['contacts'][cb_data[2]] = cb_data[1]
                                    user_data['miniapps']['walkie_talkie']['default'] = cb_data[2]

                                    reply_markup = [[{'text': idio['Add contact'][idi], 'callback_data': "add#"}, {'text': idio['Remove contact'][idi], 'callback_data': "remove#"}]]
                                    for l in list(user_data['miniapps']['walkie_talkie']['contacts'].keys()):
                                        reply_markup.append([{'text': f"{config['credentials']['usernames'][l]['name']} - {l}", 'callback_data': f"{l}#"}]) # carl - 123456
                                    text = f"{idio['Contact added'][idi]}!\n{idio['Send voice to'][idi]}\n {config['credentials']['usernames'][l]['name']} - {l}\n {idio['or select other contact'][idi]}"
                                    send_inline(BOT_TOKEN, user_id, text, reply_markup)

                                elif 'add' in cb_data:
                                    send_message(BOT_TOKEN, user_id, idio['Insert a new user ID to add to your contacts'][idi])

                                elif 'remove' in cb_data: # select contact to remove
                                    reply_markup = []
                                    for l in list(user_data['miniapps']['walkie_talkie']['contacts'].keys()):
                                        reply_markup.append([{'text': f"{l} - {config['credentials']['usernames'][l]['name']}", 'callback_data': f"{l}#delete"}]) # 123456 - carl

                                    text = f"{idio['Select contact to remove'][idi]}"
                                    send_inline(BOT_TOKEN, user_id, text, reply_markup)
                                
                                elif 'delete' in cb_data: # confirm detele contact
                                    user_data['miniapps']['walkie_talkie']['contacts'].remove(cb_data[1])
                                    if user_data['miniapps']['walkie_talkie']['default'] == cb_data[1]:
                                        if user_data['miniapps']['walkie_talkie']['contacts'] == []:
                                            send_message(BOT_TOKEN, user_id, idio['Insert a new user ID to add to your contacts'][idi])
                                        else:
                                            user_data['miniapps']['walkie_talkie']['default'] = user_data['miniapps']['walkie_talkie']['contacts'][0]
                                    else:
                                        reply_markup = [[{'text': idio['Add contact'][idi], 'callback_data': "add#"}, {'text': idio['Remove contact'][idi], 'callback_data': "remove#"}]]
                                        for l in list(user_data['miniapps']['walkie_talkie']['contacts'].keys()):
                                            reply_markup.append([{'text': f"{l} - {config['credentials']['usernames'][l]['name']}", 'callback_data': f"{l}#"}]) # 123456 - carl

                                        text = f"{idio['Contact deleted'][idi]}!\n{idio['Send voice to'][idi]}\n {config['credentials']['usernames'][l]['name']} - {l}\n {idio['or select other contact'][idi]}"
                                        send_inline(BOT_TOKEN, user_id, text, reply_markup)

                                else: # select a contact
                                    user_data['miniapps']['walkie_talkie']['default'] = cb_data[0]

                                    reply_markup = [[{'text': idio['Add contact'][idi], 'callback_data': "add#"}, {'text': idio['Remove contact'][idi], 'callback_data': "remove#"}]]
                                    for l in list(user_data['miniapps']['walkie_talkie']['contacts'].keys()):
                                        reply_markup.append([{'text': f"{l} - {config['credentials']['usernames'][l]['name']}", 'callback_data': f"{l}#"}]) # 123456 - carl

                                    default_contact = user_data['miniapps']['walkie_talkie']['default']
                                    text = f"{idio['Send voice to'][idi]}\n {config['credentials']['usernames'][default_contact]['name']} - {default_contact}\n {idio['or select other contact'][idi]}"
                                    send_inline(BOT_TOKEN, user_id, text, reply_markup)

                            # Voice2text
                            elif "-" in i['callback_query']['data']: # whisper-tiny
                                cb_data = i['callback_query']['data'].split("-")

                                if cb_data[0] == 'openai':
                                    send_message(BOT_TOKEN, user_id, "Not developed yet")
                                elif cb_data[0] == 'whisper':
                                    with open('extra.yaml', 'r') as file:
                                        extra = yaml.safe_load(file)
                                    extra['large'].append(f"{user_id}|voice2text|{cb_data[0]}|{cb_data[1]}") # user_id|voice2text|whisper|tiny

                                    with open('extra.yaml', 'w') as file:
                                        yaml.dump(extra, file)

                            # Youtube
                            elif "*" in i['callback_query']['data']: # youtube
                                cb_data = i['callback_query']['data'].split("*")

                                # 1. the resolution/audio has been chosen, the bitrate will be sent
                                if len(cb_data) == 2:
                                    user_data['miniapps']['youtube']['file']['resolution'] = cb_data[1]
                                    reply_markup = []
                                    for m in sorted(user_data['miniapps']['youtube']['file']['task']['audio']):
                                        reply_markup.append([{'text': m, 'callback_data': f"{user_id}*{cb_data[1]}*{m}"}])
                                    send_inline(BOT_TOKEN, user_id, idio["Select audio bitrate"][idi], reply_markup)

                                # 2. the audio bitrate has been chosen
                                elif len(cb_data) == 3:
                                    user_data['miniapps']['youtube']['file']['bitrate'] = cb_data[2]

                                    # If is audio
                                    if user_data['miniapps']['youtube']['file']['resolution'] == 'audio':
                                        with open('extra.yaml', 'r') as file:
                                            extra = yaml.safe_load(file)
                                            extra['large'].append(f"{user_id}|youtube|audio|{clean_text(user_data['miniapps']['youtube']['request']['fname'])}|{i['callback_query']['data']}")
                                        with open('extra.yaml', 'w') as file:
                                            yaml.dump(extra, file)

                                    # If is video
                                    else:
                                        # If there is only one framerate
                                        if len(user_data['miniapps']['youtube']['file']['task'][cb_data[1]]) == 1:
                                            with open('extra.yaml', 'r') as file:
                                                extra = yaml.safe_load(file)
                                                extra['large'].append(f"{user_id}|youtube|video|{clean_text(user_data['miniapps']['youtube']['request']['fname'])}|{i['callback_query']['data']}")
                                            with open('extra.yaml', 'w') as file:
                                                yaml.dump(extra, file)
                                        # If there are several framerates, send fps inline
                                        else:
                                            reply_markup = []
                                            for n in sorted(user_data['miniapps']['youtube']['file']['task'][cb_data[1]]):
                                                reply_markup.append([{'text': n, 'callback_data': f"{user_id}*{cb_data[1]}*{cb_data[2]}*{n}"}])
                                            send_inline(BOT_TOKEN, user_id, idio["Select framerate"][idi], reply_markup)

                                # 3. download with 3 parameters: resolution, bitrate, framerate
                                elif len(cb_data) == 4:
                                    with open('extra.yaml', 'r') as file:
                                        extra = yaml.safe_load(file)
                                        extra['large'].append(f"{user_id}|youtube|video|{clean_text(user_data['miniapps']['youtube']['request']['fname'])}|{i['callback_query']['data']}")
                                    with open('extra.yaml', 'w') as file:
                                        yaml.dump(extra, file)

                            # Generate image
                            elif "+" in i['callback_query']['data']: # text to image
                                start_time = time.time()
                                try:
                                    cb_data = i['callback_query']['data'].split("+")
                                    lex = Lexica(query=cb_data[0]).images()
                                    image_urls = random.sample(lex, int(cb_data[1]))
                                    send_mediagroup(BOT_TOKEN, user_id, image_urls)
                                except:
                                    send_message(BOT_TOKEN, user_id, idio['Error generating image'][idi])
                                add_to_data(user_id, '/text2image', start_time)

                            # Change language
                            elif "!" in i['callback_query']['data']: # change language
                                cb_data = i['callback_query']['data'].split("!")
                                user_data['idiom'] = cb_data[0]
                                send_message(BOT_TOKEN, user_id, f"{idio['Current language'][cb_data[0]]}: {cb_data[0]}")

                            # sum coins
                            elif "#" in i['callback_query']['data']:
                                cb_data = i['callback_query']['data'].split("#")
                                child_data = open_data(cb_data[0])
                                child_data['coins'] = child_data['coins'] + float(cb_data[1])
                                update_config(child_data, 'users/' + str(cb_data[0]) + '.yaml')
                                if len(user_data['childs']) > 0:
                                    for s in list(user_data['childs'].keys()):
                                        reply_markup = [[{'text': '+0.1', 'callback_data': f'{s}#0.1'}, {'text': '+0.5', 'callback_data': f'{s}#0.5'}, {'text': '+1', 'callback_data': f'{s}#1'}, {'text': '+2', 'callback_data': f'{s}#2'}, {'text': '+5', 'callback_data': f'{s}#5'}, {'text': '+10', 'callback_data': f'{s}#10'}]]
                                        send_inline(BOT_TOKEN, user_id, config['credentials']['usernames'][s]['name'] + " (" + str(s) + ")\nBalance :  $ " + str(round(user_data['coins'], 2)), reply_markup) # sends user balance

                            # rest coins
                            elif "@" in i['callback_query']['data']:
                                cb_data = i['callback_query']['data'].split("@")
                                user_data['coins'] = user_data['coins'] - float(cb_data[1])
                                reply_markup = [[{'text': '-0.1', 'callback_data': f'{user_id}@0.1'}, {'text': '-0.5', 'callback_data': f'{user_id}@0.5'}, {'text': '-1', 'callback_data': f'{user_id}@1'}, {'text': '-2', 'callback_data': f'{user_id}@2'}, {'text': '-5', 'callback_data': f'{user_id}@5'}, {'text': '-10', 'callback_data': f'{user_id}@10'}]]
                                send_inline(BOT_TOKEN, user_id, "Balance: $ " + str(round(user_data['coins'], 2)), reply_markup)

                            # If is a read-speak homework
                            elif "$" in i['callback_query']['data']:
                                user_data['miniapps']['read-speak']['current_request'] = i['callback_query']['data']
                                message, audio_file = text2voice(config, user_data, 'read-speak')
                                if audio_file == '#error':
                                    send_message(BOT_TOKEN, user_id, "Error synthesizing audio ❌\n\n"+message)
                                else:
                                    send_audio(BOT_TOKEN, user_id, message, audio_file)

                            # If is a listen-write homework
                            elif "%" in i['callback_query']['data']:
                                user_data['miniapps']['listen-write']['current_request'] = i['callback_query']['data']
                                answer, audio_file = text2voice(config, user_data, 'listen-write')
                                user_data['miniapps']['listen-write']['answer'] = clean_text(answer)
                                if audio_file == '#error':
                                    send_message(BOT_TOKEN, user_id, "Error synthesizing audio ❌\n\n")
                                else:
                                    send_audio(BOT_TOKEN, user_id, '', audio_file)   

                            elif "^" in i['callback_query']['data']:
                                cb_data = i['callback_query']['data'].split("^")
                                vocabulary = user_data['miniapps']['listen-write']['homework'][cb_data[0]].keys()
                                vocabulary = ', '.join(vocabulary)
                                send_message(BOT_TOKEN, user_id, vocabulary)

                            # If add child
                            elif "&" in i['callback_query']['data']: # user_id&1
                                cb_data = i['callback_query']['data'].split("&")

                                if cb_data[1] == '1':
                                    manager_id = open_data(cb_data[0])
                                    manager_id['childs'].append(user_id)

                                    if user_id != cb_data[0]:
                                        update_config(manager_id, 'users/' + cb_data[0] + '.yaml')
                                    else:
                                        user_data = manager_id
                                        
                                    send_message(BOT_TOKEN, cb_data[0], f"{user_id} {idio['addded succesfully!'][idi]}")
                                elif cb_data[1] == '0':
                                    user_data['childs'].remove(cb_data[0])
                                    send_message(BOT_TOKEN, user_id, f"{user_id} {idio['removed succesfully!'][idi]}")

                    update_config(user_data, 'users/' + user_id + '.yaml')
                config['telegram']['offset'] = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates?offset={i['update_id'] + 1}"
                update_config(config, 'config.yaml')
                gc.collect()

    except Exception as e:
        with open('log.txt', 'a') as f:
            import sys
            f.write(f"{datetime.datetime.now()}:\n run_telegram - line: {sys.exc_info()[-1].tb_lineno}\n{e}")
            try:
                f.write(f"{user_id} - {i['message']['text']}\n")
            except:
                try:
                    f.write(f"{user_id} - {i['message']['voice']}\n")
                except:
                    try:
                        f.write(f"{user_id} - {i['message']['photo']}\n")
                    except:
                        try:
                            f.write(f"{user_id} - {i['callback_query']['data']}\n")
                        except:
                            pass
        time.sleep(3)


if __name__ == '__main__':

    # Set commands
    with open('config.yaml', 'r') as file:
        BOT_TOKEN = yaml.safe_load(file)['telegram']['token']
    set_commands(BOT_TOKEN)

    while True:
        main()
