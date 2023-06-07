import streamlit as st
import psutil
import time
import pandas as pd

# Function to get current usage data
def get_usage_data():
    timestamp = pd.Timestamp.now()
    cpu_usage = psutil.cpu_percent()
    memory_usage = psutil.virtual_memory().percent
    disk_usage = psutil.disk_usage('/').percent
    swap_usage = psutil.swap_memory().percent
    return [timestamp, cpu_usage, memory_usage, swap_usage, disk_usage]

# Save usage data to CSV file every 5 minutes
while True:
    usage_data = get_usage_data()
    with open('system_stats.csv', 'a') as f:
        f.write(f'{usage_data[0]},{usage_data[1]},{usage_data[2]},{usage_data[3]},{usage_data[4]}\n')
    time.sleep(180)
