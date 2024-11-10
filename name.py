import json
import re
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
import time
import os
import subprocess
import signal

with open('config3.json') as config_file:
    config = json.load(config_file)

api_id = int(config['api_id'])
api_hash = config['api_hash']
bot_token = config['bot_token']

app = Client("name", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

def find_and_kill_bot():
    try:
        pid = int(subprocess.check_output(["pgrep", "-f", "name.py"]))
        
        os.kill(pid, signal.SIGTERM)
        print(f"Stopped bot with PID {pid}")
        
        time.sleep(2)
    except subprocess.CalledProcessError:
        print("Bot is not running.")

def start_bot():
    subprocess.Popen(["nohup", "python3", "name.py", "&"])
    print("Bot restarted.")

@app.on_message(filters.command("restart"))
def restart(client, message):
    find_and_kill_bot()
    start_bot()
    client.send_message(message.chat.id, "Bot restarted.")

@app.on_message(filters.text)
async def text_handler(client, message: Message):
    user_response = message.text.strip()

    match = re.match(r"^(\d+)\s*@(.+)$", user_response)
    if not match:
        await message.reply("لطفاً پیام را به فرمت صحیح وارد کنید:\n<episode_count>\n@<base_name>")
        return

    episode_count = int(match.group(1))
    base_name = match.group(2)

    resolutions = ["360p", "480p", "540p", "720p", "1080p"]

    for res in resolutions:
        count = 0
        for i in range(1, episode_count + 1):
            episode_name = f"@{base_name}.E{i:02}.{res}"
            await message.reply(f'`{episode_name}`')
            count += 1

            if count % 5 == 0:
                await asyncio.sleep(1)

app.run()
