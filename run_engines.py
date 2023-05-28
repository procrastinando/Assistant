import yaml
import subprocess
import sys

telegram_token = sys.argv[1]
streamlit_url = sys.argv[2]
admin_id = sys.argv[3]
preauthorized_mail = sys.argv[4]

# Update basic configuration
with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)

config['telegram']['token'] = telegram_token
config['admin']['url'] = streamlit_url
config['admin']['id'] = admin_id
config['preauthorized']['emails'] = preauthorized_mail

with open('config.yaml', 'w') as file:
    yaml.dump(config, file)

# Run commands
commands = [['nohup', 'python', 'run_telegram.py']]

for i in range(int(config['engines']['large'])):
    commands.append(['python', 'run_extra.py', 'large'])

for i in range(int(config['engines']['short'])):
    commands.append(['python', 'run_extra.py', 'short'])
    
for command in commands:
    subprocess.Popen(command)
