import yaml
import subprocess

try:
    # Update basic configuration
    with open('config.yaml', 'r') as file:
        config = yaml.safe_load(file)

    # Run commands
    commands = [['python', 'run_telegram.py'], ['python', 'run_stats.py']]

    for i in range(int(config['engines']['large'])):
        commands.append(['python', 'run_extra.py', 'large'])

    for i in range(int(config['engines']['short'])):
        commands.append(['python', 'run_extra.py', 'short'])
        
    for command in commands:
        subprocess.Popen(command)

except:
    time.sleep(2)
    print("Engines not running, please complete initial setup")
