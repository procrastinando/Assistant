import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from pytube import YouTube
import subprocess
import os
import gc
import time

from run_telegram import open_data, update_config, send_message, add_to_data
from miniapps.languages import clean_text

def download_button(file_path, label, file_name, mime):
    with open(file_path, "rb") as file:
        btn = st.download_button(
                label=label,
                data=file,
                file_name=file_name,
                mime=mime
            )

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

    st.header(idio['YouTube downloader assistant'][idi])

    #if True:
    try:
        url = st.text_input(idio['Insert YouTube URL'][idi], user_data['miniapps']['youtube']['request']['url'])

        if st.button(f"⏩ {idio['Analyze URL'][idi]}"):
            start_time = time.time()
            try:
                yt = YouTube(url)
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
                user_data['miniapps']['youtube']['request']['url'] = url
                update_config(st.session_state["username"], 'users/'+st.session_state["username"]+'.yaml')

            except:
                st.error(idio['The video/audio can not be downloaded'][idi])
            
            add_to_data(user_id, '/youtube', start_time)

        # Make a download settings list
        if len(user_data['miniapps']['youtube']['file']) > 0:
            st.write(user_data['miniapps']['youtube']['request']['fname'])

            ftypes = sorted(list(user_data['miniapps']['youtube']['file']['task'].keys()))
            try:
                ftype = st.selectbox(idio['Select file type'][idi], ftypes, index=ftypes.index(user_data['miniapps']['youtube']['file']['resolution']))
            except:
                ftype = st.selectbox(idio['Select file type'][idi], ftypes)
            abitrates = sorted(user_data['miniapps']['youtube']['file']['task']['audio'])
            try:
                abitrate = st.selectbox(idio['Select file type'][idi], abitrates, index=abitrates.index(user_data['miniapps']['youtube']['file']['bitrate']))
            except:
                abitrate = st.selectbox(idio['Select file type'][idi], abitrates)

            if ftype != 'audio':
                if len(user_data['miniapps']['youtube']['file']['task'][ftype]) == 1:
                    if st.button(f"⏩ {idio['Select file settings'][idi]}"):
                        start_time = time.time()
                        yt = YouTube(url).streams
                        yt.filter(type="video", res=ftype)[0].download(output_path='miniapps/youtube/', filename=st.session_state["username"]+'v')
                        yt.filter(type="audio", abr=abitrate)[0].download(output_path='miniapps/youtube/', filename=st.session_state["username"]+'a')
                        subprocess.run(['ffmpeg', '-loglevel', 'quiet', '-i', 'miniapps/youtube/'+st.session_state["username"]+'v', '-i', 'miniapps/youtube/'+st.session_state["username"]+'a', '-c:v', 'copy', '-c:a', 'libmp3lame', '-b:a',  abitrate.split('b')[0], '-strict', '-2', 'miniapps/youtube/'+clean_text(user_data['miniapps']['youtube']['request']['fname'])+'.mp4', '-y'])
                        
                        user_data['miniapps']['youtube']['file']['resolution'] = ftype
                        user_data['miniapps']['youtube']['file']['bitrate'] = abitrate
                        update_config(user_data, 'users/'+st.session_state["username"]+'.yaml')
                        add_to_data(st.session_state["username"], '/youtube', start_time)
                else:
                    vfpss = sorted(user_data['miniapps']['youtube']['file']['task'][ftype])
                    try:
                        vfps = st.selectbox(idio['Select framerate'][idi], vfpss, index=vfpss.index(user_data['miniapps']['youtube']['file']['framerate']))
                    except:
                        vfps = st.selectbox(idio['Select framerate'][idi], vfpss)
                    if st.button(f"⏩ {idio['Select file settings'][idi]}"):
                        start_time = time.time()
                        yt = YouTube(url).streams
                        yt.filter(type="video", res=ftype, fps=int(vfps))[0].download(output_path='miniapps/youtube/', filename=st.session_state["username"]+'v')
                        yt.filter(type="audio", abr=abitrate)[0].download(output_path='miniapps/youtube/', filename=st.session_state["username"]+'a')
                        subprocess.run(['ffmpeg', '-loglevel', 'quiet', '-i', 'miniapps/youtube/'+st.session_state["username"]+'v', '-i', 'miniapps/youtube/'+st.session_state["username"]+'a', '-c:v', 'copy', '-c:a', 'libmp3lame', '-b:a',  abitrate.split('b')[0], '-strict', '-2', 'miniapps/youtube/'+clean_text(user_data['miniapps']['youtube']['request']['fname'])+'.mp4', '-y'])
                        
                        user_data['miniapps']['youtube']['file']['resolution'] = ftype
                        user_data['miniapps']['youtube']['file']['bitrate'] = abitrate
                        user_data['miniapps']['youtube']['file']['framerate'] = vfps
                        update_config(user_data, 'users/'+st.session_state["username"]+'.yaml')
                        add_to_data(st.session_state["username"], '/youtube', start_time)
            else:
                if st.button(f"⏩ {idio['Select file settings'][idi]}"):
                    start_time = time.time()
                    info_placeholder = st.empty()
                    info_placeholder.info(idio['Transcribing'][idi])

                    yt = YouTube(url).streams
                    yt.filter(type="audio", abr=abitrate)[0].download(output_path='miniapps/youtube/', filename=st.session_state["username"]+'a')
                    subprocess.run(['ffmpeg', '-loglevel', 'quiet', '-i', 'miniapps/youtube/'+st.session_state["username"]+'a', '-c:a', 'libmp3lame', '-b:a',  abitrate.split('b')[0], '-strict', '-2', 'miniapps/youtube/'+clean_text(user_data['miniapps']['youtube']['request']['fname'])+'.mp3', '-y'])
                    
                    user_data['miniapps']['youtube']['file']['resolution'] = ftype
                    user_data['miniapps']['youtube']['file']['bitrate'] = abitrate
                    update_config(user_data, 'users/'+st.session_state["username"]+'.yaml')

                    info_placeholder.info(idio['Finished!'][idi])
                    add_to_data(st.session_state["username"], '/youtube', start_time)

            gc.collect()

        # Create a download button
        try:
            if user_data['miniapps']['youtube']['file']['resolution'] != 'audio':
                if os.path.exists('miniapps/youtube/'+clean_text(user_data['miniapps']['youtube']['request']['fname'])+'.mp4'):
                    download_button('miniapps/youtube/'+clean_text(user_data['miniapps']['youtube']['request']['fname'])+'.mp4', f"✅ {idio['Download'][idi]}", f"{user_data['miniapps']['youtube']['request']['fname']}.{'mp4'}", "video/mp4")
                    os.remove('miniapps/youtube/'+st.session_state["username"]+'a')
                    os.remove('miniapps/youtube/'+st.session_state["username"]+'v')
            else:
                if os.path.exists('miniapps/youtube/'+clean_text(user_data['miniapps']['youtube']['request']['fname'])+'.mp3'):
                    download_button('miniapps/youtube/'+clean_text(user_data['miniapps']['youtube']['request']['fname'])+'.mp3', idio['Download'][idi], f"{user_data['miniapps']['youtube']['request']['fname']}.{'mp3'}", "audio/mpeg")
                    os.remove('miniapps/youtube/'+st.session_state["username"]+'v')
        except:
            pass

    except ValueError as e:
        with open('config.yaml', 'r') as file:
            BOT_TOKEN = yaml.safe_load(file)['telegram']['token']
        send_message(BOT_TOKEN, '649792299', e)

if __name__ == '__main__':
    st.set_page_config(
        page_title="Youtube downloader",
        page_icon="📺",
    )

    main()
