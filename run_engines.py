import yaml
import subprocess

with open('config.yaml', 'r') as file:
    engines = yaml.safe_load(file)['engines']
commands = [['nohup', 'python', 'run_telegram.py']]

for i in range(int(engines['large'])):
    commands.append(['python', 'run_extra.py', 'large'])

for i in range(int(engines['short'])):
    commands.append(['python', 'run_extra.py', 'short'])
    
for command in commands:
    subprocess.Popen(command)
