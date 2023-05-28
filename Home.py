import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import os

from run_telegram import open_data, update_config

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

    with open('idiom.yaml') as file:
        idio = yaml.load(file, Loader=SafeLoader)
    idi = user_data['idiom']
    if idi not in list(idio['Add homework'].keys()):
        idi = 'en'
    
    authenticator.logout('Logout', 'sidebar')

    st.title(f'Welcome *{st.session_state["name"]}*')

    # --- Show users balance:
    st.subheader(f"1. {idio['Teacher assistant'][idi]}:")
    user_coins = round(user_data['coins'], 2)
    st.write(f"{idio['Your balance'][idi]}: $ {user_coins}")

    # --- Show child details
    with open('config.yaml', 'r') as file:
        usernames = yaml.safe_load(file)['credentials']['usernames']

    if user_data['childs'] != None:
        col1, col2 = st.columns([1, 1])
        with col1:
            i = st.selectbox(f"{idio['Child'][idi]}:", user_data['childs'])
            child_data = open_data(i)

        child_name = usernames[i]['name']
        child_data = open_data(i)

        child_coins = round(child_data['coins'], 2)
        st.subheader(f'✔️ {child_name}')
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
        languages_current = round(languages_current / languages_target * 100, 2)
        languages_coins = round(languages_target * child_data['miniapps']['read-speak']['target_score'] / child_data['miniapps']['read-speak']['ex_rate'], 2)
        st.write(f"{idio['Read and speak'][idi]}: {languages_current}%   ▶️   Expected coins: {languages_coins}")

        lw_current = 0
        number_lwhw = 0
        for l in list(child_data['miniapps']['listen-write']['homework_conf'].keys()):
            lw_current = lw_current + child_data['miniapps']['listen-write']['homework_conf'][l]['score']
            number_lwhw = number_lwhw + 1
        lw_current = lw_current / number_lwhw
        lw_current = round(lw_current / child_data['miniapps']['listen-write']['target_score'] * 100, 2)
        lw_coins = round(number_lwhw * child_data['miniapps']['listen-write']['target_score'] / child_data['miniapps']['listen-write']['ex_rate'], 2)
        st.write(f"{idio['Listen and write'][idi]}: {lw_current}%   ▶️   Expected coins: {lw_coins}")

        # --- Block to children
        blocked = st.multiselect(idio['Blocked commands for children'][idi], ['/settings', '/teacher', '/text2image', '/youtube', '/console', '/change_name', '/add_member', '/remove_member'], child_data['blocked'])
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
        if st.session_state["username"] == '649792299':

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
    with open('config.yaml', 'r') as file:
        config = yaml.safe_load(file)

    if len(config['credentials']['usernames']) < 1:
        st.title("Set up bot")
        
        tt = st.text_input("Set Telegram bot Token")
        au = st.text_input("Set App URL")
        ad = st.text_input("Set admin user ID (Telegram ID)")
        pe = st.text_input("Set preauthorized email")

        if st.button("Start"):
            config['telegram']['token'] = tt
            config['admin']['url'] = au
            config['admin']['id'] = ad
            config['preauthorized']['emails'] = pe

            with open('config.yaml', 'w') as file:
                yaml.dump(config, file)

            st.write("Please, restart the container")

    else:
        main()
