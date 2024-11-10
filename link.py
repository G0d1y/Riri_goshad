import json
import re
from pyrogram import Client, filters 
from pyrogram.types import Message 
import time
import os
import subprocess
import signal

with open('config.json') as config_file:
    config = json.load(config_file)

api_id = int(config['api_id'])
api_hash = config['api_hash']
bot_token = config['bot_token']

app = Client("link", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

url_pattern = re.compile(r'https?://[^\s]+')

def find_and_kill_bot():
    try:
        pid = int(subprocess.check_output(["pgrep", "-f", "link.py"]))
        
        os.kill(pid, signal.SIGTERM)
        print(f"Stopped bot with PID {pid}")
        
        time.sleep(2)
    except subprocess.CalledProcessError:
        print("Bot is not running.")

def start_bot():
    subprocess.Popen(["nohup", "python3", "link.py", "&"])
    print("Bot restarted.")

@app.on_message(filters.command("restart"))
def restart(client, message):
    find_and_kill_bot()
    start_bot()
    client.send_message(message.chat.id, "Bot restarted.")

@app.on_message(filters.text)
def handle_message(client: Client, message: Message):
    urls = url_pattern.findall(message.text)
    
    if urls:
        for url in urls:
            client.send_message(
                chat_id=message.chat.id,
                text=f"`{url}`"
            )

app.run()
