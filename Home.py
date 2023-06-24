import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import os
import random
import string
import pandas as pd

from dateutil.tz import tzlocal
from run_telegram import open_data, update_config

def plot_bar_chart(user_name, admin, idio, idi, key):
    jobs_type = ['/image2text', '/teacher', '/text2image', '/voice2text', '/walkie_talkie', '/youtube', 'others']
    jobs_type_filter = st.multiselect(idio['Filter requests'][idi], jobs_type, jobs_type, key=key)
    
    data = pd.read_csv('data.csv')
    if admin == False:
        data = pd.read_csv('data.csv')[data['User'] == int(user_name)]
    data = data[data['job_type'].isin(jobs_type_filter)]

    # Convert date column to datetime format
    data['date'] = pd.to_datetime(data['date'], format='%Y-%m-%d-%H:%M:%S')

    # Convert date column from UTC to local time zone
    local_tz = tzlocal()
    data['date'] = data['date'].dt.tz_localize('UTC').dt.tz_convert(local_tz)

    # Create a select slider for time range
    time_range = st.select_slider(
        idio['Recent activity'][idi],
        options=['Last 24 hours', 'Last 7 days', 'Last 30 days', 'Last 365 days'],
        key=key+2
    )

    # Get the maximum date in the data
    max_date = data['date'].max()

    # Filter data based on selected time range
    if time_range == 'Last 24 hours':
        data = data[data['date'] >= max_date - pd.Timedelta(days=1)]
    elif time_range == 'Last 7 days':
        data = data[data['date'] >= max_date - pd.Timedelta(days=7)]
    elif time_range == 'Last 30 days':
        data = data[data['date'] >= max_date - pd.Timedelta(days=30)]
    else:
        data = data[data['date'] >= max_date - pd.Timedelta(days=365)]

    # Group data by time period and job_type and sum the time column
    if time_range == 'Last 24 hours':
        data = data.groupby([pd.Grouper(key='date', freq='15min'), 'job_type'])['time'].sum().reset_index()
    elif time_range == 'Last 7 days':
        data = data.groupby([pd.Grouper(key='date', freq='1H'), 'job_type'])['time'].sum().reset_index()
    elif time_range == 'Last 30 days':
        data = data.groupby([pd.Grouper(key='date', freq='8H'), 'job_type'])['time'].sum().reset_index()
    else:
        data = data.groupby([pd.Grouper(key='date', freq='3D'), 'job_type'])['time'].sum().reset_index()

    # Pivot the data to create a stacked column chart
    data = data.pivot(index='date', columns='job_type', values='time')

    # Plot the chart using streamlit
    st.bar_chart(data)

def create_new_user(config, user_id, name, pa, tt, au, pe, ce, ck, cn):
    user_data = {
        'idiom': 'English',
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
            'image2text': ['en'],
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

    config['credentials']['usernames'][user_id] = {}
    config['credentials']['usernames'][user_id]['name'] = name
    config['credentials']['usernames'][user_id]['password'] = stauth.Hasher([pa]).generate()[0]

    config['telegram']['token'] = tt
    config['telegram']['offset'] = f"https://api.telegram.org/bot{tt}/getUpdates"
    config['admin']['url'] = au
    config['admin']['id'] = ad
    config['preauthorized']['emails'] = pe
    config['cookie']['expiry_days'] = int(ce)
    config['cookie']['key'] = ck
    config['cookie']['name'] = cn

    update_config(config, 'config.yaml')

def update_childs_credentials(user_id):
    user_data = open_data(user_id)
    for child_id in user_data['childs']:
        child_data = open_data(child_id)
        child_data['credentials']['openai'] = user_data['credentials']['openai']
        child_data['credentials']['azure'] = user_data['credentials']['azure']
        update_config(child_data, f"users/{child_id}.yaml")

def del_childs_credentials(user_id):
    user_data = open_data(user_id)
    for child_id in user_data['childs']:
        child_data = open_data(child_id)
        child_data['credentials'].pop('openai')
        child_data['credentials']['azure'] = {}
        update_config(child_data, f"users/{child_id}.yaml")

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

    st.markdown("[Register new user](https://t.me/ibarcenaBot)")

    if st.session_state["authentication_status"]:
        start(authenticator)
    elif st.session_state["authentication_status"] == False:
        st.error('User ID or password is incorrect')
    elif st.session_state["authentication_status"] == None:
        pass

def start(authenticator):
    user_data = open_data(st.session_state["username"])

    with open('config.yaml') as file:
        usernames = yaml.load(file, Loader=SafeLoader)['credentials']['usernames']
    with open('config.yaml') as file:
        admin_id = yaml.load(file, Loader=SafeLoader)['admin']['id']
    with open('idiom.yaml') as file:
        idio = yaml.load(file, Loader=SafeLoader)
    idi = user_data['idiom']
    if idi not in list(idio['Add homework'].keys()):
        idi = 'en'
    
    authenticator.logout('Logout', 'sidebar')

    st.title(f'Welcome *{st.session_state["name"]}*')

    # --- Show child details
    if user_data['childs'] != []:
        col1, col2 = st.columns([1, 1])
        with col1:
            i = st.selectbox(f"{idio['Child'][idi]}:", user_data['childs'])
            child_data = open_data(i)

        child_name = usernames[i]['name']
        child_data = open_data(i)

        child_coins = round(child_data['coins'], 2)
        st.subheader(f'✔️ {child_name}')

        ### --- Bar chart
        plot_bar_chart(i, False, idio, idi, 1)

        st.write(f"{idio['Balance'][idi]}: $ {child_coins}")

        mathematics_current = round(child_data['miniapps']['mathematics']['current_score'] / child_data['miniapps']['mathematics']['target_score'] * 100, 2)
        mathematics_coins = round(child_data['miniapps']['mathematics']['target_score'] / child_data['miniapps']['mathematics']['ex_rate'], 2)
        st.write(f"{idio['Mathematics'][idi]}: {mathematics_current}%   ▶️   Expected coins: {mathematics_coins}")

        languages_current = 0
        languages_target = 0
        for j in list(child_data['miniapps']['read-speak']['homework'].keys()):
            for k in list(child_data['miniapps']['read-speak']['homework'][j].keys()):
                if child_data['miniapps']['read-speak']['homework'][j][k]['score'] > child_data['miniapps']['read-speak']['target_score']:
                    languages_current = languages_current + 1
                languages_target = languages_target + 1
        try:
            languages_current = round(languages_current / languages_target * 100, 2)
        except:
            languages_current = '0.0%'
        languages_coins = round(languages_target * child_data['miniapps']['read-speak']['target_score'] / child_data['miniapps']['read-speak']['ex_rate'], 2)
        st.write(f"{idio['Read and speak'][idi]}: {languages_current}%   ▶️   Expected coins: {languages_coins}")

        lw_current = 0
        number_lwhw = 0
        for l in list(child_data['miniapps']['listen-write']['homework_conf'].keys()):
            lw_current = lw_current + child_data['miniapps']['listen-write']['homework_conf'][l]['score']
            number_lwhw = number_lwhw + 1
        try:
            lw_current = lw_current / number_lwhw
        except:
            lw_current = 0.0
        lw_current = round(lw_current / child_data['miniapps']['listen-write']['target_score'] * 100, 2)
        lw_coins = round(number_lwhw * child_data['miniapps']['listen-write']['target_score'] / child_data['miniapps']['listen-write']['ex_rate'], 2)
        st.write(f"{idio['Listen and write'][idi]}: {lw_current}%   ▶️   Expected coins: {lw_coins}")

        # --- Block to children
        blocked = st.multiselect(idio['Blocked commands for children'][idi], ['/settings', '/teacher', '/text2image', '/voice2text', '/youtube', '/console', '/change_name', '/add_member', '/remove_member'], child_data['blocked'])
        if st.button(idio['Update blocked commands list'][idi]):
            child_data['blocked'] = blocked
            update_config(child_data, f"users/{child_id}.yaml")

    else:
        st.write(idio['You have no childs, to add a child send /add_child using telegram'][idi])

    # --- Token
    st.divider()
    if st.checkbox(idio['Show advanced options'][idi], False):

        openai_token = st.text_input(idio['Openai token'][idi])
        azure_token = st.text_input(idio['Azure speechkey'][idi])
        azure_region = st.text_input(idio['Azure region'][idi])

        col1, col2 = st.columns(2)
        with col1:
            if st.button(f"{idio['Delete credentials'][idi]} ⚠️"):
                try:
                    user_data['azure'].pop('token')
                    user_data['azure'].pop('region')
                    user_data.pop('openai')
                    user_data['credentials']['share'] = share_credentials
                    update_config(user_data, 'users/'+st.session_state["username"]+'.yaml')
                except:
                    pass
        with col2:
            if st.button(idio['Save credentials'][idi]):
                user_data['openai'] = openai_token
                user_data['azure']['token'] = azure_token
                user_data['azure']['region'] = azure_region
                update_config(user_data, 'users/'+st.session_state["username"]+'.yaml')

        if user_data['childs'] != []:
            share_credentials = st.multiselect(idio['Share credentials with children'][idi], user_data['childs'], user_data['credentials']['share'])
            if st.button(idio['Update list'][idi]):
                for child_id in user_data['childs']:
                    if child_id in share_credentials:
                        user_data['credentials']['share'] = share_credentials
                        update_childs_credentials(st.session_state["username"])
                    else:
                        user_data['credentials']['share'] = share_credentials
                        del_childs_credentials(st.session_state["username"])
                update_config(user_data, 'users/'+st.session_state["username"]+'.yaml')

        # --- If admin
        if st.session_state["username"] == admin_id:

            with open('config.yaml', 'r') as file:
                config = yaml.safe_load(file)
        
            cola, colb = st.columns(2)
            with cola:
                large_engine = st.number_input(idio['Large process engine'][idi], min_value=1, max_value=10, value=config['engines']['large'])
            with colb:
                short_engine = st.number_input(idio['Short process engine'][idi], min_value=0, max_value=10, value=config['engines']['short'])

            if st.button(idio['Save'][idi]):
                config['engines']['large'] = large_engine
                config['engines']['short'] = short_engine
                update_config(config, 'config.yaml')
                st.write(idio['Please restart the container'][idi])

            ### --- Bar chart
            plot_bar_chart(st.session_state["username"], True, idio, idi, 2)

            # Show the resources usage
            st.divider()
            range_time = st.select_slider("Select time range", options=['1 hour', '1 day', '1 week', '1 month', '1 year'])
            range_time_dic = {'1 hour': 60, '1 day': 1440, '1 week': 10080, '1 month': 43200, '1 year': 525600}

            data = pd.read_csv('system_stats.csv', names=['Timestamp', 'CPU Usage', 'Memory Usage', 'Swap Usage', 'Disk Usage'])
            data['Timestamp'] = pd.to_datetime(data['Timestamp'])
            data.set_index('Timestamp', inplace=True)
            last_hour_data = data.tail(range_time_dic[range_time])
            st.line_chart(last_hour_data)

    # --- Delete data
    if st.button(f"{idio['Delete all my data'][idi]} ❗"):
        st.write(f"{idio['All data will be deteted, this operation can not be undone, are you sure'][idi]}?")
        if st.button(f"{idio['Confirm to delete'][idi]} ❗"):
            os.remove("users/" + st.session_state["name"] + ".yaml")
            with open('config.yaml') as file:
                config = yaml.load(file, Loader=SafeLoader)
            config['credenials']['usernames'].pop(st.session_state["name"])
            update_config(config, 'config.yaml')

if __name__ == '__main__':
    st.set_page_config(
        page_title="Assistant",
        page_icon="💡",
    )

    data = {
        'admin': {
            'id': None,
            'url': None
        },
        'cookie': {
            'expiry_days': None,
            'key': None,
            'name': None
        },
        'credentials': {
            'usernames': {}
        },
        'engines': {
            'large': 1,
            'short': 1
        },
        'preauthorized': {
            'emails': None
        },
        'telegram': {
            'offset': None,
            'token': None
        }
    }

    if not os.path.exists('config.yaml'):
        with open('config.yaml', 'w') as file:
            yaml.dump(data, file)
    if not os.path.exists('system_stats.yaml'):
        with open('system_stats.csv', 'w') as file:
            pass
    
    with open('config.yaml', 'r') as file:
        config = yaml.safe_load(file)

    if config['telegram']['token'] and config['admin']['id']:
        main()

    else: 
        st.title("Set up first boot")

        ad = st.text_input("Set admin user ID (Telegram ID)")
        pa = st.text_input("Set admin password (Telegram ID)")
        na = st.text_input("Set name")
        tt = st.text_input("Set Telegram bot Token")
        pe = st.text_input("Set preauthorized email")
        au = st.text_input("Set App URL", "http://localhost:8501/")
        ce = st.text_input("Set cookie expiry days", 30)
        ck = st.text_input("Set cookie key", ''.join(random.choice(string.ascii_lowercase) for _ in range(16)))
        cn = st.text_input("Set cookie name", ''.join(random.choice(string.ascii_lowercase) for _ in range(16)))

        if st.button("Start"):
            # Create basic directories
            for dir_path in ['miniapps/languages/images/', 'miniapps/voice2text/', 'miniapps/youtube/', 'miniapps/walkie_talkie/', 'users/']:
                if not os.path.exists(dir_path):
                    os.mkdir(dir_path)

            create_new_user(config, ad, na, pa, tt, au, pe, ce, ck, cn)
            st.write("Please, restart container")
