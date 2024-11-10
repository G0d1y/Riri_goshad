import json
import re
from pyrogram import Client, filters
from pyrogram.types import Message
import time
import os
import subprocess
import signal
with open('config2.json') as config_file:
    config = json.load(config_file)

api_id = int(config['api_id'])
api_hash = config['api_hash']
bot_token = config['bot_token']

app = Client("sync", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

mkv_pattern = re.compile(r'https?://\S+\.mkv', re.IGNORECASE)
srt_pattern = re.compile(r'https?://\S+\.srt', re.IGNORECASE)

collecting_links = False
mkv_links = []
srt_links = []
names = []

def find_and_kill_bot():
    try:
        pid = int(subprocess.check_output(["pgrep", "-f", "sync.py"]))
        
        os.kill(pid, signal.SIGTERM)
        print(f"Stopped bot with PID {pid}")
        
        time.sleep(2)
    except subprocess.CalledProcessError:
        print("Bot is not running.")

def start_bot():
    subprocess.Popen(["nohup", "python3", "sync.py", "&"])
    print("Bot restarted.")

@app.on_message(filters.command("restart"))
def restart(client, message):
    find_and_kill_bot()
    start_bot()
    client.send_message(message.chat.id, "Bot restarted.")

@app.on_message(filters.command("start"))
async def start_collecting(client, message: Message):
    global collecting_links, mkv_links, srt_links, names
    collecting_links = True
    mkv_links = []
    srt_links = []
    names = []
    await message.reply("لینک هارا بفرست و بعد اسم و بعد /end .")

@app.on_message(filters.command("end"))
async def end_collecting(client, message: Message):
    global collecting_links, mkv_links, srt_links, names
    collecting_links = False

    if not mkv_links or not srt_links:
        await message.reply("اول لینک هارا بفرست")
        return

    if len(names) != len(mkv_links) or len(names) != len(srt_links):
        await message.reply("تعداد نام‌ها با تعداد لینک‌ها تطابق ندارد. لطفاً برای هر جفت لینک نام اضافه کنید.")
        return

    formatted_messages = [
        f"{mkv}\n\n{srt}\n\n{name}"
        for mkv, srt, name in zip(mkv_links, srt_links, names)
    ]

    for i in range(0, len(formatted_messages), 10):
        batch = formatted_messages[i:i+10]
        await message.reply("\n\n".join(batch))
    
    await message.reply("شروع مجدد /start")

    mkv_links = []
    srt_links = []
    names = []

@app.on_message(filters.text)
async def collect_links(client, message: Message):
    global collecting_links, mkv_links, srt_links, names
    if not collecting_links:
        return

    mkv_match = mkv_pattern.search(message.text)
    srt_match = srt_pattern.search(message.text)
    
    if mkv_match and not srt_match:
        mkv_links.append(mkv_match.group(0))
    elif srt_match and not mkv_match:
        srt_links.append(srt_match.group(0))
    elif mkv_match and srt_match:
        mkv_links.append(mkv_match.group(0))
        srt_links.append(srt_match.group(0))
    elif not mkv_match and not srt_match:
        names.append(message.text.strip())

app.run()
